# Status: PO_Slack

## Standing rule

Same as [Fauci_Diary](../Fauci_Diary): this repo is the sole home of the
P.O. Slack app and its data. Do not symlink to or depend on Google
Drive / DataWharehouse paths; all PDFs, JSON, and scripts live inside
`page_based/`.

## Done
- Identified and resolved the two source PDFs (both were macOS alias files
  pointing at Google Drive / DataWharehouse; real files copied into the repo):
  - `slack-part1.pdf` (140p, OCR'd screenshots, Feb 1 &ndash; Apr 30 2020)
  - `slack-part2.pdf` (1,123p, clean text-layer export, Apr 30 2020 &ndash; Jun 2023)
- Confirmed continuity: Part 2's first message is identical to Part 1's last
  message, i.e. one continuous conversation split across two releases.
- Wrote `build_part2.py`: reshapes the pre-existing high-quality message
  parse of Part 2 (`DataWharehouse/.../slack-drop-pm.json`, 11,357 messages,
  clean timestamps/senders/thread-ids) into the app's entry schema.
- Forked Fauci_Diary's `page_based/index.html` into a P.O. Slack app:
  rebranded, SOURCES config repointed at the two parts, sender/time shown in
  result cards, page-map lookup simplified to per-entry `idx` keys (needed
  since Part 2 has thousands of messages sharing the same date, unlike the
  diary's one-entry-per-date assumption).
- Verified end-to-end in a real browser: search, highlighting, per-part PDF
  switching, and jump-to-page all work correctly for both parts.
- Initialized as a local git repo (no remote yet).
- **Rewrote `parse_part1.py` to message-level granularity** (was day-level:
  58 entries; now 1,260), anchored on the five known channel participants'
  name+timestamp headers rather than day-dividers alone. Handles: colon-
  dropped/garbled times ("1211" → 12:11), OCR-mangled day-dividers wrapped
  across lines or fused onto a header's own line, the "1st" digit misread as
  a letter ("Februsey ist, 2020"), attachment filenames pulled out of body
  text into a separate `attachments` list, and entries where a header was
  found but no content followed (flagged `redacted: true`, since these
  correspond to black-box-redacted or image-only content the OCR layer
  can't see at all).
- Added `slack_notice.py` (shared by both builders): re-attributes Slack
  system events (channel created, joined/left, renamed, archived/unarchived)
  to a synthetic **Slack Notice** sender instead of the mentioned person,
  applied consistently to both Part 1 and Part 2 (Part 2 had one such case:
  the closing "archived the private channel").
- Added a "▪ redacted" tag and a distinct (italic/grey) style for "Slack
  Notice" entries in the result cards.
- Author name moved to right after the date in result cards ("2020-04-09
  Andrew Rambaut ..."), per request.
- **Re-OCR'd Part 1 from scratch with Tesseract** (`reocr_part1.py`: renders
  all 140 pages at 300dpi via `pdftoppm`, OCRs each with `tesseract --oem 1
  --psm 6`), replacing the low-quality OCR text layer baked into the PDF by
  the original "PDF24 Tools - OCR" pass. Spot checks against the actual page
  images confirmed the source screenshots are sharp — the garbled text was
  purely a bad-OCR-pass problem, not a source-quality ceiling. Quality
  improvement is dramatic: full clean sentences and accurate sender/time
  headers ("Andrew Rambaut 19:19") vs. previously mangled fragments
  ("Mi Andrew Rambaut +219"). `parse_part1.py` now reads
  `slack-part1_ocr.txt` (checked in, ~380KB) instead of calling `pdftotext`
  directly. 1,256 entries (was 1,260 — comparable count, much cleaner text).
- **Cleaned the "I" → "|" OCR misread** (`clean_ocr_noise` in
  `parse_part1.py`): a standalone `|` bounded by whitespace/punctuation is
  almost always a garbled capital "I" ("| agree" → "I agree"), fixed across
  ~780 occurrences. Skipped on lines that look like pasted genomic/accession
  data (FASTA headers, GISAID `EPI_ISL` ids), where `|` is a real field
  separator — verified none of those lines were affected. Left alone: `|`
  fused directly onto an adjacent letter with no space (too ambiguous to
  fix confidently, e.g. "loop region come in|it's").
- **Separated authored chat from attachment cards in Part 1** (and showed
  Part 2 filenames the same way). `parse_part1.py` now: strips leading
  avatar/icon garbage (`@B Nice channel title` → `Nice channel title`,
  `@ Morning` → `Morning`, keeping real `@Andrew` / `@channel` mentions);
  drops Slack's ▾ chevron OCR'd as `¥`; and wraps Post / Word / G Suite /
  file / image cards plus their preview body with `== ATTACHMENT ==`.
  Result cards render that block as a distinct inset. 102 Part 1 entries
  carry the marker (entry count unchanged at 1,256).
- **Fixed Part 2 timestamp/sender off-by-one.** The export is
  `[timestamp]` then `[sender]` then body; the old parser treated the
  stamp as a *trailing* closer on the previous message, so every time
  (and therefore the date) belonged to the wrong entry — e.g. Eddie's
  last chat inherited the 2023-06-27 unarchive time. `parse_part2.py`
  now reads `slack-part2.pdf` locally (no DataWharehouse JSON). 11,351
  entries (48 of them from 6 image-only pages in `part2_ocr_pages.json`).
  Part 2 result-card headers show time before the name (`2022-06-02
  13:15:20 Eddie Holmes`); Part 1 stays date → name → time.
- **Isolated end-of-range days are visible on the timeline.** A 1-entry
  day at the far end of ~1,200 day-categories was a clipped sub-pixel
  sliver (the Jun 2023 archive notices). Time-axis offset is on, and
  entry days get a 3px minimum mark so those last two cards show as a
  2023 tick.
- **Multi-file attachment blocks list each name.** `== ATTACHMENT(2) ==`
  then one filename per line (e.g. the two `.geneious` files). Slack's
  "2 files / Zip Zip" chrome is dropped. Single files stay
  `== ATTACHMENT ==`.
- **Slack Posts are embedded documents, not files.** The "Post ¥"
  chrome becomes the stub `embedded`, then `== EMBEDDED DOC ==`, the
  title (`Ideas for analyses`), and the body one line per bullet.
  Word / G Suite / shared-post cards use the same marker.
- **Feb 15-style OCR crumbs:** strip `4B`/`6` avatar prefixes, `g0`→`go`,
  leaked `February 15th, 2U20` day-dividers, and image-OCR soup after
  `png.*` (now `== ATTACHMENT ==` / `image.png`). HIT nav shows the
  message time when the OCR recovered one; many Slack-grouped headers
  on this page have no time in the text layer.

## Done (mixed sources — branch `po-sources-and-boxes`)
- **Branch `po-sources-and-boxes`** carries this work; `main` is untouched until
  it is reviewed.
- **Scroll / large-box fixes ported** from `Fauci_Diary`: every result card's
  text box scrolls on its own with an always-visible draggable scrollbar
  (native bar hidden, because macOS overlay bars are invisible at rest and the
  Up/Down keys belong to the match list), a `Full text` expander that lifts the
  height cap, a `scroll inside this box` hint, and one keydown handler that
  gives PageUp/PageDown to the box under the pointer, Up/Down to the match list
  and Left/Right to the PDF.
- **Box types**: every entry carries a `kind` (slack / email / attachment /
  note / draft / document). Cards show a kind badge and a source badge; the
  toolbar's **Box types** button ticks which kinds are listed, applied to
  search, the browse window, the timeline day-counts and the stats line, stored
  in `localStorage`. A new source needs no UI change.
- **`SOURCES` now drives loading** (json, page map, PDF, badge, badgeTitle):
  adding a release is a config entry. Sources without a PDF are skipped rather
  than failing the load.
- **Third and fourth sources ingested**
  - `po-emails.pdf` — the FOI'd P.O. email release, cited 71x in the article.
    Re-OCR'd (image-only scans) and parsed into **87 messages**, 31 Jan –
    27 Jul 2020, 34 thread links. One entry per message, ET-normalised with the
    zone assumption recorded per entry.
  - `sscp-drafts.pdf` — the manuscript as revised, parsed into **20 dated
    versions**, 1 Feb – 5 Mar 2020, matching the public `PO#1…#19` clean copies.
- **Thread links run both ways**: a card links to the message it answers and to
  the ones that answered it (`rebuildThreadDownLinks` re-inverts across releases).
- **The P.O. guide**: a left rail lists the article's own dated sections with
  the released documents each cites (name, page, date) and a link to the public
  copy where the article gives one. Built by `build_po_guide.py` from the three
  parts of the article (214 sections, 446 citations, 51 documents, 21 verified
  Drive links) into `po_guide.json` + `SOURCES.md`.
- **Data fixes found while testing**: 7 messages split across a page boundary
  are rejoined (Outlook repeats the header on the continuation page); entry keys
  are now unique, so two messages in the same minute no longer collide; the
  `SOURCES` key was `poemails` while the data says `po-emails`.
- **Tests**: `node test_app.mjs` (32 checks) runs `index.html`'s own script
  against the real data under a DOM shim; `python3 audit_app.py` (19 checks)
  covers duplicate ids, `getElementById` targets, inline handlers, CSS classes,
  tag balance, fetched files and every `SOURCES` path.
- **Standards written down** in `page_based/SPEC.md` (kinds, message splitting,
  the time-zone table, threading, entry shape, page maps, and the recipe for
  adding a release or a source with no PDF).

## TODO — also ingest the other dated sources the piece leans on
Agreed to add these in a later pass; each is catalogued in `page_based/SOURCES.md`
with its citation count, pages cited and Drive link where the article gives one.
Prioritised by how much of the argument they carry:

- [ ] `Baric-Emails-2.17.21.pdf` (8x) and the EHA/WIV correspondence
- [ ] `UTMB-LeDuc-batch-1.pdf` (7x) — LeDuc's pointed questions, 9–10 Feb
- [ ] `01981-F-Dec-2022-Production-OPAQUE.pdf` (8x) and the other USRTK
      productions (`USRTK_UCDavis_PROD_*`, 11x)
- [ ] `Biohazard_FOIA_Maryland_Emails_11.6.20.pdf` (6x) and
      `HHS_Garrett-Grigsby_12.30.21_production.pdf` (5x)
- [ ] `OSU-records-Shan-Liu-Aug-4.pdf`, `nih-foia-request-60081and-59096` (2x)
- [ ] Hearing transcripts: `2023.06.16-Andersen-Transcript.pdf` (12x),
      `Baric-TI-Transcript.pdf` (11x), `Tabak-TI`, `2023.04.06-Lipkin`,
      `Lane-Transcript`
- [ ] `1265-pages.pdf` (9x) and the other unnamed productions
- **Not ingestible as documents** (tweets, press, video): ~30 citations. They
  are already catalogued in the guide as `social` / `press` / `link` evidence
  and shown as such; they need no app entries.

## Done (review round — guide, emails, timeline)
- **Guide is collapsible like the Dual timeline.** The Hide/Show button is gone
  (it left the rail unrecoverable). The guide header now carries a `◀/▶` chevron
  and collapses to a 36px vertical rail; the list+detail sit in a `.guide-body`
  that hides on collapse. State persists in `localStorage`, and there is always
  a visible rail to click back open.
- **Email parsing cleaned.** The scans are Outlook screenshots, so header fields
  carried avatar glyphs (`(€]`, `[E] ees`) and quoted-image OCR leaked "glyph
  soup" into the body. `parse_po_emails.py` now strips avatar brackets/glyphs
  from To/Cc/Bcc/Subject, applies the sender roster to the From line, and drops
  body lines with no real word (unless a URL/number). 0 noisy header lines
  remain.
- **Right PDF now shows.** Clicking an email/draft result previously set `pdfDoc`
  to a source whose PDF was still loading, so nothing rendered. New
  `renderEntryPdf(source, page)` loads the source PDF on demand (reusing the
  in-flight promise) and renders the requested page once ready; `selectResult`
  uses it, so a click always lands on the correct release + page.
- **Timeline stacked by media × release.** The entries side is now a stack of
  one dataset per (source, kind): colour = media (Slack blue, Email green,
  Draft amber, Attachment violet, Note grey), shade = release (Slack P1 and
  Slack P2 are two blues; each FOIA production its own shade). A legend under
  the chart lists each segment (swatch + label + total), click-to-toggle, and a
  hover title explains the chart; the guide rail also gained a hover title. The
  min-size mark plugin now draws neutral grey (it used the removed per-year
  colours).

## Done (review round 2 — labels, timeline handles, resize)
- **App is no longer "P.O. Slack Search".** The title, heading, subtitle and
  placeholders now say "P.O. Record Search" / "Search the P.O. record", and the
  subtitle lists Slack + FOI'd emails + drafts, with the corrected 12,714-entry
  count (Jan 2020 - Jun 2023).
- **Both timelines open by default, handles consistent.** The guide no longer
  persists a collapsed state, so it opens open every load like the Dual
  timeline. When collapsed, its expand chevron now sits at the top (the title
  had `flex: 1`, which pushed it to the bottom while the Dual timeline's stayed
  at the top).
- **The Dual timeline block is resizable.** A drag handle sits between the
  timeline and the results panel: drag it to change the timeline's width in
  landscape, or its height in portrait, with the same handle styling as the PDF
  panel. The width/height easing is disabled while dragging.

## Done (review round 3 — counts, legend, labels)
- **Counts made trustworthy.** File-carrying Slack messages were being
  reclassified as `attachment`, so the "Slack" count silently dropped ~1000
  messages and the numbers looked suspiciously round (11,600 + 1,000). A Slack
  message is now `slack` whether or not it carries a file (files stay as chips).
  Counts are now Slack 12,600 + 7 notices, Email 87, Draft 20 = 12,714, and they
  reconcile with the per-day totals (asserted in the test). Only the `kind` field
  changed — content, dates and senders are byte-identical to before.
- **Legend taller in landscape.** The media legend no longer caps at 64px with a
  scroll; in landscape it takes its natural height so all sources are visible
  without scrolling.
- **"Box types | All box types" → "Sources | All types".** The redundant pairing
  is gone, including the button's dynamic labels (All types / N types / No types).
- **"Jump to date" → "Jump to date:" and labels are blue.** Established the visual
  idiom: labels are blue (`var(--blue)`), editable fields are dark (`var(--input)`),
  action buttons are accent-filled. Applied to both the "Sources" and "Jump to
  date:" labels.

## Known limitations
- Part 1 message boundaries are best-effort, not exact: Slack visually groups
  consecutive same-sender messages without repeating the header, so a run of
  un-headered short paragraphs after one header may really be 2-3 separate
  messages rather than one. They're kept as a single entry — correctly
  attributed to the right sender, just coarser than a true
  one-row-per-message split. Part 2 (clean text export) has no such issue.
- Black-box redactions that fall *inside* an otherwise non-empty Part 1
  message leave no distinguishing trace in the OCR text and can't be flagged;
  only messages that are *entirely* redacted (header with zero content
  before the next header) are caught and marked `redacted: true`.
- Two entries in Part 1 (around 2020-02-18/20 and 2020-03-23/24) are out of
  strict chronological order due to an OCR-garbled day-divider; content is
  intact, just filed under the wrong day for a short stretch.
- Part 1 attachment markers are best-effort: image/file cards are the
  filename plus following OCR crumbs, while a Slack Post / Google Doc
  preview is marked from the card to the next card (or end of the message).
  Commentary typed after a document card can still land inside the block.
- `git-lfs` is not installed on this machine; `.gitattributes` marks the two
  PDFs for LFS tracking so it activates automatically once installed, but for
  now they're committed as regular (large) blobs. Install `git-lfs` and run
  `git lfs migrate import --include="page_based/*.pdf"` before adding a
  remote, if the repo is meant to go to GitHub.

## Optional later
- No `server_based/` variant exists yet (only `page_based/` was requested).
- **Browser testing was done without a browser.** This machine has no headless
  browser available (Chrome and Playwright are not installed and there is no
  network to fetch them; Brave's headless mode aborts under the sandbox, and
  `screencapture` cannot reach a display). The app's real script is therefore run
  under a DOM shim (`test_app.mjs`), which tests its logic and the markup it
  generates, and the markup is checked statically (`audit_app.py`) — but the
  layout and CSS have not been seen rendered. **Worth a manual pass in a real
  browser before this is published**: scroll a long email, drag a box
  scrollbar, expand a card, walk the box-type filter, pick a guide section.
- The Google Drive clean copies (`PO#1…#19`, `Rebuttal#1…#5`) are **linked,
  not downloaded**: the sandbox has no DNS, so the binaries cannot be fetched
  here. Download them into `page_based/` if you want them served alongside the
  app.
- `git-lfs` is not installed, so the PDFs are committed as large blobs.
  `page_based/farrar-fauci-comms.pdf` is the one exception: at 99.6 MiB it
  sits 0.4 MiB under GitHub's 100 MiB per-file limit, so it stays on disk but
  **deliberately untracked** (`.gitignore`) even though the app now reads it
  (farrar-fauci source, see below) — install `git-lfs` and
  `git lfs migrate import --include="page_based/*.pdf"` before adding it.

## Done (review round 4 — bookmarks, manual, DRASTIC mark, email headers)

- **DRASTIC mark** in the header's top right, copied from `import/` to
  `page_based/drastic-logo.png`; it links to the manual in a new tab.
- **Bookmarks**: a third collapsible rail (vertical in landscape, horizontal in
  portrait, arrows turning ▲▼ → ◀▶), a 🔖 toggle on every box, Save/Load to a
  named JSON file. Entries carry a `bm_key` that is unique across releases —
  the two Slack parts both number from `idx 0`, so a bare index would have made
  a Part 1 bookmark jump into Part 2. The file format is versioned and records
  `app` + `url`, so one bookmarks file can hold pointers into the Fauci Diary
  and the Daszak calendar; this app jumps to entries it holds and opens the url
  for the rest.
- **`help.html`**: a full manual (12 sections) + release notes, with the DRASTIC
  mark, opened in a new tab from the header.
- **Guide**: citations now sort alphabetically by document.
- **Email headers repaired.** The OCR read `Cc:` as `Ce:` and `To:` as `Pe:`;
  more seriously, a glyph fragment between fields ("Pe") or a torn-off scrap of
  a wrapped two-column recipient list was closing the header block early, so
  `Subject:` lines were left stranded in the message body. Fixed at four levels:
  field aliases, junk-line skipping, recipient-run continuation
  (`continues_recipient_run`, used only inside a run, never to open one), and a
  bounded header block (`MAX_HEADER_LINES`, since Outlook never prints 18 header
  lines — what follows a long list here is quoted letterhead).
  **Subjects recovered on 76 of 86 messages, up from 0.** Zero messages now have
  their own subject stranded in their body. The 10 still empty are ones whose
  subject the scans lost outright; they are left empty rather than guessed.
  (Now 95 of 100 — see the counts note below.)
- **Signatures separated.** A title block is no longer read as message prose: it
  is cut off the text into its own `signature` field and shown after a rule, with
  its own line returns preserved. Holmes's block had been flattened into the body.
- **Line returns repaired.** Breaks that were an artefact of the scan column
  width are rejoined (`unwrap_lines`); returns the author made are kept.
- Counts: Slack 12,600 + 7 notices, Email 100, Draft 20 = **12,727**.
  (Was 86: fourteen messages whose `From:` line the scan swallowed had been
  fused into their neighbours, most visibly entry 22 with its doubled Subject
  and stamp. `segment()` now also opens on a `Date:`/`Sent:` line when the
  current message is already in its body and the `From:` above is more than a
  full header block away; quoted history can't trigger it. Five of the new
  messages recover their sender from the signature block via the same roster
  (recorded as `sender_how`); the rest stay honestly senderless. Two further
  fixes fell out along the way: the body-sweep parsed the recipient run up to
  but *excluding* the Subject line itself (`range(found)` → `range(found+1)`),
  which recovered 7 more subjects (now 95 of 100), and the page map no longer
  pairs entries to messages by position after the chronological sort — pages
  ride on the entries, giving 103/103 coverage. The release's duplicate prints
  (REV batch + LIP/GARRY batch) merge without doubling their bodies.)
- **Testing.** A real browser suite now exists: `page_based/test_browser.mjs`
  drives Chrome for Testing (from the Playwright cache — the MCP browser server
  looks for a Google Chrome install that is not present on this machine) and
  checks what the other two suites cannot: that the bookmarks rail really is a
  vertical column in landscape and a horizontal strip in portrait, that its
  arrows really do turn sideways, that a clipped box really does show its
  scrollbar, that the DRASTIC logo really loads, and that a bookmark really
  survives a reload. **34 browser + 66 functional + 55 static checks pass.**
  Run it with the app served: `python3 -m http.server 8099 && node test_browser.mjs`.

## Done (review round 5 — Farrar-Fauci-Collins emails ingested, fifth source)
- **`farrar-fauci-comms.pdf` re-OCR'd to completion** (174/174 pages; the prior
  pass had only reached page 80). Same recipe as the other releases: `pdftoppm`
  at 300dpi + `tesseract --oem 1 --psm 6`, resumable
  (`reocr_farrar_fauci.py`), because the PDF's own text layer glues words
  together and misreads glyphs (`sent: Fri,24Jul202010:37:4640000To:
  JeremyFarrar`) where the rendered page images are sharp.
- **`parse_farrar_fauci.py`** (new) turns the OCR text into entries, following
  the same rules as `parse_po_emails.py` (SPEC.md) but adapted to this
  release's shape, which is plain Outlook headers rather than screenshots:
  - **Explicit UTC offsets win.** Most top-level stamps carry a bare
    RFC-2822-style offset (`Sent: Fri, 24 Jul 2020 10:37:46 +0000`), with no
    parens — a new stamp format the po-emails parser never needed. The zone
    table only matters for the stamps that lack one.
  - **Inline quote markers recovered as their own entries.** SPEC.md 2.3 calls
    for this and po-emails' parser never implemented it; here "On 8 Feb 2020,
    at 22:15, Kristian G. Andersen wrote:" opens a new message (synthetic
    `From:`/`Sent:` lines built from the marker) instead of leaving the quoted
    reply glued into the message that quotes it. No Subject is invented for
    these — left empty rather than guessed.
  - **A handful of German-language headers** (Von/Gesendet/An/Betreff, from
    messages relayed through a German mail client) are recognised as field
    aliases alongside the usual OCR misreadings (Ce:/Pe:/Fe:).
  - **165 entries, 159 dated** (23 Jan – 24 Jul 2020), **6 undated** (2 where
    the scan lost the Sent: line entirely with no recoverable stamp, 1 each in
    Dutch and Spanish locale date formats not yet handled, 2 others) — left
    undated rather than guessed, same policy as every other source.
  - Sender roster extended for this release's correspondents (Viner, Dzau,
    Collins, Smith, Bianchi, Gibbons, the GPMB/WHO governance thread, etc.);
    a handful of senders with heavily redacted or truncated OCR text still
    fall back to raw cleaned text (e.g. bare "SMITH", "Jeremy") rather than a
    forced roster match — same best-effort standard as po-emails.
- **Registered as a fifth source** (`farrar-fauci`) in `index.html`'s
  `SOURCES`, wired into `guideDocToSource` so the guide's
  `farrar-fauci-comms-full.pdf` / `farrar-fauci-comms.pdf` citations are now
  clickable PDF links instead of inert labels. `build_po_guide.py` already had
  the `LOCAL_DOCS` mapping from an earlier pass; nothing there needed to
  change.
- **Fixed a latent `test_browser.mjs` bug** found while testing: the Email
  formatting check's card-selection predicate used an anchored regex
  (`/^Subject: /m`) against `.textContent`, which never has real newlines
  between header fields, so it could never match and always fell through to
  `cards[0]` — happening to pass only because the previously-first
  chronological email result always had a Subject. Adding an earlier-dated
  source with some blank-subject (inline-quote-recovered) entries exposed it.
  Fixed to use the same non-anchored test as the real assertion below it.
- Counts: Slack 12,600 + 7 notices, Email 100, Farrar-Fauci-Collins 165,
  Draft 20 = **12,892**.
- **Tests**: 67/67 functional, 58/58 static, 32/34 browser (the 2 remaining
  failures are the portrait bookmark-rail layout check, pre-existing and
  unrelated to this source — tracking the rail's old horizontal-strip
  portrait behaviour, which a separate concurrent change already moved away
  from without updating this assertion).

## Done (review round 6 — OCR fixes: Farrar-Fauci "I"/bullets, sscp version mix-up)
- **Fixed a real content/stamp mismatch in the manuscript drafts.** Every
  printed copy in `sscp-drafts.pdf` carries a diagonal version-stamp
  watermark on each of its pages, but `pypdf.extract_text()` places that
  stamp's text *after* the page's body in the extracted string even though
  it sits visually at/near the top — so the stamp is a closer of the content
  that precedes it, not an opener of what follows. `parse_sscp.py` had it
  backwards: it treated a stamp as starting a new version and attributed
  everything *after* it (up to the next stamp) to that version — which is
  actually the next page's content. The entry labelled "2020-02-01 20:57pm"
  was showing the "Four features — already noticed..." bullet notes that
  really belong to "2020-02-02 18:29pm" (one stamp later), while the prose
  that genuinely carries the 20:57 stamp sat one entry early. Rewrote the
  segmentation to seal a version on *finding* its stamp rather than on
  seeing the next one. Version count unchanged (20, same 1 Feb – 5 Mar 2020
  range) — only which text goes with which stamp changed. Also fixed a
  separate, unrelated extraction glitch while in there: a word's first
  letter sometimes lands alone on its own line ("B" / "amHI site doesn't
  mean..." → "BamHI site doesn't mean...", "W" / "e discussed..." → "We
  discussed...") — `merge_split_initial()` rejoins a bare (optionally
  numbered) capital letter with a following lower-case line, narrowly scoped
  so it can't touch a real line (an acronym like "ACE2" ending a wrapped
  line is far longer than the pattern allows).
  Known remaining limitation: a handful of PDFs in this release have a
  single stray space inserted inside an otherwise normal word by the same
  extraction quirk ("re sidues", "fo r interaction", "ti ssue culture") —
  rare (~10 instances across 216 pages) and left alone rather than risking a
  dictionary-based de-glue that could silently join words that were never
  meant to be one.
- **Cleaned up `farrar-fauci-comms.pdf`'s OCR noise**, the same two patterns
  parse_part1.py already fixed for the Slack scans, now ported to this
  release: a standalone `|` bounded by whitespace/punctuation is a garbled
  capital "I" (`STANDALONE_PIPE_RE`, ~380 occurrences — "| will:" → "I
  will:"), and Tesseract reads the round bullet glyph as the nearest Latin
  letter/symbol, "e" or "©" here (`RE_BULLET_MISREAD`, ~78 occurrences — "e
  Bein contact with WHO" → "• Be in contact with WHO", restoring the real
  bullet and, via a small `GLUED_WORDS` table of specifically-verified
  glue losses, the dropped space). Zero standalone pipes or bullet
  misreads remain in any of the 165 entries.
- **Tests**: 67/67 functional, 58/58 static (browser suite unchanged from
  the previous round).

## Done (review round 7 — long redacted recipient lists, embedded attachments)
- **Fixed a real header/body mix-up on GPMB Board broadcasts.** These
  messages go to 30+ redacted recipients wrapped over 20+ visual lines, far
  past what `MAX_HEADER_LINES` (12, sized for po-emails' smaller correspondent
  circles) allowed — `segment()` never re-enters header mode once it gives up,
  so the back half of the recipient list, and the Subject/Importance lines
  that followed it, fell into the message body as if they were the author's
  own prose. Raised the cap to 80 (the real gatekeeper stays the line-shape
  test, this only bounds how long it is trusted), and made the body-recovery
  sweep's own stopping rule more robust: it used to give up the moment any
  one line failed a *positive* "this still looks like a name" test, which an
  OCR-garbled name anywhere in a long list could trip (one did: "Teresa
  Miller de Vega" read as "niiller de Vega" broke the all-known-tokens check
  13 lines into a 17-line list, stranding the Subject just past it). Replaced
  it with the opposite, safer default (`looks_like_body_prose`): keep
  scanning for a stranded field until a line *positively* looks like real
  prose (a greeting, or a long sentence with several ordinary words), not the
  other way round. Also fixed two smaller bugs the same sweep uncovered: a
  second non-recipient field (Importance, after Subject) wasn't moving the
  recovery position onto itself before stopping, leaving it stranded too; and
  a Subject that wraps onto its own line with no field keyword of its own
  ("...on 2019-" / "novel coronavirus") was silently dropped by the sweep's
  one-line-at-a-time reprocessing — now reattached.
- **An attached Word document (with reviewer comments) no longer reads as
  part of the covering email.** `strip_quoted()`'s sign-off list required
  "Kind regards" and didn't match this release's "Kinds regards" (OCR
  pluralised); once fixed, the existing cut-everything-after-the-sign-off
  behaviour correctly drops the attachment along with it. Added a second,
  independent line of defence for releases/messages with no recognisable
  sign-off at all: Word's own "Commented [A1]:" / "Commented [A4R4]:" review
  markers are specific enough to never appear in real prose, so finding one
  anywhere in a body now cuts there too, leaving
  `== ATTACHMENT: document with reviewer comments (not transcribed) ==`
  rather than silently gluing the attachment's text onto the author's own.
- Two residual, lower-priority cases remain (both already-`undated` duplicate
  prints of messages that ARE fully correct in their dated form elsewhere):
  a Dutch- and a Spanish-locale version stamp, neither parsed by `parse_stamp`
  (pre-existing, documented limitation), still leave `Importance:` unresolved
  in the body for those two copies specifically.
- **Tests**: 67/67 functional, 58/58 static.
