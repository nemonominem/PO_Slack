# page_based: the published app and its data

This folder is published to GitHub Pages (the workflow uploads `page_based/`).
Everything here is served to the browser, so keep only what the app needs.

## Served app
- `index.html`: the P.O. Record Search app (single file).
- `help.html`, `drastic-logo.png`: the manual and the header logo.

## Data the app reads
- `part1.json`, `part2.json`: Slack messages (Part 1 and Part 2).
- `po-emails.json`, `farrar-fauci.json`, `sscp-drafts.json`: email and draft entries.
- `*_page_map.json`: which PDF page each entry is on.
- `po_guide.json`, `guide_summaries.json`: the Tragicomedy guide and its summaries.
- `complementary.json`, `complementary/`: linked documents.
- `article_page_map.json`: pages of the Tragicomedy text.
- `chapter_links.json`: which entries each Tragicomedy section cites (built by `tools/build_chapter_links.py`).
- `bookmark_rekey.json`: old bookmark keys mapped to current ones (built by `tools/build_bookmark_rekey.py`).

## PDFs the app opens
- `main_sources/`: the four main sources: `slack-part1.pdf`, `slack-part2.pdf`,
  `po-emails.pdf`, `sscp-drafts.pdf`.
- `other_sources/`: `farrar-fauci-comms.pdf` (Farrar-Fauci correspondence).
- `tragicomedy/`: the Tragicomedy PDFs.
- `complementary/`: linked documents cited by the guide.

## Not here
- Scripts: `tools/`. Internal analysis: `analysis/`. Project notes: `docs/`.
- OCR inputs and outputs: `source_ocr/`.
- Test files: `tools/tests/`. OCR text used by the parsers: `source_ocr/`.
