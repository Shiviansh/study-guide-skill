---
name: study-guide
description: Turn lecture slides, PDF/handwritten notes, PPTs, lecture videos and the course file (CIF / syllabus / course handout) into exam-ready study guide PDFs organised by the CIF, with figures copied from the actual slides and video frames, step-by-step derivations, worked numericals, formula sheets, traps and question banks. Use this whenever the user wants notes, a study guide, revision material, a cheat sheet, MCQs, practice questions or "prep" for a quiz, midterm, mid-sem, endterm, end-sem, final, viva or test from their class material — even if they just drop PDFs/PPTs/videos and say "make notes", "explain these for my exam tomorrow", "questions to mug up" or "merge everything for the endterm".
---

# Study Guide

Builds a polished, printable PDF study guide from a student's course material. The output style was designed with a real student and they liked it: dense but readable, every diagram taken from their own slides, every formula boxed, and exam-oriented extras (formula sheet, numbers, traps, question bank).

The toolkit is `scripts/studytool.py` (run `python <skill-dir>/scripts/studytool.py` with no args for help). It needs `pip install pymupdf pillow` and a Chromium browser (Edge/Chrome) for PDF printing.

## 1. Pick the mode from the user's words

| User says | Mode | What to emphasise |
|---|---|---|
| quiz, MCQ, short test, "questions to mug up" | **quiz** | Concise explanations, one-liners, rapid-fire Q→A bank, 50+ MCQs with answer key |
| midterm, mid-sem, viva | **midterm** | Full explanations, derivation chains, solved numericals, long-answer question bank with model answers |
| endterm, end-sem, final | **endterm** | Midterm style **plus** merge every earlier guide for the course into one PDF |
| notes, explain, summary (no exam word) | **notes** | Explanations + figures + formula sheet + traps, no question bank unless asked |
| cheat sheet, last night, formula sheet | **cheatsheet** | 2–4 pages: formulas, numbers, traps, one-liners only |

If the exam is tomorrow / in N hours, add a short revision plan (order + time per unit) to the cover. Full per-mode section lists are in `references/modes.md` — read it once you know the mode.

## 2. Read everything before writing

Start with the course file (CIF / syllabus / handout) if there is one: it fixes the unit and topic order of the guide and says which units each exam covers (e.g. "Mid Term: CO1–CO3"). Map every CIF topic to the notes/videos that cover it. Anything in the exam's scope that the user did not provide must be called out on the cover, because a student revising from the guide will otherwise assume it's complete.

Then read every page of every file (PDF reader ≤20 pages per call — take the time, skipping slides is how guides end up with holes).

Other sources — details in `references/sources.md`, read it whenever there are videos, scans or PPTs:
- `.pptx` → `pptx2pdf`.
- Scanned/handwritten notes → `ocr` for text, still view the pages for diagrams.
- Lecture videos → `transcribe` (GPU-accelerated when an NVIDIA card exists), `frames` (scene-change capture, duplicates removed) and `sheets` (overview sheets to pick the important frames). Long jobs: start them in the background early and read the PDFs while they run.

## 3. Figures from the real slides

Students trust and recognise their professor's diagrams, so copy them rather than redrawing.

```bash
python studytool.py scan  "Unit 2.pdf" 3,15,22          # figure boxes in PDF points (background art filtered)
python studytool.py crop  "Unit 2.pdf" 15 280 161 689 444 img/u2_p15.jpg
```
- Include diagrams/graphs that carry meaning (architectures, geometry of a model, plots, classification trees). Skip decorative photos and logos.
- Some diagrams are vector drawings with no embedded image — crop them by region (slide page is usually 960×540 pt; scale from the page image you viewed).
- Caption every figure with what it shows and its source: "(Unit II, slide 15)".
- You may add your own explanatory matplotlib plots, but label them "[Generated plot, not from slides]".
- Formula images on slides: retype them as math instead of cropping (searchable, crisp).

## 4. Write the HTML

Start from `assets/template.html` — it has the CSS, KaTeX auto-render and a comment block with copy-paste snippets for every component. House style details are in `references/style.md`; the essentials:
- Cover box: course, decks covered with slide counts, how to use, **missing-scope note**, box legend.
- Quick-revision one-liners → unit sections numbered like `II-B.4 Coherence time (slides 14–19)`.
- Boxes: **Exam focus** (blue), **Trap** (red), **Worked example** (green, fully solved), **Extra** (grey). Anything not on the slides goes in an Extra box so the student knows it wasn't taught — never pass outside knowledge off as slide content.
- Derivations as numbered step chains the student can reproduce in an exam.
- End matter: formula sheet (one table grouped by unit) · numbers to remember · common traps · question bank per mode.
- Math: `$…$` and `$$…$$`; write `&lt;`/`&gt;` instead of `<`/`>` inside math.

Re-check the arithmetic of every worked example — a wrong number in a study guide is worse than none.

## 5. Build and verify

```bash
python studytool.py build guide.html "<library>/<COURSE>/<Name>.pdf" previews/
```
It must report `unrendered math: none`. Then actually look at the preview PNGs (and any page with dense formulas) before sending — the build can "succeed" on a broken page.

## 6. Save to the course library and deliver

Keep everything in a durable library (default `~/Documents/StudyGuides/<COURSE>/`, or wherever the user prefers): final PDFs at the top, and `src/` with the HTML fragments, `img/` and any build script. Scratch/temp folders get wiped, and the endterm mode needs these sources later.

Send the PDF to the user and summarise: what's covered (decks + slide counts), the extras added, and anything missing.

## 7. Endterm merge

When the mode is endterm, look in the course library for earlier guides. Rebuild one combined guide from the `src/` fragments: all units in order, one unified formula sheet / numbers / traps, question bank organised by unit, earlier MCQs as a final practice section; remove duplicate sections. If only PDFs exist (no sources), `studytool.py merge out.pdf a.pdf b.pdf` is the fallback.
