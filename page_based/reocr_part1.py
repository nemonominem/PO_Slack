#!/usr/bin/env python3
"""
Re-OCR slack-part1.pdf page-by-page with Tesseract (--oem 1 --psm 6), which
is dramatically cleaner than the OCR text layer baked into the PDF by the
original "PDF24 Tools - OCR" pass (verified by comparison on several pages:
full clean sentences vs. garbled fragments with junk icon-glyph prefixes).

Requires: pdftoppm, tesseract (both via homebrew). Renders all pages once to
PNG at 300dpi (slow, ~140 pages), then OCRs each and writes a single raw text
file with "\\x0c"-separated pages, matching the format parse_part1.py expects.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(HERE, "slack-part1.pdf")
PAGES_DIR = "/tmp/slack_ocr_pages"
OUT_TXT = os.path.join(HERE, "slack-part1_ocr.txt")


def render_pages():
    os.makedirs(PAGES_DIR, exist_ok=True)
    existing = [f for f in os.listdir(PAGES_DIR) if f.endswith(".png")]
    if len(existing) >= 140:
        print("Pages already rendered (%d found), skipping render." % len(existing))
        return
    subprocess.run(
        ["pdftoppm", "-r", "300", "-png", PDF_PATH, os.path.join(PAGES_DIR, "page")],
        check=True,
    )


def ocr_pages():
    files = sorted(f for f in os.listdir(PAGES_DIR) if f.endswith(".png"))
    print("OCR-ing %d pages..." % len(files))
    parts = []
    for i, fname in enumerate(files, start=1):
        # Absolute paths trip a sandbox quirk with tesseract on this machine;
        # relative path + cwd=PAGES_DIR works fine.
        result = subprocess.run(
            ["tesseract", fname, "-", "--oem", "1", "--psm", "6"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            cwd=PAGES_DIR,
        )
        parts.append(result.stdout.decode("utf-8", errors="replace"))
        if i % 10 == 0 or i == len(files):
            print("  %d/%d" % (i, len(files)))
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\x0c".join(parts))
    print("Wrote %s" % OUT_TXT)


if __name__ == "__main__":
    render_pages()
    ocr_pages()
