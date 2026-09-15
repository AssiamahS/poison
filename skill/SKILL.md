---
name: poison
description: Turn any topic, document, codebase or Mermaid diagram into a visual explanation image (whiteboard sketch, infographic, presentation slide, technical diagram, mind map, UI mockup). Use when the user says visualize, explain visually, draw this, make an infographic, whiteboard this, mind map, wireframe, or mockup.
argument-hint: "[--style whiteboard|infographic|presentation|diagram|mindmap|mindmap-structured|mockup] [--draw-level sketch|normal|polished] [--complexity simple|moderate|detailed] [--mode single|multi-frame] [--from mermaid|mermaid-file PATH] [--backend openrouter|openai|gemini] [--size WxH] [--output DIR] [--prefix NAME] <content>"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# poison

One command, one picture. The image model is not the product; the analysis and the
spatial spec are. Every run spends most of its effort on analysis, then either draws the
picture itself as SVG (default `claude` backend, no API, $0, runs on the session you are
already paying for) or writes a 400-800 word prompt for an image model (`openrouter`,
`openai`, `gemini`). `scripts/poison_gen.py` turns either into a PNG.

## Usage

```
/poison How DNS resolution works                                  # whiteboard (default)
/poison --style infographic The foundations of machine learning
/poison --style diagram --complexity detailed Kubernetes pod networking
/poison --style mindmap The principles of object-oriented programming
/poison --style mindmap-structured Project management methodologies
/poison --style presentation --draw-level polished Microservices architecture
/poison --style mockup --device desktop An admin dashboard with sidebar, stat cards, table
/poison --mode multi-frame The OAuth2 authorization code flow
/poison --mode video --narrate How a CPU executes an instruction         # animated MP4, spoken
/poison --style whiteboard --from mermaid-file docs/architecture.mmd
/poison --backend openai --style infographic How vaccines train the immune system
```

## Arguments

`$ARGUMENTS` holds the raw string. Pull out the flags below; everything left over, joined
with spaces, is the content.

| Flag | Default | Values |
|---|---|---|
| `--style` | `whiteboard` | `whiteboard`, `infographic`, `presentation`, `diagram`, `mindmap`, `mindmap-structured`, `mockup` |
| `--draw-level` | `normal` | `sketch` (rough, playful), `normal`, `polished` (clean, professional) |
| `--complexity` | `moderate` | `simple` (3-4 concepts), `moderate` (5-7), `detailed` (8-12) |
| `--device` | `mobile` | `mobile`, `tablet`, `desktop`; only for `--style mockup` |
| `--mode` | `single` | `single`, `multi-frame` (3-5 images that build the idea up), or `video` (multi-frame rendered into an animated MP4 with Remotion) |
| `--narrate` | off | with `--mode video`: speak each frame's narration line with macOS `say` (free, offline) |
| `--voice` | `Samantha` | `say` voice for `--narrate` |
| `--from` | none | `mermaid` (content is Mermaid) or `mermaid-file PATH` |
| `--backend` | `claude` | `claude` (SVG drawn in-session, free), `openrouter`, `openai`, `gemini` |
| `--model` | backend default | any model id the backend accepts |
| `--size` | by style | `1024x1024`, `1536x1024`, `1024x1536`, or a ratio such as `16:9` |
| `--output` | `./` | directory for the PNGs |
| `--prefix` | `poison` | filename prefix, files are `PREFIX-N.png` |

Default sizes: whiteboard, presentation, mindmap, mindmap-structured = `1536x1024`;
infographic = `1024x1536`; diagram = `1024x1024`; mockup = `1024x1536` for mobile and
tablet, `1536x1024` for desktop.

## Step 1: Resolve the backend

The script lives next to this file. Locate it once:

```bash
POISON_GEN="$(dirname "$(realpath ~/.claude/skills/poison/SKILL.md)")/scripts/poison_gen.py"
python3 "$POISON_GEN" --dry-run --size <size> --backend claude --svg-file x.svg   # default
python3 "$POISON_GEN" --dry-run --size <size> --backend <openrouter|openai|gemini> [--model Y]
```

The backend is `claude` unless the user passed `--backend`. With `claude` you draw the
SVG yourself and the script rasterizes it locally (rsvg-convert, then headless Chromium,
then macOS qlmanage); the dry run confirms a renderer exists. For the API backends the
dry run prints the resolved model and aspect ratio, or exits 2 with setup instructions
when the key is missing (a key whose value is `none` counts as unset). Tell the user which
backend was picked in one line, then keep going. If the script exits 2, show its message
and stop.

If no content was given, ask what to visualize and stop.

## Step 2: Read Mermaid input when present

Treat the input as Mermaid when `--from mermaid` or `--from mermaid-file` is given, or
when the content starts with `graph`, `flowchart`, `sequenceDiagram`, `classDiagram`,
`stateDiagram`, `erDiagram`, `gantt`, `pie`, `mindmap`, `timeline`, or sits in a
```` ```mermaid ```` fence. For `mermaid-file`, Read the file first.

Extract, and write out:

- every node with id, label and shape hint (`[ ]` box, `( )` rounded, `{ }` decision, `[( )]` cylinder, `(( ))` circle)
- every edge with source, target, arrow type (solid, dotted, thick, two-way) and label
- every `subgraph` as a named group with its members
- for sequence diagrams: participants, aliases, message order, `alt`/`loop` blocks
- for class and ER diagrams: entities, fields, methods, relationships, cardinality
- for gantt and timeline: sections, tasks, dates, milestones
- the `title` directive if present, otherwise infer one

Auto-pick a style only when the user gave none: flowchart, sequence, state and class
diagrams lean `diagram`; gantt, pie and timeline lean `infographic`; Mermaid `mindmap`
leans `mindmap`. A user-specified style always wins, any Mermaid type renders in any style.

Mermaid gives you exact structure, so the prompt gets more precise, never looser: each
node is a labeled element, each edge is a drawn connector with its label, each subgraph is
a visible container.

## Step 3: Analyze the content

Write this analysis out before touching a prompt. It is the step that decides quality.

1. **Core idea** in one sentence. This becomes the title.
2. **Sub-topics**, count set by `--complexity`. Each gets a short title and 1-3 key points in the exact words that should appear in the image.
3. **Relationship type** between them: sequence, hierarchy, cause and effect, comparison, part to whole, cycle. Name the specific links (A causes B, C contains D).
4. **A visual metaphor per sub-topic**: a concrete object the model can draw (shield for security, funnel for filtering, river with tributaries for data merging, ladder for scaling).
5. **Layout strategy** matched to the relationship type: left-to-right for sequences, top-down tree for hierarchies, radial for hub-and-spoke, two columns for comparisons, ring for cycles, grid for unordered sets.
6. **Color assignment**: one named color per sub-topic, plus a background and a title color.

Keep total on-image text modest. Image models render short labels well and paragraphs badly. Prefer 2-6 words per label, under about 60 words of visible text for `simple`, about 120 for `detailed`.

## Step 4a (claude backend): Draw the SVG from the style template

Read `styles/<style>.md` and `styles/svg-guide.md` (both relative to this file). The
style template is your spec: realize every paragraph of it in SVG. Canvas and background
from CANVAS, the title from TITLE, positions from LAYOUT, one group per SECTION with its
icon drawn from primitives and its exact text, every CONNECTION as a path with an
arrowhead and a label, DECORATIONS as small primitive doodles, the PALETTE as your only
colors, TYPOGRAPHY via the font stacks in the guide, and the rough filter at the strength
the draw level asks for. Break lines by hand, keep text inside its box, and read the whole
file back for spelling before saving. Save as `<output>/<prefix>-<n>.svg`, then go to
Step 6. Skip Step 4b.

## Step 4b (API backends): Build the prompt from the style template

Read `styles/<style>.md` (relative to this file) and fill it in from the analysis. The
result must be 400-800 words and every bracketed placeholder must be replaced with
content-specific detail. Rules that apply to every style:

- Give each element a position: top-left, center, lower-right band, second column.
- Name every icon and illustration concretely. "A cracked padlock with a red X" beats "a security icon".
- Quote the exact text that must appear, in double quotes, and say where it goes.
- Name colors specifically. Hex codes are welcome in infographic, presentation, diagram and mockup styles.
- Describe typography: marker hand-lettering, bold geometric sans, monospace labels.
- Describe every connector: shape, color, thickness, direction, label.
- End with an overall-feel paragraph and one line on where the eye should travel.
- State the canvas orientation in words (landscape, portrait, square) so backends that ignore size flags still get it right.
- Never ask for watermarks, logos of real companies, or real people's likenesses.

Apply `--draw-level` inside the template: `sketch` adds visible imperfection, marker
smudges, uneven lettering, more doodles; `polished` removes them and asks for consistent
spacing and crisp edges. The draw level changes whiteboard, presentation and mockup a
lot, the other styles only slightly.

Run the checklist before generating. The prompt must contain: canvas description, title
text and styling, spatial layout, every section with title, icon and text, connectors,
named colors, typography, decorations fitting the style, overall feel, and at least 300
words. If anything is missing, add it.

## Step 5: Multi-frame mode

For `--mode multi-frame`, plan 3-5 frames before generating anything:

- Frame 1 introduces the title and the core idea with the layout skeleton visible but mostly empty.
- Middle frames add sub-topics in the order the relationship implies, keeping every earlier element in place.
- The last frame is the complete picture with a one-line summary banner.

With the `claude` backend, write frame 1 as a full SVG and produce each later frame by
copying the previous file and adding groups, so earlier elements never move. With API
backends, write a separate full prompt per frame that repeats the same canvas, palette,
typography and layout paragraphs word for word, then states "This is frame N of M; the
following elements are present:" followed by the cumulative list, and warn the user that
multi-frame costs one API call per frame.

## Step 5b: Video mode (Remotion)

`--mode video` is multi-frame plus animation. Plan and draw the 3-5 cumulative frames
exactly as in Step 5 with the `claude` backend (API backends work too, one call per
frame). For each frame also write:

- a caption of at most 12 words, shown in a pill over the bottom 110px of the frame, so keep that band of every frame free of content
- a narration line of 1-2 spoken sentences when `--narrate` is on (plain words, no
  symbols or code; `say` reads it aloud)

Save the frames as `<output>/<prefix>-<n>.svg` (or PNG for API backends), then write
`<output>/<prefix>-frames.json`:

```json
[
  {"image": "<output>/<prefix>-1.svg", "caption": "The setup", "narration": "Three actors take part: the user, the app, and the auth server."},
  {"image": "<output>/<prefix>-2.svg", "caption": "...", "narration": "..."}
]
```

and render:

```bash
python3 "$(dirname "$POISON_GEN")/poison_video.py" --title "<Title>" --frames <output>/<prefix>-frames.json --out <output> --prefix <prefix> [--narrate] [--voice Samantha] [--seconds-per-frame 4]
```

The first run installs Remotion inside the skill's `video/` folder (a few hundred MB,
needs Node 20+); say so before running it. The script reuses a Chromium already on disk
(Chrome, Playwright) so Remotion does not download one. It prints a JSON line with the
MP4 path and total seconds. Frame length follows the narration audio when narrated,
otherwise `--seconds-per-frame`. A one-second title card opens the video.

Check the result by reading a still or two: extract with
`ffmpeg -y -ss 3 -i <mp4> -frames:v 1 <png>` when ffmpeg exists, otherwise trust the
frame PNGs you already inspected.

## Step 6: Generate

`claude` backend, one call per SVG:

```bash
python3 "$POISON_GEN" --svg-file <output>/<prefix>-<n>.svg --size <size> --out <output> --prefix <prefix> --index <n>
```

API backends: write each prompt to a temp file (long prompts do not survive shell
quoting), then call the script once per image:

```bash
PROMPT_FILE=$(mktemp -t poison-prompt)
cat > "$PROMPT_FILE" <<'PROMPT'
<the full prompt>
PROMPT
python3 "$POISON_GEN" --prompt-file "$PROMPT_FILE" --size <size> --out <output> --prefix <prefix> --index <n> --backend <X> [--model Y]
```

The script prints one JSON line with `path`, `backend`, `model`, `size` and `cost`
(`claude` reports 0, OpenRouter reports real cost, the others report null). Exit 1 means the API failed and
stderr has the reason. On failure report the error once, then suggest either a simpler
`--complexity`, a shorter topic, or another `--backend`. Do not silently retry with a
changed prompt.

Read the generated PNG with the Read tool and check it against the analysis: title
present, section count right, text legible, nothing overlapping or clipped. With the
`claude` backend fix any layout defect in the SVG and re-render (it is free). With API
backends, if a section is missing or text is garbled, say so in the summary rather than
regenerating on your own; offer to regenerate.

## Step 7: Report

Save a markdown companion next to the image when the user asked for one, otherwise just
print it:

```
## poison: <Title>
Style: <style> | Draw level: <level> | Complexity: <complexity> | Backend: <backend/model> | Size: <size>

### Sections
1. <Section> — <one line>
...

### Relationships
- <A> -> <B>: <how>

### Files
<png path> [and <svg path>] [and <mp4 path>, <n> s] (cost: $<n>)
```

Close with one or two concrete refinement suggestions that fit the content, such as
`--draw-level sketch` for a more casual feel or `--style diagram` when the topic is a
process.

## Notes

- Text-heavy content reads best as `infographic`; processes as `diagram`; fun explanations as `whiteboard`; taxonomies as `mindmap` or `mindmap-structured`; screens as `mockup`.
- `claude` is free, deterministic, always spells correctly and leaves an editable SVG next to the PNG; it looks like a clean illustration rather than a photo of a whiteboard. Use an API backend when the user wants painterly, photographic or textured output.
- OpenRouter `google/gemini-2.5-flash-image` costs about $0.04 per image and honors aspect ratio. `google/gemini-3-pro-image` renders text more reliably at roughly 4x the price. OpenAI `gpt-image-1.5` costs $0.19-0.29 and honors exact pixel sizes.
- Costs are per image; multi-frame multiplies them.
