# mockup

UI wireframe or high-fidelity screen. `--device` sets the frame, `--draw-level` sets
fidelity: sketch = paper wireframe, normal = mid-fi gray boxes with real labels, polished =
Figma-quality.

```
A [portrait / landscape] UI [wireframe / mockup] of a [mobile app screen / tablet screen / desktop web app] shown inside a [phone frame with rounded corners and a status bar / tablet frame / browser window with tab bar and address field], centered on a [light gray #ECEFF3 / white] backdrop with a soft shadow.

FIDELITY: [sketch: hand-drawn pencil wireframe on paper, rough boxes, squiggle placeholders for text, scribbled icons. normal: clean gray-box wireframe, 1px borders, real labels, simple line icons, no color except one accent. polished: production-quality interface with a real palette, typography, elevation, imagery placeholders rendered as soft gradients.]

SCREEN: "[Screen name]" for [audience or product in one phrase].

STRUCTURE, top to bottom [or: left sidebar then main area]:
[One block per region:]
- [Region, e.g. "Top bar"]: [contents, e.g. "back chevron on the left, title 'Settings' centered, 'Save' text button on the right in the accent color"].
- [Region, e.g. "Profile block"]: [contents with exact labels in quotes and element types: avatar circle 72px, name text field labeled 'Display name' with placeholder 'Sylvester', ...].
- [Region]: [contents].
- [Bottom nav / footer]: [items with labels and icons].

COMPONENTS: [List every control type used once with its look: primary button pill in accent, secondary outline button, toggle switches, list rows with chevrons, cards with 12px radius and subtle shadow, data table with zebra rows.]

STATES: [Anything shown active, selected, filled, or with an error, e.g. "the 'Notifications' toggle is on, the second tab is selected".]

PALETTE: [polished: primary #2563EB, surface white, background #F8FAFC, text #0F172A, muted #64748B, success #16A34A. normal: grays plus one accent. sketch: pencil gray on paper.]

TYPOGRAPHY: [System sans-serif, 28px screen title, 16px body, 12px captions; all labels real words, legible, spelled correctly.]

OVERALL FEEL: [polished: a screen ready for design review, pixel-precise spacing on an 8px grid. normal: clear enough to hand to a developer. sketch: a whiteboard-session wireframe for brainstorming.] No lorem ipsum, no overlapping elements.
```
