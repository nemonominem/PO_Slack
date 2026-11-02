#!/usr/bin/env python3
"""Find web addresses in the OCR'd sources and test whether they are live.

Usage: scan_urls.py OUT.json   (writes one row per distinct address found)

For each address as printed (after the deterministic OCR repairs of
apply_url_fixes.normalize) it records: where it is, the next-line continuation
candidate (an address cut at a line wrap), and the HTTP status of each variant.
Status 200-399 = live; 403/429/999 = site blocks scripts (cannot tell);
404/DNS failure = broken. Used to find rows for url_fixes.json.
"""
import json, os, re, sys, urllib.request, urllib.error, socket
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_url_fixes import normalize, PB

SRC = ["part1.json", "sscp-drafts.json", "po-emails.json", "farrar-fauci.json"]
RE = re.compile(r"(?i)(?:h\w{2,3}ps?:?\s?:?\s?//|https?:\s+|www[.\-_]?\.?)\S*")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def status(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers=UA, method=method)
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 400, 404, 501):
                continue
            return e.code
        except Exception as e:
            if method == "GET":
                return "ERR:" + type(e).__name__
    return "ERR"


def main(out):
    rows = {}
    for f in SRC:
        d = json.load(open(os.path.join(PB, f), encoding="utf-8"))
        for e in (d["entries"] if isinstance(d, dict) else d):
            c = normalize(e.get("content") or "")
            for m in RE.finditer(c):
                raw = m.group(0)
                tail = c[m.end():m.end() + 80]
                nxt = ""
                if tail.startswith("\n"):
                    mm = re.match(r"\n(\S+)", tail)
                    nxt = mm.group(1) if mm else ""
                u = re.sub(r"[.,;:!?)\]>\"'’”]+$", "", raw)
                rows.setdefault(u, {"url": u, "where": [], "next": nxt})["where"].append([f, e.get("idx")])
    items = list(rows.values())

    def work(it):
        u = it["url"]
        full = u if u.startswith("http") else "https://" + u
        it["status"] = status(full)
        if it["next"] and not str(it["status"]).startswith(("2", "3")) :
            it["status_joined"] = status(full + it["next"])
        return it
    with ThreadPoolExecutor(16) as ex:
        items = list(ex.map(work, items))
    json.dump(items, open(out, "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(Counter(str(i["status"])[:3] for i in items))


if __name__ == "__main__":
    socket.setdefaulttimeout(15)
    main(sys.argv[1])
