# Mixed-source standards — P.O. Slack

How this app models documents from several releases — Slack messages, FOI'd
emails, manuscript drafts — so they live on **one timeline** and can be read in
order against each other.

Adapted from `Fauci_Diary/EMAILS.md`, which solved the same problem for a
different archive. Read this before adding a release or a new kind of source.

---

## 1. One document per entry

An entry is a single unit of authorship at a single instant. Never paste a
whole thread into one entry.

| kind | meaning | in the timeline | card badge |
|---|---|---|---|
| `slack` | an authored message in the channel | yes | 💬 Slack message |
| `email` | one email: one author, one timestamp | yes | ✉ Email |
| `draft` | one dated version of the manuscript | yes | 📝 Manuscript draft |
| `attachment` | a file or document carried by a message | yes | 📎 Attachment |
| `document` | a released document with no single authoring instant | yes | 📄 Document |
| `note` | **publisher material about a release, not a document in it** | yes | ℹ Release note |

`KIND_ALIASES` maps a parser's spelling onto these (`report` → `attachment`).
A new source therefore needs **no UI change**: tag its entries and the badge,
the Box types filter row and the counts appear by themselves.

**Publisher material is not a document.** Slack's own system notices (channel
created, joined, renamed, archived) are furniture *about* the release, so they
are `note`, not chat — the same reasoning that gives Rand Paul's analysis its
own box in the diary app.

**An email entry contains only what its author wrote** — no quoted history, no
forwarded bodies. The messages it answers are separate entries, reached through
reply links. That is what makes "the text written that day" trustworthy when it
is cited.

## 2. Splitting a release into messages

Start a new entry at every:

1. **Header** — a `From:` block with a date.
2. **Quoted header** — a `From:` block using `Sent:`, i.e. a quoted reply inside
   the outer message. It becomes its own entry too.
3. **Inline quote marker** — `On 8 Feb 2020, at 22:15, Kristian G. Andersen
   wrote:`. It carries no header block, so recover it: the marker supplies the
   author and the instant, the following lines are the body.

Stop each message's body at the **next** boundary of any of those kinds.

Practical rules learned from `po-emails.pdf`:

- The OCR glues header fields together (`Cc: Jeremy FarrarSubject: Re: Phone
  call`), so fields are found by keyword, not by line break.
- Only `From`/`To`/`Cc`/`Bcc` may continue onto the next line. `Subject`,
  `Sent` and `Date` are terminal — that is what stops the header block
  swallowing the body.
- **A long message printed over a page boundary repeats its header** at the top
  of the continuation, so it arrives as two entries with the same sender, stamp
  and subject. Group by identity and rejoin; do not rely on adjacency (other
  messages print between the halves).
- Scans carry avatar glyphs on the sender line (`Kristian G. Andersen | rrr`,
  `Jeremy Farrar esos mmm`). Match senders against a roster and keep the raw
  string.

## 3. Time zones — the part that breaks chronology

**A reply must never appear to answer a message from its own future.**

1. **An explicit UTC offset in the stamp always wins** — trust it, never
   re-zone it. (`Tue 2/4/2020 9:10:35 AM (UTC-05:00)`)
2. **Otherwise the sender's own institution decides**, because every message in
   these releases states it in the signature block or address line. Keep the
   table at the top of the parser, with the evidence in a comment:

   | Institution | Zone | Senders |
   |---|---|---|
   | Wellcome Trust / UK Government | Europe/London | Farrar, Vallance, Ferguson, Schreier, Golding |
   | NIH / NIAID, Bethesda | America/New_York | Fauci, Auchincloss, Collins, Shabman |
   | Scripps Research | America/Los_Angeles | Andersen, Farzan |
   | Tulane | America/Chicago | Garry |
   | University of Sydney | Australia/Sydney | Holmes |
   | Institut Pasteur | Europe/Paris | Fouchier |

   `ZONE_OVERRIDES` takes precedence, keyed `(date, HH:MM, subject)`, for a
   stamp that turns out to be ambiguous.
3. **Normalise to ET for ordering, and keep the local stamp.** `date` / `time`
   are the ET values (they order the timeline and form the entry key);
   `raw_date` shows local → ET; `stamp_line` is printed on the card, and
   `zone_assumed` names the evidence. Both stamps are always visible, so a
   reader can check the assumption rather than trust it.
4. Use `zoneinfo`, not fixed offsets, so DST is handled.
5. **Do not use document order to check chronology.** The email release prints a
   conversation grouped by thread, not in time order — the "Summary - Invitation
   to edit" thread runs 01:23, 19:08, 17:56, 17:08, 14:39. That looks like a
   parsing bug and is not; entries are sorted by their own stamps instead.

## 4. Threading: links in both directions

- **Upward** — `reply_to` / `reply_to_label`: the message this one answers.
  `link_kind` says how it was established. Where the release carries no
  message-id, a shared conversation is marked `inferred (same conversation)`
  rather than presented as proof.
- **Downward** — **arrays**: `replied_by`, `forwarded_by`, `attached_by`. A
  message may be answered several times, from another release, months later.

A parser links upward within its own release; the app re-inverts across all
merged sources at load (`rebuildThreadDownLinks`), so a link can cross releases.

## 5. Entry shape

```jsonc
{
  "idx": 12, "source": "po-emails",
  "date": "2020-02-01", "time": "1543",
  "kind": "email",
  "thread_key": "po-emails|2020-02-01|1543",   // unique; page-map key + link target
  "raw_date": "15:43 ET · Re: Phone call",
  "sender": "Jeremy Farrar", "sender_raw": "Jeremy Farrar esos mmm",
  "subject": "Re: Phone call",
  "stamp": "Saturday, February 1, 2020 at 20:43",
  "stamp_status": "long",          // outlook-us | long | day-month-year | offset | partial-no-time
  "zone_assumed": "Wellcome Trust / UK",
  "stamp_line": "20:43 GMT -> 15:43 ET",
  "content": "From: …\n\nTo: …\n\nSubject: …\n\n----------\n\nbody…",
  "reply_to": "po-emails|…", "reply_to_label": "…", "link_kind": "…",
  "replied_by": [ { "key": "…", "label": "…", "sender": "…" } ],
  "pages": [155, 156], "source_id": "po-emails"
}
```

`content` is the printable document: header fields, a `----------` separator,
then the body. Keeping the header **inside** `content` means From/To/Subject
stay searchable and highlightable, and the page map keeps working unchanged.
The UI splits on the rule to style the two apart.

**Keys must be unique.** They are page-map keys and link targets, so two
messages sharing a minute are disambiguated with a `|n` suffix and a
`date_note`.

## 6. Page maps

`{ "start": N, "end": M, "breaks": [[offset, page], …] }`, in a **per-source**
map keyed by the entry's own key (`thread_key`, or `idx` for the Slack parts).
Per-source maps mean two key schemes never collide.

## 7. Adding a release

1. Copy the PDF into `page_based/` (the repo is the sole home; no symlinks to
   Google Drive / DataWharehouse) and add it to `.gitattributes` for LFS.
2. Write `parse_<source>.py`, modelled on `parse_po_emails.py`: strip the
   release's furniture, segment messages, resolve stamps with the zone table,
   build `content` and the thread links, write `*_fixed.json` + a page map.
3. Tag every entry with `kind`.
4. Register it in `index.html` `SOURCES`: `json`, `pageMap`, `pdf`, `label`,
   `badge`, `badgeTitle`. Nothing else changes — loading, badges, the PDF
   switch and the filter all read from there. A source with **no** PDF is
   skipped by the loader rather than failing the load; ship `{}` as its map.
5. Check: counts per kind; ET order; every `reply_to` earlier than its replier;
   every entry key unique and present in the page map; no page out of range.
6. Run `node test_app.mjs` and `python3 audit_app.py`.

## 8. Adding a source with no PDF (metadata only)

The P.O. guide works this way: it is loaded separately and has no entries and no
PDF. Clicking into it resolves to entries in the other sources by key.

## 9. Tests

- `node test_app.mjs` runs `index.html`'s own script against the real data
  files under a DOM shim — data load, kinds, chronology, thread integrity,
  search, the generated card markup, the box-type filter, the timeline counts,
  the drafts and the guide. This machine has no headless browser, and the shim
  tests logic and generated markup, **not** layout or CSS.
- `python3 audit_app.py` covers what the shim cannot: duplicate ids,
  `getElementById` targets, inline handlers, CSS classes the script uses, tag
  balance, fetched files, and every `SOURCES` path.
