#!/usr/bin/env python3
"""Build bookmark_rekey.json: old bookmark keys -> current keys for emails.

A bookmark stores its entry's key. For emails the key is
"<source>/<thread_key>", and thread_key contains the date and time. When a
parser fix moves an email to another time, its key changes and an old bookmark
stops finding it. This script maps each committed key to the current key of the
same message, so the app can rewrite saved bookmarks when it loads them.

Old data = the committed JSON (git HEAD), i.e. what bookmarks were made against.
New data = the working-tree JSON.

A mapping is written only when the match is unambiguous: same body text,
within 24 hours, and exactly one current entry nearest in time. Old keys that
still exist unchanged are left alone; old keys that now name a different
message are reported and not mapped.
"""
import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import date

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
ANALYSIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis")
SOURCES = {"po-emails": "po-emails.json", "farrar-fauci": "farrar-fauci.json"}


def git_head_json(name):
    rel = os.path.relpath(os.path.join(HERE, name), subprocess.check_output(
        ["git", "-C", HERE, "rev-parse", "--show-toplevel"]).decode().strip())
    raw = subprocess.check_output(["git", "-C", HERE, "show", "HEAD:" + rel])
    return json.loads(raw)


def entries_of(data):
    return data["entries"] if isinstance(data, dict) and "entries" in data else data


def body_key(e):
    lines = [l for l in (e.get("content") or "").split("\n")
             if l.strip()
             and not re.match(r"^\s*(>?\s*)(From|To|Cc|Bcc|Subject|Sent|Date|Attachments|Importance)\s*:", l, re.I)
             and not re.match(r"^-{3,}$", l.strip())]
    return re.sub(r"[^a-z0-9]", "", " ".join(lines).lower())[:90]


def instant(e):
    if not e.get("date") or not e.get("time"):
        return None
    d = date.fromisoformat(e["date"])
    return (d - date(2020, 1, 1)).days * 1440 + int(e["time"][:2]) * 60 + int(e["time"][2:])


def app_key(source, e):
    return "%s/%s" % (source, e.get("thread_key") or e.get("idx"))


def accumulate(new_map, path, live_keys):
    """Keep the pairs from earlier rebuilds, so bookmarks made against any earlier
    published version still resolve. Comparing with the last commit alone would
    empty the table after the next commit.

    Chains are followed (old -> middle -> current becomes old -> current). A pair is
    dropped if its old key is a live key again (it would hijack a valid entry), or if
    its target no longer exists."""
    merged = {}
    if os.path.exists(path):
        try:
            merged.update(json.load(open(path, encoding="utf-8")))
        except (OSError, ValueError):
            pass
    merged.update(new_map)
    final = {}
    for old, target in merged.items():
        seen = {old}
        while target in merged and target not in live_keys and target not in seen:
            seen.add(target)
            target = merged[target]
        if old in live_keys or target not in live_keys or target == old:
            continue
        final[old] = target
    return final


def main():
    live_keys = set()
    mapping, report = {}, []
    for source, name in SOURCES.items():
        old = entries_of(git_head_json(name))
        new = entries_of(json.load(open(os.path.join(HERE, name), encoding="utf-8")))
        new_keys = {app_key(source, e): e for e in new}
        live_keys.update(new_keys)
        by_body = defaultdict(list)
        for e in new:
            if len(body_key(e)) >= 60:
                by_body[body_key(e)].append(e)
        for o in old:
            ok = app_key(source, o)
            if ok in new_keys:
                if body_key(new_keys[ok]) == body_key(o):
                    continue                       # unchanged message
                report.append(("COLLISION", ok, "key now names a different message"))
                continue
            if len(body_key(o)) < 60 or instant(o) is None:
                # A short or header-only copy (removed as a duplicate fragment):
                # map it to the one current entry with the same date, time and sender.
                same = [e for e in new if o.get("date") and (e.get("date"), e.get("time"), e.get("sender")) ==
                        (o.get("date"), o.get("time"), o.get("sender"))]
                if not same and instant(o) is not None:
                    # a zone change can move an entry by a few hours: same sender,
                    # unique nearest within 3 hours
                    near = sorted((abs(instant(e) - instant(o)), i) for i, e in enumerate(new)
                                  if instant(e) is not None and e.get("sender") == o.get("sender")
                                  and abs(instant(e) - instant(o)) <= 180)
                    if near and (len(near) == 1 or near[0][0] < near[1][0]):
                        same = [new[near[0][1]]]
                if len(same) == 1 and not (ok in new_keys):
                    mapping[ok] = app_key(source, same[0])
                else:
                    report.append(("NO MATCH KEY", ok, "too little text, and no unique current entry with the same date, time and sender"))
                continue
            # Sender names vary between copies ("Marion" vs "Marion Koopmans"),
            # so the text decides, and the time must be within 24 hours.
            cands = [e for e in by_body.get(body_key(o), [])
                     if instant(e) is not None and abs(instant(e) - instant(o)) <= 24 * 60]
            if not cands:
                report.append(("NOT FOUND", ok, "no current copy with the same text and sender"))
                continue
            best = min(abs(instant(e) - instant(o)) for e in cands)
            nearest = [e for e in cands if abs(instant(e) - instant(o)) == best]
            if len(nearest) != 1:
                report.append(("AMBIGUOUS", ok, "%d equally close copies" % len(nearest)))
                continue
            mapping[ok] = app_key(source, nearest[0])
    out = os.path.join(HERE, "bookmark_rekey.json")
    mapping = accumulate(mapping, out, live_keys)
    json.dump(mapping, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(ANALYSIS, "bookmark_rekey_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("Keys mapped: %d\n" % len(mapping))
        for kind, k, why in report:
            fh.write("%s | %s | %s\n" % (kind, k, why))
    print("mapped %d keys; %d not mapped (see bookmark_rekey_report.txt)" % (len(mapping), len(report)))


if __name__ == "__main__":
    main()
