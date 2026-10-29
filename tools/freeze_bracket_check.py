#!/usr/bin/env python3
"""Freeze-rule and bracketing check for the P.O. emails (rules 5.6 and 5.7 of
ZONE_AND_DATE_ANALYSIS.md). Reads page_based/po-emails.json, changes nothing,
writes analysis/freeze_bracket_check.csv and prints a summary.

Clock of a stamp (the freeze rule):
  * quoted inside another message (an explicit quote link points at it): the clock of the QUOTER'S AUTHOR;
  * otherwise (top-level): the clock of the mailbox the page belongs to (page-owner zone).
Bracketing: for a message whose time is not exact, the exact (explicit-offset) messages above it and below it
in the reply chain bound its true time. The whole-hour UTC offsets that put its printed time inside that window
are the offsets its clock can have.

Columns of the CSV: see the header row. Offsets are hours from UTC (Chicago winter = -6, Eastern = -5).
"""
import csv
import json
import os
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
PB = os.path.join(HERE, "..", "page_based")
AN = os.path.join(HERE, "..", "analysis")

NAME_TZ = [  # author's own clock, from where the person works
    (r"holmes", "Australia/Sydney"), (r"rambaut|ian\b.*edinburgh", "Europe/London"),
    (r"andersen|farzan", "America/Los_Angeles"), (r"garry", "America/Chicago"),
    (r"lipkin", "America/New_York"), (r"farrar|vallance|golding|ferguson|viner", "Europe/London"),
    (r"fauci|collins|folkers|auchincloss", "America/New_York"), (r"drosten", "Europe/Berlin"),
    (r"fouchier", "Europe/Amsterdam"), (r"daszak", "America/New_York"),
]
ZN = {"Los Angeles": "America/Los_Angeles", "Chicago": "America/Chicago", "London": "Europe/London",
      "ET": "America/New_York", "Sydney": "Australia/Sydney", "Paris": "Europe/Paris",
      "Berlin": "Europe/Berlin", "Beijing": "Asia/Shanghai"}
OWNER_TZ = {"REV": "America/Los_Angeles", "GARRY": "America/Chicago", "LIP": "America/New_York"}
ET = ZoneInfo("America/New_York")


def author_tz(sender):
    s = (sender or "").lower()
    for pat, tz in NAME_TZ:
        if re.search(pat, s):
            return tz
    return None


def main():
    d = json.load(open(os.path.join(PB, "po-emails.json"), encoding="utf-8"))
    ents = d["entries"] if isinstance(d, dict) else d
    pm = json.load(open(os.path.join(PB, "po-emails_page_map.json"), encoding="utf-8"))
    by = {e["thread_key"]: e for e in ents}

    quoter = {}
    for q in ents:
        k = q.get("reply_to")
        if k and "explicit" in (q.get("link_kind") or "") and k in by:
            quoter.setdefault(k, q)

    def et_dt(e):
        if not e.get("date") or not e.get("time") or "(time not" in (e.get("stamp_line") or ""):
            return None
        return datetime.fromisoformat(e["date"] + " " + e["time"][:2] + ":" + e["time"][2:]).replace(tzinfo=ET)

    def exact(e):
        z = e.get("zone_assumed") or ""
        return z.startswith(("explicit", "anchored", "verified"))

    def anchor(e):
        """Precisely timed: an explicit/anchored/verified stamp, or a top-level stamp in the REV mailbox
        (settled: Pacific). Quoted REV blocks are not anchors (their clock is the quoter's)."""
        if exact(e):
            return True
        return owner_of(e) == "REV" and e["thread_key"] not in quoter and not (
            "(time not" in (e.get("stamp_line") or ""))

    def pages(e):
        p = pm.get(e["thread_key"])
        return "" if not p else (str(p["start"]) if p["start"] == p["end"] else "%d-%d" % (p["start"], p["end"]))

    def owner_of(e):
        z = e.get("zone_assumed") or ""
        if "REV export" in z:
            return "REV"
        if "Garry's own" in z:
            return "GARRY"
        if "Lipkin's own" in z:
            return "LIP"
        return None

    # naive wall-clock time as printed: undo the conversion the pipeline made
    def wall(e):
        t = et_dt(e)
        if t is None:
            return None
        m = re.match(r"\d\d:\d\d (.+?) ->", e.get("stamp_line") or "")
        zname = m.group(1) if m else "ET"
        tz = ZoneInfo(ZN.get(zname, "America/New_York"))
        return t.astimezone(tz).replace(tzinfo=None)


    def clock(e):
        """(role, tz name or None) of the clock that froze this stamp."""
        q = quoter.get(e["thread_key"])
        if q is not None:
            return "quoted by " + (q.get("sender") or "?"), author_tz(q.get("sender"))
        o = owner_of(e)
        return ("mailbox " + o if o else "mailbox"), OWNER_TZ.get(o)

    def inst_under(e, tzname):
        w = wall(e)
        if w is None or tzname is None:
            return None
        return w.replace(tzinfo=ZoneInfo(tzname)).astimezone(timezone.utc)

    def inst_now(e):
        t = et_dt(e)
        return None if t is None else t.astimezone(timezone.utc)

    def chain(e, nxt, strong_only):
        seen, out, stack = set(), [], [e]
        while stack:
            x = stack.pop()
            for k in nxt(x):
                y = by.get(k)
                if y is None or id(y) in seen:
                    continue
                if strong_only and not strong_link(x, y):
                    continue
                seen.add(id(y)); out.append(y); stack.append(y)
        return out

    def strong_link(a, b):  # a and b adjacent in the chain; strong when the quote link is explicit
        for q, p in ((a, b), (b, a)):
            if q.get("reply_to") == p["thread_key"] and "explicit" in (q.get("link_kind") or ""):
                return True
        return False

    up = lambda x: [x["reply_to"]] if x.get("reply_to") else []
    down = lambda x: [r["key"] for r in (x.get("replied_by") or []) if isinstance(r, dict)]

    rows = []
    for e in ents:
        if exact(e) or et_dt(e) is None:
            continue
        # REV top-level entries are still tested (they are also anchors for others)
        w = wall(e)
        role, tzn = clock(e)
        cur = inst_now(e)
        frz = inst_under(e, tzn)
        res = {}
        for label, strong in (("strong", True), ("weak", False)):
            A = [inst_now(x) for x in chain(e, up, strong) if anchor(x) and inst_now(x)]
            D = [inst_now(x) for x in chain(e, down, strong) if anchor(x) and inst_now(x)]
            lo = max(A) if A else None
            hi = min(D) if D else None
            ok = []
            for u in range(-12, 15):
                t = (w - timedelta(hours=u)).replace(tzinfo=timezone.utc)
                if (lo is None or t >= lo) and (hi is None or t <= hi):
                    ok.append(u)
            res[label] = (lo, hi, ok)
        lo, hi, okS = res["strong"]
        okW = res["weak"][2]
        cur_u = round((w - cur.replace(tzinfo=None)).total_seconds() / 3600) if cur else None
        win = "" if (lo is None or hi is None) else "%.1f" % ((hi - lo).total_seconds() / 3600)
        frz_u = None if frz is None else round((w - frz.replace(tzinfo=None)).total_seconds() / 3600)
        rows.append({
            "idx": e["idx"], "pdf_pages": pages(e), "stamp": e["stamp"], "sender": e.get("sender") or "",
            "subject": (e.get("subject") or "")[:40], "shown_ET": e["date"] + " " + e["time"],
            "clock": role, "shown_offset": cur_u,
            "freeze_offset": "" if frz_u is None else frz_u,
            "freeze_ET": "" if frz is None else frz.astimezone(ET).strftime("%Y-%m-%d %H:%M"),
            "window_h_strong": win,
            "allowed_strong": " ".join(map(str, okS)) if (res["strong"][0] or res["strong"][1]) else "no bracket",
            "allowed_weak": " ".join(map(str, okW)) if (res["weak"][0] or res["weak"][1]) else "no bracket",
            "_okS": okS, "_okW": okW, "_u": cur_u, "_owner": owner_of(e), "_role": role,
            "_bracketS": bool(res["strong"][0] or res["strong"][1]), "_bracketW": bool(res["weak"][0] or res["weak"][1]),
        })

    cols = ["idx", "pdf_pages", "stamp", "sender", "subject", "shown_ET", "clock", "shown_offset",
            "freeze_offset", "freeze_ET", "window_h_strong", "allowed_strong", "allowed_weak"]
    with open(os.path.join(AN, "freeze_bracket_check.csv"), "w", newline="", encoding="utf-8") as fh:
        w_ = csv.writer(fh)
        w_.writerow(cols)
        for r in rows:
            w_.writerow([r[c] for c in cols])

    # summary
    n_q = sum(1 for r in rows if r["_role"].startswith("quoted"))
    print("entries not exact: %d; quoted (clock = quoter's author): %d; top-level: %d"
          % (len(rows), n_q, len(rows) - n_q))
    shifted = [r for r in rows if r["_role"].startswith("quoted") and r["freeze_offset"] != "" and r["freeze_offset"] != r["shown_offset"]]
    print("quoted entries whose freeze-rule clock differs from the shown one: %d" % len(shifted))
    for own in ("GARRY", "REV", "LIP"):
        top = [r for r in rows if r["_owner"] == own and not r["_role"].startswith("quoted")]
        for label, key, bk in (("strong", "_okS", "_bracketS"), ("weak", "_okW", "_bracketW")):
            br = [r for r in top if r[bk]]
            votes = {}
            for r in br:
                for u in r[key]:
                    votes[u] = votes.get(u, 0) + 1
            narrow = [r for r in br if len(r[key]) <= 3]
            print("%s top-level (mailbox clock): %d, bracketed (%s): %d, narrow (<=3 offsets): %d; offsets allowed by all bracketed: %s"
                  % (own, len(top), label, len(br), len(narrow),
                     sorted(u for u, c in votes.items() if c == len(br))))
    # reply-order test: current times against freeze-rule times
    def frozen_inst(e):
        if exact(e) or et_dt(e) is None:
            return inst_now(e)
        role, tzn = clock(e)
        if role.startswith("quoted") and tzn:
            return inst_under(e, tzn)
        return inst_now(e)
    for kind in ("explicit", "inferred"):
        bad_now, bad_frz, fixed, broken, n = 0, 0, [], [], 0
        for q in ents:
            lk = q.get("link_kind") or ""
            par = by.get(q.get("reply_to"))
            if par is None or kind not in lk:
                continue
            a, b, c, d = inst_now(par), inst_now(q), frozen_inst(par), frozen_inst(q)
            if None in (a, b, c, d):
                continue
            n += 1
            now_bad, frz_bad = b < a, d < c
            bad_now += now_bad
            bad_frz += frz_bad
            if now_bad and not frz_bad:
                fixed.append((par, q))
            if frz_bad and not now_bad:
                broken.append((par, q))
        print("\n%s links: %d pairs; reply before parent: now %d, under the freeze rule %d (fixed %d, newly broken %d)"
              % (kind, n, bad_now, bad_frz, len(fixed), len(broken)))
        for lab, lst in (("  fixed", fixed), ("  newly broken", broken)):
            for par, q in lst[:25]:
                print("%s: p.%s %s (%s) -> p.%s %s (%s)" % (lab, pages(par), par["stamp"][:30], (par.get("sender") or "")[:10],
                      pages(q), q["stamp"][:30], (q.get("sender") or "")[:10]))
    print()
    print("GARRY top-level, bracketed by anchors (weak links included): offsets -6 (Chicago) / -5 (Eastern)")
    for r in rows:
        if r["_owner"] == "GARRY" and not r["_role"].startswith("quoted") and r["_bracketW"]:
            print("  p.%s %s | %s | allowed: %s" % (r["pdf_pages"], r["stamp"], r["sender"], r["allowed_weak"]))
    return rows


if __name__ == "__main__":
    main()
