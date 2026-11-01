#!/usr/bin/env python3
"""Cross-release quote check (item A8 of the old reviewer list).

A quoted message cannot be later than the message that quotes it, even when the two
sit in different releases. For each entry X, look for the body of every entry Y of
the OTHER release inside X's text, away from X's own start: then Y is quoted by X, and
Y's time must not be later than X's. Reads the working-tree JSON, changes nothing,
writes analysis/cross_release_check.csv.
"""
import csv
import json
import os
import re

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PB, AN = os.path.join(HERE, "page_based"), os.path.join(HERE, "analysis")


def load(name):
    d = json.load(open(os.path.join(PB, name + ".json"), encoding="utf-8"))
    return d["entries"] if isinstance(d, dict) else d


def body(e):
    c = e.get("content") or ""
    c = c.split("----------", 1)[1] if "----------" in c else c
    return re.sub(r"[^a-z0-9]", "", c.lower())


SIGNATURE = re.compile(r"universityofsydney|wellcomeexists|disclaimer|nationalinstitute|professor|associateprofessor")


def inst(e):
    return (e["date"], e["time"]) if e.get("date") and e.get("time") else None


def main():
    rel = {"po-emails": load("po-emails"), "farrar-fauci": load("farrar-fauci")}
    rows = []
    n_pairs = 0
    for a, b in (("po-emails", "farrar-fauci"), ("farrar-fauci", "po-emails")):
        bodies = [(y, body(y)[:70]) for y in rel[b] if len(body(y)) >= 150 and inst(y) and not SIGNATURE.search(body(y)[:150])]
        common = {}
        for _, k in bodies:
            common[k] = common.get(k, 0) + 1
        bodies = [(y, k) for y, k in bodies if common[k] < 5]   # signatures and disclaimers repeat
        for x in rel[a]:
            bx = body(x)
            if not inst(x):
                continue
            for y, key in bodies:
                at = bx.find(key)
                if at < 150:     # not found, or it is X's own text
                    continue
                n_pairs += 1
                if inst(y) > inst(x):
                    rows.append([a, x["idx"], x.get("sender"), x["stamp"], "%s %s" % inst(x),
                                 b, y["idx"], y.get("sender"), y["stamp"], "%s %s" % inst(y)])
    with open(os.path.join(AN, "cross_release_check.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quoter_release", "quoter_idx", "quoter_sender", "quoter_stamp", "quoter_ET",
                    "quoted_release", "quoted_idx", "quoted_sender", "quoted_stamp", "quoted_ET"])
        w.writerows(rows)
    print("cross-release quote pairs found: %d; quoted later than its quoter: %d" % (n_pairs, len(rows)))
    for r in rows:
        print("  %s %s %s (%s) quotes %s %s %s (%s)" % (r[0][:2], r[1], r[3][:28], r[4], r[5][:2], r[6], r[8][:28], r[9]))


if __name__ == "__main__":
    main()
