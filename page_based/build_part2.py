#!/usr/bin/env python3
"""
Build part2.json / part2_page_map.json for slack-part2.pdf (the clean
text-layer Slack export, May 2020 - 2023) from the existing high-quality
message parse already produced by DataWharehouse/_tooling/slack_pdf_to_json.py
(11,357 messages, timestamps, senders, thread ids, attachments).

Reshapes each message into the same {date, raw_date, content, page, idx}
entry schema used by part1.json so the web app can treat both parts
uniformly, while keeping sender/time/thread_id/attachments as extra fields
for display.
"""

import json
import os

from slack_notice import apply_notice_normalization

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_JSON = (
    "/Users/gillesdemaneuf/Work/DataWharehouse/DRASTIC/external_processed/"
    "congressional/slack-drop-pm.json"
)
OUT_JSON = os.path.join(HERE, "part2.json")
OUT_PAGE_MAP = os.path.join(HERE, "part2_page_map.json")
SOURCE_PDF = "slack-part2.pdf"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def raw_date_from_iso(y, m, d):
    return "%s %d, %d" % (MONTHS[m - 1], d, y)


def main():
    with open(SOURCE_JSON, encoding="utf-8") as f:
        src = json.load(f)

    entries = []
    page_map = {}
    unresolved_date = None  # carry-forward date for messages with no timestamp

    for msg in src["messages"]:
        ts = msg.get("timestamp")
        if ts:
            date_part = ts.split(" ")[0]
            time_part = ts.split(" ")[1] if " " in ts else None
            y, mo, d = (int(x) for x in date_part.split("-"))
            raw = raw_date_from_iso(y, mo, d)
            unresolved_date = (date_part, raw)
        elif unresolved_date:
            date_part, raw = unresolved_date
            time_part = None
        else:
            date_part, raw, time_part = "2020-04-30", "April 30, 2020", None

        sender, content = apply_notice_normalization(msg.get("sender"), msg.get("content", ""))

        idx = len(entries)
        entry = {
            "idx": idx,
            "date": date_part,
            "raw_date": raw,
            "sender": sender,
            "time": time_part,
            "thread_id": msg.get("thread_id"),
            "attachments": msg.get("attachments") or [],
            "content": content,
            "redacted": False,
            "page": msg.get("page"),
        }
        entries.append(entry)
        page = msg.get("page") or 1
        page_map[str(idx)] = {"start": page, "end": page, "breaks": [[0, page]]}

    dates_list = sorted(e["date"] for e in entries)
    date_range = {"start": dates_list[0], "end": dates_list[-1]} if dates_list else {}

    out = {
        "source_file": SOURCE_PDF,
        "title": "P.O. Slack — Part 2 (paper-2020-nature_medicine-proximal_origin, continued)",
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
    senders = sorted({e["sender"] for e in entries if e["sender"]})
    print("Senders:", senders)


if __name__ == "__main__":
    main()
