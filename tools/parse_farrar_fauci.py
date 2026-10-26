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

The segmentation/zone/signature/stamp grammar itself lives in the shared
`foia_parser` package (Work/Edition/foia_parser) -- the engine this release
shares with po-emails (see parse_po_emails.py) and, going forward, any other
FOIA'd email release. This file supplies only what is specific to THIS
release. The rules followed are the ones written down in that package's
SKILL.md (shared with po-emails.pdf):

  * one entry per message -- an author at an instant -- never a whole thread
  * an entry holds only what its author wrote; quoted history is its own entry
  * an explicit UTC offset in the stamp always wins
  * otherwise the sender's own institution decides the zone, and the
    assumption is recorded, never silent
  * everything is normalised to ET for ordering, with the local stamp kept

Output: farrar-fauci.json (entries) + farrar-fauci_page_map.json (PDF pages).
"""

import os
import re

from foia_parser import Profile, run_release

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
ANALYSIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis")

# ── time zones ──────────────────────────────────────────────────────────────
# Most top-level stamps in this release carry an explicit UTC offset ("Sent:
# Fri, 24 Jul 2020 10:37:46 +0000"), which always wins over this table. The
# table is only reached for a stamp with none -- mainly the nested "Date:"/
# inline "On ... wrote:" quotes -- using each correspondent's own institution,
# as stated in their signature or address:
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

# ── OCR clean-up ────────────────────────────────────────────────────────────
# The scans leave black-box redactions as glyph soup on header lines
# ("Fauci, Anthony (NIH/NIAID) [E] OO", "Dzau, Victor J yoo"); the tail after
# the real name/affiliation is stripped the same way po-emails strips avatar
# glyphs.
NOISE_TAIL = re.compile(r"\s*[|Il\[\]{}<>«»“”„’‘—–\-–—_=+*#§¶©®™✓✔✗✘»«»…@]+"
                        r"\s*(?:[a-zA-Z]{1,6})?\s*$")
# A standalone "|" bounded by whitespace/punctuation is almost always a
# garbled capital "I" ("| will:" -> "I will:", "| believe" -> "I believe").
# ~380 occurrences in this release.
STANDALONE_PIPE_RE = re.compile(r"(?<![^\s])\|(?![^\s.,!?;:'\")\]])")
# Tesseract reads a round bullet glyph as the nearest Latin letter/symbol --
# "e" or "©" here -- so a line that opens on a bare one of those followed by
# a capitalised word is a bullet point, not a word starting a sentence
# (English prose essentially never opens a line on a lone lower-case "e").
# ~78 occurrences.
RE_BULLET_MISREAD = re.compile(r"^[e©]\s+(?=[A-Z])")
# A handful of specific word-glue losses the scan makes at a line-wrap or
# bullet boundary, each confirmed by checking every occurrence in context
# (not a general dictionary de-gluer, which risks inventing words it
# shouldn't touch).
GLUED_WORDS = {
    "itis": "it is", "Bein": "Be in", "Atable": "A table",
    "ina": "in a", "toa": "to a",
}
GLUED_WORDS_RE = re.compile(r"\b(%s)\b" % "|".join(map(re.escape, GLUED_WORDS)))


def clean_line_extra(line):
    line = STANDALONE_PIPE_RE.sub("I", line)
    line = RE_BULLET_MISREAD.sub("• ", line)
    line = GLUED_WORDS_RE.sub(lambda m: GLUED_WORDS[m.group(1)], line)
    return line


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
# "Von:" opens a message the same way "From:" does (German Outlook export);
# a handful of messages in this release were forwarded/printed in German.
MSG_OPEN_RE = re.compile(r"^(?:From|rom|Fram|Von):\s*(.+)$", re.I)
HDR_DATE_RE = re.compile(r"^(?:Sent|Date|Gesendet)\s*:\s*(.+)$", re.I)
FIELD_ALIASES = {
    "ce": "Cc", "cc": "Cc", "bce": "Bcc", "bcc": "Bcc", "gc": "Cc",
    "fe": "To", "pe": "To", "to": "To", "fo": "From",
    "rom": "From", "fram": "From",
    "subiect": "Subject", "subjec": "Subject", "subject": "Subject",
    "senf": "Sent", "sent": "Sent", "dafe": "Date", "date": "Date",
    # German Outlook export (Von/Gesendet/An/Betreff), seen on a handful of
    # pages where the message was relayed through a German mail client.
    "von": "From", "gesendet": "Sent", "an": "To", "betreff": "Subject",
}
# Outlook's own screenshots (po-emails.pdf) never print more than a dozen
# header lines, but this release also carries GPMB Board broadcasts to 30+
# redacted recipients wrapped over 20+ visual lines.
MAX_HEADER_LINES = 80
REOPEN_MIN_DISTANCE = 16
RECIPIENT_TOKENS = frozenset({"to", "cc", "bcc", "ce", "fe", "pe", "gc", "an"})
SUBJECT_FALLBACK_RE = re.compile(r"^\s*(?:Subjec\w*|Betreff):?\s*(.+)$", re.I)

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

HEADER_FRAGMENT_NAME_RE = re.compile(
    r"(?:andersen|rambaut|farrar|holmes|garry|fauci|drosten|"
    r"koopmans|pohlmann|farzan|fouchier|schreier|"
    r"ferguson|golding|lipkin|vallance|collins|auchincloss|"
    r"conrad|shabman|folkers|burke|pope|viner|dzau|smith|"
    r"edward|andrew|jeremy|kristian|robert|anthony|christian|"
    r"marion|stefan|michael|claire|patricia|reed|martina|"
    r"greg|josie|amanda|francis|martin|rory|russell|victor|"
    r"eddie|tony|toney|farrar|beach|comin|perdue)", re.I)

# ── signature blocks ─────────────────────────────────────────────────────────
SIG_AFFIL_RE = re.compile(
    r"^(?:ARC |THE |UNIVERSITY|University|Institut|CENTRE|Centre|School|"
    r"Department|Dept\.|Faculty|College|Hospital|Institute|Trust|Laborator|"
    r"Director|Regents|Dean|Regent|Professor Emeritus|Charit|Campus|"
    r"Marie Bashir|Wellcome|MRC|NIH|NIAID|Atlanta|Bethesda|London|Sydney|"
    r"Berlin|D-\d{5})\b")

# "Thanks," and "Many thanks" are deliberately left out here -- both are also
# how a lot of genuine prose opens ("Thanks, Jeremy. Great chatting with you
# and Patrick. Will stay in close touch." -- a real reply this exact regex
# used to wipe out entirely, taking the rest of the body with it), so they're
# handled by foia_parser's shared strip_quoted_short_re instead, which only
# trusts them as a sign-off when the whole line is short.
STRIP_QUOTED_RE = re.compile(
    r"^(Best regards|Best wishes|Warm regards|Kinds?\s+regards|"
    r"With best wishes|Yours sincerely|Yours,|Best,|"
    r"Jeremy Farrar$|Anthony S\. Fauci|Tony$|Eddie$|Anders$|Christian$|"
    r"Kristian$|Andrew Rambaut$|Robert Garry$)", re.I)

# ── timestamps ───────────────────────────────────────────────────────────────
# German month names/abbreviations, for the handful of Von/Gesendet headers.
MONTHS_DE = {
    "jan": 1, "januar": 1, "feb": 2, "februar": 2, "mär": 3, "maer": 3,
    "marz": 3, "märz": 3, "mrz": 3, "apr": 4, "april": 4, "mai": 5,
    "jun": 6, "juni": 6, "jul": 7, "juli": 7, "aug": 8, "august": 8,
    "sep": 9, "september": 9, "okt": 10, "oktober": 10, "nov": 11,
    "november": 11, "dez": 12, "dezember": 12,
}
# "24 Jul 2020 10:37:46" (day-month-year, 24h clock, this release's default
# top-level stamp shape; the explicit "+0000" offset that usually follows is
# pulled separately by STAMP_BARE_OFFSET_RE) and "05 March 2020 02:06" (no
# am/pm at all, UK-forwarded).
STAMP_DMY_RE = re.compile(
    r"(\d{1,2})\s+([A-Za-z]{3,9})\.?\s*,?\s*(\d{4})\s*,?\s*(?:at\s+)?(\d{1,2}):(\d{2})"
    r"(?::(\d{2}))?\s*([AaPp]\.?[Mm]\.?)?")
# "4. Mai 2020 13:38" (German day-month-year with a period after the day).
STAMP_DE_RE = re.compile(
    r"(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]{3,10})\s+(\d{4})\s+(\d{1,2}):(\d{2})")
# "... 10:37:46 +0000" -- the bare RFC-2822 offset this release's top-level
# stamps carry, with no parens. Anchored at the end of the stamp string so it
# is never mistaken for a page/phone number elsewhere in the line.
STAMP_BARE_OFFSET_RE = re.compile(r"([+-])(\d{2})(\d{2})\s*$")


PROFILE = Profile(
    source_id="farrar-fauci",
    source_file="farrar-fauci-comms.pdf",
    title="Farrar-Fauci-Collins emails (FOI release)",
    ocr_txt=os.path.join(HERE, "..", "source_ocr", "farrar-fauci-comms_ocr.txt"),
    out_json=os.path.join(HERE, "farrar-fauci.json"),
    out_map=os.path.join(HERE, "farrar-fauci_page_map.json"),
    sender_roster=SENDER_ROSTER,
    first_names=FIRST_NAMES,
    header_fragment_name_re=HEADER_FRAGMENT_NAME_RE,
    zone_by_affiliation=ZONE_BY_AFFILIATION,
    default_zone=DEFAULT_ZONE,
    default_zone_why=DEFAULT_ZONE_WHY,
    furniture_re=FURNITURE,
    noise_tail_re=NOISE_TAIL,
    extra_clean_line=clean_line_extra,
    field_aliases=FIELD_ALIASES,
    msg_open_re=MSG_OPEN_RE,
    hdr_date_re=HDR_DATE_RE,
    max_header_lines=MAX_HEADER_LINES,
    reopen_min_distance=REOPEN_MIN_DISTANCE,
    recipient_tokens=RECIPIENT_TOKENS,
    subject_fallback_re=SUBJECT_FALLBACK_RE,
    sig_affil_re=SIG_AFFIL_RE,
    strip_quoted_re=STRIP_QUOTED_RE,
    stamp_dmy_re=STAMP_DMY_RE,
    stamp_bare_offset_re=STAMP_BARE_OFFSET_RE,
    stamp_de_re=STAMP_DE_RE,
    months_de=MONTHS_DE,
)


def main():
    run_release(PROFILE)


if __name__ == "__main__":
    main()
