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
- Wrote `parse_part1.py`: day-chunk parser for the OCR'd Part 1 text (58
  day-entries), reusing Fauci_Diary's date-header-driven chunking approach
  since per-message OCR parsing wasn't reliable enough for this source.
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

## Known limitations
- Part 1's day-chunks are not further split into individual messages (OCR
  quality doesn't support it reliably); search still works within a day, just
  at coarser granularity than Part 2.
- One pair of entries in Part 1 (2020-03-23 / 2020-03-24) is slightly
  out of strict chronological order due to an OCR misread; content is intact,
  just filed under the date appearing twice non-contiguously.
- `git-lfs` is not installed on this machine; `.gitattributes` marks the two
  PDFs for LFS tracking so it activates automatically once installed, but for
  now they're committed as regular (large) blobs. Install `git-lfs` and run
  `git lfs migrate import --include="page_based/*.pdf"` before adding a
  remote, if the repo is meant to go to GitHub.

## Optional later
- No `server_based/` variant exists yet (only `page_based/` was requested).
