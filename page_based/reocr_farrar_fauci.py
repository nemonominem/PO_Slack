#!/usr/bin/env python3
"""Re-OCR farrar-fauci-comms.pdf from scratch with Tesseract.

Why: the PDF's own text layer is broken two ways -- words are glued
("JeremyFarrarsent:") AND glyphs are misread ("Tor" for "To", "healt" for
"health", "whww" for "www"). PyMuPDF recovers the word boxes but not the
glyphs. The page images are sharp (verified p.1, p.50), so Tesseract on
300dpi renders reads cleanly:

  text layer: From: Fauci,Anthony(NIH/NIAID)[€]sent: Fri,24Jul202010:37:46
  re-OCR:     From: Fauci, Anthony (NIH/NIAID) [E] / Sent: Fri, 24 Jul 2020 ...

Recipe (mirrors reocr_po_emails.py, same 300dpi + PSM 6 + OEM 1):
  1. pdftoppm renders every page to PNG (needs ~2GB scratch for 174 pages).
  2. tesseract OCRs each PNG; text lands in farrar-fauci-comms_ocr.txt,
     pages split by \\x0c, exactly like po-emails_ocr.txt.
  3. parse_farrar_fauci.py (next step) reads the OCR text, not the PDF layer.

Run: python3 reocr_farrar_fauci.py [--max-pages N]
Resume: pages already OCR'd are skipped (checks farrar-fauci-comms_ocr.txt).
"""
import os
import subprocess
import sys
import tempfile

PDF = "farrar-fauci-comms.pdf"
OUT_TXT = "farrar-fauci-comms_ocr.txt"
DPI = 300


def page_count():
    import pypdf
    return len(pypdf.PdfReader(PDF).pages)


def already_done():
    if not os.path.exists(OUT_TXT):
        return set()
    done = set()
    with open(OUT_TXT, encoding="utf-8") as f:
        for i, chunk in enumerate(f.read().split("\x0c"), start=1):
            if chunk.strip():
                done.add(i)
    return done


def main():
    max_pages = None
    for a in sys.argv[1:]:
        if a.startswith("--max-pages"):
            max_pages = int(a.split("=")[1])
    n = page_count()
    if max_pages:
        n = min(n, max_pages)
    ocr_range(1, n)


def ocr_page(p, tmp):
    """Render page p at 300dpi and OCR it. Returns text."""
    png_base = os.path.join(tmp, "p")
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-f", str(p),
                    "-l", str(p), PDF, png_base],
                   check=True, capture_output=True)
    png = "%s-%03d.png" % (png_base, p)
    home_png = os.path.expanduser("~/ff_reocr_tmp.png")
    # Tesseract on this machine cannot read /tmp (sandbox); home works.
    os.rename(png, home_png)
    try:
        r = subprocess.run(["tesseract", home_png, "stdout",
                            "--oem", "1", "--psm", "6"],
                           capture_output=True, text=True)
        return r.stdout
    finally:
        if os.path.exists(home_png):
            os.remove(home_png)


def save_pages(texts):
    """Merge new page texts into OUT_TXT, keeping page order."""
    old = {}
    if os.path.exists(OUT_TXT):
        with open(OUT_TXT, encoding="utf-8") as f:
            for i, chunk in enumerate(f.read().split("\x0c"), start=1):
                old[i] = chunk
    old.update(texts)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for i in range(1, max(old) + 1):
            if i > 1:
                f.write("\x0c")
            f.write(old.get(i, ""))
    print("wrote %s (%d pages)" % (OUT_TXT, len(old)))


def ocr_range(lo, hi):
    """OCR pages lo..hi, resumable (skips pages already in OUT_TXT)."""
    import shutil
    done = already_done()
    todo = [p for p in range(lo, hi + 1) if p not in done]
    print("pages %d..%d, todo: %d" % (lo, hi, len(todo)), flush=True)
    tmp = tempfile.mkdtemp(prefix="ff_reocr_")
    texts = {}
    try:
        for p in todo:
            texts[p] = ocr_page(p, tmp)
            print("  OCR'd %d" % p, flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if texts:
        save_pages(texts)
    else:
        print("nothing new")


def main():
    max_pages = None
    for a in sys.argv[1:]:
        if a.startswith("--max-pages"):
            max_pages = int(a.split("=")[1])
    n = page_count()
    if max_pages:
        n = min(n, max_pages)
    ocr_range(1, n)


if __name__ == "__main__":
    main()
