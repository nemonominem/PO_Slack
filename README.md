# P.O. Slack Search

Searchable web app for the Slack messages between the "Proximal Origin" paper
authors (Kristian Andersen, Andrew Rambaut, Eddie Holmes, Robert Garry),
released by Chairman Rand Paul's Senate committee.

## Coverage

| Part | Period | Entries | PDF pages | Format |
|---|---|---|---|---|
| **Part 1** — `paper-2020-nature_medicine-proximal_origin` (screenshots) | Feb 1 &ndash; Apr 30, 2020 | 58 (day-level) | 140 | OCR'd Slack screenshots |
| **Part 2** — Slack export continuation | Apr 30, 2020 &ndash; Jun 28, 2023 | 11,357 (message-level) | 1,123 | Clean text-layer export |
| **Combined** | Feb 2020 &ndash; Jun 2023 | 11,415 | 1,263 | |

Part 2 begins with the exact same message that closes Part 1 ("Yes, both are
in the wrong...", Eddie Holmes, Apr 30 2020) &mdash; the two releases are a
continuous conversation, not overlapping ranges. Both are merged into a single
searchable timeline in the app; the PDF viewer automatically switches to the
correct source PDF when you click a result.

## Why two different granularities

Part 1 was released as stitched Slack-UI screenshots; OCR text quality is
poor enough that reliable per-message boundaries can't be extracted with
confidence, so entries are chunked **per day** (mirroring how
[Fauci_Diary](../Fauci_Diary) chunks per diary date) using the day-divider
lines Slack inserts between messages, which do survive OCR cleanly.

Part 2 was released as a genuine text-layer Slack export (message ⟶
timestamp ⟶ sender bracketed blocks), so it parses cleanly at **per-message**
granularity, with accurate timestamps, senders, thread IDs, and attachments.

## Structure

| File | Purpose |
|---|---|
| `page_based/index.html` | Self-contained static search app (forked from Fauci_Diary's page_based app) |
| `page_based/slack-part1.pdf`, `slack-part2.pdf` | Source PDFs |
| `page_based/part1.json`, `part2.json` | Parsed entries |
| `page_based/part1_page_map.json`, `part2_page_map.json` | Entry &rarr; PDF page lookup for the viewer's jump-to-page feature |
| `page_based/parse_part1.py` | Day-chunk parser for the OCR'd Part 1 PDF |
| `page_based/build_part2.py` | Reshapes the existing high-quality Part 2 message parse into the app's entry schema |

## How to use

```bash
cd page_based
python3 -m http.server 8080
# open http://localhost:8080
```

Any static HTTP server works (this is a GitHub-Pages-shaped static bundle).
Opening `index.html` directly via `file://` will not work — browsers block
`fetch()` of local JSON/PDF from `file://` URLs.

## Search tips

- `word1 word2` — AND
- `word1|word2` — OR
- `lab*` — wildcard
- `"exact phrase"` — quoted phrase

Click **?** in the header for the full help popup. Use HIT Prev/Next to step
through matches inside an entry. Toggle Landscape / Portrait layout with the
header button.
