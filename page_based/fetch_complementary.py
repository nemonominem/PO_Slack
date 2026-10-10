#!/usr/bin/env python3
"""
Download the Complementary-tab source PDFs (documents the P.O. piece cites
but that are not one of the five ingested Timeline sources) and trim each
to just its cited pages.

Full copies are not worth hosting: most of these releases run to hundreds
or thousands of pages, and the piece cites a sparse handful from each.
Downloading the whole file costs bandwidth and disk for content nobody will
ever read here, so instead: download once (to a scratch temp file, not
committed), extract only the cited page ranges (each page individually,
not the full file) into a small trimmed PDF under
page_based/complementary/, and record a page map from the ORIGINAL page
number (the one the article's own citations use) to its position in the
trimmed PDF.

Google Drive serves small files directly; a file above its virus-scan
threshold (~25MB+) serves an HTML interstitial instead, with a confirm
token embedded in the page -- handled below. Some files are too large even
for that to succeed cleanly from here; those are reported, not silently
skipped, for a human to fetch by hand.

Output: page_based/complementary/<doc>.pdf (trimmed) + complementary.json
        (doc -> {"pdf": filename, "page_map": {orig_page: trimmed_page},
                  "total_pages_original": N})
"""
import json
import os
import re
import sys

import requests
import pypdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "complementary")
OUT_JSON = os.path.join(HERE, "complementary.json")
SCRATCH = "/tmp/po_complementary_scratch"

DOCS = [
    ("Baric-TI-Transcript.pdf",
     "173bZUapV1fbWx7KXqD30uynH1sQddOLs",
     ['15', '18', '20-21', '22-23', '30-32', '108-110', '120-121', '121', '122', '125']),
    ("1265-pages.pdf",
     "1T2MNgjgjXKDGZFjyJvE2MO0RDb8UFcIe",
     ['1', '2', '274', '319', '343-344', '351', '355', '365-366', '505-506']),
    ("UTMB-LeDuc-batch-1.pdf",
     "1O6_TaUYbPeAsdwOj-1JkvzKQFVBtx_Jw",
     ['1', '2', '4', '206', '486-487', '593-594', '806-809', '1448', '2816', '2825']),
    ("Biohazard_FOIA_Maryland_Emails_11.6.20.pdf",
     "12NTOh9Aswk5pBf-X_INFB_sdrmoLinjC",
     ['255', '278', '284', '292', '304']),
    ("USRTK_UCDavis_PROD_06-ocr.pdf",
     "14b5S7CZnQndWzZxBuLFxDbvarZgItEj9",
     ['21', '1004']),
    ("USRTK_UCDavis_PROD_38-ocr.pdf",
     "1jNeqlHWUnV2QoEL5fvnzHX7sq867ue3Z",
     ['1205']),
]


def expand_pages(page_specs):
    """['20-21', '121'] -> [20, 21, 121], de-duped, ascending."""
    out = set()
    for spec in page_specs:
        spec = spec.strip()
        if "-" in spec:
            a, b = spec.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(spec))
    return sorted(out)


def drive_download(file_id, dest):
    """Download a Google Drive file by id, following the large-file confirm
    interstitial when one appears. Returns True on success.

    Above Drive's virus-scan size threshold, /uc?export=download returns an
    HTML page (not the file) whose <form action="https://drive.usercontent.
    google.com/download"> carries the real download as hidden fields (id,
    export, confirm, uuid) -- a different domain from the initial request,
    not just an extra query param on the same one.
    """
    sess = requests.Session()
    url = "https://drive.google.com/uc?export=download&id=%s" % file_id
    resp = sess.get(url, stream=True, timeout=60)
    ctype = resp.headers.get("Content-Type", "")
    if "text/html" in ctype:
        html = resp.text
        fields = dict(re.findall(r'name="([a-zA-Z0-9_]+)"\s+value="([^"]*)"', html))
        action_m = re.search(r'<form[^>]*action="([^"]+)"', html)
        if fields.get("confirm") and action_m:
            resp = sess.get(action_m.group(1), params=fields, stream=True, timeout=180)
            ctype = resp.headers.get("Content-Type", "")
        if "text/html" in ctype:
            return False, "Drive served an HTML interstitial with no usable confirm token"
    total = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
            total += len(chunk)
    if total < 1000:
        return False, "downloaded file suspiciously small (%d bytes)" % total
    return True, None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    results = {}
    failures = []

    for doc, file_id, page_specs in DOCS:
        print("=== %s ===" % doc)
        scratch_path = os.path.join(SCRATCH, doc)
        ok, err = drive_download(file_id, scratch_path)
        if not ok:
            print("  FAILED to download: %s" % err)
            failures.append((doc, err))
            continue
        size_mb = os.path.getsize(scratch_path) / 1e6
        print("  downloaded %.1f MB" % size_mb)
        try:
            reader = pypdf.PdfReader(scratch_path)
            n_pages = len(reader.pages)
        except Exception as e:
            print("  FAILED to read as PDF: %s" % e)
            failures.append((doc, "not a valid PDF after download: %s" % e))
            continue
        wanted = [p for p in expand_pages(page_specs) if 1 <= p <= n_pages]
        missing = [p for p in expand_pages(page_specs) if p > n_pages]
        if missing:
            print("  NOTE: cited pages beyond the document's %d pages, skipped: %s"
                  % (n_pages, missing))
        writer = pypdf.PdfWriter()
        page_map = {}
        for i, p in enumerate(wanted, start=1):
            writer.add_page(reader.pages[p - 1])
            page_map[str(p)] = i
        out_pdf = os.path.join(OUT_DIR, doc)
        with open(out_pdf, "wb") as f:
            writer.write(f)
        out_size_kb = os.path.getsize(out_pdf) / 1e3
        print("  trimmed to %d of %d pages, %.0f KB -> %s"
              % (len(wanted), n_pages, out_size_kb, out_pdf))
        results[doc] = {
            "pdf": doc,
            "page_map": page_map,
            "total_pages_original": n_pages,
            "pages_included": wanted,
        }
        os.remove(scratch_path)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print("\nWrote %s (%d documents)" % (OUT_JSON, len(results)))
    if failures:
        print("\n%d document(s) need manual help:" % len(failures))
        for doc, err in failures:
            print("  - %s: %s" % (doc, err))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
