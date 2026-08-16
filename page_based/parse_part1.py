#!/usr/bin/env python3
"""
Message-level parser for slack-part1.pdf (OCR'd Slack screenshots,
Feb 1 - Apr 30, 2020).

Reads slack-part1_ocr.txt, produced by reocr_part1.py (Tesseract, --oem 1
--psm 6, over 300dpi page renders). This re-OCR is dramatically cleaner than
the OCR text layer baked into the PDF by the original "PDF24 Tools - OCR"
pass — spot checks against the actual page images showed the source
screenshots are sharp; the PDF's own OCR pass was simply low quality.

Unlike slack-part2 (a clean text-layer Slack export with one bracketed
message per block), slack-part1 is still OCR'd from stitched screenshots:
reading order is columnar and sender/time headers are occasionally garbled.
This parser anchors on the five known channel participants to find each
message header ("<Sender> <HH:MM>", with an OCR-garbage icon glyph
occasionally prefixing the name and the time occasionally missing a colon or
a digit), then accumulates the lines that follow as that message's content
up to the next header or day-divider.

Two things this cannot fully recover, given the source:
  - Slack visually groups consecutive messages from the same sender without
    repeating the header, so a run of un-headered short paragraphs following
    one header may really be 2-3 separate messages rather than one. They are
    kept as a single entry (correctly attributed, just coarser-grained than
    part2's true one-row-per-message).
  - Black-box redactions in the source produce no OCR text at all, so they
    leave no trace to flag; they are invisible rather than mis-attributed.

OCR cleanup applied while assembling each entry:
  - Leading avatar/icon garbage ("@B Nice channel title" → "Nice channel
    title", "@ Morning" → "Morning"); real @mentions are kept.
  - Slack's document-card chevron (▾), OCR'd as ¥, is dropped.
  - File/image cards are wrapped with "== ATTACHMENT ==" (or
    "== ATTACHMENT(N) =="). Slack Posts / Word / G Suite / shared posts
    are "== EMBEDDED DOC ==" — the Slack "Post ¥" chrome becomes the
    stub "embedded", then the title and body, one line per paragraph.

Slack's own system notices (channel-created banner, "X joined the channel",
channel renames, ...) are re-attributed to a synthetic 'Slack Notice' sender
(the real actor's name is kept in the content text) instead of being
conflated with that person's authored chat messages.
"""

import json
import os
import re

from slack_notice import apply_notice_normalization

HERE = os.path.dirname(os.path.abspath(__file__))
OCR_TEXT_PATH = os.path.join(HERE, "slack-part1_ocr.txt")
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
NOISE_STANDALONE = {"sce"}

FILE_EXT = r"pdf|png|jpe?g|zip|docx?|xlsx?|csv|gif|geneious|pptx?|txt|fasta|gz|ong|prg|xisx"
ATTACHMENT_FILENAME_RE = re.compile(
    r"^[\w.\-+ ]{1,80}\.(?:" + FILE_EXT + r")$",
    re.IGNORECASE,
)
# One filename token. Spaces are allowed only in Slack "Screen Shot …" names;
# two names on one line ("a.geneious b.geneious") are separate files.
FILENAME_TOKEN_RE = re.compile(
    r"(?:Screen\s+Shot\s+\d{4}-\d{2}-\d{2}\s+at\s+[\d.:]+\s*(?:AM|PM)?\.[\w]+"
    r"|[\w.\-+]+\.(?:" + FILE_EXT + r"))",
    re.I,
)
N_FILES_RE = re.compile(r"(?i)^(\d+)\s+files$")

# Slack's ▾ / document-card chevron is consistently OCR'd as yen (¥).
# Real mentions are @Name with no space; "@B Nice..." / "@ Morning" are
# leftover avatar/icon glyphs and should be stripped.
KNOWN_MENTION_RE = re.compile(
    r"^@+(?:Andrew|Eddie|Robert|Kristian|USLACKBOT|channel)\b",
    re.I,
)
LEADING_AT_GARBAGE_RE = re.compile(r"^@+(?:B|[A-Za-z]{1,3})?\s+")

# Slack file/doc type chips that are UI chrome, not authored text.
TYPE_CHIP_RE = re.compile(
    r"(?ix)^(?:(?:a[d.]?\s+)?word\s+doc(?:ument|x)?|google\s+do[cx]|"
    r"g\s*suite\s+document|excel\s+spreadsheet|exce!\s+spreadsheet|"
    r"plain\s+text|zip|pdf|pof|post)"
    r"(?:\s+(?:a[d.]?\s+)?(?:word\s+doc(?:ument|x)?|google\s+do[cx]|"
    r"excel\s+spreadsheet|exce!\s+spreadsheet|plain\s+text|zip|pdf|pof|post|wd))*$"
)

# Cards whose following lines are the attachment preview (title + body).
DOC_ATTACH_RE = re.compile(
    r"(?ix)^(?:post|"
    r"(?:a[d.]?\s+)?word\s+doc(?:ument|x)?|"
    r"g\s*suite\s+document|"
    r"e-?mail\s+from\s+slack\s+for\s+gmail|"
    r"private\s+post[, ]+shared\s+in\s+\d+\s+places?)"
    r"[\s¥*+~»©|.0-9]*$"
)

# Filenames / "N files" / image stubs / PDF chips. Chat often resumes after.
FILE_ATTACH_RE = re.compile(
    r"(?ix)^(?:\d+\s+files|"
    r"pdf|pof|"
    r"(?:[a-z]\.?\s+)?(?:image|mage)[.\w\-]*|"
    r"screen\s*shot\b.+|"
    r"(?:[\w.\-+]+\.(?:pdf|png|jpe?g|gif|zip|docx?|xlsx?|csv|geneious|pptx?|"
    r"txt|fasta|ong|prg|xisx)(?:\s+[¥*+~»©]*)?\s*)+|"
    r".+\(\d+\s*kB\))"
    r"[\s¥*+~»©|.]*$"
)

HEADER_TIME_RE = re.compile(r"^\+?(\d{1,2})[:.](\d{2})$")
HEADER_TIME_DIGITS_RE = re.compile(r"^(\d{3,4})$")

SEQUENCE_LINE_RE = re.compile(r">\w|EPI_ISL|gbkey=|\bgene=|[ACGTNacgtn]{15,}")
# OCR reliably misreads a capital "I" as a pipe when it stands alone as a
# word (preceded/followed by whitespace or sentence punctuation) — verified
# safe by checking every occurrence in this corpus. Left untouched: lines
# that look like pasted genomic/accession data (real "|" field separators,
# e.g. FASTA headers, GISAID EPI_ISL ids) and pipes fused directly onto an
# adjacent letter with no space (too ambiguous to fix confidently).
STANDALONE_PIPE_RE = re.compile(r"(?<![^\s])\|(?![^\s.,!?;:'\")\]])")


def clean_ocr_noise(line):
    if SEQUENCE_LINE_RE.search(line):
        return line
    return STANDALONE_PIPE_RE.sub("I", line)


def strip_leading_at_garbage(line):
    """Drop OCR'd Slack avatar/icon prefixes ('@B ', '@ ', '@@e ').

    Keep real @mentions (@Andrew, @channel, ...).
    """
    if KNOWN_MENTION_RE.match(line):
        return line
    return LEADING_AT_GARBAGE_RE.sub("", line)


def strip_trailing_ui_crumbs(line):
    """Drop Slack chevrons (¥) and leftover | ~ » chrome at end of a line."""
    line = re.sub(r"\s+¥+\s+", " ", line)
    line = re.sub(r"\s*¥+\s*$", "", line)
    line = re.sub(r"\s+[|~»©]+\s*$", "", line)
    return line.strip()


def is_junk_line(line):
    """True for symbol-soup / tiny OCR crumbs that are not authored text."""
    if not line:
        return True
    if re.match(r"^[=_\-—–‐―]{2,}", line):
        return True
    if len(re.findall(r"[-_=—–‐―]", line)) >= 4 and not re.search(r"[A-Za-z]{4,}", line):
        return True
    if re.fullmatch(r"[¥\s\d.,'‘’]+", line):
        return True
    if re.fullmatch(r"[eEoO0\-\s]{2,}", line):
        return True
    if re.fullmatch(r"[\W_eEoO0\-\s]+", line) and not re.search(r"[A-Za-z]{3,}", line):
        return True
    if not re.search(r"[A-Za-z]{3,}", line) and len(line) <= 8:
        return True
    return False


def classify_line(line):
    """'file' | 'doc' | 'chip' | 'junk' | 'chat'."""
    if FILE_ATTACH_RE.match(line) or ATTACHMENT_FILENAME_RE.match(line):
        return "file"
    if DOC_ATTACH_RE.match(line):
        return "doc"
    if TYPE_CHIP_RE.match(line):
        return "chip"
    if is_junk_line(line):
        return "junk"
    return "chat"


def extract_filenames(line):
    """Pull filename tokens out of an attachment line (one name per file)."""
    found = [m.group(0).strip("¥*+~»©|,") for m in FILENAME_TOKEN_RE.finditer(line)]
    found = [n for n in found if n]
    if len(found) >= 2:
        return found
    stripped = line.strip()
    if ATTACHMENT_FILENAME_RE.match(stripped):
        return [stripped]
    return found


def prepare_content_line(raw):
    s = raw.strip()
    if not s:
        return ""
    s = strip_leading_at_garbage(s)
    s = re.sub(r"^[A-Z]\s+(?=Private post\b)", "", s)
    s = re.sub(r"^[a-zA-Z]\.?\s+(?=(?:image|mage))", "", s, flags=re.I)
    s = strip_trailing_ui_crumbs(s)
    if FILE_ATTACH_RE.match(s) or DOC_ATTACH_RE.match(s) or ATTACHMENT_FILENAME_RE.match(s):
        s = re.sub(r"\s+[*+]+\s*$", "", s).strip()
    if s.lower() in NOISE_STANDALONE:
        return ""
    return s


def segment_content(lines):
    """Split prepared lines into ordered ('chat'|'file'|'doc', [lines]) segments.

    File/image cards consume the filename plus immediately following junk.
    Embedded documents (Slack Post, Word, G Suite, shared post, email)
    keep the title + body until the next card or end of the message.
    """
    segments = []
    current = []
    mode = "chat"
    filenames = []

    def flush():
        if current:
            segments.append((mode, current[:]))
            current.clear()

    for line in lines:
        kind = classify_line(line)
        if kind in ("file", "doc"):
            if mode == "chat" or (mode != kind and mode != "chat"):
                flush()
                mode = kind
            if kind == "file":
                filenames.extend(extract_filenames(line))
            current.append(line)
            continue
        if mode == "file":
            if kind == "chip":
                continue
            if kind == "junk":
                current.append(line)
                continue
            if kind == "chat":
                flush()
                mode = "chat"
                current.append(line)
                continue
            current.append(line)
            continue
        if mode == "doc":
            if kind == "chip":
                continue
            current.append(line)
            continue
        if kind in ("chip", "junk"):
            continue
        current.append(line)

    flush()
    return segments, filenames


def format_attach_block(seglines):
    """One file per line; == ATTACHMENT(N) == when N > 1."""
    names = []
    other = []
    for line in seglines:
        cleaned = clean_ocr_noise(line)
        if not cleaned:
            continue
        if N_FILES_RE.match(cleaned):
            continue
        extracted = extract_filenames(cleaned)
        if extracted:
            names.extend(extracted)
            continue
        other.append(cleaned)
    if names:
        label = "== ATTACHMENT(%d) ==" % len(names) if len(names) > 1 else "== ATTACHMENT =="
        return label + "\n" + "\n".join(names)
    if not other:
        return ""
    return "== ATTACHMENT ==\n" + "\n".join(other)


def format_embed_block(seglines):
    """Slack Post / Word / G Suite card → == EMBEDDED DOC == + title + body.

    Slack prints the type twice on a Post (once above the card, once on it).
    That second 'Post' is not another document.
    """
    n_docs = 0
    since_start = 0
    body = []
    for line in seglines:
        cleaned = clean_ocr_noise(line)
        if not cleaned:
            continue
        if DOC_ATTACH_RE.match(cleaned):
            if n_docs == 0 or since_start >= 2:
                n_docs += 1
            since_start = 0
            continue
        if TYPE_CHIP_RE.match(cleaned):
            continue
        body.append(cleaned)
        since_start += 1
    if not body:
        return "", n_docs
    label = "== EMBEDDED DOC(%d) ==" % n_docs if n_docs > 1 else "== EMBEDDED DOC =="
    return label + "\n" + "\n".join(body), max(n_docs, 1)


def format_segments(segments):
    pieces = []
    for kind, seglines in segments:
        if kind == "file":
            block = format_attach_block(seglines)
            if block:
                pieces.append(block)
            continue
        if kind == "doc":
            block, _n = format_embed_block(seglines)
            if not block:
                continue
            # A Slack Post with no authored chat is just the embed chrome
            # ("Post ¥"). Surface that as the stub "embedded".
            if not pieces:
                pieces.append("embedded")
            pieces.append(block)
            continue
        cleaned = [clean_ocr_noise(x) for x in seglines if x]
        if cleaned:
            pieces.append("\n".join(cleaned))
    return "\n\n".join(pieces).strip()


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
    prepared = []
    for ln in content_lines:
        s = prepare_content_line(ln)
        if s:
            prepared.append(s)
    segments, attachments = segment_content(prepared)
    content = format_segments(segments)
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
    with open(OCR_TEXT_PATH, encoding="utf-8") as f:
        text = f.read()
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
    print("With attachment marker: %d" % sum(1 for e in entries if "== ATTACHMENT ==" in e["content"]))
    print("With attachments list: %d" % sum(1 for e in entries if e["attachments"]))
    senders = {}
    for e in entries:
        senders[e["sender"]] = senders.get(e["sender"], 0) + 1
    for s, c in sorted(senders.items(), key=lambda x: -x[1]):
        print("  %-20s %d" % (s, c))


if __name__ == "__main__":
    main()
