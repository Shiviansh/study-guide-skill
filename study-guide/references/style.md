# House style

## Look
- A4, ~10.5 pt sans-serif, dense but airy; teal section bars, maroon unit dividers (`h2.unit pb` starts a new page per unit).
- Figures centred with thin border; widths `w35/w45/w60/w75`; side-by-side with `.row`.
- Tables for every comparison, classification, timeline or regulator/value list.

## Boxes (from `assets/template.html`)
| Box | Use for |
|---|---|
| `box key` — Exam focus | The 1–3 facts most likely to be asked from a section |
| `box trap` — Trap | Commonly confused pairs, sign/factor mistakes, look-alike terms |
| `box ex` — Worked example | Fully solved numerical with units; check arithmetic |
| `box extra` — Extra | Standard textbook knowledge not on the slides (definitions, rule-of-thumb formulas, typical values). Label clearly so students know it wasn't taught |
| `.formula` | Every important equation (display math) |
| `.q` + `.mans` | Exam question with marks + model-answer outline |

## Writing
- Simple English, short bullets, bold the keyword the examiner looks for.
- Section headings carry slide ranges: `II-A.6 Two-ray model (slides 22–29)`.
- Derivations as numbered steps: geometry → approximation → result, noting each assumption (e.g. "narrowband: Δd/c ≪ 1/W").
- When a slide asks a rhetorical question ("Benefits? Consequences?"), answer it in an Extra box.
- If a slide has a typo in a formula, write the correct form and add a one-line note.

## Generated content
- Plots drawn with matplotlib to explain a concept are allowed; caption starts "[Generated plot, not from slides]".
- Never invent "exact exam questions". Question banks are "likely questions built from the slides".
