#!/usr/bin/env python3
"""
Parse sscp-drafts.pdf into one entry per dated version of the Proximal Origin
manuscript (cited in the P.O. piece as SSCP-Drafts-of-Proximal-Origin.pdf).

The release prints the manuscript over and over as it was revised, and every
copy ends with a version stamp - "February 1, 2020  7:40pm". A new stamp means
a new version; the same stamp recurring across pages just means that version ran
past a page break. That makes the stamps, not the page boundaries, the thing to
segment on, and it is why the count of versions (166 stamps, far fewer distinct)
is the number that matters.

The stamps also line up with the public Drive copies, which are named for the
same moments - PO#4_20200203_1159_FirstFormattedVersion_(FirstToFauci)_clean.pdf
is the 3 Feb 11:59 version - so a version here can be matched to a clean copy.

Output: sscp-drafts.json + sscp_page_map.json
"""

import json
import os
import re
import sys
from collections import OrderedDict

import pypdf

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "sscp-drafts.pdf")
OUT_JSON = os.path.join(HERE, "sscp-drafts.json")
OUT_MAP = os.path.join(HERE, "sscp_page_map.json")
SOURCE_ID = "sscp"

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

# "February 1, 2020       7:40pm" -- the stamp that closes every printed version
RE_STAMP = re.compile(
    r"^\s*([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})\s+(\d{1,2}):(\d{2})\s*([AaPp]\.?[Mm]\.?)?\s*$")
# OCR has been known to read the year as "2U2U" / "2U20" in these scans
RE_BAD_YEAR = re.compile(r"^2U2[0U]$", re.I)


def page_texts():
    reader = pypdf.PdfReader(PDF)
    return [(i + 1, (p.extract_text() or "")) for i, p in enumerate(reader.pages)]


def parse_stamp(line):
    m = RE_STAMP.match(line)
    if not m:
        return None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None
    year = m.group(3)
    if RE_BAD_YEAR.match(year):
        return None                      # OCR lost the year; not a usable stamp
    hour = int(m.group(4))
    ap = (m.group(6) or "am").lower().replace(".", "")
    if ap.startswith("p") and hour != 12:
        hour += 12
    if ap.startswith("a") and hour == 12:
        hour = 0
    return "%04d-%02d-%02d" % (int(year), mon, int(m.group(2))), "%02d%02d" % (hour, int(m.group(5)))


def main():
    pages = page_texts()
    n_pages = len(pages)

    # Split the running text into versions at each new stamp.
    versions, cur = [], None
    for pageno, text in pages:
        lines = [l.rstrip() for l in text.split("\n")]
        for line in lines:
            stamp = parse_stamp(line)
            if stamp:
                date, time = stamp
                if cur is None or cur["stamp"] != date + " " + time:
                    cur = {"date": date, "time": time, "stamp": date + " " + time,
                           "lines": [], "pages": [pageno]}
                    versions.append(cur)
                else:
                    cur["pages"].append(pageno)
                continue
            if cur is not None:
                if line.strip():
                    cur["lines"].append(line.rstrip())
                cur["pages"].append(pageno)

    entries = []
    for i, v in enumerate(versions):
        body = "\n".join(v["lines"]).strip()
        if not body:
            continue
        hhmm = v["time"]
        stamp_line = "%s:%s%s" % (hhmm[:2], hhmm[2:],
                                  "pm" if int(hhmm[:2]) >= 12 else "am")
        pages = sorted(set(p for p in v["pages"] if 1 <= p <= n_pages))
        entries.append(OrderedDict([
            ("idx", len(entries)),
            ("date", v["date"]),
            ("time", hhmm),
            ("kind", "draft"),
            ("raw_date", "%s %s · P.O. manuscript draft" % (v["date"], stamp_line)),
            ("sender", "Proximal Origin manuscript"),
            ("subject", "Manuscript version of %s %s" % (v["date"], stamp_line)),
            ("thread_key", "%s|%s|%s" % (SOURCE_ID, v["date"], hhmm)),
            ("replied_by", []),
            ("content", body),
            ("pages", pages),
            ("source", SOURCE_ID),
        ]))

    out = OrderedDict([
        ("source_file", "sscp-drafts.pdf"),
        ("source_id", SOURCE_ID),
        ("title", "Proximal Origin manuscript drafts (FOI release)"),
        ("total_entries", len(entries)),
        ("date_range", {"start": min(e["date"] for e in entries),
                        "end": max(e["date"] for e in entries)}),
        ("entries", entries),
    ])
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    pmap = {e["thread_key"]: {"start": e["pages"][0], "end": e["pages"][-1], "breaks": []}
            for e in entries if e["pages"]}
    with open(OUT_MAP, "w", encoding="utf-8") as f:
        json.dump(pmap, f, indent=1)

    keys = [e["thread_key"] for e in entries]
    print("Pages: %d" % n_pages)
    print("Versions: %d (stamps seen: %d)" % (len(entries), len(versions)))
    print("Range: %s .. %s" % (out["date_range"]["start"], out["date_range"]["end"]))
    print("Unique keys: %d / %d" % (len(set(keys)), len(keys)))
    print("Page map: %d keys" % len(pmap))
    print("Wrote %s and %s" % (OUT_JSON, OUT_MAP))


if __name__ == "__main__":
    main()
