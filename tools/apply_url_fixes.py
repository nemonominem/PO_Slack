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


# Deterministic OCR confusions in addresses (each checked against the live site).
RULES = [
    (re.compile(r"\bh(?:i|ii|t)?t?tps?\s?[:.;]\s?(?:/{1,2}|[A-Za-z]/|\s)?\s?(?=\w)", re.I), "https://"),   # hittps:, https: //, https:/www, https:i/www, https. www
    (re.compile(r"(?<=https://)[iIlW]/(?=\w)"), ""),                                              # https://i/www, https://W/abc
    (re.compile(r"(?<=//)\s*w{2,4}\s?[-_.]+\s*(?=\w)", re.I), "www."),
    (re.compile(r"(?<=//)\s*ww(?:e|r)w\.", re.I), "www."),
    (re.compile(r"\bnim\.nih\.gov", re.I), "nlm.nih.gov"),
    (re.compile(r"\b(?:www\.)?(?:nebinim|ncbinlm|ncbLnlm|ncbi\.nimnih|nebi\.nlm|nebi\.nim|ncb\.nim)(?:\.nin|\.nih)?\.", re.I), "www.ncbi.nlm.nih."),
    (re.compile(r"\b(?:nebi|ncb)\b", re.I), "ncbi"),
    (re.compile(r"(?<=nih\.gov/)pme/", re.I), "pmc/"),
    (re.compile(r"\bbbe\.com", re.I), "bbc.com"),
    (re.compile(r"\bgiobaltimes\.cn/content/1178363\.shtm!?", re.I), "globaltimes.cn/content/1178363.shtml"),
    (re.compile(r"\bdocs\.(?:googie|gocgle)\.com", re.I), "docs.google.com"),
    (re.compile(r"\bvirologicaLorg", re.I), "virological.org"),
    (re.compile(r"tom-cotion", re.I), "tom-cotton"),
    (re.compile(r"deletion-in-the-spke-protein", re.I), "deletion-in-the-spike-protein"),
    (re.compile(r"\bscencemag\.org", re.I), "sciencemag.org"),
    (re.compile(r"\bbioriv\.org", re.I), "biorxiv.org"),
    (re.compile(r"(?<=https://)(?:vwww|wvew|wwws|wwwe|wvvw|waw)\.", re.I), "www."),
    (re.compile(r"(?<=https://)wwwn[ce]?\.cde\.gov", re.I), "wwwnc.cdc.gov"),
    (re.compile(r"(?<=https://)www\.(?:cde)\.gov", re.I), "www.cdc.gov"),
]


def normalize(text):
    """Apply the deterministic repairs to the address-looking parts of text."""
    def fix(m):
        u = m.group(0)
        for rx, rep in RULES:
            u = rx.sub(rep, u)
        return u
    return re.sub(r"(?i)\b(?:h\w{2,3}ps?\s?[:.;]\s?(?:/{1,2}|[a-z]/|\s)?\s?|www\.)\S+", fix, text)


def pattern(broken):
    # whitespace may be missing or extra; a hyphen or underscore at a line wrap may have become a space
    parts = [r"\s*" if c.isspace() else r"\s*-?\s*" if c == "-" else r"\s*_?\s*" if c == "_" else re.escape(c) for c in broken]
    return re.compile(r"\s*".join(p.strip() or p for p in parts) + r"(?![\w/-])")


def main():
    fixes = json.load(open(os.path.join(HERE, "url_fixes.json"), encoding="utf-8"))
    # longest first, so the full address wins over its shorter prefix
    fixes.sort(key=lambda f: -len(f["broken"]))
    pats = [(pattern(f["broken"]), f["correct"]) for f in fixes]
    total = 0
    for name in ("po-emails.json", "farrar-fauci.json", "part1.json", "sscp-drafts.json"):
        path = os.path.join(PB, name)
        data = json.load(open(path, encoding="utf-8"))
        ents = data["entries"] if isinstance(data, dict) else data
        n = 0
        for e in ents:
            for field in ("content",):
                c = e.get(field)
                if not c:
                    continue
                c0, c = c, normalize(c)
                for rx, good in pats:
                    c = rx.sub(lambda m: good, c)
                n += c != c0
                e[field] = c
        if n:
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False,
                      indent=2 if name in ("part1.json", "sscp-drafts.json") else 1)
        print("%s: %d entr(ies) changed" % (name, n))
        total += n
    return total


if __name__ == "__main__":
    main()
