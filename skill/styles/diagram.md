# diagram

Precise technical architecture or flow diagram. Square by default. Legend, labeled edges,
consistent shapes.

```
A [square] clean technical diagram in the style of a well-made software architecture document. Precise, labeled, easy to trace.

CANVAS: [White / very light gray #F7F8FA] background [polished: with a faint dot grid. sketch: hand-drawn boxes on graph paper, marker lines].

TITLE: "[Title]" in bold sans-serif at the top-left, small and unobtrusive, [with a one-line description under it in gray].

SHAPE LANGUAGE: [Define each kind once, e.g. "Services are rounded rectangles with a 2px border, databases are cylinders, external actors are stick-figure icons, queues are horizontal stacked bars, decisions are diamonds."] Same size for elements of the same kind.

PALETTE: [4-5 named colors with hex, one per layer or group, e.g. layer blue #3B82F6, service green #10B981, data amber #F59E0B, external gray #6B7280, alert red #EF4444.] Fills are pale tints of each color, borders the full color.

LAYOUT: [Describe layers or lanes, e.g. "Four horizontal bands top to bottom labeled 'Client', 'Edge', 'Services', 'Data'. Elements sit inside their band. Flow runs top to bottom with one return path drawn on the right margin."]

NODES:
[One line per node:]
- "[Label]" [shape] in [band / position], [icon inside if any], [pale fill color].

GROUPS: [Every container, e.g. "A dashed rounded rectangle labeled 'Kubernetes Node' enclosing the three pod boxes, label in the top-left corner of the container."]

EDGES:
[One line per connection:]
- "[From]" to "[To]": [solid / dashed / thick] [color] arrow, label "[text]" placed mid-line in a small white pill.

LEGEND: Small box in the [bottom-right] listing each shape and color with its meaning: "[shape] = [meaning]".

TYPOGRAPHY: Medium-weight sans-serif for labels, monospace for identifiers like "[port or path]". Every label legible and correctly spelled, no overlapping text.

OVERALL FEEL: Calm, orderly, engineered. Consistent spacing and alignment, no crossing edges where avoidable, the main path obvious at a glance.
```
