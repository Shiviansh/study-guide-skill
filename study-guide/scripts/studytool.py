"""studytool — helpers for building exam study guides from lecture material.

Commands
  scan       deck.pdf [3,15,22]                  figure boxes (PDF points) per page; background art filtered out
  crop       deck.pdf PAGE x0 y0 x1 y1 out.jpg   crop a slide region at 3x zoom (max 1100 px wide);
             frame.jpg 0 x0 y0 x1 y1 out.jpg     ...or a pixel region of an image / video frame
  build      guide.html out.pdf [previews_dir]   inline img/* as base64 -> out.html, print to PDF with a
                                                 Chromium browser (Edge/Chrome), report unrendered math,
                                                 save 4 preview PNGs if previews_dir is given
  merge      out.pdf a.pdf b.pdf ...             concatenate PDFs (e.g. quiz + midterm packs for an endterm)
  pptx2pdf   slides.pptx out.pdf                 convert via PowerPoint (Windows) or LibreOffice (soffice)
  frames     lecture.mp4 outdir [scene=0.25] [max_gap_sec=90]
                                                 keep a frame whenever the picture changes (new slide / new board
                                                 drawing) plus at least one every max_gap_sec; near-duplicates
                                                 removed; files named by timestamp (f_0h12m34s.jpg)
  sheets     framesdir out_prefix [per_sheet=16] overview sheets (4x4 thumbnails with timestamps) to review a
                                                 whole lecture's frames at once
  transcribe lecture.mp4 out.txt [model] [hints.txt]
                                                 speech-to-text with faster-whisper; uses the NVIDIA GPU
                                                 (float16, large-v3-turbo) when available, else CPU (small);
                                                 hints.txt = course terms to help spell jargon ("-" = default model)
  ocr        notes.pdf|page.png out.txt [lang=eng]  OCR scanned/photographed notes with Tesseract

Requires: pip install pymupdf pillow   (KaTeX math is loaded from a CDN, so `build` needs internet)
Video:    ffmpeg + pip install faster-whisper (GPU: pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12>=9,<10")
"""
import base64, glob, os, pathlib, re, shutil, site, subprocess, sys, tempfile, time

import pymupdf as fitz
from PIL import Image

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def browser():
    for b in BROWSERS:
        if os.path.exists(b):
            return b
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        if shutil.which(name):
            return shutil.which(name)
    sys.exit("No Chromium-based browser found (Edge/Chrome/Chromium) for PDF printing.")


def scan(pdf, pages=None):
    doc = fitz.open(pdf)
    print("pages", len(doc), "size", doc[0].rect)
    want = [int(p) for p in pages.split(",")] if pages else range(1, len(doc) + 1)
    seen = {}  # boxes repeated on most pages are slide-template background art
    for pg in doc:
        for i in pg.get_image_info():
            b = tuple(round(v) for v in i["bbox"])
            seen[b] = seen.get(b, 0) + 1
    for p in want:
        for i in doc[p - 1].get_image_info():
            b = tuple(round(v) for v in i["bbox"])
            if seen[b] < len(doc) * 0.5 and b[2] - b[0] > 60 and b[3] - b[1] > 40:
                print(f"p{p}", b, f'{i["width"]}x{i["height"]}')


def crop(pdf, page, x0, y0, x1, y1, out):
    """PDF: region in points on PAGE. Image (video frame/photo): pass PAGE as 0 and the region in pixels."""
    if pathlib.Path(pdf).suffix.lower() in (".jpg", ".jpeg", ".png"):
        im = Image.open(pdf).convert("RGB").crop(tuple(int(float(v)) for v in (x0, y0, x1, y1)))
    else:
        pg = fitz.open(pdf)[int(page) - 1]
        pix = pg.get_pixmap(matrix=fitz.Matrix(3, 3), clip=fitz.Rect(*map(float, (x0, y0, x1, y1))) & pg.rect)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if im.width > 1100:
        im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=85)
    print(out, im.size)


def build(src, pdf, previews=None):
    src, pdf = pathlib.Path(src).resolve(), pathlib.Path(pdf).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)

    def inline(m):
        p = src.parent / m.group(1)
        if not p.exists():  # e.g. the example snippet inside the template comment
            return m.group(0)
        mime = "image/png" if p.suffix == ".png" else "image/jpeg"
        return f'src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"'

    html = re.sub(r'src="(img/[^"]+)"', inline, src.read_text(encoding="utf-8"))
    out_html = pdf.with_suffix(".html")
    out_html.write_text(html, encoding="utf-8")
    # Windows browsers fail on paths > 260 chars, so print from/to a short temp path
    tmp = pathlib.Path(tempfile.gettempdir()) / "studytool_print.pdf"
    tmp_html = tmp.with_suffix(".html")
    tmp.unlink(missing_ok=True)
    shutil.copy(out_html, tmp_html)
    # own profile dir: otherwise a running Edge/Chrome takes the job and the call returns before the PDF exists
    profile = pathlib.Path(tempfile.gettempdir()) / "studytool_browser_profile"
    subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--user-data-dir={profile}", "--virtual-time-budget=30000",
                    f"--print-to-pdf={tmp}", tmp_html.as_uri()], capture_output=True)
    # newer Edge launchers return at once and print in the background: wait until the PDF exists and stops growing
    last = -1
    for _ in range(240):
        size = tmp.stat().st_size if tmp.exists() else -1
        if size > 0 and size == last:
            break
        last = size
        time.sleep(0.5)
    if not tmp.exists():
        sys.exit("Browser did not produce a PDF.")
    shutil.move(tmp, pdf)
    doc = fitz.open(pdf)
    if "ERR_" in doc[0].get_text():
        sys.exit(f"Browser printed an error page instead of the guide: {doc[0].get_text()[:120]!r}")
    bad = [i + 1 for i, p in enumerate(doc) if re.search(r"\$|\\frac|\\sum|\\lambda", p.get_text())]
    print(f"{pdf.name}: {len(doc)} pages, {pdf.stat().st_size // 1024} KB, pages with unrendered math: {bad or 'none'}")
    if previews:
        pathlib.Path(previews).mkdir(parents=True, exist_ok=True)
        for i in sorted({0, len(doc) // 3, 2 * len(doc) // 3, len(doc) - 1}):
            doc[i].get_pixmap(dpi=75).save(f"{previews}/page_{i + 1}.png")
        print("previews ->", previews)


def merge(out, *pdfs):
    doc = fitz.open()
    for p in pdfs:
        doc.insert_pdf(fitz.open(p))
    doc.save(out)
    print(out, len(doc), "pages")


def pptx2pdf(pptx, out):
    pptx, out = str(pathlib.Path(pptx).resolve()), str(pathlib.Path(out).resolve())
    if sys.platform == "win32":
        ps = (f"$p=New-Object -ComObject PowerPoint.Application;"
              f"$d=$p.Presentations.Open('{pptx}',$true,$false,$false);$d.SaveAs('{out}',32);$d.Close();$p.Quit()")
        if subprocess.run(["powershell", "-NoProfile", "-Command", ps]).returncode == 0 and os.path.exists(out):
            return print(out)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("Need Microsoft PowerPoint (Windows) or LibreOffice to convert .pptx")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(pathlib.Path(out).parent), pptx], check=True)
    shutil.move(pathlib.Path(out).parent / (pathlib.Path(pptx).stem + ".pdf"), out)
    print(out)


def ffmpeg_bin():
    f = shutil.which("ffmpeg")
    if not f:  # winget installs update PATH only for new shells
        hits = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\*\bin\ffmpeg.exe"))
        f = hits[0] if hits else None
    if not f:
        sys.exit("ffmpeg not found (winget install Gyan.FFmpeg / brew install ffmpeg / apt install ffmpeg)")
    return f


def _ahash(path):
    """16x16 average hash: frames whose hashes differ in few bits look the same."""
    px = list(Image.open(path).convert("L").resize((16, 16)).tobytes())
    m = sum(px) / len(px)
    return [p > m for p in px]


def frames(video, outdir, scene="0.25", max_gap="90"):
    out = pathlib.Path(outdir)
    raw = out / "_raw"
    shutil.rmtree(raw, ignore_errors=True)
    raw.mkdir(parents=True)
    # keep the first frame, every scene change, and at least one frame per max_gap seconds
    # (slow whiteboard drawing never triggers a scene change, the gap rule catches it)
    sel = f"select='isnan(prev_selected_t)+gt(scene,{scene})+gte(t-prev_selected_t,{max_gap})',showinfo"
    r = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", video, "-vf", sel, "-fps_mode", "vfr", "-q:v", "3",
                        str(raw / "%05d.jpg")], capture_output=True, text=True, encoding="utf-8", errors="replace")
    times = [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    cands = sorted(raw.glob("*.jpg"))
    if not cands:
        sys.exit(f"ffmpeg produced no frames:\n{r.stderr[-800:]}")
    kept, last = 0, None
    for f, t in zip(cands, times):
        h = _ahash(f)
        if last is not None and sum(a != b for a, b in zip(h, last)) < 12:  # near-duplicate of previous kept frame
            continue
        last, kept = h, kept + 1
        f.replace(out / f"f_{int(t // 3600):01d}h{int(t % 3600 // 60):02d}m{int(t % 60):02d}s.jpg")
    shutil.rmtree(raw, ignore_errors=True)
    print(f"{kept} frames kept (of {len(cands)} candidates) -> {out}")


def sheets(framesdir, prefix, per_sheet="16"):
    from PIL import ImageDraw, ImageFont
    fs, n, cols, W, H = sorted(pathlib.Path(framesdir).glob("f_*.jpg")), int(per_sheet), 4, 480, 270
    font = ImageFont.load_default(size=18)
    pathlib.Path(prefix).parent.mkdir(parents=True, exist_ok=True)
    for s in range(0, len(fs), n):
        chunk = fs[s:s + n]
        sheet = Image.new("RGB", (cols * W, -(-len(chunk) // cols) * (H + 24)), "white")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            im = Image.open(f).convert("RGB")
            im.thumbnail((W - 6, H - 6))
            x, y = (i % cols) * W, (i // cols) * (H + 24)
            sheet.paste(im, (x + 3, y + 3))
            d.text((x + 6, y + H), f.stem[2:], fill="black", font=font)
        name = f"{prefix}_{s // n + 1:02d}.jpg"
        sheet.save(name, quality=80)
        print(name, f"({len(chunk)} frames)")


def _cuda_dlls():
    """pip's nvidia-* wheels put cuBLAS/cuDNN DLLs in site-packages/nvidia/*/bin; make them loadable."""
    for root in site.getsitepackages() + [site.getusersitepackages()]:
        for d in glob.glob(os.path.join(root, "nvidia", "*", "bin")):
            os.add_dll_directory(d)
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]


def transcribe(video, out, model=None, hints=None):
    """hints: optional text file of course terms (e.g. headings from the notes) to bias spelling."""
    if sys.platform == "win32":
        _cuda_dlls()
    try:
        import ctranslate2
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit('pip install faster-whisper  (GPU: also pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12>=9,<10")')
    gpu = ctranslate2.get_cuda_device_count() > 0
    model = model if model and model != "-" else ("large-v3-turbo" if gpu else "small")
    path = model
    if not os.path.isdir(model):
        # download into a plain folder: the default HF cache uses symlinks, which fail on Windows without admin
        from faster_whisper.utils import download_model
        path = pathlib.Path.home() / ".cache" / "study-guide" / "whisper" / model
        if not (path / "model.bin").exists():
            print(f"downloading Whisper model '{model}' (one-time) ...")
            download_model(model, output_dir=str(path))
    wm = WhisperModel(str(path), device="cuda" if gpu else "cpu", compute_type="float16" if gpu else "int8")
    prompt = pathlib.Path(hints).read_text(encoding="utf-8")[:800] if hints else None
    t0 = time.time()
    # decode with ffmpeg ourselves (16 kHz mono float) instead of faster-whisper's PyAV, whose API breaks across versions
    import numpy as np
    pcm = subprocess.run([ffmpeg_bin(), "-loglevel", "error", "-i", video, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segs, info = wm.transcribe(audio, vad_filter=True, beam_size=5, initial_prompt=prompt)
    with open(out, "w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"[{int(s.start // 3600)}:{int(s.start % 3600 // 60):02d}:{int(s.start % 60):02d}] {s.text.strip()}\n")
    mins = (time.time() - t0) / 60
    print(f"transcript -> {out}: {info.duration / 60:.1f} min of audio in {mins:.1f} min "
          f"({'GPU' if gpu else 'CPU'}, {model}, language={info.language})")


def ocr(src, out, lang="eng"):
    tess = shutil.which("tesseract") or next(iter(glob.glob(r"C:\Program Files\Tesseract-OCR\tesseract.exe")), None)
    if not tess:
        sys.exit("Tesseract not found (winget install UB-Mannheim.TesseractOCR / brew install tesseract)")
    src = pathlib.Path(src)
    with tempfile.TemporaryDirectory() as td:
        pages = [src]
        if src.suffix.lower() == ".pdf":
            pages = []
            for i, pg in enumerate(fitz.open(src)):
                p = pathlib.Path(td) / f"p{i + 1}.png"
                pg.get_pixmap(dpi=300).save(p)
                pages.append(p)
        with open(out, "w", encoding="utf-8") as f:
            for i, p in enumerate(pages, 1):
                r = subprocess.run([tess, str(p), "stdout", "-l", lang], capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
                f.write(f"=== page {i} ===\n{r.stdout.strip()}\n\n")
    print(f"OCR -> {out} ({len(pages)} pages)")


if __name__ == "__main__":
    cmds = {f.__name__: f for f in (scan, crop, build, merge, pptx2pdf, frames, sheets, transcribe, ocr)}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](*sys.argv[2:])
