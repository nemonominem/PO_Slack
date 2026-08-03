# P.O. Slack Search

Searchable web app for the Slack messages between the "Proximal Origin" paper
authors (Kristian Andersen, Andrew Rambaut, Eddie Holmes, Robert Garry),
released by Chairman Rand Paul's Senate committee.

## Coverage

| Part | Period | Entries | PDF pages | Format |
|---|---|---|---|---|
| **Part 1** — `paper-2020-nature_medicine-proximal_origin` (screenshots) | Feb 1 &ndash; Apr 30, 2020 | 1,256 (message-level) | 140 | OCR'd Slack screenshots |
| **Part 2** — Slack export continuation | Apr 30, 2020 &ndash; Jun 28, 2023 | 11,357 (message-level) | 1,123 | Clean text-layer export |
| **Combined** | Feb 2020 &ndash; Jun 2023 | 12,617 | 1,263 | |

Part 2 begins with the exact same message that closes Part 1 ("Yes, both are
in the wrong...", Eddie Holmes, Apr 30 2020) &mdash; the two releases are a
continuous conversation, not overlapping ranges. Both are merged into a single
searchable timeline in the app; the PDF viewer automatically switches to the
correct source PDF when you click a result.

Slack's own system notices (channel created, joined/left, renamed, archived)
are attributed to a synthetic **Slack Notice** sender in both parts (shown
italicized/greyed in the UI), rather than being conflated with the mentioned
person's authored chat messages. The real actor's name is kept in the notice
text, e.g. "Kristian Andersen joined paper-2020-nature_medicine-proximal_origin."

## Both parts are message-level, with one caveat for Part 1

Part 1 was released as stitched Slack-UI screenshots. The PDF's own baked-in
OCR text layer (from "PDF24 Tools - OCR") was low quality, but the source
screenshots themselves are sharp — so `reocr_part1.py` re-OCRs all 140 pages
from scratch (300dpi renders via `pdftoppm`, then `tesseract --oem 1 --psm
6`), which gets full clean sentences and accurate sender/time headers
instead of mangled fragments. `parse_part1.py` then anchors on the five
known channel participants' name+timestamp headers (tolerating missing
colons, dropped digits, and occasional OCR-mangled same-line day-dividers)
to split messages, and tracks the day-divider lines Slack inserts before the
first message of each day to date them. Two known limitations, inherent to
the source rather than the parser:

- Slack visually groups consecutive messages from the same sender without
  repeating the header; a run of un-headered short paragraphs following one
  header may really be 2-3 separate messages rather than one. They're kept as
  a single entry — correctly attributed, just coarser than a true
  one-row-per-message split.
- Black-box redactions in the source produce no OCR text at all. Where a
  header is found with no content at all before the next header, the entry
  is flagged `redacted: true` (shown as an orange "▪ redacted" tag) with a
  placeholder note; but a redaction that falls *inside* an otherwise
  non-empty message leaves no distinguishing trace and can't be flagged.

Part 2 was released as a genuine text-layer Slack export (message ⟶
timestamp ⟶ sender bracketed blocks), so it parses exactly at per-message
granularity, with accurate timestamps, senders, thread IDs, and attachments.

## Structure

| File | Purpose |
|---|---|
| `page_based/index.html` | Self-contained static search app (forked from Fauci_Diary's page_based app) |
| `page_based/slack-part1.pdf`, `slack-part2.pdf` | Source PDFs |
| `page_based/part1.json`, `part2.json` | Parsed entries |
| `page_based/part1_page_map.json`, `part2_page_map.json` | Entry &rarr; PDF page lookup for the viewer's jump-to-page feature |
| `page_based/reocr_part1.py` | Re-OCRs Part 1's 140 pages with Tesseract (run once; writes `slack-part1_ocr.txt`) |
| `page_based/slack-part1_ocr.txt` | Re-OCR'd text, consumed by `parse_part1.py` |
| `page_based/parse_part1.py` | Message-level parser for the re-OCR'd Part 1 text |
| `page_based/build_part2.py` | Reshapes the existing high-quality Part 2 message parse into the app's entry schema |
| `page_based/slack_notice.py` | Shared Slack-system-notice detection used by both builders |

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
