#!/usr/bin/env python3
"""
Parser for slack-part1.pdf (OCR'd Slack screenshots, Feb 1 - Apr 30, 2020).

Unlike slack-part2 (a clean text-layer Slack export with one bracketed
message per block), slack-part1 is OCR'd from stitched screenshots: reading
order is unreliable, sender/time lines are garbled, and message boundaries
are not machine-parseable with confidence. Day-divider lines ("February
1st, 2020", "April 30th, 2020 ~") do come through cleanly, though, so this
parser chunks content by day the same way Fauci_Diary's reparse_diary.py
chunks diary entries by date header: accumulate lines until the day
advances, flush one entry per day, and track the PDF page each day's chunk
starts on for the viewer's jump-to-page feature.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_TXT = os.path.join(HERE, "slack-part1_raw.txt")
OUT_JSON = os.path.join(HERE, "part1.json")
OUT_PAGE_MAP = os.path.join(HERE, "part1_page_map.json")
SOURCE_PDF = "slack-part1.pdf"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_INDEX = {m: i + 1 for i, m in enumerate(MONTHS)}

DATE_RE = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b"
)

NOISE_LINE_RE = re.compile(r"^\s*REV\d+\s*$")


def fix_year_ocr_typo(year):
    # Recurring OCR artifact in this scan: "2020" misread as "2920" (9/0 mixup).
    if year == "2920":
        return "2020"
    return year


def iso_date(month_name, day, year):
    year = fix_year_ocr_typo(year)
    return "%04d-%02d-%02d" % (int(year), MONTH_INDEX[month_name], min(int(day), 31))


def raw_date(month_name, day, year):
    year = fix_year_ocr_typo(year)
    return "%s %s, %s" % (month_name, day, year)


def parse():
    text = open(RAW_TXT, encoding="utf-8").read()
    pages = text.split("\x0c")

    entries = []
    cur_key = None       # (iso, raw)
    cur_lines = []
    cur_start_page = None
    cur_last_page = None

    def flush():
        if cur_key is None:
            return
        content = "\n".join(cur_lines).strip()
        content = re.sub(r"\n{3,}", "\n\n", content)
        if not content:
            return
        entries.append({
            "date": cur_key[0],
            "raw_date": cur_key[1],
            "content": content,
            "page": cur_start_page,
            "page_end": cur_last_page,
        })

    for page_num, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        for line in page_text.split("\n"):
            stripped = line.strip()
            if not stripped or NOISE_LINE_RE.match(stripped):
                continue

            squeezed = re.sub(r"\s+", " ", stripped)
            m = DATE_RE.search(squeezed)
            # A day-divider line is short (just the date, plus maybe a
            # trailing "~" or "-"); a date appearing mid-sentence in pasted
            # article text is not a divider, so require the match to cover
            # most of the (whitespace-squeezed) line.
            is_divider = bool(m) and len(squeezed) - (m.end() - m.start()) <= 6

            if is_divider:
                month_name, day, year = m.group(1), m.group(2), m.group(3)
                key = (iso_date(month_name, day, year), raw_date(month_name, day, year))
                if key != cur_key:
                    flush()
                    cur_key = key
                    cur_lines = []
                    cur_start_page = page_num
                cur_last_page = page_num
                continue

            if cur_key is None:
                # Content before the very first day-divider (channel-creation
                # banner on page 1) — attach to a synthetic pre-Feb-1 bucket.
                cur_key = (iso_date("February", "1", "2020"), raw_date("February", "1", "2020"))
                cur_start_page = page_num
            cur_last_page = page_num
            cur_lines.append(line)

    flush()
    return entries


def build_page_map(entries):
    page_map = {}
    for idx, e in enumerate(entries):
        start = e.pop("page")
        end = e.pop("page_end") or start
        page_map[str(idx)] = {"start": start, "end": end, "breaks": [[0, start]]}
    return page_map


def main():
    entries = parse()
    for idx, e in enumerate(entries):
        e["idx"] = idx

    page_map = build_page_map(entries)

    dates_list = sorted(e["date"] for e in entries)
    date_range = {"start": dates_list[0], "end": dates_list[-1]} if dates_list else {}

    out = {
        "source_file": SOURCE_PDF,
        "title": "P.O. Slack — Part 1 (paper-2020-nature_medicine-proximal_origin)",
        "released_by": "Chairman Rand Paul",
        "total_entries": len(entries),
        "date_range": date_range,
        "entries": entries,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(OUT_PAGE_MAP, "w", encoding="utf-8") as f:
        json.dump(page_map, f, ensure_ascii=False, indent=2)

    print("Entries: %d" % len(entries))
    print("Date range: %s" % date_range)
    for e in entries[:5]:
        print(" ", e["date"], e["raw_date"], "->", len(e["content"]), "chars")
    print("...")
    for e in entries[-5:]:
        print(" ", e["date"], e["raw_date"], "->", len(e["content"]), "chars")


if __name__ == "__main__":
    main()
