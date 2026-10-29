#!/usr/bin/env python3
"""
Parse the FOIA'd P.O. email release (po-emails.pdf, cited throughout the
P.O. "Tragicomedy" piece as Proximal_Origin_Emails.pdf) into one entry per
email message.

The release ships as scanned page images with no text layer, so the text comes
from reocr_po_emails.py. What that OCR gives us is a stream of Outlook
message headers -- an outer header per message, plus the quoted headers of the
messages it answers, all inside one printed chain.

The segmentation/zone/signature/stamp grammar itself lives in the shared
`foia_parser` package (Work/Edition/foia_parser) -- the engine this release
shares with farrar-fauci-comms (see parse_farrar_fauci.py) and, going
forward, any other FOIA'd email release. This file supplies only what is
specific to THIS release: who the correspondents are, which affiliation
implies which time zone, and which OCR noise this particular scan leaves
behind. See that package's SKILL.md for the rules this follows (borrowed
from the Fauci diary's own email work):

  * one entry per message -- an author at an instant -- never a whole thread
  * an entry holds only what its author wrote; quoted history is its own entry
  * an explicit UTC offset in the stamp always wins
  * otherwise the sender's own institution decides the zone, and the
    assumption is recorded, never silent
  * everything is normalised to ET for ordering, with the local stamp kept

Output: po-emails.json (entries) + po-emails_page_map.json (PDF pages).
"""

import os
import re

from foia_parser import Profile, run_release

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
ANALYSIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis")

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
    (re.compile(r"lipkin|columbia", re.I), "America/New_York", "Columbia University"),
    (re.compile(r"sydney|holmes|university of sydney", re.I), "Australia/Sydney",
     "University of Sydney"),
    (re.compile(r"pasteur|fouchier|paris|institut", re.I), "Europe/Paris", "Institut Pasteur"),
]
DEFAULT_ZONE = "Europe/London"      # the Wellcome Trust ran this exercise
DEFAULT_ZONE_WHY = "Wellcome Trust (the release's convener)"

# ── OCR clean-up ────────────────────────────────────────────────────────────
# The scans are screenshots of Outlook, so each header carries avatar glyphs
# and stray marks ("Edward Holmes | rrr-iYS", "Jeremy Farrar a").
NOISE_TAIL = re.compile(r"\s*[|Il\[\]{}<>«»“”„’‘—–\-–—_=+*#§¶©®™✓✔✗✘»«»…]+"
                        r"\s*(?:[a-zA-Z]{1,4})?\s*$")

FURNITURE = re.compile(
    r"^(REV\d+|GARRY\d+|CONFIDENTIAL|NIAID|EXCERPT FROM|"
    r"National Institute of Allergy|National Institutes of Health|Bethesda, MD|"
    r"Phone:|FAX:|E-mail:|Director, National|The information in this e-mail|"
    r"it is not intended that|you should delete|received this e-mail in error|"
    r"or any other storage devices|liable for any statements|"
    r"on behalf of the|Building \d+|Room \d+|Contor Drive|NSC \d+|"
    r"National Institutes of Health$|"
    # A multi-line committee banner ("CONFIDENTIAL TREATMENT / REQUESTED -
    # NOT FOR / CIRCULATION / COMMITTEE / MEMBERS AND STAFF ONLY
    # LIP-000472") printed mid-page on some of the LIP-stamped pages -- the
    # trailing Bates code is still recovered by page_owner_map(), which
    # reads the raw, unfiltered text independently of this list.
    r"REQUESTED - NOT FOR|CIRCULATION / COMMITTEE|MEMBERS AND STAFF ONLY)",
    re.I)

# ── header grammar ──────────────────────────────────────────────────────────
# A field header, possibly OCR-glued to the next one ("Cc: Jeremy FarrarSubject:
# x"). The OCR routinely reads the two capitals in "Cc:" as "Ce:" (and "To:" as
# "Pe:"/"Fe:"), so the alternation lists those readings too -- otherwise a Cc
# list stays glued to a Subject line and "Subject: Fwd: ..." leaks into the
# message body.
FIELD_ALIASES = {
    "ce": "Cc", "cc": "Cc", "bce": "Bcc", "bcc": "Bcc", "gc": "Cc",
    "fe": "To", "pe": "To", "to": "To", "fo": "From",
    # "rom:" (line 4711) is a From: whose capital F the scan amputated with the
    # page furniture ("\x0crom: Edward Holmes"). Single occurrence in the
    # release; kept as an alias rather than a special case so the normal
    # header path handles it.
    "rom": "From",
    "subiect": "Subject", "subjec": "Subject", "subject": "Subject",
    "senf": "Sent", "sent": "Sent", "dafe": "Date", "date": "Date",
}

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
# recognise a roll of recipients as such (is_wrapped_recipient), which is
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

# A stray scrap of a header the two-column scan tore off is recognised by
# shape (is_header_fragment) plus a hit against this correspondent-name
# alternation, so a single ordinary capitalised word (prose, far more often
# than a torn header) is not mistaken for one.
HEADER_FRAGMENT_NAME_RE = re.compile(
    r"(?:andersen|rambaut|farrar|holmes|garry|fauci|drosten|"
    r"koopmans|pohlmann|farzan|andersen|fouchier|schreier|"
    r"ferguson|golding|lipkin|vallance|collins|auchincloss|"
    r"conrad|shabman|folkers|burke|pope|thomas|"
    r"edward|andrew|jeremy|kristian|robert|anthony|christian|"
    r"marion|stefan|michael|claire|patricia|reed|martina|"
    r"greg|andrew|josie|amanda|francis|jeremy|martin|rory|"
    r"eddie|tony|toney|farrar|beach|comin|perdue)", re.I)

# "Thanks," and "Many thanks" are deliberately left out here -- both are also
# how a lot of genuine prose opens ("Thanks, Kristian. Talk soon on the
# call."), so they're handled by foia_parser's shared strip_quoted_short_re
# instead, which only trusts them as a sign-off when the whole line is short.
STRIP_QUOTED_RE = re.compile(
    r"^(Best regards|Best wishes|Warm regards|Kinds?\s+regards|"
    r"With best wishes|Yours sincerely|Yours,|Best,|"
    r"Jeremy Farrar$|Anthony S\. Fauci|Tony$|Eddie$|Anders$|"
    r"Andrew Rambaut$|Robert Garry$)", re.I)

# ── page-owner (mailbox) codes ────────────────────────────────────────────────
# This release is a mash-up of several mailboxes' own exports, each page
# carrying its owner's Bates-style stamp as the page's own last line. See
# THREADING_PLAN.md §2 for the reasoning (a quoted stamp is frozen in the
# REPLIER's zone, not the original sender's -- the page-owner code is one way
# to recover whose zone a thread's last, otherwise-unzoned message was read
# in) and the evidence behind this specific table.
#
# Confirmed: pages 28-34 and 65 carry "GARRY0000NNN" (25 pages total) --
# Robert Garry's own mailbox export, spliced into the REV-stamped run at
# those points. Tulane -> America/Chicago matches the zone this release's
# own sender-affiliation table (ZONE_BY_AFFILIATION above) already assigns
# Garry by his name alone, so this is a confirming cross-check, not a new
# claim.
#
# "REV%07d" is the OTHER stamp family (108 pages) -- but unlike GARRY it is
# NOT contiguous (it covers both ~0000750-0000803 and ~0001890-0002865, with
# the GARRY run spliced in between), which argues against it being one
# person's single mailbox export and for it being a recurring legal-review/
# processing stamp applied across many different real mailboxes instead --
# confirmed unidentified (never traced to a specific person or office), but
# empirically recorded in US Pacific time: UTC-8 standard / UTC-7 daylight,
# could be off by up to an hour. ZoneInfo handles the DST switch on its own,
# so the single zone key covers both.
#
# "LIP-%06d" is a third family (17 pages, two short runs: 472-473 and
# 615-652) -- Lipkin's own mailbox export (W. Ian Lipkin, Columbia
# University), printed glued onto the tail of a multi-line committee banner
# ("...MEMBERS AND STAFF ONLY LIP-000472") rather than standing alone the
# way GARRY/REV do -- hence page_owner_re matching the tail of the line, not
# the whole of it (see page_owner_map() in core.py).
PAGE_OWNER_RE = re.compile(r"\b(REV|GARRY|LIP)-?\d{4,8}\s*$")
PAGE_OWNERS = {
    "GARRY": ("America/Chicago", "Robert Garry's own mailbox export (page-owner code GARRY)"),
    "REV": ("America/Los_Angeles",
            "REV export: US Pacific time (UTC-8 winter / UTC-7 summer); fits Kristian "
            "Andersen's mailbox (Scripps Research, La Jolla, San Diego)"),
    "LIP": ("America/New_York",
            "W. Ian Lipkin's own mailbox export (Columbia University; page-owner code LIP)"),
}


PROFILE = Profile(
    source_id="po-emails",
    source_file="po-emails.pdf",
    title="P.O. emails (FOI release)",
    ocr_txt=os.path.join(HERE, "..", "source_ocr", "po-emails_ocr.txt"),
    out_json=os.path.join(HERE, "po-emails.json"),
    out_map=os.path.join(HERE, "po-emails_page_map.json"),
    sender_roster=SENDER_ROSTER,
    first_names=FIRST_NAMES,
    header_fragment_name_re=HEADER_FRAGMENT_NAME_RE,
    zone_by_affiliation=ZONE_BY_AFFILIATION,
    default_zone=DEFAULT_ZONE,
    default_zone_why=DEFAULT_ZONE_WHY,
    furniture_re=FURNITURE,
    noise_tail_re=NOISE_TAIL,
    field_aliases=FIELD_ALIASES,
    strip_quoted_re=STRIP_QUOTED_RE,
    # MAX_HEADER_LINES / REOPEN_MIN_DISTANCE: see foia_parser's SKILL.md --
    # deliberately two separate constants, never share one. A group message
    # (NASEM/GPMB-style broadcasts) can carry 20+ redacted recipients wrapped
    # over as many lines, so the header cap is generous; the reopen distance
    # is kept much smaller so an ordinary short message still re-triggers the
    # "Date:/Sent: with no From: above it" recovery for the message after it.
    max_header_lines=80,
    # A stamp that names its zone is explicit: it outranks every other rule.
    named_zone_offsets={"AEDT": 11, "AEST": 10, "EST": -5, "EDT": -4,
                        "CST": -6, "CDT": -5, "PST": -8, "PDT": -7,
                        "GMT": 0, "BST": 1, "CET": 1, "CEST": 2},
    reopen_min_distance=16,
    page_owner_re=PAGE_OWNER_RE,
    page_owners=PAGE_OWNERS,
)


def main():
    run_release(PROFILE)


if __name__ == "__main__":
    main()
