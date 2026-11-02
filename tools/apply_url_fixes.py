#!/usr/bin/env python3
"""Repair web addresses the OCR broke (a space or line break inside, a lost hyphen).

Reads tools/url_fixes.json ({"broken": text as it reads in the data, "correct": the
real address, found by web search}) and rewrites page_based/po-emails.json and
farrar-fauci.json in place. Whitespace in "broken" is matched loosely (any run of
whitespace, or none). Idempotent: run it after every rebuild (it changes only
entries that still hold a broken form). Add a row for each broken link you find.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PB = os.path.join(HERE, "..", "page_based")


def pattern(broken):
    parts = [re.escape(c) if not c.isspace() else r"\s*" for c in broken]
    return re.compile("".join(parts) + r"(?![\w/])")


def main():
    fixes = json.load(open(os.path.join(HERE, "url_fixes.json"), encoding="utf-8"))
    # longest first, so the full address wins over its shorter prefix
    fixes.sort(key=lambda f: -len(f["broken"]))
    pats = [(pattern(f["broken"]), f["correct"]) for f in fixes]
    total = 0
    for name in ("po-emails.json", "farrar-fauci.json"):
        path = os.path.join(PB, name)
        data = json.load(open(path, encoding="utf-8"))
        ents = data["entries"] if isinstance(data, dict) else data
        n = 0
        for e in ents:
            for field in ("content",):
                c = e.get(field)
                if not c:
                    continue
                for rx, good in pats:
                    c, k = rx.subn(lambda m: good, c)
                    n += k
                e[field] = c
        if n:
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("%s: %d address(es) repaired" % (name, n))
        total += n
    return total


if __name__ == "__main__":
    main()
