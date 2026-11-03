#!/usr/bin/env python3
"""Write analysis/UNRESOLVED_LINKS.md from analysis/url_scan.json (made by scan_urls.py).

Settled   = repaired and the corrected address answers 200 (rows of url_fixes.json)
Likely    = address now reads sensibly but the site blocks scripts / is paywalled (403, 402, 406),
            or could not be reached from here (timeout): cannot confirm the page
Unknown   = still broken: cut off in the screenshot, or the page is gone, or a damaged slug
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
PB = os.path.join(HERE, "..", "page_based")

scan = json.load(open(os.path.join(AN, "url_scan.json"), encoding="utf-8"))
fixes = json.load(open(os.path.join(HERE, "url_fixes.json"), encoding="utf-8"))
ents = {}
for f in ("part1", "sscp-drafts", "po-emails", "farrar-fauci"):
    d = json.load(open(os.path.join(PB, f + ".json"), encoding="utf-8"))
    ents[f + ".json"] = {e["idx"]: e for e in d["entries"]}
PM = {f: json.load(open(os.path.join(PB, p), encoding="utf-8")) for f, p in
      (("part1.json", "part1_page_map.json"), ("sscp-drafts.json", "sscp_page_map.json"),
       ("po-emails.json", "po-emails_page_map.json"), ("farrar-fauci.json", "farrar-fauci_page_map.json"))}
PDF = {"part1.json": "slack-part1.pdf", "sscp-drafts.json": "sscp-drafts.pdf",
       "po-emails.json": "po-emails.pdf", "farrar-fauci.json": "farrar-fauci-comms.pdf"}
NAME = {"part1.json": "Slack Part 1", "sscp-drafts.json": "Manuscript drafts",
        "po-emails.json": "P.O. emails", "farrar-fauci.json": "Farrar-Fauci emails"}


def where(f, idx):
    e = ents[f][idx]
    key = str(idx) if f == "part1.json" else e.get("thread_key")
    p = PM[f].get(key)
    pg = "" if not p else (str(p["start"]) if p["start"] == p["end"] else "%d-%d" % (p["start"], p["end"]))
    who = e.get("sender") or ""
    return "%s · %s %s ET · %s · %s p.%s" % (NAME[f], e.get("date", ""), e.get("time") or "", who, PDF[f], pg)


def reason(it):
    u, st = it["url"], str(it["status"])
    tail = re.sub(r"^https?://", "", u)
    path = tail.split("/", 1)[1] if "/" in tail else ""
    if re.search(r"(/|-|=|\.[a-z]{1,3}|d/|^www|^docs|^twitter\.cor?|\.col?)$", tail) and len(path) < 40 or not path and not re.search(r"\.[a-z]{2,}$", tail.split("/")[0]):
        return "cut off in the screenshot (the rest of the address is not in the image)"
    if st.startswith("ERR:Timeout"):
        return "site did not answer from here (could not check)"
    if st.startswith("ERR"):
        return "domain does not resolve: OCR error in the domain, or the site is gone"
    if st.startswith("404"):
        return "page not found: slug damaged by OCR, or the page has been removed"
    return "answered %s" % st[:3]


rows = {"S": [], "L": [], "U": []}
for it in scan:
    st = str(it["status"])
    f, idx = it["where"][0]
    if st.startswith(("2", "3")):
        continue
    r = reason(it)
    cut = r.startswith("cut off")
    (rows["L"] if (st.startswith(("403", "402", "406")) or "could not check" in r) and not cut else rows["U"]).append((it, r))

n_live = sum(1 for it in scan if str(it["status"]).startswith(("2", "3")))
n_block = sum(1 for it in scan if str(it["status"]).startswith("403"))
out = []
out.append("# Unresolved links: analysis for the human reviewer\n")
out.append("Source: `tools/scan_urls.py` (every web address in the OCR'd sources, tested live), "
           "`tools/url_fixes.json` (%d repair rows), `tools/apply_url_fixes.py` (applies them), "
           "`analysis/url_scan.json` (the scan this report reads). Slack Part 2 is native text, not OCR, and was not repaired.\n" % len(fixes))
out.append("## Counts\n")
out.append("| Status | Meaning | Addresses |\n|---|---|---|")
out.append("| Settled | repaired or already clean; the address answers 200/3xx | %d |" % n_live)
out.append("| Likely | address looks right but the site blocks scripts (403), is paywalled (402/406) or did not answer from here: page not confirmed | %d |" % len(rows["L"]))
out.append("| Unknown | still broken | %d |" % len(rows["U"]))
out.append("")
out.append("Counts are distinct addresses as they read after repair. About 110 addresses were repaired in this pass (scheme, `www`, domain and slug typos, line-wrap splits).\n")
out.append("## How a link gets repaired\n")
out.append("1. Deterministic OCR confusions (`apply_url_fixes.RULES`): `hittps:`, `https: //`, `wwew`, `nim.nih`, `nebi`, `bbe.com`, `cde.gov`, ...\n"
           "2. A hand-checked row in `url_fixes.json` (broken form -> correct address, found by web search). Whitespace and a lost hyphen/underscore inside the broken form are tolerated.\n"
           "3. The app links any `https://` or `www.` address it finds, in the Content and Thread panels.\n"
           "To add a repair: append a row to `url_fixes.json`, run `python3 tools/apply_url_fixes.py`, then rescan.\n")
out.append("## Likely (page cannot be confirmed from here, address looks right)\n")
out.append("| # | Address as it reads now | Where | Why |\n|---|---|---|---|")
for i, (it, r) in enumerate(rows["L"], 1):
    out.append("| L%d | `%s` | %s | %s (%s) |" % (i, it["url"][:100], where(*it["where"][0]), r, str(it["status"])[:12]))
out.append("\nNothing to do unless you want them opened by hand once.\n")
out.append("## Unknown (still broken)\n")
groups = {}
for it, r in rows["U"]:
    groups.setdefault(r.split(" (")[0], []).append(it)
n = 0
for r, its in sorted(groups.items(), key=lambda x: -len(x[1])):
    out.append("### %s: %d\n" % (r[0].upper() + r[1:], len(its)))
    out.append("| # | Address as it reads now | Where |\n|---|---|---|")
    for it in its:
        n += 1
        out.append("| U%d | `%s` | %s |" % (n, it["url"][:110], where(*it["where"][0])))
    out.append("")
out.append("## What would settle each group\n")
out.append("- **Cut off in the screenshot:** the printed address ends mid-word. Only the page image can tell whether the full address is visible further on; the Slack preview card under the link shows the page title, so a web search on that title finds the page. Reviewer decision: do these by hand, or leave unlinked.\n"
           "- **Page not found:** try the address in the Wayback Machine (`web.archive.org/web/2020/<address>`); a damaged slug usually shows as the one word that differs from the title under the link.\n"
           "- **Domain does not resolve:** compare with the domain named in the preview card (it is printed on the line below the link and usually OCRs better).\n"
           "- **Could not check:** retry later or open in a browser.\n")
open(os.path.join(AN, "UNRESOLVED_LINKS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("Unknown %d, Likely %d, live %d" % (len(rows["U"]), len(rows["L"]), n_live))
