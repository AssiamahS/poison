# Writing the SVG yourself (claude backend, $0)

With the `claude` backend there is no image model. You are the renderer: after the
analysis, write a complete SVG that realizes the chosen `styles/<style>.md` template, save
it, and call `poison_gen.py --svg-file` to rasterize it. Every rule in the style template
still applies (positions, icons, connectors, palette, typography, overall feel). This file
covers the mechanics that make hand-written SVG look good.

## Canvas

Use a `viewBox` with the style's default aspect and no fixed width/height:

| Size | viewBox |
|---|---|
| 1536x1024 (landscape) | `0 0 1536 1024` |
| 1024x1536 (portrait) | `0 0 1024 1536` |
| 1024x1024 (square) | `0 0 1024 1024` |

Start with `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" font-family="...">`
and a full-bleed background `<rect>` as the first child. Keep a 48px safe margin.

## Fonts (installed on macOS, no downloads)

| Role | font-family |
|---|---|
| whiteboard / mindmap / sketch headings | `'Marker Felt', 'Chalkboard SE', 'Comic Sans MS', cursive` |
| whiteboard body notes | `'Chalkboard SE', 'Bradley Hand', 'Comic Sans MS', cursive` |
| infographic / presentation / diagram / mockup / mindmap-structured | `'Avenir Next', 'Helvetica Neue', Helvetica, Arial, sans-serif` |
| code, ports, identifiers | `Menlo, 'SF Mono', monospace` |

Always give a fallback stack. Set `font-family` once on the root and override per group.

## Text rules (the part image models get wrong, you must not)

- SVG has no automatic wrapping. Break lines yourself with one `<text>` per line or `<tspan x=".." dy="1.2em">`.
- Budget characters per line from font size: roughly `line_width_px / (0.55 * font_size)`. At 22px a 300px-wide box fits about 24 characters.
- Center with `text-anchor="middle"`; align to boxes with `dominant-baseline="middle"` only on single lines.
- Sizes that stay legible at 1536px wide: title 48-64, section heads 28-34, body 20-24, captions 16-18. Never below 15.
- Spell-check by reading the text back before rendering. Typos are the one thing this backend must never produce.

## Hand-drawn look (whiteboard, sketch draw level, mindmap)

Define once in `<defs>` and apply with `filter="url(#rough)"` to strokes and boxes, not to text:

```svg
<filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="4" xChannelSelector="R" yChannelSelector="G"/>
</filter>
```

- `scale` 3-4 = normal, 6-8 = sketch, 0 (no filter) = polished.
- Marker strokes: `stroke-width` 5-7, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`.
- Draw boxes as slightly irregular `<path>` polygons, not perfect `<rect>`, when draw level is sketch.
- Doodles are 3-8 primitives each: a star is one `<polygon>`, a lightbulb is a circle plus a small rect, sparkles are three short lines.

## Connectors

Put arrowheads in `<defs>` once per color:

```svg
<marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 z" fill="#2563EB"/>
</marker>
```

Curved arrows are quadratic paths: `<path d="M x1,y1 Q cx,cy x2,y2" marker-end="url(#arrow-blue)"/>`.
Edge labels sit on a small white pill: a `<rect rx="8" fill="#fff">` under a `<text>`.
Dotted = `stroke-dasharray="8 8"`, thick = width 7, thin = width 2.5.

## Icons

Draw every icon from primitives inside a `<g transform="translate(x,y) scale(s)">` on a
64x64 design grid, two-tone (fill in the section color, darker stroke). Reliable shapes:
server/db = stacked `<ellipse>` + `<rect>`; document = rect with folded corner path;
shield = path; gear = circle with 8 short rects rotated; person = circle head + rounded
rect body; padlock = rect body + arc path; funnel = trapezoid path + rect spout; envelope
= rect + V path; laptop = two rects; brain/cloud = overlapping circles. Do not rely on
emoji or external images; renderers differ.

## Layout helpers

- Radial (mindmap): center at (768,512); branch k of n leaves at angle `-90 + k*360/n` degrees, endpoint radius 330-380, labels 40px beyond.
- Left-to-right flow: n stations at x = margin + k*(W-2*margin)/(n-1), boxes 220-260 wide.
- Cards (infographic): full-width cards 120-160 tall with 24px gaps, number badge 56px circle at the left edge.
- Lanes (diagram): equal-height horizontal bands with a 20% tinted fill and a label in the top-left.
- Mockup: draw the device frame first (phone: 420x860 rounded rect rx=48 centered; desktop: 1400x860 browser window with a 44px tab bar), then lay out inside it on an 8px grid.

## Checklist before rasterizing

- `xmlns` present, one root `<svg>`, background rect first.
- All text inside the viewBox, no line longer than its box.
- Every `url(#id)` reference has a matching `<defs>` entry.
- Palette limited to the style's 4-6 colors plus text and background.
- Read the whole SVG once for spelling and balanced tags, then render.
