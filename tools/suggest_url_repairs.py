#!/usr/bin/env python3
"""For each address scan_urls.py found broken, try mechanical repairs and keep the
first that is live. Usage: suggest_url_repairs.py SCAN.json OUT.json"""
import json, re, sys, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_urls import status

DOMAIN_FIX = [("cde.gov", "cdc.gov"), ("nrde.org", "nrdc.org"), ("semp.com", "scmp.com"),
              ("bioriv.org", "biorxiv.org"), ("biorsiv.org", "biorxiv.org"), ("bloralv.org", "biorxiv.org"),
              ("giobaltimes", "globaltimes"), ("gocgle", "google"), ("outiook", "outlook"),
              ("ncbinim", "ncbi.nlm"), ("washingtonexaminer", "washingtonexaminer"),
              ("virology.ws", "virology.ws"), ("jvi.asm", "jvi.asm"), ("cnn.com", "cnn.com"),
              ("waw.cnn", "www.cnn"), ("wwwne.cdc", "wwwnc.cdc"), ("wwwnce.cdc", "wwwnc.cdc"),
              ("wwwevirology", "www.virology"), ("wwwscmp", "www.scmp"), ("wwwdeonard", "www.leonard"),
              ("wwws.", "www."), ("wvew.", "www."), ("vwww.", "www."), ("wwwe.", "www.")]
def variants(u):
    base = u
    base = re.sub(r"^https?:\s*/{1,2}\s*", "https://", base)
    base = re.sub(r"^https://(?:i/|W/|/|I/)+", "https://", base)
    base = re.sub(r"^https://w{2,4}[ewvnrs]{0,2}\.?(?=[a-z0-9-]+\.[a-z])", "https://www.", base) if False else base
    outs = [base]
    b = base
    for a, c in DOMAIN_FIX:
        b = b.replace(a, c)
    outs.append(b)
    # www prefix glitches: wwwXYZ.domain -> www.domain
    b2 = re.sub(r"^https://(?:w|v)(?:w|v|a|e)(?:w|v|e)[a-z]{0,2}\.?(?=[a-z0-9-]+\.[a-z]{2,})", "https://www.", b)
    b2 = re.sub(r"^https://w{2,4}\.?([a-z]+\.[a-z]{2,}[a-z./]*)", r"https://www.\1", b2)
    outs.append(b2)
    outs.append(b2.replace("tom-cotion", "tom-cotton").replace("trall", "trail").replace("bioweapor", "bioweapon").replace("joumal", "journal").replace("detalls", "details").replace("artides", "articles").replace("artcles", "articles").replace("0ncow", "ncov"))
    seen = []
    for o in outs:
        if o not in seen:
            seen.append(o)
    return seen

def main(scan, out):
    items = json.load(open(scan))
    bad = [i for i in items if not str(i["status"]).startswith(("2", "3", "403"))]
    def work(i):
        i["tried"] = []
        for v in variants(i["url"]) + ([variants(i["url"])[-1] + i["next"]] if i["next"] else []):
            s = status(v)
            i["tried"].append([v, s])
            if str(s).startswith(("2", "3", "403")) and v != i["url"]:
                i["fixed"] = v
                break
        return i
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(work, bad))
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print("tried %d, fixed %d" % (len(res), sum(1 for r in res if "fixed" in r)))
    for r in res:
        if "fixed" in r:
            print("OK ", r["where"][0][1], r["url"][:70], "->", r["fixed"][:100])
main(sys.argv[1], sys.argv[2])
