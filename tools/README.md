# tools: scripts that build the data

Run from this folder. Each script reads and writes `../page_based/` (the data the app
serves) and `../analysis/` (internal reports). The shared parser is `foia_parser`,
in `Edition/foia_parser` (set `PYTHONPATH` to it).

## Rebuild order (Slack)
`parse_part1.py`, `parse_part2.py` (needs `slack_notice.py`). Standard time is New York time (ET):
Part 1 is already Eastern; Part 2 is on Pacific time and is converted to ET (+3 h) here, keeping the
printed Pacific time in `stamp_line`.

`slack_time_check.py` lists the places where Part 1 times run backwards (`../analysis/slack_part1_time_check.csv`).
`slack_date_fixes.json` holds hand-checked day corrections for Part 1, each with its evidence; `parse_part1.py` applies them.

## Rebuild order (emails)
1. `parse_po_emails.py`, `parse_farrar_fauci.py`: parse the OCR text into entries.
2. `anchor_copies.py`: rule 1b (exact copy with an explicit offset).
3. `apply_verified_overrides.py`: rule 1c. Applies the hand-checked corrections in
   `verified_overrides.json`, each with its evidence. Add an entry there only when a page
   image or the message text fixes both the time and its clock.
4. `dedupe_same_instant.py`: remove duplicates and repoint links; also rebuilds the audit file.
5. `build_chapter_links.py`: links boxes to Tragicomedy sections.
6. `build_bookmark_rekey.py`: maps old bookmark keys to current keys.
7. `build_zone_audit.py`: `analysis/zone_format_audit.csv` (run by step 4 as well).

After a rebuild, check: no dangling or one-sided reply links, no reply before its parent.

- `entry_ref.py`: turns a `PO n` / `FF n` entry number into its PDF pages, printed header and subject (for the analysis docs).

## Checks (write to `analysis/`)
- `owner_zone_check.py`: exact-copy pairs for page owners.
- `reply_order_check.py`: reply-order test by zone group.

## Tests
- `tests/`: checks for the app (see `tests/README.md`).

## Other
- `parse_part1.py`, `parse_part2.py`, `parse_sscp.py`: Slack and draft parsers.
- `reocr_*.py`: re-run OCR on pages.
- `build_po_guide.py`, `build_article_page_map.py`, `fetch_complementary.py`: guide and article data.
- `audit_app.py`, `slack_notice.py`: utilities; not part of the email rebuild.
