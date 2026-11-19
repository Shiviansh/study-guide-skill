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
- **Plain language is the default** (user asked for this), **but never replace the course's keywords.** Write for a student meeting the topic for the first time, in a way that still scores marks:
  - Keep every term, definition phrase and label exactly as the slides/teacher word it (e.g. "restrict output", "homogeneous", "differentiated", "under/over-allocates", "unpriced by-product", "third party", "offset (countervail)", "overconsumption", "irretrievable costs", "hidden information"). The examiner marks these words. Never swap them for a simpler synonym.
  - Make it simple by *adding*, not replacing: put the slide wording first in bold, then a plain gloss in brackets or the next sentence ("**restrict output** (sell less)").
  - Plain wording is for the explanation around the keywords: short sentences, everyday words in connecting text, jargon explained on first use.
  - Add a green `box key` titled "In simple words" where an idea is easy to lose (the intuition), before the "Exam focus" box.
  - **Spell out every abbreviation and symbol at its first use** in the notes (e.g. "MPB (marginal private benefit)", "CR4 (four-firm concentration ratio)", "NPPA (National Pharmaceutical Pricing Authority)", "AVC (average variable cost)"), in the one-liners too, and again in the first caption/example if far from the first use. Also add an "Abbreviations (full forms)" table (short form | full form) at the start of the formula-sheet section, and in any interactive quiz as a collapsible list. Never leave MSB, MPB, ATC, HHI-style letters unexplained.
  - Worked examples as numbered steps ("Step 1, what the market does: ...").
  - Table cells, one-liners, rapid-fire answers, traps and formula-sheet rows keep the slide keywords too; only shorten the connecting words.
  - Plain does not mean vague: keep every number, condition and exam keyword intact.
- Short bullets, bold the keyword the examiner looks for.
- Section headings carry slide ranges: `II-A.6 Two-ray model (slides 22–29)`.
- Derivations as numbered steps: geometry → approximation → result, noting each assumption (e.g. "narrowband: Δd/c ≪ 1/W").
- When a slide asks a rhetorical question ("Benefits? Consequences?"), answer it in an Extra box.
- If a slide has a typo in a formula, write the correct form and add a one-line note.

## Generated content
- Plots drawn with matplotlib to explain a concept are allowed; caption starts "[Generated plot, not from slides]".
- Never invent "exact exam questions". Question banks are "likely questions built from the slides".
