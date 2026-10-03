#!/usr/bin/env python3
"""
Re-OCR po-emails.pdf (the FOIA'd P.O. email release cited throughout the
P.O. "Tragicomedy" piece as `Proximal_Origin_Emails.pdf`) page-by-page with
Tesseract.

The release ships as scanned page images with NO text layer at all
(verified: pypdf extracts '' from every page), so OCR is the only way in --
the same situation as slack-part1.pdf, and solved the same way, by
re-rendering at 300dpi and OCR-ing with Tesseract instead of trusting a
low-quality baked-in text layer.

These are email screenshots: a narrow header block (From/Sent/Date/Subject)
followed by the body, sometimes two columns. --psm 6 (one uniform block)
is the right default for the single-column pages; the script records which
pages fell back to --psm 4 and at what length so the parser knows where
the layout was ambiguous.

Writes a single text file with "\\x0c"-separated pages (the format
parse_po_emails.py expects) plus a small JSON side-car of per-page
geometry/PSM decisions.

Requires: pdftoppm, tesseract (both via homebrew).
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(HERE, "po-emails.pdf")
PAGES_DIR = "/tmp/po_emails_ocr_pages"
OUT_TXT = os.path.join(HERE, "po-emails_ocr.txt")
OUT_META = os.path.join(HERE, "po-emails_ocr_pages.json")

EXPECTED_PAGES = 163
BATCH = 10

# A page shorter than this under --psm 6 is almost certainly a two-column or
# otherwise mangled layout: retry once with --psm 4 (single column of variable
# text sizes) before accepting it.
MIN_CHARS = 220


def page_count():
    out = subprocess.run(["pdfinfo", PDF_PATH], check=True, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL).stdout.decode()
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else EXPECTED_PAGES


def render_pages():
    """Render in batches of BATCH pages.

    Asking pdftoppm for all 163 pages in one go exhausted memory on this
    machine and it died silently at page 20; a batch of pages at a time is
    slower to start but completes reliably, and a failed batch is retried
    page-by-page so one bad page cannot lose the run.
    """
    os.makedirs(PAGES_DIR, exist_ok=True)
    total = page_count()
    for start in range(1, total + 1, BATCH):
        end = min(start + BATCH - 1, total)
        need = [p for p in range(start, end + 1)
                if not os.path.exists(os.path.join(PAGES_DIR, "page-%03d.png" % p))]
        if not need:
            continue
        for p in need:   # render one at a time; simple and never loses the run
            r = subprocess.run(["pdftoppm", "-r", "300", "-png",
                                "-f", str(p), "-l", str(p), PDF_PATH,
                                os.path.join(PAGES_DIR, "page")],
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if r.returncode != 0:
                print("  WARN page %d failed: %s" % (p, r.stderr.decode()[:120]))
        print("  rendered %d/%d" % (end, total))


def ocr_one(fname, psm, attempts=3):
    """OCR one page, retrying.

    tesseract occasionally exits non-zero on this machine under memory
    pressure -- it did so on page 20 of the first run -- and one failure must
    not abort 163 pages of work, so a bad page is retried and finally recorded
    as empty (and flagged by its char count in the meta side-car) rather than
    killing the run.
    """
    for i in range(attempts):
        # Absolute paths trip a sandbox quirk with tesseract on this machine;
        # relative path + cwd=PAGES_DIR works fine.
        r = subprocess.run(
            ["tesseract", fname, "-", "--oem", "1", "--psm", str(psm)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PAGES_DIR,
        )
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace")
        print("  WARN %s psm%d attempt %d failed: %s"
              % (fname, psm, i + 1, r.stderr.decode()[:100]))
        time.sleep(2)
    return ""


def ocr_pages():
    files = sorted(f for f in os.listdir(PAGES_DIR) if f.endswith(".png"))
    print("OCR-ing %d pages..." % len(files))
    parts, meta = [], []
    for i, fname in enumerate(files, start=1):
        text = ocr_one(fname, 6)
        psm = 6
        if len(text.strip()) < MIN_CHARS:
            retry = ocr_one(fname, 4)
            if len(retry.strip()) > len(text.strip()):
                text, psm = retry, 4
        parts.append(text)
        meta.append({"page": i, "psm": psm, "chars": len(text.strip())})
        if i % 10 == 0 or i == len(files):
            print("  %d/%d" % (i, len(files)))
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\x0c".join(parts))
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    retried = [m["page"] for m in meta if m["psm"] == 4]
    thin = [m["page"] for m in meta if m["chars"] < 80]
    print("Wrote %s (%d pages; psm4 fallback: %s; near-empty: %s)"
          % (OUT_TXT, len(files), retried, thin))


if __name__ == "__main__":
    render_pages()
    ocr_pages()
