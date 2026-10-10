#!/usr/bin/env python3
"""
Map each guide section to the PDF page of the article it actually starts on.

"read this section in the piece" currently guesses a Medium URL fragment
(base_url + "#" + section number) -- unverifiable from this sandbox (Medium
is Cloudflare-blocked here), and Medium does not reliably anchor on
arbitrary text anyway. The three parts' own PDF exports (next to the
markdown this project already parses) have a clean text layer and each
page happens to open right on a heading, so the section's own heading text
can be searched for directly: normalise both sides (lowercase, collapse
whitespace, drop punctuation) and find the first page whose normalised text
starts with the section's normalised heading.

Output: page_based/article_page_map.json -- {section_id: page_number}
(1-indexed, into the per-part PDF copied into page_based/tragicomedy/).
"""
import json
import os
import re
import sys

import pypdf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_po_guide as guide_mod

TRAGICOMEDY_DIR = os.path.join(HERE, "tragicomedy")
PART_PDF = {
    "summary": "summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506.pdf",
    "p1": "full-text-proximal-origin-a-tragicomedy-of-our-times-draft-p1-626c72cb05b1.pdf",
    "p2": "full-text-proximal-origin-a-tragicomedy-of-our-times-draft-p2-39b90684bf01.pdf",
}


def norm(text):
    text = text.lower()
    text = re.sub(r"[‘’“”]", "'", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def main():
    guide = json.load(open(os.path.join(HERE, "po_guide.json"), encoding="utf-8"))

    page_texts = {}
    for pid, fname in PART_PDF.items():
        path = os.path.join(TRAGICOMEDY_DIR, fname)
        reader = pypdf.PdfReader(path)
        page_texts[pid] = [norm(p.extract_text() or "") for p in reader.pages]
        print("%s: %d pages" % (pid, len(page_texts[pid])))

    result = {}
    misses = []
    for s in guide["sections"]:
        if not s.get("number"):
            continue
        heading_n = norm(s["heading"])
        # The first ~8 words of the heading are specific enough to be a
        # unique anchor (the section number alone repeats across parts /
        # sub-levels) without being so long that a trivial OCR/typesetting
        # difference (a hyphenated line break, a smart-quote variant norm()
        # didn't catch) breaks the match.
        needle = " ".join(heading_n.split()[:8])
        pages = page_texts.get(s["part"], [])
        found = None
        for i, text in enumerate(pages, start=1):
            if text.startswith(needle):
                found = i
                break
        if found is None:
            # Fall back to "needle appears anywhere on the page" -- some
            # sections' first page opens on something other than the
            # heading itself (a block quote, a pull-image caption).
            for i, text in enumerate(pages, start=1):
                if needle in text:
                    found = i
                    break
        if found is not None:
            result[s["id"]] = found
        else:
            misses.append(s["id"])

    out_path = os.path.join(HERE, "article_page_map.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    print("Mapped %d / %d sections" % (len(result), sum(1 for s in guide["sections"] if s.get("number"))))
    if misses:
        print("Unmapped (%d): %s" % (len(misses), misses[:20]))
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
