#!/usr/bin/env python3
"""
Build chapter_links.json: for each message box in the release data, the P.O.
Tragicomedy sections (x.y) that quote or cite it.

The app shows a "P.O. Chapter" button on a content box or thread box only when
this file lists that box. The matching is deliberately strict, so a wrong
button is worse than a missing one:

  * the citation's document must map to a source (same rule as the app's
    guideDocToSource());
  * the entry must be on the citation's date, read in Eastern time;
  * when the caption gives a time, the entry's time must be within
    TOLERANCE_MIN minutes of it, after converting the caption's zone (UK,
    Germany, Eastern, Pacific, Sydney) with DST;
  * when the caption gives no time, the citation is left unlinked: a date
    alone is not enough, and some guide dates are themselves wrong;
  * a citation whose date or time cannot be matched is reported, not guessed.

Output: chapter_links.json, {bm_key: [{id, number, title}, ...]} and a
report of unlinked citations (chapter_links_report.txt).

Entry keys follow the app: "<source>/<thread_key>" when the entry has one,
otherwise "<source>/<idx>".
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
ANALYSIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis")
TOLERANCE_MIN = 10

SOURCE_FILES = {
    "part1": "part1.json",
    "part2": "part2.json",
    "sscp": "sscp-drafts.json",
    "po-emails": "po-emails.json",
    "farrar-fauci": "farrar-fauci.json",
}

ZONES = {
    "EST": "America/New_York", "EDT": "America/New_York", "ET": "America/New_York",
    "UK": "Europe/London", "GMT": "Europe/London", "BST": "Europe/London",
    "CET": "Europe/Berlin", "CEST": "Europe/Berlin", "GERMANY": "Europe/Berlin",
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles", "PT": "America/Los_Angeles",
    "AEDT": "Australia/Sydney",
}
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def doc_to_source(doc, date):
    """Same rule as the app's guideDocToSource()."""
    if not doc:
        return None
    d = doc.lower()
    if "proximal_origin_slack" in d:
        return "part2" if (date and date > "2020-04-30") else "part1"
    if "proximal_origin_emails" in d:
        return "po-emails"
    if "sscp-drafts-of-proximal-origin" in d or "drafts-of-proximal-origin" in d:
        return "sscp"
    if "farrar-fauci-comms" in d:
        return "farrar-fauci"
    return None


def caption_time(raw):
    """(hour, minute, zone-name-or-None) from the first clock time in a caption."""
    m = re.search(r"(\d{1,2})[:.](\d{2})(?::\d{2})?\s*([ap]\.?m\.?)?\s*"
                  r"(EST|EDT|ET|UK|GMT|BST|CET|CEST|Germany|PST|PDT|PT|AEDT)?",
                  raw or "", re.I)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    ap = (m.group(3) or "").lower().replace(".", "")
    if ap.startswith("p") and h < 12:
        h += 12
    if ap.startswith("a") and h == 12:
        h = 0
    zone = ZONES.get(m.group(4).upper()) if m.group(4) else None
    return h, mi, zone


def to_eastern(day, hm, zone):
    """Local stamp in zone -> (ISO date, minutes of day) in Eastern time."""
    y, mo, d = day
    h, mi = hm
    dt = datetime(y, mo, d, h, mi, tzinfo=ZoneInfo(zone)).astimezone(ZoneInfo("America/New_York"))
    return dt.date().isoformat(), dt.hour * 60 + dt.minute


def entry_minutes(e):
    t = (e.get("time") or "").strip()
    m = re.match(r"^(\d{2}):?(\d{2})", t)
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def bm_key(source, e):
    return "%s/%s" % (source, e["thread_key"] if e.get("thread_key") else e.get("idx"))


def main():
    guide = json.load(open(os.path.join(HERE, "po_guide.json"), encoding="utf-8"))
    entries = {}
    for src, fn in SOURCE_FILES.items():
        data = json.load(open(os.path.join(HERE, fn), encoding="utf-8"))
        entries[src] = data["entries"] if isinstance(data, dict) and "entries" in data else data

    links = defaultdict(list)
    report = []
    counts = defaultdict(int)

    for sec in guide.get("sections", []):
        for ev in sec.get("evidence", []):
            raw = ev.get("raw") or ""
            date = ev.get("date")
            if ev.get("kind") not in ("slack", "email", "draft"):
                continue
            src = doc_to_source(ev.get("doc"), date)
            if not src:
                counts["no source for document"] += 1
                continue
            if not date:
                counts["no date"] += 1
                report.append("%s  NO DATE  %s" % (sec.get("number") or sec["id"], raw))
                continue
            y, mo, d = map(int, date.split("-"))
            pool = entries.get(src, [])
            ct = caption_time(raw)
            target = None
            if ct:
                zone = ct[2] or ZONES["EST"]
                day_et, min_et = to_eastern((y, mo, d), (ct[0], ct[1]), zone)
                close = []
                for e in pool:
                    xm = entry_minutes(e)
                    if xm is None or e.get("date") != day_et:
                        continue
                    dd = abs(xm - min_et)
                    if dd <= TOLERANCE_MIN:
                        close.append((dd, e))
                if len(close) == 1:
                    target = close[0][1]
                elif len(close) > 1:
                    close.sort(key=lambda t: t[0])
                    if close[0][0] < close[1][0]:
                        target = close[0][1]
                if target is None:
                    counts["time not found"] += 1
                    report.append("%s  TIME NOT FOUND  %s  (ET %s %02d:%02d)" % (
                        sec.get("number") or sec["id"], raw, day_et, min_et // 60, min_et % 60))
                    continue
            else:
                # A date with no time is not enough to link a box: the guide's
                # date for some citations is itself wrong (see p1-10.4, which
                # would have linked a 25 Jul email to a 5 Feb section).
                counts["no time: not linked"] += 1
                report.append("%s  NO TIME, not linked  %s" % (
                    sec.get("number") or sec["id"], raw))
                continue
            key = bm_key(src, target)
            entry_ref = {"id": sec["id"], "number": sec.get("number"), "title": sec.get("title")}
            if entry_ref not in links[key]:
                links[key].append(entry_ref)
            counts["linked"] += 1

    out = os.path.join(HERE, "chapter_links.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ANALYSIS, "chapter_links_report.txt"), "w", encoding="utf-8") as f:
        f.write("Unlinked citations (strict matching):\n")
        f.write("\n".join(report) + "\n")
    print("boxes with a chapter link:", len(links))
    for k, v in sorted(counts.items()):
        print("  %-28s %d" % (k, v))


if __name__ == "__main__":
    main()
