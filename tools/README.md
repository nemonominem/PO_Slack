# tools: scripts that build the data

Run from this folder. Each script reads and writes `../page_based/` (the data the app
serves) and `../analysis/` (internal reports). The shared parser is `foia_parser`,
in `Edition/foia_parser` (set `PYTHONPATH` to it).

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
