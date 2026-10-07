# study-guide: a Claude Code skill that turns class material into exam-ready PDFs

Drop in your lecture slides, PPTs, scanned notes, lecture videos and the course handout (CIF / syllabus). Say *"make notes for my midterm"* and Claude builds a printable A4 study-guide PDF organised the way your **course file** organises the syllabus. It includes **figures cropped from your own slides and video frames**, worked numericals, a formula sheet, traps, and a question bank with model answers.

---

## What you get

| Mode (picked from your words) | Trigger phrases | Output |
|---|---|---|
| **quiz** | "quiz", "MCQ", "questions to mug up" | Quick-revision one-liners, formula sheet, 150-300 rapid-fire Q-to-A rows, 50+ MCQs with an answer key |
| **midterm** | "midterm", "mid-sem", "viva" | Full explanations, derivation chains, solved numericals, long-answer bank with model answers |
| **endterm** | "endterm", "final" | Midterm style **plus** a merge of every earlier guide for the course into one PDF |
| **notes** | "notes", "explain", "summary" | Explanations, figures, formula sheet, traps |
| **cheatsheet** | "last night", "formula sheet" | 2-4 pages: formulas, numbers, traps, one-liners |

Every guide has a cover (decks covered, how to use it, **what is missing from the syllabus**, box legend) and unit sections numbered with slide ranges, such as `II-B.4 Coherence time (slides 14-19)`. It uses colour-coded boxes:

- **Exam focus** (blue): the 1-3 facts most likely to be asked.
- **Trap** (red): commonly confused pairs, sign and factor mistakes.
- **Worked example** (green): fully solved, with units.
- **Extra** (grey): anything *not* taught in your slides, so you know what came from outside.

If you mention the exam time ("tomorrow", "in 6 hours"), it adds a revision plan to the cover.

---

## Requirements

### Required
| Need | Why | Install |
|---|---|---|
| [Claude Code](https://claude.com/claude-code) | Runs the skill | n/a |
| Python 3.9+ | Runs `studytool.py` | n/a |
| `pymupdf`, `pillow` | Read PDFs, crop figures | `pip install pymupdf pillow` |
| Edge, Chrome or Chromium | Prints the HTML to PDF | usually already installed |
| Internet during build | Math is rendered by KaTeX from a CDN | n/a |

### Optional (only for the matching source type)
| Source | Need | Install |
|---|---|---|
| `.pptx` slides | PowerPoint (Windows) **or** LibreOffice | `winget install TheDocumentFoundation.LibreOffice` |
| Lecture videos | `ffmpeg` | `winget install Gyan.FFmpeg` / `brew install ffmpeg` |
| Video transcripts | `faster-whisper` | `pip install faster-whisper` |
| GPU transcription (NVIDIA) | CUDA libraries | `pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12>=9,<10"` |
| Scanned / handwritten notes | Tesseract | `winget install UB-Mannheim.TesseractOCR` / `brew install tesseract` |

The toolkit looks for browsers and tools in the usual Windows, macOS and Linux locations, but it has been used mostly on Windows.

---

## Install

```bash
git clone https://github.com/Shiviansh/study-guide-skill.git
cp -r study-guide-skill/study-guide ~/.claude/skills/     # Windows: copy into %USERPROFILE%\.claude\skills\
pip install pymupdf pillow
```

Restart Claude Code, then ask:

> "using my study guide skill make me perfect notes for my mid term" *(attach or point to your PDFs / PPTs / videos / CIF)*

Optional: add a line to your global `CLAUDE.md` pointing at a course library folder (for example `Documents\StudyGuides\<COURSE>\`). Every guide's sources are then kept for the endterm merge.

---

## How it works

1. **Pick the mode** from your words.
2. **Read the course file first.** It fixes the unit and topic order and the exam's scope.
3. **Read every page** of every source. Videos are transcribed and frame-grabbed.
4. **Crop figures** from the real slides and frames (`scan` finds figure boxes, `crop` cuts them).
5. **Write HTML** from `assets/template.html` (KaTeX, boxes, tables).
6. **Build** with `studytool.py build`. It reports any unrendered math, and Claude then views the preview PNGs before delivering.
7. **Save** the PDF, HTML fragments and images to a per-course library for later merging.

### The toolkit (`scripts/studytool.py`)

| Command | Does |
|---|---|
| `scan` | Finds figure boxes on slide pages, filtering repeated background art |
| `crop` | Crops a PDF region or video-frame region at 3x zoom |
| `build` | Inlines images, prints to PDF via headless Chromium, reports unrendered math, saves previews |
| `merge` | Concatenates PDFs (endterm fallback) |
| `pptx2pdf` | PowerPoint / LibreOffice conversion |
| `transcribe` | faster-whisper speech-to-text, automatic GPU use, optional hints file for jargon |
| `frames` | Scene-change frame capture (plus one every 90 s for board work), de-duplicated |
| `sheets` | 4x4 timestamped contact sheets so a whole lecture can be skimmed in a few images |
| `ocr` | Tesseract OCR for scans |

---

## Advantages over a generic "summarise my notes" prompt

This compares design choices, not benchmarks.

| | Generic summariser | **study-guide** |
|---|---|---|
| Structure | Whatever the model decides | Follows **your CIF / syllabus** unit by unit, tagged with slide ranges and video timestamps |
| Diagrams | Redrawn, missing, or described in words | **Cropped from your professor's own slides and video frames**, captioned with the source |
| Videos | Ignored, or text only | Transcribed, scene-change frames extracted, overview sheets for quick review |
| Gaps | Silently incomplete | The cover lists **syllabus topics with no material provided** |
| Outside knowledge | Mixed in unlabelled | Confined to **Extra** boxes, so you know what wasn't taught |
| Errors in the source | Copied | Slide typos corrected with a note; lecturer mistakes flagged in **Trap** boxes |
| Numericals | Often unchecked | Every worked example re-verified, solved with units |
| Exam fit | One-size summary | Five modes, a model-answer question bank, a revision plan if the exam time is known |
| Questions | May invent "exact exam questions" | Banks are labelled "likely questions built from the slides", never a leaked paper |
| Output | Chat text | **Printable A4 PDF**, checked for broken math at build time |
| Reuse | One-off | Per-course library of sources, so the **endterm merge** rebuilds one unified guide |
| Scope | Covers everything given | Honours the exam's stated scope (for example midterm = Units I-II only) |

---

## Limitations

- Quality depends on the material you provide. Gaps are flagged, not filled silently.
- Handwriting OCR is weak, so scans are also viewed visually.
- Math rendering needs internet (KaTeX CDN).
- Lecture videos behind a college login must be downloaded by you. The skill never handles your credentials.
- It helps you study. It does not replace attending lectures, and generated answers should be checked against your own notes.

## Repo layout

```
study-guide/
  SKILL.md              # workflow + modes (what Claude reads)
  assets/template.html  # CSS, KaTeX, component snippets
  references/           # modes.md, sources.md, style.md
  scripts/studytool.py  # the toolkit
```

## License

MIT, see [LICENSE](LICENSE).
