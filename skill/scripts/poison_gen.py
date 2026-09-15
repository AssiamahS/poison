#!/usr/bin/env python3
"""poison image backend — one prompt in, one PNG out.

Backends (auto-detected from env, or forced with --backend):
  openrouter  OPENROUTER_API_KEY  google/gemini-2.5-flash-image (default, ~$0.04/img)
  openai      OPENAI_API_KEY      gpt-image-1.5 (~$0.19-0.29/img)
  gemini      GEMINI_API_KEY      gemini-2.5-flash-image (direct, free tier)

Usage:
  poison_gen.py --prompt-file p.txt --size 1536x1024 --out ./ --prefix poison --index 1
  cat p.txt | poison_gen.py --size 1024x1024

Prints one JSON line on success: {"path", "backend", "model", "size", "cost"}.
Exit 2 = config problem (no key / bad args), exit 1 = API failure.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

SIZES = {"1024x1024": "1:1", "1536x1024": "3:2", "1024x1536": "2:3"}
RATIOS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"}
DEFAULT_MODEL = {
    "openrouter": "google/gemini-2.5-flash-image",
    "openai": "gpt-image-1.5",
    "gemini": "gemini-2.5-flash-image",
}
KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def env_key(name):
    v = os.environ.get(name, "").strip()
    return v if v and v.lower() not in ("none", "null", "unset") else ""


def detect_backend(forced):
    if forced:
        if not env_key(KEY_ENV[forced]):
            die(2, f"--backend {forced} needs {KEY_ENV[forced]} in the environment")
        return forced
    for b in ("openrouter", "openai", "gemini"):
        if env_key(KEY_ENV[b]):
            return b
    die(2, "no image API key found. Set one of:\n"
           "  export OPENROUTER_API_KEY=...   # openrouter.ai/keys (default, cheapest)\n"
           "  export OPENAI_API_KEY=sk-...    # platform.openai.com/api-keys\n"
           "  export GEMINI_API_KEY=AIza...   # aistudio.google.com/apikey")


def die(code, msg):
    print(f"poison: {msg}", file=sys.stderr)
    sys.exit(code)


def post(url, headers, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")[:600]
            last = f"HTTP {e.code}: {text}"
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            break
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
    die(1, f"request failed: {last}")


def gen_openrouter(prompt, model, ratio, key):
    d = post(
        "https://openrouter.ai/api/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
         "HTTP-Referer": "https://github.com/AssiamahS/poison", "X-Title": "poison"},
        {"model": model,
         "messages": [{"role": "user", "content": prompt}],
         "modalities": ["image", "text"],
         "max_tokens": 2048,  # one image is ~1290 output tokens; a low cap keeps the credit reservation small
         "image_config": {"aspect_ratio": ratio}},
    )
    if "error" in d:
        die(1, f"openrouter error: {d['error']}")
    msg = d["choices"][0]["message"]
    imgs = msg.get("images") or []
    if not imgs:
        die(1, f"openrouter returned no image (text was: {(msg.get('content') or '')[:200]!r})")
    url = imgs[0]["image_url"]["url"]
    raw = base64.b64decode(url.split(",", 1)[1])
    return raw, d.get("usage", {}).get("cost")


def gen_openai(prompt, model, size, key):
    d = post(
        "https://api.openai.com/v1/images/generations",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        {"model": model, "prompt": prompt, "size": size, "quality": "high", "output_format": "png"},
        timeout=300,
    )
    if "error" in d:
        die(1, f"openai error: {d['error']}")
    b64 = d["data"][0].get("b64_json")
    if not b64:
        die(1, "openai returned no b64_json")
    return base64.b64decode(b64), None


def gen_gemini(prompt, model, ratio, key):
    d = post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        {"Content-Type": "application/json"},
        {"contents": [{"parts": [{"text": prompt}]}],
         "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                              "imageConfig": {"aspectRatio": ratio}}},
    )
    if "error" in d:
        die(1, f"gemini error: {d['error']}")
    for part in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"]), None
    die(1, "gemini returned no inline image")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt-file", help="file holding the prompt (default: stdin)")
    ap.add_argument("--backend", choices=list(DEFAULT_MODEL))
    ap.add_argument("--model", help="override the backend's default model")
    ap.add_argument("--size", default="1536x1024",
                    help="1024x1024 | 1536x1024 | 1024x1536 | or an aspect ratio like 16:9")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--prefix", default="poison")
    ap.add_argument("--index", type=int, default=1, help="frame number for the filename")
    ap.add_argument("--dry-run", action="store_true", help="resolve config, print it, do not call the API")
    a = ap.parse_args()

    if a.size in SIZES:
        size, ratio = a.size, SIZES[a.size]
    elif a.size in RATIOS:
        size, ratio = a.size, a.size
    else:
        die(2, f"bad --size {a.size!r}; use {', '.join(SIZES)} or a ratio like 16:9")

    backend = detect_backend(a.backend)
    model = a.model or DEFAULT_MODEL[backend]
    if backend == "openai" and size not in SIZES:
        die(2, "openai only accepts 1024x1024, 1536x1024 or 1024x1536")

    if a.dry_run:
        print(json.dumps({"backend": backend, "model": model, "size": size, "ratio": ratio}))
        return

    prompt = open(a.prompt_file).read() if a.prompt_file else sys.stdin.read()
    prompt = prompt.strip()
    if len(prompt) < 40:
        die(2, "prompt is empty or far too short; poison prompts are 400-800 words")

    key = env_key(KEY_ENV[backend])
    if backend == "openrouter":
        raw, cost = gen_openrouter(prompt, model, ratio, key)
    elif backend == "openai":
        raw, cost = gen_openai(prompt, model, size, key)
    else:
        raw, cost = gen_gemini(prompt, model, ratio, key)

    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, f"{a.prefix}-{a.index}.png")
    with open(path, "wb") as f:
        f.write(raw)
    print(json.dumps({"path": path, "backend": backend, "model": model, "size": size, "cost": cost}))


if __name__ == "__main__":
    main()
