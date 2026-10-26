#!/usr/bin/env python3
"""Write zone_format_audit.csv: one row per email entry, with the rule that set its time.

Run after every email rebuild (parse_po_emails.py, parse_farrar_fauci.py and
dedupe_same_instant.py). Columns:

  release        po-emails or farrar-fauci
  idx            entry number in the current JSON (shifts when times change)
  thread_key     the key bookmarks and chapter links use
  date, time     current Eastern date and time shown in the app
  sender         as parsed (blank = not in the scan)
  stamp          the stamp text as printed
  stamp_format   day-month-year, long, offset, partial-no-time, ...
  rule           the rule that set the time (plain words, see RULE_NAMES)
  pdf            the PDF file the entry is on
  pdf_pages      PDF page(s) from the page map
  zone_status    Settled, Supported or Not settled, from the evidence for its zone source
  status_reason  why it is (or is not) settled
  check          why the entry needs a look, or blank
  note           a note from a check against the page image, if one exists
"""
import csv
import json
import os
import re

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
ANALYSIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis")
FILES = [("po-emails", "po-emails.json"), ("farrar-fauci", "farrar-fauci.json")]
PAGE_MAPS = {"po-emails": "po-emails_page_map.json", "farrar-fauci": "farrar-fauci_page_map.json"}
PDFS = {"po-emails": "po-emails.pdf", "farrar-fauci": "farrar-fauci-comms.pdf"}

# Notes from checks against the page images. Keyed by thread_key. Kept here so
# they survive every rebuild.
NOTES = {
    "po-emails|2020-01-31|1938": "Checked by owner_zone_check.py: the printed 4:38 PM on this REV page matches a farrar-fauci copy with +0000 (same message, 0.99 similarity), giving UTC-8 (Pacific). One data point only.",
    "po-emails|2020-01-31|1500": "Time corrected to 5:57 PM Eastern from the page image (po-emails.pdf p.2); OCR had dropped it. See tools/verified_overrides.json.",
    "po-emails|2020-01-31|1500|1": "A distinct message (Farrar's original 'Phone call', 5:23 PM Eastern, po-emails.pdf p.3), not a duplicate. Time corrected from the page image; body text still lost by OCR. See tools/verified_overrides.json.",
    "farrar-fauci|2020-01-31|1257": "Time corrected to 5:57 PM Eastern (same message as po-emails|2020-01-31|1500). See tools/verified_overrides.json.",
}

RULE_NAMES = [
    (r"^verified", "1c. Verified from the page image"),
    (r"^explicit", "1. Zone written in the stamp"),
    (r"^anchored", "1b. Exact copy with an explicit offset"),
    (r"^frozen in", "2. Quoted copy: replier's zone"),
    (r"REV mailbox", "4. Page owner REV (assumed Pacific)"),
    (r"GARRY|Robert Garry", "4. Page owner GARRY (assumed Chicago)"),
    (r"W\. Ian Lipkin", "4. Page owner LIP (Eastern)"),
    (r"Wellcome|Vallance|Farrar|Golding|Ferguson|Viner|Rambaut|UK government", "3. Sender's institution: London"),
    (r"NIH|NIAID|Bethesda|Fauci|Collins", "3. Sender's institution: New York"),
    (r"Scripps|Andersen|Farzan", "3. Sender's institution: Los Angeles"),
    (r"Tulane", "3. Sender's institution: Chicago"),
    (r"Sydney|Holmes", "3. Sender's institution: Sydney"),
    (r"Pasteur|Fouchier", "3. Sender's institution: Paris"),
    (r"China CDC|Gao", "3. Sender's institution: Beijing"),
    (r"Charite|Drosten", "3. Sender's institution: Berlin"),
    (r"Eastern display", "3. Unzoned default: Eastern"),
]


def rule_of(e):
    z = (e.get("zone_assumed") or "").strip()
    if not z:
        return "none (no time)" if e.get("stamp_status") == "partial-no-time" else "unparsed"
    for pat, name in RULE_NAMES:
        if re.search(pat, z, re.I):
            return name
    return "other: " + z[:60]


# Settled or not, per zone source, from the evidence in ZONE_AND_DATE_ANALYSIS.md
# (zone status table). Matched on the zone text the parser recorded.
STATUS = [
    (r"^verified", "Settled", "verified from the page image (see verified_overrides.json)"),
    (r"^explicit", "Settled", "zone written in the stamp"),
    (r"^anchored", "Settled", "exact copy with an explicit offset"),
    (r"REV mailbox", "Settled", "accepted: one exact pair (UTC-8). Applies to the page owner's own clock; a quoted block on a REV page can be frozen on another author's clock (see PO 0 and PO 1)"),
    (r"W\. Ian Lipkin", "Supported", "consistent with reply order; reply order cannot catch a time that is too early"),
    (r"release's convener", "Supported", "consistent with reply order; quoted copies can be frozen on another clock (see FF 22)"),
    (r"NIH, Bethesda", "Supported", "consistent with reply order; reply order cannot catch a time that is too early"),
    (r"Robert Garry's own", "Not settled", "Chicago or Eastern; no exact copy (reply order excludes Pacific)"),
    (r"^frozen in", "Not settled", "footnote rule; not tested on web clients"),
    (r"Wellcome Trust / UK", "Not settled", "too few reply pairs"),
    (r"Scripps|Sydney|Charite|Tulane|Pasteur|China CDC", "Not settled", "too few reply pairs"),
]


def status_of(e):
    z = (e.get("zone_assumed") or "").strip()
    if not z:
        return "Not settled", "no zone: partial or unparsed stamp; needs the page image"
    for pat, st, why in STATUS:
        if re.search(pat, z, re.I):
            return st, why
    return "Not settled", "no evidence recorded"


def check_of(e, rule):
    notes = []
    if e.get("stamp_status") == "partial-no-time":
        notes.append("no time in the stamp")
    if e.get("stamp_status") == "unparsed" or not e.get("date"):
        notes.append("stamp not parsed")
    if rule.startswith("4. Page owner REV") or rule.startswith("4. Page owner GARRY"):
        notes.append("owner zone not yet verified")
    if rule.startswith("2."):
        notes.append("zone taken from the quoting message")
    if not e.get("sender") and e.get("date"):
        notes.append("sender not in the scan")
    return "; ".join(notes)


def pages_of(release, thread_key):
    try:
        pm = json.load(open(os.path.join(HERE, PAGE_MAPS[release]), encoding="utf-8"))
    except (OSError, KeyError):
        return ""
    p = pm.get(thread_key)
    if not p:
        return ""
    return str(p["start"]) if p["start"] == p["end"] else "%d-%d" % (p["start"], p["end"])


def load(name):
    data = json.load(open(os.path.join(HERE, name), encoding="utf-8"))
    return data["entries"] if isinstance(data, dict) and "entries" in data else data


def main():
    out = os.path.join(ANALYSIS, "zone_format_audit.csv")
    rows = []
    for release, name in FILES:
        for e in load(name):
            rule = rule_of(e)
            tk = e.get("thread_key") or ""
            rows.append([release, e.get("idx"), tk,
                         e.get("date") or "", e.get("time") or "", e.get("sender") or "",
                         e.get("stamp") or "", e.get("stamp_status") or "", rule,
                         PDFS[release], pages_of(release, tk),
                         status_of(e)[0], status_of(e)[1],
                         check_of(e, rule), NOTES.get(tk, "")])
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["release", "idx", "thread_key", "date", "time", "sender", "stamp",
                    "stamp_format", "rule", "pdf", "pdf_pages", "zone_status", "status_reason",
                    "check", "note"])
        w.writerows(rows)
    print("wrote %d rows to zone_format_audit.csv" % len(rows))


if __name__ == "__main__":
    main()
