"""Human-readable references for email entries: PDF pages, the date/time as printed
in the header, sender and subject. The entry numbers (PO n / FF n) are the `idx` stored in
the JSON files and are only a lookup key; readers should use the pages and the
printed header.

    python3 entry_ref.py PO:7 FF:19 FF:134        # markdown table rows
"""
import json, os, sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
FILES = {"PO": ("po-emails.json", "po-emails_page_map.json", "po-emails.pdf"),
         "FF": ("farrar-fauci.json", "farrar-fauci_page_map.json", "farrar-fauci-comms.pdf")}


def load(rel):
    data, pmap, pdf = FILES[rel]
    d = json.load(open(os.path.join(HERE, data), encoding="utf-8"))
    return (d if isinstance(d, list) else d["entries"]), json.load(open(os.path.join(HERE, pmap), encoding="utf-8")), pdf


def ref(rel, i, cache={}):
    if rel not in cache:
        cache[rel] = load(rel)
    E, M, pdf = cache[rel]
    e = next(x for x in E if x.get("idx") == i)
    pg = M.get(e.get("thread_key"))
    pages = "" if not pg else ("p.%d" % pg["start"] if pg["start"] == pg["end"] else "pp.%d-%d" % (pg["start"], pg["end"]))
    printed = (e.get("stamp") or "").strip() or "(no date or time printed or recovered)"
    return {"pdf": pdf, "pages": pages or "?", "printed": printed,
            "sender": (e.get("sender") or "").strip() or "(unknown sender)",
            "subject": (e.get("subject") or "").strip() or "(no subject)"}


if __name__ == "__main__":
    for a in sys.argv[1:]:
        rel, n = a.split(":")
        r = ref(rel, int(n))
        print("| %s %s | %s %s | %s | %s | %s |" % (rel, n, r["pdf"], r["pages"], r["printed"], r["sender"], r["subject"]))
