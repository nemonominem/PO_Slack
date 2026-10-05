#!/usr/bin/env python3
"""
Parse the FOIA'd P.O. email release (po-emails.pdf, cited throughout the
P.O. "Tragicomedy" piece as Proximal_Origin_Emails.pdf) into one entry per
email message.

The release ships as scanned page images with no text layer, so the text comes
from reocr_po_emails.py. What that OCR gives us is a stream of Outlook
message headers -- an outer header per message, plus the quoted headers of the
messages it answers, all inside one printed chain.

The rules this follows are the ones written down in SPEC.md (borrowed from the
Fauci diary's email work):

  * one entry per message -- an author at an instant -- never a whole thread
  * an entry holds only what its author wrote; quoted history is its own entry
  * an explicit UTC offset in the stamp always wins
  * otherwise the sender's own institution decides the zone, and the
    assumption is recorded, never silent
  * everything is normalised to ET for ordering, with the local stamp kept

Output: po-emails.json (entries) + po-emails_page_map.json (PDF pages).
"""

import json
import os
import re
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OCR_TXT = os.path.join(HERE, "po-emails_ocr.txt")
OUT_JSON = os.path.join(HERE, "po-emails.json")
OUT_MAP = os.path.join(HERE, "po-emails_page_map.json")
SOURCE_ID = "po-emails"

ET = ZoneInfo("America/New_York")

# ── time zones ──────────────────────────────────────────────────────────────
# The senders in this release sit in five countries, and a stamp with no zone
# has to mean something before a thread can be read in order. The evidence
# used is the sender's own institution, which every message in this release
# states in its signature block or address line:
#
#   Wellcome Trust / UK Government  -> London   (Farrar, Vallance, Ferguson)
#   NIH / NIAID, Bethesda            -> New York (Fauci, Auchincloss, Collins)
#   Scripps Research                -> Los Angeles (Andersen, Farzan)
#   Tulane                          -> Chicago     (Garry)
#   University of Sydney            -> Sydney      (Holmes)
#   Pasteur Institute               -> Paris       (Fouchier)
#
# This is an assumption, and it is applied per sender, not per document: the
# same chain moves between London and Bethesda several times a day.
ZONE_BY_AFFILIATION = [
    (re.compile(r"wellcome|vallance|schreier|ferguson|golding|edinburgh|rambaut|uk "
                r"government|dphe", re.I), "Europe/London", "Wellcome Trust / UK"),
    (re.compile(r"nih|niaid|fauci|auchincloss|collins|shabman|tabak|burke|bfarrar@nih",
                re.I), "America/New_York", "NIH / NIAID, Bethesda"),
    (re.compile(r"scripps|andersen|farzan", re.I), "America/Los_Angeles", "Scripps Research"),
    (re.compile(r"tulane|garry", re.I), "America/Chicago", "Tulane University"),
    (re.compile(r"sydney|holmes|university of sydney", re.I), "Australia/Sydney",
     "University of Sydney"),
    (re.compile(r"pasteur|fouchier|paris|institut", re.I), "Europe/Paris", "Institut Pasteur"),
]
DEFAULT_ZONE = "Europe/London"      # the Wellcome Trust ran this exercise
DEFAULT_ZONE_WHY = "Wellcome Trust (the release's convener)"

# Per-message overrides, each with the evidence that justifies it. Empty unless
# a stamp turns out to be ambiguous; the format is
#   ("2020-02-04", "09:10", "subject-fragment") -> zone
ZONE_OVERRIDES = {}

# ── OCR clean-up ────────────────────────────────────────────────────────────
# The scans are screenshots of Outlook, so each header carries avatar glyphs
# and stray marks ("Edward Holmes | rrr-iYS", "Jeremy Farrar a").
NOISE_TAIL = re.compile(r"\s*[|Il\[\]{}<>«»“”„’‘—–\-–—_=+*#§¶©®™✓✔✗✘»«»…]+"
                        r"\s*(?:[a-zA-Z]{1,4})?\s*$")
HEADER_JUNK = re.compile(r"^[^A-Za-z0-9]+|[^A-Za-z0-9)\]]+$")
# Avatar glyphs the scans leave on header values: "(€]", "[E] ees", "(E]".
# The bracket holds at most two characters (a glyph, or a single letter tag),
# which is what distinguishes it from a real "(NIH/NIAID)" or "(UTC-05:00)".
RE_AVATAR_BRACKET = re.compile(r"[\[(][^)\]]{0,2}[)\]]")
RE_AVATAR_GLYPH = re.compile(r"[€¢§¶©®™]")

FURNITURE = re.compile(
    r"^(REV\d+|CONFIDENTIAL|NIAID|EXCERPT FROM|"
    r"National Institute of Allergy|National Institutes of Health|Bethesda, MD|"
    r"Phone:|FAX:|E-mail:|Director, National|The information in this e-mail|"
    r"it is not intended that|you should delete|received this e-mail in error|"
    r"or any other storage devices|liable for any statements|"
    r"on behalf of the|Building \d+|Room \d+|Contor Drive|NSC \d+|"
    r"National Institutes of Health$)", re.I)

# ── header grammar ──────────────────────────────────────────────────────────
HEADER_FIELDS = ("From", "To", "Cc", "Bcc", "Subject", "Sent", "Date", "Importance")
RE_FROM = re.compile(r"^From:\s*(.+)$", re.I)
# A field header, possibly OCR-glued to the next one ("Cc: Jeremy FarrarSubject:
# x"). The OCR routinely reads the two capitals in "Cc:" as "Ce:" (and "To:" as
# "Pe:"/"Fe:"), so the alternation lists those readings too and split_fields()
# folds them back onto the real field name -- otherwise a Cc list stays glued to
# a Subject line and "Subject: Fwd: ..." leaks into the message body.
FIELD_ALIASES = {
    "ce": "Cc", "cc": "Cc", "bce": "Bcc", "bcc": "Bcc", "gc": "Cc",
    "fe": "To", "pe": "To", "to": "To", "fo": "From",
    "subiect": "Subject", "subjec": "Subject", "subject": "Subject",
    "senf": "Sent", "sent": "Sent", "dafe": "Date", "date": "Date",
}
FIELD_ALIAS_RE = re.compile(
    r"\b(%s)\s*:" % "|".join(sorted(set(HEADER_FIELDS) | set(FIELD_ALIASES),
                                       key=len, reverse=True)), re.I)
RE_FIELD = FIELD_ALIAS_RE
# quoted reply marker: "On 8 Feb 2020, at 22:15, Kristian G. Andersen wrote:"
# The most header lines Outlook ever prints in this release: From, Sent, To,
# Cc, Subject, and a recipient list that wrapped over a few lines. Anything
# beyond this is quoted material, not header.
MAX_HEADER_LINES = 12

RE_INLINE_QUOTE = re.compile(
    r"^On\s+(.{3,40}?),\s*(?:at\s*)?(\d{1,2}:\d{2}\s*(?:am|pm)?|[ap]\.?m\.?),?\s+"
    r"(.+?)\s*(?:<[^>]*>)?\s*(?:wrote|writes):", re.I)


# ── sender names ────────────────────────────────────────────────────────────
# The scans are screenshots of Outlook, so a sender line carries its avatar
# and the tail of the ribbon: "Kristian G. Andersen | rrr", "Edward Holmes
# iii", "Jeremy Farrar esos mmm", "Garry, Robert , 0LUhUtt~'tisisCS@CY". A
# name that matches a known correspondent is normalised to that name; the raw
# string is kept alongside so nothing is silently rewritten.
SENDER_ROSTER = [
    (re.compile(r"andersen", re.I), "Kristian G. Andersen"),
    (re.compile(r"holmes|^edward h", re.I), "Edward Holmes"),
    (re.compile(r"rambaut", re.I), "Andrew Rambaut"),
    (re.compile(r"garry|gary", re.I), "Robert Garry"),
    (re.compile(r"farrar|forar|fara", re.I), "Jeremy Farrar"),
    (re.compile(r"fauci", re.I), "Fauci, Anthony"),
    (re.compile(r"lipkin", re.I), "Lipkin"),
    (re.compile(r"fouchier", re.I), "R.A.M. Fouchier"),
    (re.compile(r"drosten", re.I), "Christian Drosten"),
    (re.compile(r"koopmans", re.I), "Marion Koopmans"),
    (re.compile(r"pohlmann", re.I), "Stefan Pohlmann"),
    (re.compile(r"farzan", re.I), "Michael Farzan"),
    (re.compile(r"auchincloss", re.I), "Auchincloss, Ashley"),
    (re.compile(r"collins", re.I), "Collins, Francis"),
    (re.compile(r"vallance", re.I), "Vallance, Jeremy"),
    (re.compile(r"schreier", re.I), "Schreier, Martin"),
    (re.compile(r"ferguson", re.I), "Ferguson, Rory"),
    (re.compile(r"golding", re.I), "Golding, Josie"),
    (re.compile(r"pope", re.I), "Pope, Andrew"),
    (re.compile(r"thomas", re.I), "Clare Thomas"),
    (re.compile(r"conrad", re.I), "Conrad, Patricia"),
    (re.compile(r"shabman", re.I), "Shabman, Reed"),
    (re.compile(r"folkers", re.I), "Folkers, Greg"),
    (re.compile(r"burke", re.I), "Burke, Martina"),
    (re.compile(r"nature\.com", re.I), "medicine@us.nature.com"),
    # Correspondents who appear only in recipient lists. Listing them makes a
    # wrapped list recognisable; clean_sender still prefers a sender-specific
    # pattern above, and the roster order is what decides between them.
    (re.compile(r"\bbaric\b", re.I), "Baric, Ralph"),
    (re.compile(r"\bdaszak\b", re.I), "Daszak, Peter"),
    (re.compile(r"\btrevor\b|bedford", re.I), "Trevor, Bedford"),
    (re.compile(r"zhai", re.I), "Zhai, Yi"),
    (re.compile(r"chakravarti", re.I), "Chakravarti, Aravinda"),
    (re.compile(r"\bhassell\b", re.I), "Hassell, David"),
    (re.compile(r"\bmich\b", re.I), "Mich, Robert"),
    (re.compile(r"\bshea\b", re.I), "Shea, John"),
]

# First names seen in this release's recipient lists. They are used ONLY to
# recognise a roll of recipients as such (see is_wrapped_recipient), which is
# what lets the Subject line following a wrapped list be recovered instead of
# being left in the message body. They never name a sender: clean_sender reads
# SENDER_ROSTER alone, so a sender line is never rewritten from a first name.
FIRST_NAMES = {
    "ralph", "peter", "andrew", "robert", "edward", "jeremy", "kristian",
    "christian", "marion", "stefan", "michael", "claire", "patricia", "reed",
    "greg", "martina", "francis", "martin", "rory", "josie", "amanda", "tony",
    "eddie", "trevor", "bedford", "aravinda", "david", "john", "richard",
    "yvonne", "sylvia", "susan", "karen", "nicole", "maria", "thomas",
}


def clean_sender(raw):
    raw = re.sub(r"\s*<[^>]*>\s*$", "", (raw or "").strip())
    raw = re.sub(r"\s*\[[^\]]*\]\s*$", "", raw).strip()
    for rx, name in SENDER_ROSTER:
        if rx.search(raw):
            return name, raw
    tail = re.sub(r"[^A-Za-z].*$", "", raw).strip()
    return (tail or raw), raw


# ── timestamps ──────────────────────────────────────────────────────────────
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

# "1/31/2020 6:25:48 PM"  (Outlook US)
RE_STAMP_US = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(?:at\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)")
# "Friday, January 31, 2020 8:05 PM"
RE_STAMP_LONG = re.compile(
    r"(?:[A-Za-z]+,?\s+)?([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\s+"
    r"(?:at\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)")
# "05 March 2020 02:06" (day-month-year, no am/pm -- a UK-forwarded stamp)
RE_STAMP_DMY = re.compile(
    r"(\d{1,2})\s+([A-Za-z]{3,9})\.?\s*,?\s*(\d{4})\s+(?:at\s+)?(\d{1,2}):(\d{2})"
    r"(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)?")
# "Tue 2/4/2020 9:10:35 AM (UTC-05:00)"
RE_STAMP_OFFSET = re.compile(r"\((?:UTC|GMT)?\s*([+-])\s*(\d{1,2}):?(\d{2})\)", re.I)
# a stamp the OCR mangled: "Friday, January 31, :" -- day and month survive
RE_STAMP_PARTIAL = re.compile(
    r"(?:[A-Za-z]+,?\s+)?([A-Za-z]{3,9})\.?\s+(\d{1,2})\s*(?:,|:|$)")


def _ampm(h, ap):
    h = int(h)
    ap = ap.lower().replace(".", "")
    if ap.startswith("p") and h != 12:
        h += 12
    if ap.startswith("a") and h == 12:
        h = 0
    return h


def parse_stamp(text):
    """-> (naive datetime, offset-or-None, how) or (None, None, 'unparsed')"""
    t = text.strip()
    off = None
    om = RE_STAMP_OFFSET.search(t)
    if om:
        sign = 1 if om.group(1) == "+" else -1
        off = timedelta(hours=sign * int(om.group(2)), minutes=sign * int(om.group(3)))
    m = RE_STAMP_US.search(t)
    if m:
        mo, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12:
            dt = datetime(yr, mo, day, _ampm(m.group(4), m.group(7)), int(m.group(5)))
            return dt, off, ("offset" if off else "outlook-us")
    m = RE_STAMP_DMY.search(t)
    if m:
        mo = MONTHS.get(m.group(2)[:3].lower())
        if mo:
            ap = m.group(7) or "12:00am"
            dt = datetime(int(m.group(3)), mo, int(m.group(1)),
                          _ampm(m.group(4), ap), int(m.group(5)))
            return dt, off, ("offset" if off else "day-month-year")
    m = RE_STAMP_LONG.search(t)
    if m:
        mo = MONTHS.get(m.group(1)[:3].lower())
        if mo:
            dt = datetime(int(m.group(3)), mo, int(m.group(2)),
                          _ampm(m.group(4), m.group(7)), int(m.group(5)))
            return dt, off, ("offset" if off else "long")
    m = RE_STAMP_PARTIAL.search(t)
    if m:
        mo = MONTHS.get(m.group(1)[:3].lower())
        if mo:
            return datetime(2020, mo, int(m.group(2)), 12, 0), off, "partial-no-time"
    return None, None, "unparsed"


def zone_for(sender, subject, dt):
    """Pick a zone and say why. Explicit offsets are handled by the caller."""
    for key in (dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")) if dt else ():
        pass
    if dt:
        ov = ZONE_OVERRIDES.get((dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M"),
                                 (subject or "")[:40]))
        if ov:
            return ZoneInfo(ov[0]), ov[1]
    for rx, zone, why in ZONE_BY_AFFILIATION:
        if rx.search(sender or ""):
            return ZoneInfo(zone), why
    return ZoneInfo(DEFAULT_ZONE), DEFAULT_ZONE_WHY


def to_et(dt, tzinfo, why):
    """Normalise to ET, keeping the local stamp for display."""
    local = dt.replace(tzinfo=tzinfo)
    et = local.astimezone(ET)
    if local.utcoffset() == et.utcoffset():
        return et, "%s %s" % (et.strftime("%H:%M"), "ET")
    return et, "%s %s -> %s ET" % (
        local.strftime("%H:%M"), tzinfo.key.split("/")[-1].replace("_", " "),
        et.strftime("%H:%M"))


# ── reading the OCR ─────────────────────────────────────────────────────────

def load_pages():
    """-> [(page_no, [lines])]"""
    with open(OCR_TXT, encoding="utf-8") as f:
        raw = f.read()
    out = []
    for i, page in enumerate(raw.split("\x0c"), start=1):
        lines = [clean_line(l) for l in page.split("\n")]
        lines = [l for l in lines if l and not FURNITURE.match(l)]
        if lines:
            out.append((i, lines))
    return out


def clean_line(line):
    line = line.replace(" ", " ")
    line = re.sub(r"[ \t]+", " ", line).strip()
    if RE_FROM.match(line):
        line = HEADER_JUNK.sub("", line)
        line = NOISE_TAIL.sub("", line)
    return line.strip()


def split_fields(block):
    """Split a run of lines into header fields.

    The OCR glues fields together ("Cc: Jeremy FarrarSubject: Re: Phone call"),
    so fields are found by their keywords rather than by line breaks. Only
    From/To/Cc/Bcc may continue onto the next line; Subject, Sent and Date are
    terminal -- that is what stops the header block swallowing the body.
    """
    fields, order = OrderedDict(), []
    current = None
    for line in block:
        parts = RE_FIELD.split(" " + line)
        # parts[0] is the text before the first keyword (often empty)
        if len(parts) == 1:
            if current in ("From", "To", "Cc", "Bcc"):
                fields[current] += " " + line.strip()
            continue
        if parts[0].strip():
            if current in ("From", "To", "Cc", "Bcc"):
                fields[current] += " " + parts[0].strip()
        for i in range(1, len(parts) - 1, 2):
            # "Ce:" -> "Cc", "Pe:" -> "To": fold the OCR's misreading back onto
            # the real Outlook field name (see FIELD_ALIASES).
            name = FIELD_ALIASES.get(parts[i].strip().lower()) \
                or parts[i].strip().title()
            if name not in HEADER_FIELDS:
                name = name.title()
            value = parts[i + 1].strip() if parts[i + 1].strip() else ""
            if name not in fields:
                order.append(name)
            fields[name] = (fields.get(name, "") + (" " if name in fields else "") + value).strip()
            current = name
    return fields


def segment(pages):
    """Split the page stream into messages.

    A new message starts at a line that opens a From: header. Everything until
    the next such line is that message's header block plus body; an inline
    "On <date>, <person> wrote:" marker inside a body starts a recovered
    quoted message of its own, so its words are not silently attributed to
    the person who replied.
    """
    messages = []
    cur = None
    for pageno, lines in pages:
        body_mode = False
        for li, line in enumerate(lines):
            nxt = lines[li + 1] if li + 1 < len(lines) else None
            if RE_FROM.match(line):
                cur = {"header_lines": [line], "body": [], "pages": [pageno]}
                messages.append(cur)
                body_mode = False
                continue
            if cur is None:
                continue
            cur["pages"].append(pageno)
            if not body_mode:
                # The header block ends at the first line that is not a field --
                # but the scans drop glyph fragments between the fields ("Pe",
                # "E|", "T {"). Those lines carry no word and no digit, so they
                # are skipped rather than treated as the start of the body;
                # otherwise the Subject line after one lands in the body and the
                # subject is lost from the header.
                if len(cur["header_lines"]) > 1 and is_junk_line(line):
                    continue
                # still inside the header block until a blank-looking break:
                # a line with no field keyword after at least one field
                has_field = bool(RE_FIELD.search(line))
                if cur["header_lines"] and not has_field and len(cur["header_lines"]) > 1:
                    # A long To:/Cc: list wraps over several visual lines before
                    # the Subject arrives. Those belong to the header: treating
                    # the first of them as the body stranded every following
                    # field ("Subject: ...") in the message text.
                    #
                    # The block is also bounded. Outlook never prints eighteen
                    # header lines: what follows a long recipient list here is
                    # quoted letterhead ("The National Academies of / SCIENCES
                    # ... / Cheers, / Peter") that the scan ran on from. Past the
                    # bound the block is closed, whatever the line looks like, so
                    # quoted material cannot be absorbed into the header and
                    # push the real Subject out of reach.
                    if (cur.get("in_addr") and len(cur["header_lines"]) <= MAX_HEADER_LINES
                            and (is_address_continuation(line)
                                 or is_wrapped_recipient(line, nxt))):
                        cur["header_lines"].append(line)
                        continue
                    body_mode = True
                    cur["body"].append(line)
                elif has_field or len(cur["header_lines"]) == 1:
                    cur["header_lines"].append(line)
                    # Track which field we are in, so only the recipient fields
                    # are allowed to wrap.
                    names = [n.strip().lower() for n in RE_FIELD.findall(line)]
                    if names:
                        cur["in_addr"] = names[-1] in (
                            "to", "cc", "bcc", "fe", "pe", "ce")
                else:
                    body_mode = True
                    cur["body"].append(line)
            else:
                cur["body"].append(line)
    return messages


def is_junk_line(line):
    """True for the OCR scatter a quoted image leaves behind.

        iY Ae ms F 4
        , 'y '
        ~ ne a
        Pe

    A line that carries no real word -- nothing three letters or longer -- no
    URL and no long number is that kind of noise. Real prose, names and even a
    bare "Tony" survive; the image scatter and the stray glyph fragments do not.
    """
    s = (line or "").strip()
    if not s:
        return True
    return not (re.search(r"[A-Za-z]{3,}", s)
                or re.search(r"https?://|www\.|@", s)
                or re.search(r"\b\d{4,}\b", s))


def strip_glyph_soup(lines):
    """Drop the OCR noise the scans inject when an email quotes an image.

    See is_junk_line(): a line with no real word and no URL is image scatter.
    """
    return [ln for ln in lines if not is_junk_line(ln)]


def clean_field_value(name, value, sender):
    """A header value as it should read on the card.

    From is the roster-canonical sender; the other fields get their avatar
    brackets and glyphs stripped. The raw value survives in `sender_raw`, so
    nothing is silently rewritten.
    """
    v = (value or "").strip()
    if name == "From":
        return sender
    v = RE_AVATAR_BRACKET.sub("", v)
    v = RE_AVATAR_GLYPH.sub("", v)
    # A short letter-run glued after a closing bracket is the avatar's tail
    # ("... (NIH/NIAID) ees" -> "... (NIH/NIAID)"), not part of the address.
    v = re.sub(r"([)\]])\s+[A-Za-z]{1,3}\s*$", r"\1", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v



# ── signature blocks ─────────────────────────────────────────────────────────
# Edward Holmes signs off with a title block and no salutation, so the block is
# recognised by shape. These are the lines that open one: a name carrying
# post-nominals, an all-caps title, or an affiliation.
RE_SIG_NAME = re.compile(
    r"^(?:PROFESSOR|Professor|DR|Dr|MR|Mr|MS|Ms|SIR|Sir|DAME|Dame)\b"
    r"|^(?:[A-Z][A-Z.'-]+\s+){1,4}[A-Z][A-Z.'-]*"
    r"\s+(?:FAA|FRS|FBA|FRCS|FACP|PhD|Ph\.D|MD|M\.D|MP|MSc|BSc|MBBS)\b")
RE_SIG_AFFIL = re.compile(
    r"^(?:ARC |THE |UNIVERSITY|University|Institut|CENTRE|Centre|School|"
    r"Department|Dept\.|Faculty|College|Hospital|Institute|Trust|Laborator|"
    r"Director|Regents|Dean|Regent|Professor Emeritus|"
    r"Marie Bashir|Wellcome|MRC|NIH|NIAID|Atlanta|Bethesda|London|Sydney)\b")
RE_SIG_CONT = re.compile(
    r"^(?:The University of|University of|Sydney|NSW|Australia|Victoria)\b")


def is_signature_line(s):
    """True if this line opens (or continues) a title/sign-off block."""
    s = (s or "").strip()
    if not s:
        return False
    if RE_SIG_NAME.match(s) or RE_SIG_AFFIL.match(s):
        return True
    # A continuation line, but only once a block has started -- handled by the
    # caller, which stops cutting at the first line that is neither.
    return False


# ── page-width line wrapping ─────────────────────────────────────────────────
# The scans are screenshots, so a paragraph is broken wherever the Outlook pane
# ended it -- an artefact of the column width, not a return the author typed.
# A line that neither ends a sentence nor starts a new one is joined to the
# next; a line ending in '.', '!', '?', ':' or a comma-separated clause keeps
# its return, because that one is the author's.
RE_SENTENCE_END = re.compile(r"[.!?:;…]['\")\]]?\s*$")
RE_SOFT_START = re.compile(r"^\s*[,;:.)\]]")


# A line that continues a recipient list rather than starting the body. The
# scans wrap long To:/Cc: lists over several visual lines, each carrying the
# avatar glyphs ("\"rambaut , "rfgarry!"), so a continuation has separators and
# glyphs but no sentence-ending punctuation. Prose has the opposite shape.
RE_ADDR_CONT = re.compile(r"[,;|/\\]|(?:^|[\s(])[\"']?[A-Za-z]{1,3}[\"']?(?:[\s,|]|$)")


def is_address_continuation(line):
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s):
        return False
    if len(s) > 160:
        return False
    return bool(RE_ADDR_CONT.search(s))


def is_name_debris(line):
    """A scrap of a wrapped recipient list: names and glyphs, not prose.

    Prose always carries a real word -- a lower-case run of five letters or more
    ("Information and discussion", "ist February"). A recipient scrap is
    surnames, initials and OCR glyphs ("<rfzarry RR Mich! Fcc", ""spoehlmann
    "a rambau"). That difference is what tells the two apart when the scan has
    torn the list across lines.
    """
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 200:
        return False
    return not re.search(r"[a-z]{5,}", s)


def is_wrapped_recipient(line, nxt=None):
    """True for a line inside a To:/Cc: list that the scan wrapped.

    Two ways to qualify. The cheap one is is_name_debris(): no sentence
    punctuation and no real word. When a line does carry a real word but is
    neither sentence-terminated nor anything but capitalised names
    ("spoehlmann "a rambau "Kristian G."), it still counts if the NEXT line
    continues the same list -- which is the signal the scan itself gives us.
    Looking ahead is safe because the caller has already established we are
    inside a recipient field, and prose is never followed by two address lines.
    """
    if is_name_debris(line):
        return True
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 120:
        return False
    # No sentence punctuation, and shaped like a name list rather than prose.
    names = re.findall(r"[A-Z][a-zA-Z.'-]{2,}", s)
    words = re.findall(r"[A-Za-z']{2,}", s)
    if not names:
        return False
    # Either mostly names, or a comma-separated roll of them: recipient lists
    # run to a dozen surnames per line ("Brown, Lisa Downey, Autumn Wollek,
    # Scott ; Kanarek, Morgan Dzau"), which reads as prose by word count alone.
    # A bare roll of personal names with nothing else on the line ("Ralph
    # Baric trevor Peter Daszak") is the same thing without the commas.
    comma_list = s.count(",") >= 2 and len(names) >= 2
    bare_names = s.count(",") == 0 and len(names) >= 3
    # No need to look ahead once the line is unambiguously a list of names.
    if comma_list or bare_names:
        return True
    tokens = re.findall(r"[A-Za-z']{2,}", s)
    all_known = bool(tokens) and all(
        (t.lower() in FIRST_NAMES
         or any(rx.search(t) for rx, _ in SENDER_ROSTER))
        for t in tokens)
    if not all_known and len(names) * 2 < len(words):
        return False
    return nxt is not None and (is_name_debris(nxt) or RE_FIELD.match(nxt.strip()))


# ── recipient-run continuation ───────────────────────────────────────────────
# Once the header block is known to be inside a To:/Cc: list, the run continues
# until something that cannot be a recipient appears. Individual lines are hard
# to judge alone -- "ee SheltonDavenport, Marilee a ee" is neither prose nor a
# clean name list -- but in context they are simply more of the same list. So
# this weaker test is used only inside a run, never to open one.
def continues_recipient_run(line, nxt=None):
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 200:
        return False
    # Prose: far more ordinary words than capitalised names. Compared as a ratio,
    # not a multiple -- "Morgan Dzau, VictorJ. Beachy" reads as one word to the
    # name regex and two to the word regex, and a strict multiple rejected it.
    words = re.findall(r"[a-z]{3,}", s)
    names = re.findall(r"[A-Z][a-zA-Z.'-]{2,}", s)
    if len(words) > 4 and len(names) * 2 < len(words):
        return False
    # A comma-separated roll of names cannot be prose, whatever it contains: the
    # separators decide it. ("Morgan Dzau, VictorJ. Beachy, Sarah ; Logan" has
    # a full stop in it, but no sentence test can tell that from a surname.)
    if s.count(",") >= 2 and len(names) >= 2:
        return True
    # Two sentences: not a list. A middle initial ("VictorJ. Beachy") is not a
    # sentence end, so the capital after the period must start a real word.
    if re.search(r"[.!?]\s+[A-Z][a-z]{2,}", s):
        return False
    return True


def unwrap_lines(lines):
    """Rejoin paragraphs that the scan width broke, keeping real returns.

    Two signals are used together, so neither alone can invent or destroy a
    return:

      * the previous line must not end a sentence (no . ! ? : ;), and
      * the next line must start like a continuation -- lower-case, or a
        conjunction/particle, or a bracket.

    A line ending in a full stop keeps its return even if the next line starts
    lower-case, because that is a new sentence and only its capital was lost to
    the scan. Signature blocks and quoted history are left alone: their returns
    are the author's.
    """
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if out and out[-1].strip() and not RE_SENTENCE_END.search(out[-1]):
            prev = out[-1].rstrip()
            # mid-sentence break + next line reads as a continuation -> one line
            cont = (prev.endswith("-")                 # hyphenated word split
                    or RE_SOFT_START.match(s)          # starts on a bracket
                    or (s[:1].islower() and prev[-1:].isalpha()))
            if cont and not re.match(r"^(?:[-*•>]|\d+[.)])\s", s):
                out[-1] = (prev[:-1] if prev.endswith("-") else prev) + " " + s
                continue
        out.append(line)
    return out


def is_header_fragment(line):
    """A stray scrap of a header that the two-column scan tore off.

    A quoted message printed beside its parent has its header lines split
    across the column boundary, so a name lands on its own line between fields
    ("... ; Jeremy" / "Farrar" / "Subject: ..."). Such a scrap is short, has no
    sentence-ending punctuation, and does not read as prose: it is one or two
    capitalised words and nothing else.
    """
    s = (line or "").strip()
    if not s or len(s) > 40 or RE_SENTENCE_END.search(s):
        return False
    if not re.match(r"^[A-Z][A-Za-z'.-]*(?:[ /][A-Za-z][A-Za-z'.-]*){0,3}$", s):
        return False
    # A single ordinary capitalised word is prose far more often than a torn
    # header, so require it to look like a name from the roster.
    return bool(re.search(r"(?:andersen|rambaut|farrar|holmes|garry|fauci|drosten|"
                           r"koopmans|pohlmann|farzan|andersen|fouchier|schreier|"
                           r"ferguson|golding|lipkin|vallance|collins|auchincloss|"
                           r"conrad|shabman|folkers|burke|pope|thomas|"
                           r"edward|andrew|jeremy|kristian|robert|anthony|christian|"
                           r"marion|stefan|michael|claire|patricia|reed|martina|"
                           r"greg|andrew|josie|amanda|francis|jeremy|martin|rory|"
                           r"eddie|tony|toney|farrar|beach|comin|perdue)", s, re.I))


def split_signature(body):
    """-> (body_lines, signature_lines): cut the sign-off block off the message.

    strip_quoted used to key on a salutation ("Best regards", "Jeremy Farrar"),
    which catches the senders who sign off but not Edward Holmes: his messages
    run straight from the text into his title block

        PROFESSOR EDWARD C. HOLMES FAA FRS
        ARC Australian Laureate Fellow
        THE UNIVERSITY OF SYDNEY
        Marie Bashir Institute for Infectious Diseases & Biosecurity, ...

    with no salutation to key on, so the block was read as message text and its
    line returns lost. It is recognised by shape instead -- a credentialed
    name line, or an affiliation line -- and is returned separately so it can be
    shown as a signature (with its returns) rather than as prose.

    The cut is only taken once some prose has been read, so a message that opens
    on an affiliation line keeps it.
    """
    out, sig, cut = [], [], None
    for i, line in enumerate(body):
        s = line.strip()
        if cut is None and out and is_signature_line(s):
            cut = i
        if cut is None:
            out.append(line)
        else:
            sig.append(line)
    return out, sig


def strip_quoted(body):
    """Drop the signature block: everything from the sign-off onwards."""
    out, cut = [], None
    for i, line in enumerate(body):
        if cut is None and re.match(
                r"^(Best regards|Best wishes|Warm regards|Thanks,|Kind regards|"
                r"With best wishes|Yours sincerely|Yours,|Best,|Many thanks|"
                r"Jeremy Farrar$|Anthony S\. Fauci|Tony$|Eddie$|Anders$|"
                r"Andrew Rambaut$|Robert Garry$)", line.strip(), re.I):
            cut = i
        if cut is None:
            out.append(line)
    return out


def build_entries(messages):
    entries = []
    for msg in messages:
        fields = split_fields(msg["header_lines"])
        sender, sender_raw = clean_sender(fields.get("From") or "")
        stamp = fields.get("Sent") or fields.get("Date") or ""
        body = strip_quoted(msg["body"])
        # The screenshot layout puts Cc/Subject on their own visual lines, and
        # the OCR sometimes yields them after the block has already been read
        # as body. Anything that is plainly a header field at the very top of
        # the body belongs to the header, not to the message text. Skipping the
        # junk lines first matters: "Pe" between the To: and Subject: lines used
        # to stop this loop before it reached the Subject, which then stayed in
        # the message body ("Subject: Fwd: ..." printed as prose).
        while body:
            head = body[0].strip()
            if RE_FIELD.match(head):
                extra = split_fields(body[:1])
                for k, v in extra.items():
                    if v and not fields.get(k):
                        fields[k] = v
                body = body[1:]
                continue
            if is_junk_line(head) or is_header_fragment(head):
                body = body[1:]
                continue
            break
        # The screenshot layout puts Cc/Subject on their own visual lines, and
        # the OCR sometimes yields them after the block has already been read as
        # body -- the header block having been closed early by a glyph fragment
        # ("Pe") or by a torn-off scrap of a two-column recipient list. Chasing
        # those one at a time is fragile, so the top of the body is swept once
        # instead: a field within a short window is promoted back into the header
        # where it belongs, and the debris before it is dropped.
        #
        # The window is deliberately small. A Subject line appearing further down
        # is quoted history inside the message, not this message's own header,
        # and promoting it would put the wrong subject on the card.
        #
        # A trailing Subject is also handled here: when a wrapped recipient list
        # swallowed the line after the Subject ("Cc: ... Message" + the subject on
        # the next line), the Subject is still recovered from the text just
        # below, which is what it was.
        window = min(len(body), 8)
        found = -1
        for i in range(window):
            if RE_FIELD.match(body[i].strip()):
                found = i
                break
        if found >= 0:
            # Keep going while the recipient fields continue, and take the LAST
            # field of the run -- that is the one whose line must be consumed
            # from the body. Stopping at the first would leave the Subject that
            # follows the run stranded in the message text.
            j = found + 1
            while j < min(len(body), 60):
                if RE_FIELD.match(body[j].strip()):
                    names = [n.strip().lower() for n in RE_FIELD.findall(body[j])]
                    if any(n in ("to", "cc", "bcc", "ce", "fe", "pe", "gc")
                           for n in names):
                        found = j
                        j += 1
                        continue
                    # A non-recipient field (Subject/Sent/Date) ends the run and
                    # is itself part of the header, so it is consumed too:
                    # the loop below splits fields up to `found` and drops the
                    # body from `found + 1` onward.
                    found = j
                    break
                if not continues_recipient_run(body[j]):
                    break
                j += 1
            else:
                found = j - 1
        if found < 0:
            # A group message can carry a forty-line recipient list, pushing the
            # real Subject well past the short window. Widen the search only
            # while every line skipped is recipient debris -- a name list, never
            # prose -- so a Subject inside quoted history is still not promoted.
            # The loop starts one line early because a recipient field ("Cc:",
            # OCR'd as "GC:") may itself sit past the window.
            i = max(0, window - 1)
            while i < min(len(body), 60):
                if RE_FIELD.match(body[i].strip()):
                    found = i
                    break
                if not (is_name_debris(body[i]) or is_header_fragment(body[i])
                        or is_wrapped_recipient(body[i], body[i + 1] if i + 1 < len(body) else None)
                        or is_junk_line(body[i])):
                    break
                i += 1
            if found >= 0:
                # Follow the recipient run to its end, so the Subject behind it
                # is reached rather than the Cc line in front of it.
                j = found + 1
                while j < min(len(body), 60):
                    if RE_FIELD.match(body[j].strip()):
                        names = [n.strip().lower() for n in RE_FIELD.findall(body[j])]
                        if not any(n in ("to", "cc", "bcc", "ce", "fe", "pe", "gc")
                                   for n in names):
                            break
                        found = j
                        j += 1
                        continue
                    if not continues_recipient_run(body[j]):
                        break
                    j += 1
        # No field at all. A Subject can still be sitting immediately
        # below a torn-off fragment of the recipient list, because the list ran
        # past the column and the Subject's own line was swallowed with it
        # ("... Edward Holmes" + "Subject: Teleconterence"). It is only taken
        # when it is a genuine Subject line -- an earlier version inferred one
        # from whatever prose came next, which invented subjects such as
        # "Ralph Baric trevor Peter Daszak".
        if found < 0 and not fields.get("Subject") and body:
            m = re.match(r"^\s*Subjec\w*:?\s*(.+)$", body[0], re.I)
            if m and len(m.group(1).strip()) > 3:
                fields["Subject"] = m.group(1).strip()
                body = body[1:]
                found = 0
        if found >= 0:
            for j in range(found):
                extra = split_fields(body[j:j + 1])
                for k, v in extra.items():
                    if v and not fields.get(k):
                        fields[k] = v
            body = body[found + 1:]
        subject = (fields.get("Subject") or "").strip()
        # Order matters: junk is dropped first (so it cannot open a block), then
        # the signature is cut off the message text, and only then are the
        # scan-width breaks rejoined -- over the message text only, so the
        # signature's own returns survive.
        body = strip_glyph_soup(body)
        body, signature = split_signature(body)
        body = unwrap_lines(body)
        content_body = "\n".join(body).strip()

        dt, off, how = parse_stamp(stamp)
        if dt is None:
            # no usable stamp: keep the text, but never invent a date
            entries.append({
                "date": None, "time": None, "kind": "email",
                "raw_date": subject or "(undated message)",
                "sender": sender, "sender_raw": sender_raw, "subject": subject,
                "content": header_block(fields, content_body, sender, signature),
                "date_note": "no usable timestamp in the release; not plotted",
                "pages": sorted(set(msg["pages"])), "source": SOURCE_ID,
                "stamp_status": how,
            })
            continue

        if off is not None:
            tzinfo = ZoneInfo("UTC")
            local = dt - off          # fold the offset back in, then convert
            et = local.astimezone(ET)
            zone_why = "explicit UTC%s%02d:%02d in the stamp" % (
                "+" if off.total_seconds() >= 0 else "-",
                abs(off.total_seconds()) // 3600,
                (abs(off.total_seconds()) % 3600) // 60)
            stamp_line = "%s %s -> %s ET" % (
                stamp.strip(), ("UTC%s%02d:%02d" % (
                    "+" if off.total_seconds() >= 0 else "-",
                    int(abs(off.total_seconds()) // 3600),
                    int(abs(off.total_seconds()) % 3600 // 60))), et.strftime("%H:%M"))
            del tzinfo
        else:
            tzinfo, zone_why = zone_for(sender, subject, dt)
            et, stamp_line = to_et(dt, tzinfo, zone_why)
            if how == "partial-no-time":
                stamp_line += " (time not recovered)"

        entries.append({
            "date": et.strftime("%Y-%m-%d"),
            "time": et.strftime("%H%M"),
            "kind": "email",
            "raw_date": "%s ET · %s" % (et.strftime("%H:%M"), subject or "(no subject)"),
            "sender": sender, "sender_raw": sender_raw,
            "subject": subject,
            "content": header_block(fields, content_body, sender, signature),
            "signature": "\n".join(signature).strip() if signature else None,
            "stamp": stamp.strip(),
            "stamp_status": how,
            "zone_assumed": zone_why,
            "stamp_line": stamp_line,
            "pages": sorted(set(msg["pages"])),
            "source": SOURCE_ID,
        })
    return entries


def header_block(fields, body, sender, signature=None):
    """From/To/Cc/Subject/Sent stay inside `content` so they remain searchable
    and highlightable; the UI splits on the rule to style them apart.

    Header values are shown cleaned: From is the roster-canonical sender, and
    the other fields have their avatar glyphs stripped (the raw text survives
    in `sender_raw`).

    The signature block is appended after its own rule, one line per return, so
    it reads as a signature rather than as more of the message. Its returns are
    the sender's own, so they are kept exactly as scanned."""
    head = []
    for k in ("From", "To", "Cc", "Bcc", "Subject", "Sent", "Date", "Importance"):
        if fields.get(k):
            head.append("%s: %s" % (k, clean_field_value(k, fields[k], sender)))
    out = "\n\n".join(head) + "\n\n----------\n\n" + body
    if signature:
        out += "\n\n----------\n\n" + "\n".join(signature).strip()
    return out


# ── page-break repair ───────────────────────────────────────────────────────
# A long message is printed across two pages and Outlook repeats its header at
# the top of the continuation, so the stream looks like two messages with the
# same sender, stamp and subject but different bodies. Left alone that both
# mis-counts the release and collides their entry keys (the key is built from
# the date and minute). Consecutive entries with the same identity are one
# message, so their bodies are joined.
def merge_page_splits(entries):
    """Join messages the printer split across a page boundary.

    A long message printed over two pages shows its header again at the top of
    the continuation, so it arrives as two entries with the same sender, stamp
    and subject but different bodies -- and, because the entry key is built from
    the date and minute, colliding keys. The halves are not adjacent in the
    stream (other messages print between them), so they are grouped by
    identity and rejoined in page order.
    """
    groups, order = {}, []
    for e in entries:
        ident = (e.get("sender"), e.get("subject"), e.get("stamp"),
                 e.get("stamp_status"), e.get("kind"))
        if ident not in groups:
            groups[ident] = []
            order.append(ident)
        groups[ident].append(e)

    out = []
    for ident in order:
        parts = groups[ident]
        head = parts[0]
        for extra in parts[1:]:
            h, sep, body = extra["content"].partition("----------")
            head["content"] = (head["content"].rstrip() + "\n" +
                               (body if sep else extra["content"]).strip())
            head["pages"] = sorted(set(head.get("pages", []) + extra.get("pages", [])))
            head["merged_pages"] = head.get("merged_pages", 0) + 1
        out.append(head)
    return out


# ── threading ───────────────────────────────────────────────────────────────
# The release prints a conversation grouped by thread, NOT in time order: the
# "Summary - Invitation to edit" thread runs 01:23, 19:08, 17:56, 17:08, 14:39.
# (That is worth stating because it looks like a parsing bug and is not --
# it also means document order cannot be used to check chronology here.)
#
# What it does give us for free is the thread membership. Messages sharing a
# normalised subject belong to one conversation, so once they are sorted by
# their own stamps, each links to the one before it. The link is marked
# inferred: the release carries no message-id to prove it, unlike the inline
# "On <date>, <person> wrote:" markers, which are explicit and are labelled as
# such when found.
RE_SUBJ_PREFIX = re.compile(r"^\s*(re|fw|fwd?|fwd)\s*[:\-]\s*", re.I)


def norm_subject(subject):
    prev = None
    s = (subject or "").strip()
    while prev != s:
        prev = s
        s = RE_SUBJ_PREFIX.sub("", s).strip()
    return s.lower()


def thread_entries(entries):
    """Link messages that share a conversation, in time order."""
    groups = defaultdict(list)
    for e in entries:
        if e.get("date"):
            groups[norm_subject(e.get("subject"))].append(e)
    linked = 0
    for key, group in groups.items():
        if not key or len(group) < 2:
            continue
        group.sort(key=lambda e: (e["date"], e.get("time") or ""))
        for prev_e, e in zip(group, group[1:]):
            e["reply_to"] = prev_e["thread_key"]
            e["reply_to_label"] = prev_e["thread_label"]
            e["link_kind"] = "inferred (same conversation)"
            prev_e.setdefault("replied_by", []).append(
                {"key": e["thread_key"], "label": e["thread_label"]})
            linked += 1
    return linked


# ── page map ────────────────────────────────────────────────────────────────

def build_page_map(entries, n_pages):
    """Map each entry to the PDF pages its text came from.

    Kept alongside the other releases' maps ({"start","end","breaks"}), keyed
    by a source-qualified entry key so the app can merge all sources without
    their keys colliding.
    """
    pmap = {}
    for i, e in enumerate(entries):
        pages = [p for p in e.get("pages") or [] if 1 <= p <= n_pages]
        if not pages:
            continue
        pmap[entry_key(e, i)] = {"start": pages[0], "end": pages[-1], "breaks": []}
    return pmap


def entry_key(e, i):
    # The same key the entry carries, so the app can look a page up from an
    # entry without knowing which release it came from.
    return e.get("thread_key") or "%s|%s" % (SOURCE_ID, e.get("idx", i))


def main():
    pages = load_pages()
    messages = segment(pages)
    entries = merge_page_splits(build_entries(messages))
    # thread keys, then chronological order: the release is not in time order
    seen_keys = {}
    for e in entries:
        e["source"] = SOURCE_ID
        base = "%s|%s|%s" % (SOURCE_ID, e.get("date") or "undated",
                             e.get("time") or e["raw_date"][:40])
        n = seen_keys.get(base, 0)
        seen_keys[base] = n + 1
        e["thread_key"] = base if n == 0 else "%s|%d" % (base, n)
        if n:
            # two genuinely distinct messages share a minute; say so rather
            # than letting one silently overwrite the other
            e["date_note"] = (e.get("date_note", "") +
                              ("same minute as another message" if n == 1 else "")).strip()
        e["thread_label"] = "%s %s · %s" % (e.get("date") or "undated",
                                            (e.get("time") or "")[:2] + ":" +
                                            (e.get("time") or "")[2:4] if e.get("time") else "",
                                            e.get("sender") or "")
        e["replied_by"] = []
    entries.sort(key=lambda e: (e.get("date") or "9999", e.get("time") or "9999"))
    for i, e in enumerate(entries):
        e["idx"] = i
        e.pop("pages", None)
    linked = thread_entries(entries)

    n_pages = len(open(OCR_TXT, encoding="utf-8").read().split("\x0c"))
    page_map = build_page_map(
        [dict(e, pages=m["pages"]) for e, m in zip(entries, messages)], n_pages)

    dated = [e for e in entries if e.get("date")]
    undated = [e for e in entries if not e.get("date")]
    senders = defaultdict(int)
    for e in dated:
        senders[e["sender"]] += 1

    out = OrderedDict([
        ("source_file", "po-emails.pdf"),
        ("source_id", SOURCE_ID),
        ("title", "P.O. emails (FOI release)"),
        ("total_entries", len(entries)),
        ("date_range", {"start": min(e["date"] for e in dated) if dated else None,
                        "end": max(e["date"] for e in dated) if dated else None}),
        ("entries", entries),
    ])
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(OUT_MAP, "w", encoding="utf-8") as f:
        json.dump(page_map, f, indent=1)

    print("Messages segmented: %d" % len(messages))
    print("Thread links (same conversation): %d" % linked)
    print("Entries: %d (%d dated, %d undated)"
          % (len(entries), len(dated), len(undated)))
    if dated:
        print("Range: %s .. %s" % (out["date_range"]["start"], out["date_range"]["end"]))
    print("Senders:")
    for s, c in sorted(senders.items(), key=lambda kv: -kv[1]):
        print("  %4d  %s" % (c, s))
    st = defaultdict(int)
    for e in dated:
        st[e["stamp_status"]] += 1
    print("Stamp parsing: %s" % dict(st))
    print("Page map: %d keys over %d PDF pages" % (len(page_map), n_pages))
    print("Wrote %s and %s" % (OUT_JSON, OUT_MAP))


if __name__ == "__main__":
    main()
