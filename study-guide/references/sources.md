# Getting content out of different sources

All commands are `python <skill-dir>/scripts/studytool.py <command> ...`.

## Course file first (CIF / syllabus / course handout)
Read it before anything else. Extract units → topics → which exam covers them (evaluation table, e.g. "Mid Term: CO1–CO3"). Build a coverage map: every CIF topic → the lecture notes / videos that cover it. Use it to
- order the guide exactly as the CIF orders units and topics,
- tag each section with its sources ("Lecture 4, slides 10–18; Video 3, 12:40–25:10"),
- list CIF topics that no provided material covers on the cover (and in the summary to the user).

## PDF lecture notes / slides
Read every page (≤20 pages per Read call). `scan` locates figures, `crop deck.pdf PAGE x0 y0 x1 y1 img/x.jpg` cuts them (PDF points; pages are often 960×540 for slides, 595×842 for A4).

## Scanned or handwritten notes
If a PDF has little or no extractable text, run `ocr notes.pdf notes_ocr.txt` (Tesseract) to get searchable text, but still view the pages yourself — OCR is weak on handwriting and equations. Crop diagrams from the page images as usual.

## PowerPoint (.pptx)
`pptx2pdf slides.pptx slides.pdf` (PowerPoint on Windows, else LibreOffice), then treat as PDF.

## Lecture videos
1. **Transcript.**
   - YouTube/online with captions: fetch the captions.
   - Local files: `transcribe lecture.mp4 lecture.txt - hints.txt`. Uses the NVIDIA GPU automatically (large-v3-turbo, float16; many times faster than real time on an RTX-class laptop GPU), else CPU `small` (≈ real time — warn the user for long videos and run in the background). `hints.txt` = a few hundred characters of course terms (section headings, symbol names from the notes) so jargon is spelled right. Lines carry `[h:mm:ss]` timestamps.
   - Run several videos one after another in a background shell; GPU memory fits one large model at a time.
2. **Frames.** `frames lecture.mp4 frames/lec3` keeps a frame at every scene change (new slide / new board content) plus at least one every 90 s for slow board drawing, and drops near-duplicates. Files are named by timestamp. Tune: talking-head videos with small slides → lower `scene` (0.15); shaky camera video → raise it (0.35) or the gap.
3. **Review.** `sheets frames/lec3 sheets/lec3` makes 4×4 overview sheets with timestamps. View the sheets (not hundreds of single frames) and note the timestamps of frames that show meaningful diagrams, derivations or board work.
4. **Use.** Prefer the same diagram from the PDF notes when it exists (sharper). For video-only content, crop the frame: `crop frames/lec3/f_0h12m40s.jpg 0 x0 y0 x1 y1 img/v3_board.jpg` (pixels). Caption with "(Video 3, 12:40)".
5. **Content.** Merge transcript explanations into the matching CIF topic. Spoken hints like "this is important for the exam" or "this will come" become Exam-focus boxes. Fix transcript errors against the notes.

Videos behind a college login: ask the user to download them; never enter their credentials.

## Old question papers
If provided, mirror their question style and marks pattern in the question bank and mark repeated topics as Exam focus.
