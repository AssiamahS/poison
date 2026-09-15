# poison

Turn any topic, document, codebase or Mermaid diagram into a visual explanation from inside
Claude Code. One slash command, one picture.

```
/poison --style infographic The foundations of machine learning
```

Seven styles: whiteboard, infographic, presentation, diagram, mindmap, mindmap-structured,
mockup. Three fidelity levels, three complexity levels, a multi-frame mode that builds an idea
up over 3-5 images, and Mermaid input so an existing flowchart or sequence diagram can be
rendered in any style.

The image model is not the product. The skill first analyzes the content (core idea,
sub-topics, relationships, a visual metaphor per concept, a layout strategy, a color per
section), then writes a 400-800 word prompt from a style template that spells out every
position, icon, label, connector, color and typeface. That prompt is what produces images on
par with the visual summaries in NotebookLM or Gemini, from your own terminal, with your own
templates.

## Examples

| Whiteboard: How DNS resolution works | Infographic: Foundations of machine learning |
|---|---|
| <img src="examples/whiteboard-dns-1.png" width="560" alt="whiteboard"> | <img src="examples/infographic-ml-1.png" width="300" alt="infographic"> |

Both rendered with the default OpenRouter backend at about four cents each.

## Backends

| Backend | Env var | Default model | Cost per image | Notes |
|---|---|---|---|---|
| `openrouter` | `OPENROUTER_API_KEY` | `google/gemini-2.5-flash-image` | ~$0.04 | default when present; honors aspect ratio; occasional typos in small text |
| `openai` | `OPENAI_API_KEY` | `gpt-image-1.5` | $0.19-0.29 | exact pixel sizes, best text rendering |
| `gemini` | `GEMINI_API_KEY` | `gemini-2.5-flash-image` | free tier | direct Google API |

Auto-detection order is OpenRouter, OpenAI, Gemini. Force one with `--backend`, or pick any
model the backend accepts with `--model`, for example
`--backend openrouter --model google/gemini-3-pro-image` when small text must be perfect.

## Install

```bash
git clone https://github.com/AssiamahS/poison.git
cd poison
make install        # copies skill/ to ~/.claude/skills/poison
make check          # verifies python3, files, and that an API key is visible
```

Set at least one key in your shell profile:

```bash
export OPENROUTER_API_KEY="sk-or-..."   # openrouter.ai/keys
```

The skill is available as `/poison` in every Claude Code session immediately. The only
runtime dependency is `python3`; the generator uses the standard library.

## Usage

```
/poison [--style S] [--draw-level L] [--complexity C] [--mode M] [--from F] [--backend B] [--size WxH] [--output DIR] [--prefix NAME] <content>
```

```bash
/poison How DNS resolution works
/poison --style infographic The foundations of machine learning
/poison --draw-level sketch How Git branching works
/poison --style diagram --complexity detailed Kubernetes pod networking
/poison --style presentation --draw-level polished Microservices architecture
/poison --style mindmap The principles of object-oriented programming
/poison --style mindmap-structured Project management methodologies
/poison --style mockup --device desktop An admin dashboard with sidebar nav, stat cards and a data table
/poison --mode multi-frame The OAuth2 authorization code flow
/poison --style whiteboard --from mermaid-file docs/architecture.mmd
/poison --output ./docs/images --prefix arch System architecture of the payments service
```

Because it runs inside Claude Code, it composes with file reading:

```
Read docs/api-spec.md, then /poison --style diagram the request lifecycle it describes
Review src/ and /poison --style diagram --complexity detailed the module dependency graph
Read notes/retro.md and /poison --draw-level sketch a whiteboard of the takeaways
```

### Options

| Option | Values | Default |
|---|---|---|
| `--style` | `whiteboard` `infographic` `presentation` `diagram` `mindmap` `mindmap-structured` `mockup` | `whiteboard` |
| `--draw-level` | `sketch` `normal` `polished` | `normal` |
| `--complexity` | `simple` (3-4) `moderate` (5-7) `detailed` (8-12 concepts) | `moderate` |
| `--device` | `mobile` `tablet` `desktop` (mockup only) | `mobile` |
| `--mode` | `single` `multi-frame` | `single` |
| `--from` | `mermaid` `mermaid-file PATH` | none |
| `--backend` | `openrouter` `openai` `gemini` | auto |
| `--model` | any model id for the backend | backend default |
| `--size` | `1024x1024` `1536x1024` `1024x1536` or a ratio like `16:9` | by style |
| `--output` | directory | `./` |
| `--prefix` | filename prefix | `poison` |

## Layout

```
skill/
  SKILL.md                 the pipeline Claude follows: parse flags, read Mermaid, analyze, build prompt, generate, report
  styles/<style>.md        one prompt template per style, read on demand
  scripts/poison_gen.py    backend script: prompt file in, PNG out, prints a JSON line with path and cost
examples/                  rendered samples
Makefile                   install / uninstall / check / info
```

The generator can be used on its own:

```bash
python3 skill/scripts/poison_gen.py --prompt-file prompt.txt --size 1536x1024 --out ./out --prefix demo
# {"path": "./out/demo-1.png", "backend": "openrouter", "model": "google/gemini-2.5-flash-image", "size": "1536x1024", "cost": 0.0389}
```

## Credits

Shape of the idea and the style list come from Eric Blue's
[visual-explainer-skill](https://github.com/ericblue/visual-explainer-skill) (MIT). Templates,
pipeline and generator here are written from scratch, with OpenRouter as the default backend.

MIT.
