#!/usr/bin/env python3
"""
Build the P.O. "guide" dataset: the index of which released document backs
which claim in Gilles Demaneuf's "Proximal Origin - A Tragicomedy of our
Times" (Summary + Part 1 + Part 2).

Why this exists
---------------
The P.O. article is evidence-first: almost every assertion sits on a quote
from a released document, and the article says which one, on which page, on
what date. That citation apparatus *is* an index into the FOI'd record, and
it is what is missing when the Slack messages are read on their own -- the
Slack channel is the tip of the story; the emails, drafts and transcripts
are the body of evidence.

So we parse the three parts of the article and emit, per dated section: the
section heading, every piece of evidence cited in it (document, page, date),
and the public Drive URL for that document when the article footnotes one.

Media is inlined in the article markdown as base64 (the .md files are
87 MB / 115 MB), so every line longer than MAX_LINE is dropped: no caption,
heading or footnote is anywhere near that size, but every base64 image blob
is.

Emits:
  po_guide.json  -- machine-readable guide (consumed by the app)
  SOURCES.md     -- the same inventory as a human-readable provenance table

Usage:  python3 build_po_guide.py [--article-dir DIR]
"""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARTICLE_DIR = ("/Users/gillesdemaneuf/Work/Edition/medium_to_md/"
                       "examples/proximal_origin")

MAX_LINE = 400          # base64 image blobs are the only very long lines

PARTS = [
    ("summary", "summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506.md",
     "Summary", "https://gillesdemaneuf.medium.com/summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506"),
    ("p1", "full-text-proximal-origin-a-tragicomedy-of-our-times-draft-p1-626c72cb05b1.md",
     "Part 1", "https://medium.com/p/626c72cb05b1"),
    ("p2", "full-text-proximal-origin-a-tragicomedy-of-our-times-draft-p2-39b90684bf01.md",
     "Part 2", "https://medium.com/p/39b90684bf01"),
]

RE_HEADING = re.compile(r"^(#{2,4})\s+(.*)$")
RE_SECTION_NO = re.compile(r"^(\d{1,2})\.(\d{1,2})\s+(.*)$")
RE_TOP_NO = re.compile(r"^(\d{1,2})\.\s+(.*)$")
RE_CAPTION = re.compile(r"^>\s*_(.+?)_\s*$")
RE_INLINE_SRC = re.compile(r"source:\s*(.+)$", re.I)
RE_FOOTNOTE_DEF = re.compile(r"^\[\^([0-9A-Za-z_]+)\]:\s*(\S+)\s*$")
RE_FOOTNOTE_REF = re.compile(r"\[\^([0-9A-Za-z_]+)\](?!:)")
RE_DOC = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.\-]*\.(?:pdf|docx|xlsx|txt|csv|json))", re.I)
# a document name with its footnote marker written right after it
RE_DOC_REF = re.compile(
    r"([A-Za-z0-9][A-Za-z0-9_.\-]*\.(?:pdf|docx|xlsx|txt|csv|json))\s*,?\s*\[\^([0-9A-Za-z_]+)\]", re.I)
RE_PAGE = re.compile(
    r"\bpp?\.\s*([0-9]+(?:\s*[–\-—]\s*[0-9]+)?(?:\s*,\s*[0-9]+(?:\s*[–\-—]\s*[0-9]+)?)*)"
    r"(?!\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b)", re.I)
RE_DRIVE_FILE = re.compile(r"drive\.google\.com/file/d/([A-Za-z0-9_\-]+)")
RE_DRIVE_FOLDER = re.compile(r"drive\.google\.com/drive/folders/([A-Za-z0-9_\-]+)")

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
RE_DATE = re.compile(
    r"\b(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+(20\d\d)\b", re.I)
RE_YEAR_ONLY = re.compile(r"\b(20\d\d)\b")
# a day and month with no year: "31 Jan", "1 Feb" -- the article's usual form
RE_MONTH_DAY = re.compile(
    r"\b(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b", re.I)
# a Slack message quoted with its author and time: "Robert Garry, 23 Feb 2020, 11:58 pm UK"
RE_SLACK_ATTRIB = re.compile(
    r"^[A-Z][a-z]+\s+[A-Z][A-Za-z']+,\s*\d{1,2}\s+[A-Z][a-z]{2,8}\s+20\d\d", re.M)

DOC_CLASSES = [
    (re.compile(r"Proximal_Origin_Slack", re.I), "slack"),
    (re.compile(r"Proximal_Origin_Emails", re.I), "email"),
    (re.compile(r"farrar-fauci-comms", re.I), "email"),
    (re.compile(r"SSCP-Drafts-of-Proximal-Origin|COMBINED-SSCP", re.I), "draft"),
    (re.compile(r"Baric-Emails", re.I), "email"),
    (re.compile(r"Transcript", re.I), "transcript"),
    (re.compile(r"UTMB|LeDuc", re.I), "email"),
    (re.compile(r"USRTK|US-CDK|US-CIC", re.I), "email"),
    (re.compile(r"OSU", re.I), "email"),
    (re.compile(r"Nature|NatMed|manuscript|virological|draft", re.I), "document"),
]

LOCAL_DOCS = {
    "Proximal_Origin_Slack.pdf": ("po-slack", "slack-part1.pdf + slack-part2.pdf"),
    "Proximal_Origin_Emails.pdf": ("po-emails", "po-emails.pdf"),
    "farrar-fauci-comms-full.pdf": ("farrar-fauci", "farrar-fauci-comms.pdf"),
    "farrar-fauci-comms.pdf": ("farrar-fauci", "farrar-fauci-comms.pdf"),
    "SSCP-Drafts-of-Proximal-Origin.pdf": ("sscp", "sscp-drafts.pdf"),
}


def classify(doc):
    for rx, kind in DOC_CLASSES:
        if rx.search(doc):
            return kind
    return "other"


def norm_pages(pages):
    out = []
    for chunk in re.split(r"\s*,\s*", pages):
        c = re.sub(r"\s*[–—]\s*", "-", chunk.strip())
        c = re.sub(r"\s+", "", c)
        if c:
            out.append(c)
    return out


def parse_date(text):
    """Resolve a date the way the article writes them.

    Captions and headings often give a day and month with no year
    ("31 Jan 10:32 pm EST"), so the year is carried forward from the last
    full date seen. The piece is a Jan-Jul 2020 narrative, so 2020 is the
    starting assumption and it is corrected the moment a caption does carry
    a year. parse_date is called in document order, so the carry-forward
    follows the story.
    """
    m = RE_DATE.search(text)
    if m:
        parse_date.year = int(m.group(3))
        return "%04d-%02d-%02d" % (int(m.group(3)), MONTHS[m.group(2)[:3].lower()],
                                   int(m.group(1)))
    md = RE_MONTH_DAY.search(text)
    if md:
        return "%04d-%02d-%02d" % (parse_date.year, MONTHS[md.group(2)[:3].lower()],
                                   int(md.group(1)))
    y = RE_YEAR_ONLY.search(text)
    return ("%d-01-01" % int(y.group(1))) if y else None


parse_date.year = 2020


def first_url(text):
    m = RE_DRIVE_FILE.search(text) or RE_DRIVE_FOLDER.search(text)
    if m:
        return m.group(0)
    m = re.search(r"https?://\S+", text)
    return m.group(0) if m else None


def classify_caption(raw):
    """A caption with no filename is still evidence -- usually a Slack message
    quoted as 'Robert Garry, 23 Feb 2020, 11:58 pm UK', a tweet, or a link.
    Classify it rather than dropping it: the guide's promise is that every one
    of the article's citations is accounted for, resolved or not."""
    if re.search(r"slack", raw, re.I):
        return "slack"
    if RE_SLACK_ATTRIB.search(raw):
        return "slack"
    if re.search(r"\btweet|facebook|linkedin|bluesky", raw, re.I):
        return "social"
    if re.search(r"^\s*https?://", raw) or "bit.ly" in raw:
        return "link"
    if re.search(r"WSJ|Post\b|Guardian|NYT|Times\b|CNN|Reuters|CGTN|Vanity Fair|Atlantic",
                 raw, re.I):
        return "press"
    return "other"


def make_evidence(raw, part, refs=()):
    doc_m = RE_DOC.search(raw)
    doc = doc_m.group(1) if doc_m else None
    page_m = RE_PAGE.search(raw)
    return OrderedDict([
        ("doc", doc),
        ("kind", classify(doc) if doc else classify_caption(raw)),
        ("pages", norm_pages(page_m.group(1)) if (page_m and doc) else []),
        ("date", parse_date(raw)), ("url", first_url(raw)),
        ("source_part", part), ("raw", raw.strip()), ("_refs", list(refs)),
    ])


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line) <= MAX_LINE:
                yield line


def new_section(part_id, number, title, heading):
    dm = RE_DATE.search(heading)
    return OrderedDict([
        ("id", "%s-%s" % (part_id, number) if number else "%s-preamble" % part_id),
        ("part", part_id), ("number", number), ("title", title),
        ("heading", heading), ("date", parse_date(heading)),
        ("date_raw", dm.group(0) if dm else None), ("evidence", []),
    ])


def parse_part(part_id, path):
    sections, evidence, footnote_urls = [], [], {}
    cur = [None]

    def ensure():
        if cur[0] is None:
            cur[0] = new_section(part_id, None, "(preamble)", "(preamble)")
            sections.append(cur[0])
        return cur[0]

    def add(raw, refs=()):
        ev = make_evidence(raw, part_id, refs)
        ensure()["evidence"].append(ev)
        evidence.append(ev)

    lines = []
    for line in read_lines(path):
        lines.append(line)
        fm = RE_FOOTNOTE_DEF.match(line)
        if fm:
            footnote_urls[fm.group(1)] = fm.group(2)
            continue
        hm = RE_HEADING.match(line)
        if hm:
            level, text = len(hm.group(1)), hm.group(2).strip()
            sm, tm = RE_SECTION_NO.match(text), RE_TOP_NO.match(text)
            if sm and level >= 3:
                cur[0] = new_section(part_id, "%s.%s" % (sm.group(1), sm.group(2)),
                                     sm.group(3).strip(), text)
                sections.append(cur[0])
            elif tm and level <= 3:
                cur[0] = new_section(part_id, tm.group(1), tm.group(2).strip(), text)
                sections.append(cur[0])
            else:
                ensure()   # "Insight:", "Sideline:", appendices stay inside
            continue
        cm = RE_CAPTION.match(line)
        if cm:
            add(cm.group(1))
            continue
        im = RE_INLINE_SRC.search(line)
        if im:
            # markers adjacent to a filename on this very line, nothing looser
            add(im.group(1), [m.group(2) for m in RE_DOC_REF.finditer(line)])
    return sections, evidence, footnote_urls, lines


def build_doc_urls(lines, footnote_urls):
    """Map a cited document to its public Drive file.

    Only a marker written immediately after the filename counts, e.g.

        > '...' source: farrar-fauci-comms-full.pdf[^166], p.112, 2 Feb 2020
        > _Baric-TI-Transcript.pdf[^47], p.30-32_

    That adjacency is what proves the link belongs to that document. Two
    earlier versions were wrong: matching on "a marker seen in the preceding
    lines", and then on "the first marker anywhere on the line". The article
    footnotes many things per page, so neither proximity nor first-wins means
    anything -- both attached the same few Drive ids to unrelated documents.
    A document with no adjacent marker gets no link, which is honest: it is
    listed as cited-but-not-linked rather than pointed at the wrong PDF.
    """
    mapping = {}
    for line in lines:
        for m in RE_DOC_REF.finditer(line):
            url = footnote_urls.get(m.group(2))
            if url and RE_DRIVE_FILE.search(url):
                mapping.setdefault(m.group(1), url)
    return mapping


def attach_urls(sections, doc_urls, footnote_urls):
    """Give each citation the Drive file proven to be its own.

    Two proven sources, in order: the marker on the citation's own line
    (`... farrar-fauci-comms-full.pdf[^166] ...`), then the document-level
    map built from every such line in the article."""
    for sec in sections:
        for ev in sec["evidence"]:
            refs = ev.pop("_refs", [])
            if ev["url"]:
                continue
            for fid in refs:
                url = footnote_urls.get(fid)
                if url and RE_DRIVE_FILE.search(url):
                    ev["url"] = url
                    break
            if not ev["url"] and ev["doc"]:
                ev["url"] = doc_urls.get(ev["doc"])


def write_sources_md(guide, path):
    t, L, a = guide["totals"], [], None
    a = L.append
    a("# Source inventory — P.O. Slack")
    a("")
    a("Auto-generated by `build_po_guide.py` from the three parts of")
    a("[*%s*](%s) by Gilles Demaneuf." % (guide["title"], guide["article_url"]))
    a("")
    a("Every released document the article cites, how often, and whether we hold it")
    a("locally. **%d** dated sections, **%d** evidence citations, **%d** distinct"
      % (t["sections"], t["citations"], t["documents"]))
    a("documents, **%d** public Drive links." % t["drive_links"])
    a("")
    a("## Held locally (ingested into the app)")
    a("")
    a("| Source id | Local file | Cited as | Citations |")
    a("|---|---|---|---|")
    for r in guide["documents"].values():
        if r["local"]:
            a("| `%s` | `%s` | `%s` | %d |" % (r["local"], r["local_file"], r["doc"], r["cites"]))
    a("")
    a("## Cited but not yet ingested")
    a("")
    a("TODO — the P.O. piece also leans on these; candidates for the next ingestion")
    a("pass (see STATUS.md).")
    a("")
    a("| Kind | Document | Citations | Pages cited | Date range | Link |")
    a("|---|---|---|---|---|---|")
    for r in guide["documents"].values():
        if r["local"]:
            continue
        pages = ", ".join(r["pages_cited"][:8])
        if len(r["pages_cited"]) > 8:
            pages += ", ... (%d)" % len(r["pages_cited"])
        d = r["dates"]
        dr = "%s -> %s" % (d[0], d[-1]) if d else "-"
        link = r["urls"][0] if r["urls"] else ""
        a("| %s | `%s` | %d | %s | %s | %s |"
          % (r["kind"], r["doc"], r["cites"], pages or "-", dr,
             "[link](%s)" % link if link else "-"))
    a("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article-dir", default=DEFAULT_ARTICLE_DIR)
    args = ap.parse_args()

    all_sections, all_evidence, footnotes, all_lines = [], [], {}, []
    parts_meta, missing = [], []
    for pid, fname, label, url in PARTS:
        path = os.path.join(args.article_dir, fname)
        if not os.path.exists(path):
            missing.append(path)
            continue
        secs, evs, fns, lines = parse_part(pid, path)
        all_sections.extend(secs)
        all_evidence.extend(evs)
        footnotes.update(fns)
        all_lines.extend(lines)
        parts_meta.append({"id": pid, "label": label, "url": url, "file": fname,
                           "sections": len(secs), "evidence": len(evs)})
        print("%-8s %4d sections, %4d evidence citations" % (label, len(secs), len(evs)))

    if missing:
        print("WARNING: missing article files:\n  " + "\n  ".join(missing), file=sys.stderr)

    doc_urls = build_doc_urls(all_lines, footnotes)
    attach_urls(all_sections, doc_urls, footnotes)

    docs = {}
    undoc = {"cites": 0, "by_kind": {}}
    for ev in all_evidence:
        if not ev["doc"]:
            undoc["cites"] += 1
            undoc["by_kind"][ev["kind"]] = undoc["by_kind"].get(ev["kind"], 0) + 1
            continue
        r = docs.setdefault(ev["doc"], OrderedDict([
            ("doc", ev["doc"]), ("kind", ev["kind"]), ("cites", 0),
            ("pages_cited", []), ("dates", []), ("urls", []), ("parts", []),
            ("local", LOCAL_DOCS.get(ev["doc"], (None, None))[0]),
            ("local_file", LOCAL_DOCS.get(ev["doc"], (None, None))[1])]))
        r["cites"] += 1
        r["pages_cited"].extend(ev["pages"])
        if ev["date"]:
            r["dates"].append(ev["date"])
        if ev["url"]:
            r["urls"].append(ev["url"])
        if ev["source_part"] not in r["parts"]:
            r["parts"].append(ev["source_part"])
    for r in docs.values():
        r["pages_cited"] = sorted(set(r["pages_cited"]), key=lambda p: int(p.split("-")[0]))
        r["dates"] = sorted(set(r["dates"]))
        r["urls"] = sorted(set(r["urls"]))
    docs = OrderedDict(sorted(docs.items(), key=lambda kv: -kv[1]["cites"]))

    guide = OrderedDict([
        ("title", "Proximal Origin — A Tragicomedy of our Times"),
        ("author", "Gilles Demaneuf"),
        ("article_url", PARTS[0][3]),
        ("parts", parts_meta),
        ("generated_from", args.article_dir),
        ("sections", all_sections),
        ("documents", docs),
        ("citations_without_document", undoc),
        ("totals", OrderedDict([
            ("sections", len(all_sections)),
            ("citations", len(all_evidence)),
            ("documents", len(docs)),
            ("slack_citations", sum(1 for e in all_evidence if e["kind"] == "slack")),
            ("drive_links", len({u for r in docs.values() for u in r["urls"]}))])),
    ])

    out_json = os.path.join(HERE, "po_guide.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(guide, f, indent=1, ensure_ascii=False)
    t = guide["totals"]
    print("\nWrote %s" % out_json)
    print("  %d sections, %d citations, %d distinct documents, %d drive links"
          % (t["sections"], t["citations"], t["documents"], t["drive_links"]))
    write_sources_md(guide, os.path.join(HERE, "SOURCES.md"))
    print("  Wrote SOURCES.md")


if __name__ == "__main__":
    main()
