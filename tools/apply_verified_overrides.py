#!/usr/bin/env python3
"""Apply hand-verified time corrections (verified_overrides.json).

Each override names an entry by thread_key, gives the printed stamp as read from
the page image, and its supported or inferred zone, with the evidence. Optional fields include
body, header_fields, sender, reply_to, clear_reply_to, time_unresolved, and new_thread_key.
Rekeying updates reply references; unresolved quoted clocks keep their documented
date without inventing a normalized time. Run after anchor_copies.py and before
dedupe_same_instant.py.
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


def entry_label(entry):
    time = entry.get("time")
    when = "%s %s:%s" % (entry.get("date"), time[:2], time[2:]) if time else "%s time unresolved" % entry.get("date")
    return "%s · %s" % (when, entry.get("sender") or "")


def apply_body_replacements(content, replacements):
    header, separator, body = content.partition("----------")
    if not separator:
        raise ValueError("Cannot correct body without a header separator")
    for replacement in replacements:
        old, new = replacement["old"], replacement["new"]
        if body.count(old) == 1:
            body = body.replace(old, new, 1)
        elif old not in body and body.count(new) == 1:
            continue
        else:
            raise ValueError("Body correction does not match exactly once: %r" % old)
    return header + separator + body


def apply_header_fields(content, fields):
    header, separator, body = content.partition("----------")
    if not separator:
        raise ValueError("Cannot correct header without a body separator")
    for label, value in fields.items():
        if label not in ("To", "Cc"):
            raise ValueError("Unsupported header field: %s" % label)
        pattern = r"(?m)^" + label + r":[^\n]*(?:\n(?!\n)[^\n]*)*"
        matches = list(re.finditer(pattern, header))
        if len(matches) == 1:
            header = header[:matches[0].start()] + label + ": " + value + header[matches[0].end():]
        elif not matches and label == "To" and "\n\nCc:" in header:
            header = header.replace("\n\nCc:", "\n\nTo: " + value + "\n\nCc:", 1)
        else:
            raise ValueError("Cannot locate unique %s header" % label)
    return header + separator + body


def rekey_entry(entries, by_key, entry, new_key):
    old_key = entry.get("thread_key")
    if not new_key or new_key == old_key:
        return
    if new_key in by_key and by_key[new_key] is not entry:
        raise ValueError("Duplicate thread key: %s" % new_key)
    entry["thread_key"] = new_key
    by_key.pop(old_key, None)
    by_key[new_key] = entry
    for candidate in entries:
        if candidate.get("reply_to") == old_key:
            candidate["reply_to"] = new_key
            candidate["reply_to_label"] = entry_label(entry)
        for reply in candidate.get("replied_by") or []:
            key = reply.get("key") if isinstance(reply, dict) else reply
            if key == old_key and isinstance(reply, dict):
                reply["key"] = new_key


def refresh_relationship_labels(entries, changed_entries):
    by_key = {e.get("thread_key"): e for e in entries}
    for entry in entries:
        parent = by_key.get(entry.get("reply_to"))
        if parent is not None and id(parent) in changed_entries and "reply_to_label" in entry:
            entry["reply_to_label"] = entry_label(parent)
        for reply in entry.get("replied_by") or []:
            key = reply.get("key") if isinstance(reply, dict) else reply
            child = by_key.get(key)
            if child is not None and id(child) in changed_entries and isinstance(reply, dict):
                reply["label"] = entry_label(child)


def set_reply_relationship(by_key, entry, parent):
    parent_key = parent["thread_key"]
    old_parent_key = entry.get("reply_to")
    if old_parent_key != parent_key:
        old_parent = by_key.get(old_parent_key)
        if old_parent is not None:
            old_parent["replied_by"] = [
                r for r in (old_parent.get("replied_by") or [])
                if (r.get("key") if isinstance(r, dict) else r) != entry["thread_key"]
            ]
        entry["reply_to"] = parent_key
        entry["reply_to_label"] = entry_label(parent)
    entry["link_kind"] = "explicit (quoted inline)"
    parent.setdefault("replied_by", [])
    if not any((r.get("key") if isinstance(r, dict) else r) == entry["thread_key"]
               for r in parent["replied_by"]):
        parent["replied_by"].append({"key": entry["thread_key"], "label": entry_label(entry)})


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
        changed_entries = set()
        pending_replies = []
        for item in items:
            e = by_key.get(item["thread_key"])
            if e is None:
                e = next((by_key.get(key) for key in item.get("lookup_thread_keys", [])
                          if by_key.get(key) is not None), None)
            if e is None:
                print("override target not found:", item["thread_key"])
                continue
            previous_label = entry_label(e)
            previous_key = e.get("thread_key")
            previous_time = (e.get("date"), e.get("time"))
            if item.get("time_unresolved"):
                e["date"] = item.get("date", e.get("date"))
                e["time"] = None
                e["stamp"] = item["stamp"]
                e["stamp_status"] = "long"
                e["zone_assumed"] = "UNRESOLVED: " + item["evidence"]
                e["raw_date"] = item.get("raw_date") or "4:16 PM · time zone unresolved · %s" % (e.get("subject") or "")
                e["stamp_line"] = item.get("stamp_line") or item["stamp"] + " (time zone unresolved)"
            elif item.get("stamp"):
                p = o.printed(item["stamp"])
                if p is None:
                    print("cannot read stamp:", item["stamp"])
                    continue
                et = p.replace(tzinfo=ZoneInfo(item["zone"])).astimezone(ZoneInfo("America/New_York"))
                e["date"], e["time"] = et.strftime("%Y-%m-%d"), et.strftime("%H%M")
                e["stamp"] = item["stamp"]
                e["stamp_status"] = "long"
                certainty = item.get("certainty", "verified")
                if certainty == "inferred":
                    prefix = "inferred from the quoting client's presumed time zone: "
                elif certainty == "supported":
                    prefix = "supported from the page image and matching source copy: "
                else:
                    prefix = "verified from the page image: "
                e["zone_assumed"] = prefix + item["evidence"]
                e["raw_date"] = "%s:%s ET · %s" % (e["time"][:2], e["time"][2:], e.get("subject") or "")
                e["stamp_line"] = item.get("stamp_line") or "%s -> %s:%s ET (verified override)" % (item["stamp"], e["time"][:2], e["time"][2:])
            e["verified_override"] = item["evidence"]
            rekey_entry(entries, by_key, e, item.get("new_thread_key"))
            if item.get("thread_label"):
                e["thread_label"] = item["thread_label"]
            elif e.get("thread_key") != item["thread_key"]:
                e["thread_label"] = entry_label(e)
            hdr, sep, rest = (e.get("content") or "").partition("----------")
            if (sep and item.get("stamp") and not item.get("time_unresolved")
                    and not re.search(r"(?m)^(Sent|Date):", hdr)):
                # Restore a source stamp only when OCR omitted its header line.
                hdr = re.sub(r"(?m)^(Sent|Date):.*$", "", hdr).rstrip() + "\n\nSent: " + item["stamp"] + "\n\n"
                e["content"] = hdr + sep + rest
            if item.get("body") is not None:   # body text OCR lost, typed from the page image
                hdr = (e.get("content") or "").partition("----------")[0]
                e["content"] = hdr + "----------\n\n" + item["body"]
            if item.get("body_replacements"):
                e["content"] = apply_body_replacements(e.get("content") or "", item["body_replacements"])
            if item.get("header_fields"):
                e["content"] = apply_header_fields(e.get("content") or "", item["header_fields"])
            if item.get("sender"):
                e["sender"] = item["sender"]
                e["content"] = re.sub(r"(?m)^From:.*$", "From: " + item["sender"], e.get("content") or "", count=1)
                if e.get("thread_key") != item["thread_key"] and not item.get("thread_label"):
                    e["thread_label"] = entry_label(e)
            if item.get("sender_how"):
                e["sender_how"] = item["sender_how"]
            if item.get("clear_reply_to") and e.get("reply_to"):
                old_parent = by_key.get(e["reply_to"])
                if old_parent is not None:
                    old_parent["replied_by"] = [r for r in (old_parent.get("replied_by") or [])
                                                if (r.get("key") if isinstance(r, dict) else r) != e["thread_key"]]
                for key in ("reply_to", "reply_to_label", "link_kind"):
                    e.pop(key, None)
            if item.get("reply_to"):
                pending_replies.append((e, item["reply_to"], item.get("link_kind")))
            if item.get("link_kind"):
                e["link_kind"] = item["link_kind"]
            if entry_label(e) != previous_label or e.get("thread_key") != previous_key:
                changed_entries.add(id(e))
            print("verified:", name, e.get("idx"), previous_time, "->", (e["date"], e["time"]))
        for entry, parent_key, link_kind in pending_replies:
            parent = by_key.get(parent_key)
            if parent is None:
                raise ValueError("Override reply target not found: %s" % parent_key)
            set_reply_relationship(by_key, entry, parent)
            if link_kind:
                entry["link_kind"] = link_kind
        refresh_relationship_labels(entries, changed_entries)
        drop_backwards_inferred_links(entries)
        if isinstance(raw, dict) and "entries" in raw:
            raw["entries"] = entries
            json.dump(raw, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        else:
            json.dump(entries, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
