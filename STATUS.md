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
- `git-lfs` is not installed on this machine; `.gitattributes` marks the two
  PDFs for LFS tracking so it activates automatically once installed, but for
  now they're committed as regular (large) blobs. Install `git-lfs` and run
  `git lfs migrate import --include="page_based/*.pdf"` before adding a
  remote, if the repo is meant to go to GitHub.

## Optional later
- No `server_based/` variant exists yet (only `page_based/` was requested).
