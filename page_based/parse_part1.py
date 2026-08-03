#!/usr/bin/env python3
"""
Message-level parser for slack-part1.pdf (OCR'd Slack screenshots,
Feb 1 - Apr 30, 2020).

Unlike slack-part2 (a clean text-layer Slack export with one bracketed
message per block), slack-part1 is OCR'd from stitched screenshots: reading
order is columnar and sender/time headers are frequently garbled. This
parser anchors on the five known channel participants to find each message
header ("<Sender> <HH:MM>", with an OCR-garbage icon glyph often prefixing
the name and the time frequently missing a colon, a digit, or entirely),
then accumulates the lines that follow as that message's content up to the
next header or day-divider.

Two things this cannot fully recover, given the source:
  - Slack visually groups consecutive messages from the same sender without
    repeating the header, so a run of un-headered short paragraphs following
    one header may really be 2-3 separate messages rather than one. They are
    kept as a single entry (correctly attributed, just coarser-grained than
    part2's true one-row-per-message).
  - Black-box redactions in the source produce no OCR text at all, so they
    leave no trace to flag; they are invisible rather than mis-attributed.

Slack's own system notices (channel-created banner, "X joined the channel",
channel renames, ...) are re-attributed to a synthetic 'Slack Notice' sender
(the real actor's name is kept in the content text) instead of being
conflated with that person's authored chat messages.
"""

import json
import os
import re
import subprocess

from slack_notice import apply_notice_normalization

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(HERE, "slack-part1.pdf")
OUT_JSON = os.path.join(HERE, "part1.json")
OUT_PAGE_MAP = os.path.join(HERE, "part1_page_map.json")
SOURCE_PDF = "slack-part1.pdf"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_INDEX = {m: i + 1 for i, m in enumerate(MONTHS)}

DATE_RE = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}|[iIl](?=st\b))(?:st|nd|rd|th)?\s*,?\s*(\d{4})\b"
)
# Day-divider text sometimes wraps across two OCR lines ("February\n3rd, 2020").
WRAPPED_DATE_RE = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\s*\n\s*(\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4})",
    re.IGNORECASE,
)

KNOWN_SENDERS = ["Andrew Rambaut", "Eddie Holmes", "Kristian Andersen", "Robert Garry", "USLACKBOT"]

NOISE_LINE_RE = re.compile(r"^\s*REV\d+\s*$")
NOISE_SUBSTRINGS = ("Add description", "Add people", "Send emails to channel", "Pinned by you", "Pinned to this channel")
NOISE_STANDALONE = {"zip", "plain text", "post", "sce"}

ATTACHMENT_FILENAME_RE = re.compile(
    r"^[\w\-. ]{1,80}\.(pdf|png|jpe?g|zip|docx?|xlsx?|csv|gif|geneious|pptx?|txt)$",
    re.IGNORECASE,
)

HEADER_TIME_RE = re.compile(r"^\+?(\d{1,2})[:.](\d{2})$")
HEADER_TIME_DIGITS_RE = re.compile(r"^(\d{3,4})$")


def fix_year_ocr_typo(year):
    # Recurring OCR artifact in this scan: "2020" misread as "2920" (9/0 mixup).
    if year == "2920":
        return "2020"
    return year


def fix_day_ocr_typo(day):
    # "1st" sometimes OCR's with the digit read as a letter ("ist", "lst").
    if not day.isdigit():
        return "1"
    return day


def iso_date(month_name, day, year):
    year = fix_year_ocr_typo(year)
    day = fix_day_ocr_typo(day)
    return "%04d-%02d-%02d" % (int(year), MONTH_INDEX[month_name], min(int(day), 31))


def raw_date(month_name, day, year):
    year = fix_year_ocr_typo(year)
    day = fix_day_ocr_typo(day)
    return "%s %s, %s" % (month_name, day, year)


def normalize_time(raw_token):
    if not raw_token:
        return None
    token = raw_token.strip().lstrip("+")
    m = HEADER_TIME_RE.match(token)
    if m:
        h, mm = int(m.group(1)), int(m.group(2))
    else:
        m2 = HEADER_TIME_DIGITS_RE.match(token)
        if not m2:
            return None
        digits = m2.group(1)
        if len(digits) == 3:
            h, mm = int(digits[0]), int(digits[1:])
        else:
            h, mm = int(digits[:2]), int(digits[2:])
    if 0 <= h < 24 and 0 <= mm < 60:
        return "%02d:%02d" % (h, mm)
    return None


def find_header(line):
    """Return (sender, raw_time_token_or_None) if `line` is a message header, else None.

    A header line's tail after the name is either empty, a time token (with
    anything after the time - typically a garbled same-line day-divider our
    date regex failed to recognize - discarded), or short non-time garbage
    (an OCR-mangled divider/icon). A *long* tail is treated as ordinary prose
    that happens to mention a participant's name near its start, not a header.
    """
    squeezed = re.sub(r"\s+", " ", line.strip())
    if not squeezed:
        return None
    for name in KNOWN_SENDERS:
        idx = squeezed.find(name)
        if 0 <= idx <= 8:
            rest = squeezed[idx + len(name):].strip()
            if rest == "":
                return name, None
            m = re.match(r"^\+?(\d{1,2}[:.]?\d{2,4})\b", rest)
            if m:
                return name, m.group(1)
            if len(rest) <= 40:
                return name, None
    return None


def extract_trailing_divider(line):
    """If `line` ends in a day-divider (possibly after real content), return
    (prefix, iso, raw) with the divider stripped; else (line, None, None)."""
    m = DATE_RE.search(line)
    if not m:
        return line, None, None
    tail = re.sub(r"\s+", "", line[m.end():])
    if len(tail) > 3:  # divider must be at (near) the end of the line
        return line, None, None
    month_name, day, year = m.group(1), m.group(2), m.group(3)
    return line[:m.start()], iso_date(month_name, day, year), raw_date(month_name, day, year)


def finalize_message(sender, time_tokens, content_lines, page, date_key):
    attachments = []
    kept_lines = []
    for ln in content_lines:
        s = ln.strip()
        if not s:
            continue
        if s.lower() in NOISE_STANDALONE:
            continue
        if ATTACHMENT_FILENAME_RE.match(s):
            attachments.append(s)
            continue
        kept_lines.append(s)
    content = "\n".join(kept_lines).strip()
    redacted = not content and not attachments
    if redacted:
        content = "[no OCR text recovered — likely an image or redacted block]"

    time_val = None
    for tok in time_tokens:
        norm = normalize_time(tok)
        if norm:
            time_val = norm
            break

    final_sender, content = apply_notice_normalization(sender, content)

    return {
        "date": date_key[0],
        "raw_date": date_key[1],
        "sender": final_sender,
        "time": time_val,
        "thread_id": None,
        "attachments": attachments,
        "content": content,
        "redacted": redacted,
        "page": page,
    }


def parse():
    text = subprocess.run(
        ["pdftotext", "-layout", PDF_PATH, "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    text = WRAPPED_DATE_RE.sub(lambda m: m.group(1) + " " + m.group(2), text)
    pages = text.split("\x0c")

    entries = []
    cur_date_key = (iso_date("February", "1", "2020"), raw_date("February", "1", "2020"))
    cur_sender = None
    cur_time_tokens = []
    cur_lines = []
    cur_page = None

    def flush():
        if cur_sender is None:
            return
        entries.append(finalize_message(cur_sender, cur_time_tokens, cur_lines, cur_page, cur_date_key))

    for page_num, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        for raw_line in page_text.split("\n"):
            if NOISE_LINE_RE.match(raw_line.strip()):
                continue
            if any(s in raw_line for s in NOISE_SUBSTRINGS):
                continue

            prefix, div_iso, div_raw = extract_trailing_divider(raw_line)
            if div_iso:
                cur_date_key = (div_iso, div_raw)
            line = prefix

            if not line.strip():
                continue

            header = find_header(line)
            if header:
                flush()
                cur_sender, time_tok = header
                cur_time_tokens = [time_tok] if time_tok else []
                cur_lines = []
                cur_page = page_num
                continue

            if cur_sender is None:
                # Pre-header content: the page-1 channel-creation banner.
                cur_sender = "Slack Notice"
                cur_time_tokens = []
                cur_page = page_num
            cur_lines.append(line)

    flush()
    return entries


def build_page_map(entries):
    page_map = {}
    for idx, e in enumerate(entries):
        page = e.pop("page")
        page_map[str(idx)] = {"start": page, "end": page, "breaks": [[0, page]]}
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
    print("Without time: %d" % sum(1 for e in entries if not e["time"]))
    print("Redacted/empty: %d" % sum(1 for e in entries if e["redacted"]))
    senders = {}
    for e in entries:
        senders[e["sender"]] = senders.get(e["sender"], 0) + 1
    for s, c in sorted(senders.items(), key=lambda x: -x[1]):
        print("  %-20s %d" % (s, c))


if __name__ == "__main__":
    main()
