#!/usr/bin/env python3
"""
Message-level parser for slack-part2.pdf (clean text-layer Slack export,
Apr 30 2020 – Jun 28 2023).

The PDF's repeating block is:

    [YYYY-MM-DD HH:MM:SS]
    [Sender Name]
    optional [thread - ID: YYYY-MM-DD HH:MM:SS]
    message body

i.e. timestamp *precedes* the sender, which precedes the content. An earlier
parser treated the timestamp as a *trailing* closer on the previous message,
so every stamp was attached to the wrong entry (visible at the end of the
export: Eddie's last chat inherited the 2023-06-27 unarchive time).

A handful of pages are image-only in the text layer. Those messages are
kept from the previous part2.json (originally recovered by OCR) and
inserted back by page.
"""

import json
import os
import re
import subprocess
from collections import defaultdict

from slack_notice import apply_notice_normalization

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(HERE, "slack-part2.pdf")
OUT_JSON = os.path.join(HERE, "part2.json")
OUT_PAGE_MAP = os.path.join(HERE, "part2_page_map.json")
OCR_JSON = os.path.join(HERE, "part2_ocr_pages.json")
SOURCE_PDF = "slack-part2.pdf"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

TIMESTAMP_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]$")
THREAD_RE = re.compile(r"^\[thread - ID: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]$")
SENDER_RE = re.compile(r"^\[([^\]]{1,80})\]$")
ATTACHMENT_RE = re.compile(r"\[shared file\(s\):\s*([^\]]+)\]")
NOISE_LINE_RE = re.compile(r"^(SLACK_\d+|Released by Chairman Rand Paul)$")
# pdftotext often glues the running header onto the same line as chat.
STAMP_RE = re.compile(r"\s*Released by Chairman Rand Paul\s*(?:SLACK_\d+)?\s*", re.I)
SLACK_ID_RE = re.compile(r"\s*SLACK_\d+\s*")
KNOWN_SENDERS = {
    "Andrew Rambaut", "Eddie Holmes", "Kristian Andersen", "Robert Garry", "USLACKBOT",
}


def raw_date_from_iso(y, m, d):
    return "%s %d, %d" % (MONTHS[m - 1], d, y)


def pdftotext_pages(pdf_path):
    proc = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        check=True, capture_output=True,
    )
    # pdftotext may warn on stderr about optional-content groups; ignore.
    text = proc.stdout.decode("utf-8", errors="replace")
    return text.split("\x0c")


def join_content_lines(lines):
    content = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if not content:
            content = line
            continue
        last_token = content.rsplit(None, 1)[-1]
        if last_token.lower().startswith(("http://", "https://")):
            content += line
        else:
            content += " " + line
    return content


def finalize_raw(cur):
    content = re.sub(r"[ \t]+", " ", join_content_lines(cur["content_lines"])).strip()
    attachments = [re.sub(r"\s+", " ", a).strip() for a in ATTACHMENT_RE.findall(content)]
    content = ATTACHMENT_RE.sub("", content).strip()
    return {
        "timestamp": cur.get("timestamp"),
        "sender": cur["sender"],
        "thread_id": cur.get("thread_id"),
        "content": content,
        "attachments": attachments,
        "page": cur["page"],
    }


def parse_pages(pages):
    """Return raw messages from the PDF text layer (timestamp-before-sender)."""
    messages = []
    cur = None
    pending_ts = None
    stray = 0

    def flush():
        nonlocal cur
        if cur is None:
            return
        msg = finalize_raw(cur)
        if msg["content"] or msg["attachments"]:
            messages.append(msg)
        cur = None

    for page_num, page_text in enumerate(pages, start=1):
        for raw_line in page_text.split("\n"):
            line = STAMP_RE.sub(" ", raw_line)
            line = SLACK_ID_RE.sub(" ", line).strip()
            if not line or NOISE_LINE_RE.match(line):
                continue

            ts_m = TIMESTAMP_RE.match(line)
            if ts_m:
                flush()
                pending_ts = ts_m.group(1)
                continue

            thread_m = THREAD_RE.match(line)
            if thread_m:
                if cur is not None:
                    cur["thread_id"] = thread_m.group(1)
                continue

            sender_m = SENDER_RE.match(line)
            if sender_m and sender_m.group(1) in KNOWN_SENDERS:
                if cur is not None and cur["content_lines"]:
                    flush()
                cur = {
                    "sender": sender_m.group(1),
                    "timestamp": pending_ts,
                    "thread_id": None,
                    "content_lines": [],
                    "page": page_num,
                }
                pending_ts = None
                continue

            if cur is None:
                stray += 1
                continue
            cur["content_lines"].append(line)

    flush()
    return messages, stray


def load_ocr_messages():
    if not os.path.exists(OCR_JSON):
        return []
    with open(OCR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("messages") or []


def merge_ocr_messages(parsed, ocr_messages):
    """Re-insert image-page messages that the text layer cannot see.

    Keep text-layer order (so an opening message with no stamp stays first
    on its page). OCR extras are appended after any text on that page —
    those pages are blank in the text layer.
    """
    by_page = defaultdict(list)
    for m in parsed:
        by_page[m.get("page") or 0].append(m)
    ocr_by_page = defaultdict(list)
    for e in ocr_messages:
        ocr_by_page[e.get("page") or 0].append({
            "timestamp": None,
            "sender": e.get("sender"),
            "thread_id": e.get("thread_id"),
            "content": e.get("content") or "",
            "attachments": e.get("attachments") or [],
            "page": e.get("page") or 1,
        })
    merged = []
    for page in sorted(set(by_page) | set(ocr_by_page)):
        merged.extend(by_page[page])
        merged.extend(ocr_by_page[page])
    return merged, sum(len(v) for v in ocr_by_page.values())


def to_entry(idx, msg, unresolved_date):
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
    return {
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
    }, unresolved_date


def main():
    pages = pdftotext_pages(PDF_PATH)
    parsed, stray = parse_pages(pages)
    merged, n_ocr = merge_ocr_messages(parsed, load_ocr_messages())

    entries = []
    page_map = {}
    unresolved = ("2020-04-30", "April 30, 2020")
    for msg in merged:
        entry, unresolved = to_entry(len(entries), msg, unresolved)
        entries.append(entry)
        page = entry.get("page") or 1
        page_map[str(entry["idx"])] = {"start": page, "end": page, "breaks": [[0, page]]}

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

    print("Pages: %d" % len(pages))
    print("Text-layer messages: %d" % len(parsed))
    print("OCR-page messages kept: %d" % n_ocr)
    print("Entries: %d" % len(entries))
    print("Date range: %s" % date_range)
    print("Without time: %d" % sum(1 for e in entries if not e["time"]))
    print("Stray lines skipped: %d" % stray)
    senders = {}
    for e in entries:
        senders[e["sender"]] = senders.get(e["sender"], 0) + 1
    for s, c in sorted(senders.items(), key=lambda x: -x[1]):
        print("  %-20s %d" % (s, c))
    print("--- first 3 ---")
    for e in entries[:3]:
        print(e["date"], e["time"], e["sender"], repr(e["content"][:70]))
    print("--- last 4 ---")
    for e in entries[-4:]:
        print(e["date"], e["time"], e["sender"], repr(e["content"][:70]))


if __name__ == "__main__":
    main()
