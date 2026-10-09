#!/usr/bin/env python3
"""
Parse the Farrar-Fauci-Collins email correspondence (farrar-fauci-comms.pdf,
cited in the P.O. "Tragicomedy" piece as farrar-fauci-comms-full.pdf /
farrar-fauci-comms.pdf) into one entry per email message.

The release is a FOIA'd stack of plain Outlook messages (not screenshots, as
po-emails.pdf was), re-OCR'd by reocr_farrar_fauci.py because the PDF's own
text layer glues words together and misreads glyphs. What that OCR gives us
is the same kind of header-plus-body stream as po-emails, with three added
wrinkles: explicit "+0000"-style UTC offsets on most top-level stamps (so the
zone table matters far less here), a handful of German-language Outlook
headers (Von/Gesendet/An/Betreff), and inline "On <date>, <name> wrote:"
quote markers that recover a quoted reply as its own entry rather than
leaving it glued into the message that quotes it.

The rules this follows are the ones written down in SPEC.md (shared with
po-emails.pdf):

  * one entry per message -- an author at an instant -- never a whole thread
  * an entry holds only what its author wrote; quoted history is its own entry
  * an explicit UTC offset in the stamp always wins
  * otherwise the sender's own institution decides the zone, and the
    assumption is recorded, never silent
  * everything is normalised to ET for ordering, with the local stamp kept

Output: farrar-fauci.json (entries) + farrar-fauci_page_map.json (PDF pages).
"""

import json
import os
import re
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OCR_TXT = os.path.join(HERE, "farrar-fauci-comms_ocr.txt")
OUT_JSON = os.path.join(HERE, "farrar-fauci.json")
OUT_MAP = os.path.join(HERE, "farrar-fauci_page_map.json")
SOURCE_ID = "farrar-fauci"

ET = ZoneInfo("America/New_York")

# ── time zones ──────────────────────────────────────────────────────────────
# Most top-level stamps in this release carry an explicit UTC offset ("Sent:
# Fri, 24 Jul 2020 10:37:46 +0000"), which always wins over this table (see
# parse_stamp/zone_for). The table is only reached for a stamp with none --
# mainly the nested "Date:"/inline "On ... wrote:" quotes -- using each
# correspondent's own institution, as stated in their signature or address:
#
#   Wellcome Trust / UK Government  -> London      (Farrar, Vallance, Viner)
#   NIH / NIAID / NICHD / NHLBI, Bethesda -> New York (Fauci, Collins, Bianchi, Gibbons)
#   Scripps Research                -> Los Angeles (Andersen, Farzan)
#   Tulane                          -> Chicago     (Garry)
#   University of Sydney            -> Sydney      (Holmes)
#   Pasteur Institute               -> Paris       (Fouchier)
#   China CDC                       -> Beijing     (Gao)
ZONE_BY_AFFILIATION = [
    (re.compile(r"wellcome|vallance|golding|ferguson|viner|rambaut|uk government|"
                r"dphe|harris|esveld", re.I), "Europe/London", "Wellcome Trust / UK"),
    (re.compile(r"nih|niaid|nichd|nhlbi|\bod\b|fauci|collins|bianchi|gibbons|"
                r"shabman|tabak|burke|marston|auchincloss", re.I),
     "America/New_York", "NIH, Bethesda"),
    (re.compile(r"scripps|andersen|farzan", re.I), "America/Los_Angeles", "Scripps Research"),
    (re.compile(r"tulane|garry", re.I), "America/Chicago", "Tulane University"),
    (re.compile(r"sydney|holmes", re.I), "Australia/Sydney", "University of Sydney"),
    (re.compile(r"pasteur|fouchier|paris|institut", re.I), "Europe/Paris", "Institut Pasteur"),
    (re.compile(r"china cdc|\bgao\b|beijing", re.I), "Asia/Shanghai", "China CDC"),
    (re.compile(r"drosten|charit|berlin", re.I), "Europe/Berlin", "Charite, Berlin"),
]
DEFAULT_ZONE = "Europe/London"      # the Wellcome Trust ran this exercise
DEFAULT_ZONE_WHY = "Wellcome Trust (the release's convener)"

ZONE_OVERRIDES = {}

# ── OCR clean-up ────────────────────────────────────────────────────────────
# The scans leave black-box redactions as glyph soup on header lines
# ("Fauci, Anthony (NIH/NIAID) [E] OO", "Dzau, Victor J yoo"); the tail after
# the real name/affiliation is stripped the same way po-emails strips avatar
# glyphs.
NOISE_TAIL = re.compile(r"\s*[|Il\[\]{}<>«»“”„’‘—–\-–—_=+*#§¶©®™✓✔✗✘»«»…@]+"
                        r"\s*(?:[a-zA-Z]{1,6})?\s*$")
HEADER_JUNK = re.compile(r"^[^A-Za-z0-9]+|[^A-Za-z0-9)\]]+$")
RE_AVATAR_BRACKET = re.compile(r"[\[(][^)\]]{0,2}[)\]]")
RE_AVATAR_GLYPH = re.compile(r"[€¢§¶©®™]")

FURNITURE = re.compile(
    r"^(REV\d+|CONFIDENTIAL|NIAID|EXCERPT FROM|"
    r"National Institute of Allergy|National Institutes of Health|Bethesda, MD|"
    r"Phone:|FAX:|E-mail:|Director, National|The information in this e-mail|"
    r"it is not intended that|you should delete|received this e-mail in error|"
    r"or any other storage devices|liable for any statements|"
    r"on behalf of the|Building \d+|Room \d+|Contor Drive|NSC \d+|"
    r"National Institutes of Health$|"
    r"Wellcome exists to improve health|health challenges, we campaign|"
    r"health research\. We are a politically|"
    r"The Wellcome Trust is a charity registered|"
    r"Limited, a company registered|London NW1)", re.I)

# ── header grammar ──────────────────────────────────────────────────────────
HEADER_FIELDS = ("From", "To", "Cc", "Bcc", "Subject", "Sent", "Date", "Importance")
RE_FROM = re.compile(r"^From:\s*(.+)$", re.I)
# "Von:" opens a message the same way "From:" does (German Outlook export);
# a handful of messages in this release were forwarded/printed in German.
RE_MSG_OPEN = re.compile(r"^(?:From|rom|Von):\s*(.+)$", re.I)
RE_HDR_DATE = re.compile(r"^(?:Sent|Date|Gesendet)\s*:\s*(.+)$", re.I)
FIELD_ALIASES = {
    "ce": "Cc", "cc": "Cc", "bce": "Bcc", "bcc": "Bcc", "gc": "Cc",
    "fe": "To", "pe": "To", "to": "To", "fo": "From",
    "rom": "From",
    "subiect": "Subject", "subjec": "Subject", "subject": "Subject",
    "senf": "Sent", "sent": "Sent", "dafe": "Date", "date": "Date",
    # German Outlook export (Von/Gesendet/An/Betreff), seen on a handful of
    # pages where the message was relayed through a German mail client.
    "von": "From", "gesendet": "Sent", "an": "To", "betreff": "Subject",
}
FIELD_ALIAS_RE = re.compile(
    r"\b(%s)\s*:" % "|".join(sorted(set(HEADER_FIELDS) | set(FIELD_ALIASES),
                                       key=len, reverse=True)), re.I)
RE_FIELD = FIELD_ALIAS_RE
MAX_HEADER_LINES = 12

# "On 8 Feb 2020, at 22:15, Kristian G. Andersen) @)@> wrote:" and its
# variants ("On Sat, Feb 8, 2020 at 12:38 PM Drosten, Christian) 7 wrote:",
# "On May 12, 2020, at 12:57 PM, Jeremy Farrar FOO wrote:"). This is a real
# message boundary per SPEC.md 2.3: the quoted reply becomes its own entry,
# recovered from the marker rather than left glued into the message quoting
# it.
RE_INLINE_QUOTE = re.compile(
    r"^On\s+(?:[A-Za-z]{3,9},?\s+)?"
    r"((?:[A-Za-z]{3,9}\.?\s+\d{1,2}|\d{1,2}\s+[A-Za-z]{3,9}\.?)\s*,?\s*\d{4})"
    r",?\s*(?:at\s+)?(\d{1,2}:\d{2}(?:\s*[AaPp]\.?[Mm]\.?)?)\s*,?\s+"
    r"(.+?)\s*wrote:\s*$", re.I)


# ── sender names ────────────────────────────────────────────────────────────
# The scans carry redaction/glyph debris on the sender line ("Fauci, Anthony
# (NIH/NIAID) [E] OO", "Jeremy Farrar FOO"). A name that matches a known
# correspondent is normalised to that name; the raw string is kept alongside
# so nothing is silently rewritten.
SENDER_ROSTER = [
    (re.compile(r"farrar|forar|fara|farrat", re.I), "Jeremy Farrar"),
    (re.compile(r"fauci", re.I), "Anthony Fauci"),
    (re.compile(r"collins", re.I), "Francis Collins"),
    (re.compile(r"andersen", re.I), "Kristian G. Andersen"),
    (re.compile(r"holmes", re.I), "Edward Holmes"),
    (re.compile(r"rambaut", re.I), "Andrew Rambaut"),
    (re.compile(r"garry|gary,? robert", re.I), "Robert Garry"),
    (re.compile(r"fouchier", re.I), "R.A.M. Fouchier"),
    (re.compile(r"drosten", re.I), "Christian Drosten"),
    (re.compile(r"koopmans", re.I), "Marion Koopmans"),
    (re.compile(r"pohlmann", re.I), "Stefan Pohlmann"),
    (re.compile(r"farzan", re.I), "Michael Farzan"),
    (re.compile(r"auchincloss", re.I), "Ashley Auchincloss"),
    (re.compile(r"vallance", re.I), "Patrick Vallance"),
    (re.compile(r"schreier", re.I), "Martin Schreier"),
    (re.compile(r"ferguson", re.I), "Mike Ferguson"),
    (re.compile(r"golding", re.I), "Josie Golding"),
    (re.compile(r"pope", re.I), "Andrew Pope"),
    (re.compile(r"conrad", re.I), "Patricia Conrad"),
    (re.compile(r"shabman", re.I), "Reed Shabman"),
    (re.compile(r"folkers", re.I), "Greg Folkers"),
    (re.compile(r"burke", re.I), "Martina Burke"),
    (re.compile(r"\bbaric\b", re.I), "Ralph Baric"),
    (re.compile(r"\bdaszak\b", re.I), "Peter Daszak"),
    (re.compile(r"bedford", re.I), "Trevor Bedford"),
    # Correspondents specific to this release, mainly the GPMB / COVID
    # governance thread (Farrar, Fauci and Collins corresponding with heads
    # of global-health bodies). Listing them lets the roster attribute the
    # common top-level senders instead of falling back to raw OCR text.
    (re.compile(r"viner", re.I), "Russell Viner"),
    (re.compile(r"smith,?\s*lan michael|smith,?\s*ian michael", re.I), "Ian Michael Smith"),
    (re.compile(r"dzau", re.I), "Victor Dzau"),
    (re.compile(r"\bmun,?\s*jenny\b|jenny mun", re.I), "Jenny Mun"),
    (re.compile(r"alex harris", re.I), "Alex Harris"),
    (re.compile(r"esveld", re.I), "Marja Esveld"),
    (re.compile(r"barasch", re.I), "Kimberly Barasch"),
    (re.compile(r"miller de vega", re.I), "Teresa Miller de Vega"),
    (re.compile(r"bianchi", re.I), "Diana Bianchi"),
    (re.compile(r"gibbons", re.I), "Gary Gibbons"),
    (re.compile(r"kickbusch", re.I), "Ilona Kickbusch"),
    (re.compile(r"brundtland", re.I), "Gro Brundtland"),
    (re.compile(r"henrietta fore|fore,? henrietta", re.I), "Henrietta Fore"),
    (re.compile(r"skvortsova", re.I), "Veronika Skvortsova"),
    (re.compile(r"vijayraghavan", re.I), "Krishnaswamy VijayRaghavan"),
    (re.compile(r"\bkaag\b", re.I), "Sigrid Kaag"),
    (re.compile(r"gashumba", re.I), "Diane Gashumba"),
    (re.compile(r"marston", re.I), "Hilary Marston"),
    (re.compile(r"schwartlander", re.I), "Bernhard Schwartlander"),
    (re.compile(r"\bryan,?\s*michael|michael j\.? ryan\b", re.I), "Michael Ryan"),
    (re.compile(r"kanarek", re.I), "Morgan Kanarek"),
    (re.compile(r"gao fu|george gao", re.I), "George Gao (Gao Fu)"),
    (re.compile(r"chris\.?\s*elias|elias,?\s*chris", re.I), "Chris Elias"),
    (re.compile(r"\bgro\b", re.I), "Gro Brundtland"),
]

FIRST_NAMES = {
    "ralph", "peter", "andrew", "robert", "edward", "jeremy", "kristian",
    "christian", "marion", "stefan", "michael", "claire", "patricia", "reed",
    "greg", "martina", "francis", "martin", "rory", "josie", "amanda", "tony",
    "eddie", "trevor", "bedford", "aravinda", "david", "john", "richard",
    "russell", "victor", "jenny", "alex", "marja", "kimberly", "teresa",
    "diana", "gary", "ilona", "gro", "henrietta", "veronika", "sigrid",
    "diane", "hilary", "bernhard", "morgan", "chris", "anthony",
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
# German month names/abbreviations, for the handful of Von/Gesendet headers.
MONTHS_DE = {
    "jan": 1, "januar": 1, "feb": 2, "februar": 2, "mär": 3, "maer": 3,
    "marz": 3, "märz": 3, "mrz": 3, "apr": 4, "april": 4, "mai": 5,
    "jun": 6, "juni": 6, "jul": 7, "juli": 7, "aug": 8, "august": 8,
    "sep": 9, "september": 9, "okt": 10, "oktober": 10, "nov": 11,
    "november": 11, "dez": 12, "dezember": 12,
}

RE_STAMP_US = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(?:at\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)")
RE_STAMP_LONG = re.compile(
    r"(?:[A-Za-z]+,?\s+)?([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\s+"
    r"(?:at\s+)?(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)")
# "24 Jul 2020 10:37:46" (day-month-year, 24h clock, this release's default
# top-level stamp shape; the explicit "+0000" offset that usually follows is
# pulled separately by RE_STAMP_BARE_OFFSET) and "05 March 2020 02:06" (no
# am/pm at all, UK-forwarded).
RE_STAMP_DMY = re.compile(
    r"(\d{1,2})\s+([A-Za-z]{3,9})\.?\s*,?\s*(\d{4})\s*,?\s*(?:at\s+)?(\d{1,2}):(\d{2})"
    r"(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)?")
# "4. Mai 2020 13:38" (German day-month-year with a period after the day).
RE_STAMP_DE = re.compile(
    r"(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]{3,10})\s+(\d{4})\s+(\d{1,2}):(\d{2})")
# "(UTC-05:00)" / "(GMT+1)" -- an explicit offset given in parens.
RE_STAMP_OFFSET = re.compile(r"\((?:UTC|GMT)?\s*([+-])\s*(\d{1,2}):?(\d{2})\)", re.I)
# "... 10:37:46 +0000" -- the bare RFC-2822 offset this release's top-level
# stamps carry, with no parens. Anchored at the end of the stamp string so it
# is never mistaken for a page/phone number elsewhere in the line.
RE_STAMP_BARE_OFFSET = re.compile(r"([+-])(\d{2})(\d{2})\s*$")
RE_STAMP_PARTIAL = re.compile(
    r"(?:[A-Za-z]+,?\s+)?([A-Za-z]{3,9})\.?\s+(\d{1,2})\s*(?:,|:|$)")


def _ampm(h, ap):
    h = int(h)
    ap = (ap or "").lower().replace(".", "")
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
    else:
        bm = RE_STAMP_BARE_OFFSET.search(t)
        if bm:
            sign = 1 if bm.group(1) == "+" else -1
            off = timedelta(hours=sign * int(bm.group(2)), minutes=sign * int(bm.group(3)))
    m = RE_STAMP_US.search(t)
    if m:
        mo, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12:
            dt = datetime(yr, mo, day, _ampm(m.group(4), m.group(7)), int(m.group(5)))
            return dt, off, ("offset" if off is not None else "outlook-us")
    m = RE_STAMP_DMY.search(t)
    if m:
        mo = MONTHS.get(m.group(2)[:3].lower())
        if mo:
            ap = m.group(7) or "12:00am"
            dt = datetime(int(m.group(3)), mo, int(m.group(1)),
                          _ampm(m.group(4), ap), int(m.group(5)))
            return dt, off, ("offset" if off is not None else "day-month-year")
    m = RE_STAMP_LONG.search(t)
    if m:
        mo = MONTHS.get(m.group(1)[:3].lower())
        if mo:
            dt = datetime(int(m.group(3)), mo, int(m.group(2)),
                          _ampm(m.group(4), m.group(7)), int(m.group(5)))
            return dt, off, ("offset" if off is not None else "long")
    m = RE_STAMP_DE.search(t)
    if m:
        mo = MONTHS_DE.get(m.group(2).lower())
        if mo:
            dt = datetime(int(m.group(3)), mo, int(m.group(1)),
                          int(m.group(4)), int(m.group(5)))
            return dt, off, ("offset" if off is not None else "german")
    m = RE_STAMP_PARTIAL.search(t)
    if m:
        mo = MONTHS.get(m.group(1)[:3].lower())
        if mo:
            return datetime(2020, mo, int(m.group(2)), 12, 0), off, "partial-no-time"
    return None, None, "unparsed"


def zone_for(sender, subject, dt):
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
    """Split a run of lines into header fields (see parse_po_emails.py)."""
    fields, order = OrderedDict(), []
    current = None
    for line in block:
        parts = RE_FIELD.split(" " + line)
        if len(parts) == 1:
            if current in ("From", "To", "Cc", "Bcc"):
                fields[current] += " " + line.strip()
            continue
        if parts[0].strip():
            if current in ("From", "To", "Cc", "Bcc"):
                fields[current] += " " + parts[0].strip()
        for i in range(1, len(parts) - 1, 2):
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


def is_junk_line(line):
    s = (line or "").strip()
    if not s:
        return True
    return not (re.search(r"[A-Za-z]{3,}", s)
                or re.search(r"https?://|www\.|@", s)
                or re.search(r"\b\d{4,}\b", s))


def strip_glyph_soup(lines):
    return [ln for ln in lines if not is_junk_line(ln)]


def clean_field_value(name, value, sender):
    v = (value or "").strip()
    if name == "From":
        return sender
    v = RE_AVATAR_BRACKET.sub("", v)
    v = RE_AVATAR_GLYPH.sub("", v)
    v = re.sub(r"([)\]])\s+[A-Za-z]{1,3}\s*$", r"\1", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v


# ── signature blocks ─────────────────────────────────────────────────────────
RE_SIG_NAME = re.compile(
    r"^(?:PROFESSOR|Professor|DR|Dr|MR|Mr|MS|Ms|SIR|Sir|DAME|Dame)\b"
    r"|^(?:[A-Z][A-Z.'-]+\s+){1,4}[A-Z][A-Z.'-]*"
    r"\s+(?:FAA|FRS|FBA|FRCS|FACP|PhD|Ph\.D|MD|M\.D|MP|MSc|BSc|MBBS)\b")
RE_SIG_AFFIL = re.compile(
    r"^(?:ARC |THE |UNIVERSITY|University|Institut|CENTRE|Centre|School|"
    r"Department|Dept\.|Faculty|College|Hospital|Institute|Trust|Laborator|"
    r"Director|Regents|Dean|Regent|Professor Emeritus|Charit|Campus|"
    r"Marie Bashir|Wellcome|MRC|NIH|NIAID|Atlanta|Bethesda|London|Sydney|"
    r"Berlin|D-\d{5})\b")


def is_signature_line(s):
    s = (s or "").strip()
    if not s:
        return False
    return bool(RE_SIG_NAME.match(s) or RE_SIG_AFFIL.match(s))


RE_SENTENCE_END = re.compile(r"[.!?:;…]['\")\]]?\s*$")
RE_SOFT_START = re.compile(r"^\s*[,;:.)\]]")
RE_ADDR_CONT = re.compile(r"[,;|/\\]|(?:^|[\s(])[\"']?[A-Za-z]{1,3}[\"']?(?:[\s,|]|$)")


def is_address_continuation(line):
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s):
        return False
    if len(s) > 160:
        return False
    return bool(RE_ADDR_CONT.search(s))


def is_name_debris(line):
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 200:
        return False
    return not re.search(r"[a-z]{5,}", s)


def is_wrapped_recipient(line, nxt=None):
    if is_name_debris(line):
        return True
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 120:
        return False
    names = re.findall(r"[A-Z][a-zA-Z.'-]{2,}", s)
    words = re.findall(r"[A-Za-z']{2,}", s)
    if not names:
        return False
    comma_list = s.count(",") >= 2 and len(names) >= 2
    bare_names = s.count(",") == 0 and len(names) >= 3
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


def continues_recipient_run(line, nxt=None):
    s = (line or "").strip()
    if not s or RE_SENTENCE_END.search(s) or len(s) > 200:
        return False
    words = re.findall(r"[a-z]{3,}", s)
    names = re.findall(r"[A-Z][a-zA-Z.'-]{2,}", s)
    if len(words) > 4 and len(names) * 2 < len(words):
        return False
    if s.count(",") >= 2 and len(names) >= 2:
        return True
    if re.search(r"[.!?]\s+[A-Z][a-z]{2,}", s):
        return False
    return True


def unwrap_lines(lines):
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if out and out[-1].strip() and not RE_SENTENCE_END.search(out[-1]):
            prev = out[-1].rstrip()
            cont = (prev.endswith("-")
                    or RE_SOFT_START.match(s)
                    or (s[:1].islower() and prev[-1:].isalpha()))
            if cont and not re.match(r"^(?:[-*•>]|\d+[.)])\s", s):
                out[-1] = (prev[:-1] if prev.endswith("-") else prev) + " " + s
                continue
        out.append(line)
    return out


def is_header_fragment(line):
    s = (line or "").strip()
    if not s or len(s) > 40 or RE_SENTENCE_END.search(s):
        return False
    if not re.match(r"^[A-Z][A-Za-z'.-]*(?:[ /][A-Za-z][A-Za-z'.-]*){0,3}$", s):
        return False
    return bool(re.search(r"(?:andersen|rambaut|farrar|holmes|garry|fauci|drosten|"
                           r"koopmans|pohlmann|farzan|fouchier|schreier|"
                           r"ferguson|golding|lipkin|vallance|collins|auchincloss|"
                           r"conrad|shabman|folkers|burke|pope|viner|dzau|smith|"
                           r"edward|andrew|jeremy|kristian|robert|anthony|christian|"
                           r"marion|stefan|michael|claire|patricia|reed|martina|"
                           r"greg|josie|amanda|francis|martin|rory|russell|victor|"
                           r"eddie|tony|toney|farrar|beach|comin|perdue)", s, re.I))


def split_signature(body):
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
    out, cut = [], None
    for i, line in enumerate(body):
        if cut is None and re.match(
                r"^(Best regards|Best wishes|Warm regards|Thanks,|Kind regards|"
                r"With best wishes|Yours sincerely|Yours,|Best,|Many thanks|"
                r"Jeremy Farrar$|Anthony S\. Fauci|Tony$|Eddie$|Anders$|Christian$|"
                r"Kristian$|Andrew Rambaut$|Robert Garry$)", line.strip(), re.I):
            cut = i
        if cut is None:
            out.append(line)
    return out


def segment(pages):
    """Split the page stream into messages.

    Three kinds of boundary open a new message: a From:/Von: header, a
    Date:/Sent:/Gesendet: line reopening a message whose From: the scan ate
    (see po-emails' parser for why), and an inline "On <date>, <name> wrote:"
    marker, which recovers the quoted reply it introduces as its own entry
    instead of leaving it glued into the message quoting it.
    """
    messages = []
    cur = None
    cur_from_at = -1
    pos = 0
    in_body = False
    for pageno, lines in pages:
        body_mode = in_body
        for li, line in enumerate(lines):
            nxt = lines[li + 1] if li + 1 < len(lines) else None
            if RE_MSG_OPEN.match(line):
                cur = {"header_lines": [line], "body": [], "pages": [pageno]}
                messages.append(cur)
                cur_from_at = pos
                body_mode = False
                in_body = False
                pos += 1
                continue
            if RE_HDR_DATE.match(line) and cur is not None and body_mode \
                    and pos - cur_from_at > MAX_HEADER_LINES + 4:
                cur = {"header_lines": [line], "body": [], "pages": [pageno]}
                messages.append(cur)
                cur_from_at = pos
                body_mode = False
                in_body = False
                pos += 1
                continue
            iq = cur is not None and RE_INLINE_QUOTE.match(line)
            if iq:
                date_str, time_str, name = iq.groups()
                cur = {"header_lines": ["From: %s" % name.strip(),
                                         "Sent: %s, %s" % (date_str.strip(), time_str.strip())],
                       "body": [], "pages": [pageno], "recovered_inline": True}
                messages.append(cur)
                cur_from_at = pos
                body_mode = False
                in_body = False
                pos += 1
                continue
            pos += 1
            if cur is None:
                continue
            cur["pages"].append(pageno)
            if not body_mode:
                if len(cur["header_lines"]) > 1 and is_junk_line(line):
                    continue
                has_field = bool(RE_FIELD.search(line))
                if cur["header_lines"] and not has_field and len(cur["header_lines"]) > 1:
                    if (cur.get("in_addr") and len(cur["header_lines"]) <= MAX_HEADER_LINES
                            and (is_address_continuation(line)
                                 or is_wrapped_recipient(line, nxt))):
                        cur["header_lines"].append(line)
                        continue
                    body_mode = True
                    in_body = True
                    cur["body"].append(line)
                elif has_field or len(cur["header_lines"]) == 1:
                    cur["header_lines"].append(line)
                    names = [n.strip().lower() for n in RE_FIELD.findall(line)]
                    if names:
                        cur["in_addr"] = names[-1] in (
                            "to", "cc", "bcc", "fe", "pe", "ce", "an")
                else:
                    body_mode = True
                    in_body = True
                    cur["body"].append(line)
            else:
                cur["body"].append(line)
                in_body = True
        in_body = body_mode
    return messages


def build_entries(messages):
    entries = []
    for msg in messages:
        fields = split_fields(msg["header_lines"])
        sender, sender_raw = clean_sender(fields.get("From") or "")
        sender_how = "inline quote marker (On ... wrote:)" if msg.get("recovered_inline") \
            else ("From: line" if fields.get("From") else "")
        stamp = fields.get("Sent") or fields.get("Date") or ""
        body = strip_quoted(msg["body"])
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
        window = min(len(body), 8)
        found = -1
        for i in range(window):
            if RE_FIELD.match(body[i].strip()):
                found = i
                break
        if found >= 0:
            j = found + 1
            while j < min(len(body), 60):
                if RE_FIELD.match(body[j].strip()):
                    names = [n.strip().lower() for n in RE_FIELD.findall(body[j])]
                    if any(n in ("to", "cc", "bcc", "ce", "fe", "pe", "gc", "an")
                           for n in names):
                        found = j
                        j += 1
                        continue
                    found = j
                    break
                if not continues_recipient_run(body[j]):
                    break
                j += 1
            else:
                found = j - 1
        if found < 0:
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
                j = found + 1
                while j < min(len(body), 60):
                    if RE_FIELD.match(body[j].strip()):
                        names = [n.strip().lower() for n in RE_FIELD.findall(body[j])]
                        if not any(n in ("to", "cc", "bcc", "ce", "fe", "pe", "gc", "an")
                                   for n in names):
                            break
                        found = j
                        j += 1
                        continue
                    if not continues_recipient_run(body[j]):
                        break
                    j += 1
        if found < 0 and not fields.get("Subject") and body:
            m = re.match(r"^\s*(?:Subjec\w*|Betreff):?\s*(.+)$", body[0], re.I)
            if m and len(m.group(1).strip()) > 3:
                fields["Subject"] = m.group(1).strip()
                body = body[1:]
                found = 0
        if found >= 0:
            for j in range(found + 1):
                extra = split_fields(body[j:j + 1])
                for k, v in extra.items():
                    if v and not fields.get(k):
                        fields[k] = v
            body = body[found + 1:]
        subject = (fields.get("Subject") or "").strip()
        body = strip_glyph_soup(body)
        body, signature = split_signature(body)
        if not fields.get("From"):
            for sline in signature:
                hit = next((name for rx, name in SENDER_ROSTER
                            if rx.search(sline.strip())), None)
                if hit:
                    sender, sender_raw = hit, sline.strip()
                    sender_how = "signature block (From: lost in scan)"
                    break
        body = unwrap_lines(body)
        content_body = "\n".join(body).strip()

        dt, off, how = parse_stamp(stamp)
        if dt is None:
            entries.append({
                "date": None, "time": None, "kind": "email",
                "raw_date": subject or "(undated message)",
                "sender": sender, "sender_raw": sender_raw, "sender_how": sender_how,
                "subject": subject,
                "content": header_block(fields, content_body, sender, signature),
                "date_note": "no usable timestamp in the release; not plotted",
                "pages": sorted(set(msg["pages"])), "source": SOURCE_ID,
                "stamp_status": how,
            })
            continue

        if off is not None:
            local = dt - off
            et = local.astimezone(ET) if local.tzinfo else local.replace(tzinfo=ZoneInfo("UTC")).astimezone(ET)
            zone_why = "explicit UTC%s%02d:%02d in the stamp" % (
                "+" if off.total_seconds() >= 0 else "-",
                abs(off.total_seconds()) // 3600,
                (abs(off.total_seconds()) % 3600) // 60)
            stamp_line = "%s %s -> %s ET" % (
                stamp.strip(), ("UTC%s%02d:%02d" % (
                    "+" if off.total_seconds() >= 0 else "-",
                    int(abs(off.total_seconds()) // 3600),
                    int(abs(off.total_seconds()) % 3600 // 60))), et.strftime("%H:%M"))
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
            "sender_how": sender_how,
            "subject": subject,
            "content": header_block(fields, content_body, sender, signature),
            "signature": "\n".join(signature).strip() if signature else None,
            "stamp": stamp.strip(),
            "stamp_status": how,
            "zone_assumed": zone_why,
            "stamp_line": stamp_line,
            "recovered_inline": bool(msg.get("recovered_inline")),
            "pages": sorted(set(msg["pages"])),
            "source": SOURCE_ID,
        })
    return entries


def header_block(fields, body, sender, signature=None):
    head = []
    for k in ("From", "To", "Cc", "Bcc", "Subject", "Sent", "Date", "Importance"):
        if fields.get(k):
            head.append("%s: %s" % (k, clean_field_value(k, fields[k], sender)))
    out = "\n\n".join(head) + "\n\n----------\n\n" + body
    if signature:
        out += "\n\n----------\n\n" + "\n".join(signature).strip()
    return out


def merge_page_splits(entries):
    """Join messages the printer split across a page boundary (see
    po-emails.py for the full rationale: same sender/stamp/subject, two
    bodies, not adjacent in the stream)."""
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
            addition = (body if sep else extra["content"]).strip()
            if addition and addition not in head["content"]:
                head["content"] = head["content"].rstrip() + "\n" + addition
            head["pages"] = sorted(set(head.get("pages", []) + extra.get("pages", [])))
            head["merged_pages"] = head.get("merged_pages", 0) + 1
        out.append(head)
    return out


# ── threading ───────────────────────────────────────────────────────────────
RE_SUBJ_PREFIX = re.compile(r"^\s*(re|fw|fwd?|fwd)\s*[:\-]\s*", re.I)


def norm_subject(subject):
    prev = None
    s = (subject or "").strip()
    while prev != s:
        prev = s
        s = RE_SUBJ_PREFIX.sub("", s).strip()
    return s.lower()


def thread_entries(entries):
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


def build_page_map(entries, n_pages):
    pmap = {}
    for i, e in enumerate(entries):
        pages = [p for p in e.get("pages") or [] if 1 <= p <= n_pages]
        if not pages:
            continue
        pmap[entry_key(e, i)] = {"start": pages[0], "end": pages[-1], "breaks": []}
    return pmap


def entry_key(e, i):
    return e.get("thread_key") or "%s|%s" % (SOURCE_ID, e.get("idx", i))


def main():
    pages = load_pages()
    messages = segment(pages)
    entries = merge_page_splits(build_entries(messages))
    seen_keys = {}
    for e in entries:
        e["source"] = SOURCE_ID
        base = "%s|%s|%s" % (SOURCE_ID, e.get("date") or "undated",
                             e.get("time") or e["raw_date"][:40])
        n = seen_keys.get(base, 0)
        seen_keys[base] = n + 1
        e["thread_key"] = base if n == 0 else "%s|%d" % (base, n)
        if n:
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
    linked = thread_entries(entries)

    n_pages = len(open(OCR_TXT, encoding="utf-8").read().split("\x0c"))
    page_map = build_page_map(entries, n_pages)
    for e in entries:
        e.pop("pages", None)

    dated = [e for e in entries if e.get("date")]
    undated = [e for e in entries if not e.get("date")]
    senders = defaultdict(int)
    for e in dated:
        senders[e["sender"]] += 1

    out = OrderedDict([
        ("source_file", "farrar-fauci-comms.pdf"),
        ("source_id", SOURCE_ID),
        ("title", "Farrar-Fauci-Collins emails (FOI release)"),
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
