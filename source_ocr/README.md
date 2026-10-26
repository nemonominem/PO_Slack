# source_ocr: OCR text used by the parsers (not published)

Text recognised from the scanned releases. The parsers in `tools/` read these; the app does not.

- `slack-part1_ocr.txt`: Slack Part 1 (screenshots). Made by `tools/reocr_part1.py`.
- `part2_ocr_pages.json`: Slack Part 2 page text. Read by `tools/parse_part2.py`.
- `po-emails_ocr.txt`, `po-emails_ocr_pages.json`: PO emails. Made by `tools/reocr_po_emails.py`.
- `farrar-fauci-comms_ocr.txt`: Farrar-Fauci correspondence. Made by `tools/reocr_farrar_fauci.py`.
