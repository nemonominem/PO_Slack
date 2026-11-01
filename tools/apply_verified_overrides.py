#!/usr/bin/env python3
"""Apply hand-verified time corrections (verified_overrides.json).

Each override names an entry by thread_key, gives the printed stamp as read from
the page image, and the zone it is on, with the evidence. Optional fields: body (text
the OCR lost), sender (corrected label), reply_to (thread_key of the message it answers). Used only for cases
settled by the page itself (for example OCR dropped a time, and the page or the
message text fixes the zone). The thread_key is left unchanged: it is an
identifier, and bookmarks and chapter links use it. Run after anchor_copies.py
and before dedupe_same_instant.py.
"""
import json
import os
import re
from zoneinfo import ZoneInfo

import owner_zone_check as o

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "page_based")
OVERRIDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verified_overrides.json")


def _instant(e):
    if not e.get("date") or not e.get("time"):
        return None
    return e["date"] + e["time"]


def drop_backwards_inferred_links(entries):
    """A link the parser only inferred ('same conversation') is dropped when the
    corrected times put the reply before its parent. Explicit links, which come
    from the text itself, are never touched."""
    by = {e.get("thread_key"): e for e in entries}
    for e in entries:
        parent = by.get(e.get("reply_to"))
        if parent is None or not str(e.get("link_kind") or "").startswith("inferred"):
            continue
        te, tp = _instant(e), _instant(parent)
        if te and tp and te < tp:
            print("dropped backwards inferred link: idx %s no longer replies to idx %s" % (e.get("idx"), parent.get("idx")))
            for k in ("reply_to", "reply_to_label", "link_kind"):
                e.pop(k, None)
            parent["replied_by"] = [r for r in (parent.get("replied_by") or [])
                                    if (r.get("key") if isinstance(r, dict) else r) != e.get("thread_key")]


def main():
    ov = json.load(open(OVERRIDES, encoding="utf-8"))
    by_file = {}
    for item in ov:
        by_file.setdefault(item["release"], []).append(item)
    for name, items in by_file.items():
        path = os.path.join(HERE, name)
        raw = json.load(open(path, encoding="utf-8"))
        entries = raw["entries"] if isinstance(raw, dict) and "entries" in raw else raw
        by_key = {e.get("thread_key"): e for e in entries}
        for item in items:
            e = by_key.get(item["thread_key"])
            if e is None:
                print("override target not found:", item["thread_key"])
                continue
            p = o.printed(item["stamp"])
            if p is None:
                print("cannot read stamp:", item["stamp"])
                continue
            et = p.replace(tzinfo=ZoneInfo(item["zone"])).astimezone(ZoneInfo("America/New_York"))
            old = (e.get("date"), e.get("time"))
            e["date"], e["time"] = et.strftime("%Y-%m-%d"), et.strftime("%H%M")
            e["stamp"] = item["stamp"]
            e["stamp_status"] = "long"
            e["zone_assumed"] = "verified from the page image: " + item["evidence"][:140]
            e["raw_date"] = "%s:%s ET · %s" % (e["time"][:2], e["time"][2:], e.get("subject") or "")
            e["stamp_line"] = "%s -> %s:%s ET (verified override)" % (item["stamp"], e["time"][:2], e["time"][2:])
            e["verified_override"] = item["evidence"]
            hdr, sep, rest = (e.get("content") or "").partition("----------")
            if sep:   # the header's Sent/Date line was cut by OCR: write the stamp read from the page
                hdr = re.sub(r"(?m)^(Sent|Date):.*$", "", hdr).rstrip() + "\n\nSent: " + item["stamp"] + "\n\n"
                e["content"] = hdr + sep + rest
            if item.get("body") is not None:   # body text OCR lost, typed from the page image
                hdr = (e.get("content") or "").partition("----------")[0]
                e["content"] = hdr + "----------\n\n" + item["body"]
            if item.get("sender"):
                e["sender"] = item["sender"]
                e["content"] = re.sub(r"(?m)^From:.*$", "From: " + item["sender"], e.get("content") or "", count=1)
            if item.get("reply_to"):
                parent = by_key.get(item["reply_to"])
                if parent is not None:
                    old = by_key.get(e.get("reply_to"))    # leave the old parent's reply list
                    if old is not None:
                        old["replied_by"] = [r for r in (old.get("replied_by") or [])
                                             if (r.get("key") if isinstance(r, dict) else r) != e["thread_key"]]
                    e["reply_to"] = parent["thread_key"]
                    e["reply_to_label"] = "%s %s:%s · %s" % (parent["date"], parent["time"][:2], parent["time"][2:], parent.get("sender") or "")
                    e["link_kind"] = "explicit (quoted inline)"
                    parent.setdefault("replied_by", [])
                    if not any((r.get("key") if isinstance(r, dict) else r) == e["thread_key"] for r in parent["replied_by"]):
                        parent["replied_by"].append({"key": e["thread_key"], "label": "%s %s:%s · %s" % (e["date"], e["time"][:2], e["time"][2:], e.get("sender") or "")})
            print("verified:", name, e.get("idx"), old, "->", (e["date"], e["time"]))
        drop_backwards_inferred_links(entries)
        if isinstance(raw, dict) and "entries" in raw:
            raw["entries"] = entries
            json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        else:
            json.dump(entries, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
