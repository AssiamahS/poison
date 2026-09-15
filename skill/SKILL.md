---
name: poison
description: Turn any topic, document, codebase or Mermaid diagram into a visual explanation image (whiteboard sketch, infographic, presentation slide, technical diagram, mind map, UI mockup). Use when the user says visualize, explain visually, draw this, make an infographic, whiteboard this, mind map, wireframe, or mockup.
argument-hint: "[--style whiteboard|infographic|presentation|diagram|mindmap|mindmap-structured|mockup] [--draw-level sketch|normal|polished] [--complexity simple|moderate|detailed] [--mode single|multi-frame] [--from mermaid|mermaid-file PATH] [--backend openrouter|openai|gemini] [--size WxH] [--output DIR] [--prefix NAME] <content>"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# poison

One command, one picture. The image model is not the product; the prompt is. Every run
spends most of its effort on analysis and on writing a 400-800 word, spatially explicit
prompt from a style template, then hands that prompt to `scripts/poison_gen.py`.

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
| `--mode` | `single` | `single` or `multi-frame` (3-5 images that build the idea up) |
| `--from` | none | `mermaid` (content is Mermaid) or `mermaid-file PATH` |
| `--backend` | auto | `openrouter`, `openai`, `gemini` |
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
python3 "$POISON_GEN" --dry-run --size <size> [--backend X] [--model Y]
```

The dry run prints the resolved backend, model and aspect ratio, or exits 2 with setup
instructions when no key is present. Detection order is `OPENROUTER_API_KEY`, then
`OPENAI_API_KEY`, then `GEMINI_API_KEY`. A key whose value is `none` counts as unset.
Tell the user which backend was picked in one line, then keep going. If the script exits
2, show its message and stop.

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

## Step 4: Build the prompt from the style template

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

Write a separate full prompt per frame. Each prompt repeats the same canvas, palette,
typography and layout paragraphs word for word, then states "This is frame N of M; the
following elements are present:" followed by the cumulative list. Warn the user that
multi-frame costs one API call per frame.

## Step 6: Generate

Write each prompt to a temp file (long prompts do not survive shell quoting), then call
the script once per image:

```bash
PROMPT_FILE=$(mktemp -t poison-prompt)
cat > "$PROMPT_FILE" <<'PROMPT'
<the full prompt>
PROMPT
python3 "$POISON_GEN" --prompt-file "$PROMPT_FILE" --size <size> --out <output> --prefix <prefix> --index <n> [--backend X] [--model Y]
```

The script prints one JSON line with `path`, `backend`, `model`, `size` and `cost`
(OpenRouter reports real cost; the others report null). Exit 1 means the API failed and
stderr has the reason. On failure report the error once, then suggest either a simpler
`--complexity`, a shorter topic, or another `--backend`. Do not silently retry with a
changed prompt.

Read the generated PNG with the Read tool and check it against the analysis: title
present, section count right, text legible. If a section is missing or text is garbled,
say so in the summary rather than regenerating on your own; offer to regenerate.

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
<path> (cost: $<n>)
```

Close with one or two concrete refinement suggestions that fit the content, such as
`--draw-level sketch` for a more casual feel or `--style diagram` when the topic is a
process.

## Notes

- Text-heavy content reads best as `infographic`; processes as `diagram`; fun explanations as `whiteboard`; taxonomies as `mindmap` or `mindmap-structured`; screens as `mockup`.
- OpenRouter default `google/gemini-2.5-flash-image` costs about $0.04 per image and honors aspect ratio. `google/gemini-3-pro-image` renders text more reliably at roughly 4x the price. OpenAI `gpt-image-1.5` costs $0.19-0.29 and honors exact pixel sizes.
- Costs are per image; multi-frame multiplies them.
