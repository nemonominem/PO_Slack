# Current project status

The `po-sources-and-boxes` branch includes the February 8 correspondence
corrections (`d311367`) and the updated article PDFs/section guide (`c0f6933`).
The app's current generated-data inventory is 13,087 timeline entries across
five sources. The guide indexes 221 article sections and 322 citations; the
Complementary view currently has 11 trimmed PDFs.

The Part 1 Medium article reordering and chronology corrections have been
applied by the user. Cross-references and Part 2 edits for §§14.4, 15.2 and
15.3 were still in progress at the last report; the live Medium article has
not been independently checked here. The checked-in guide still contains
evidence/date and chapter-link inconsistencies described in
[`analysis/chronology/ZONE_AND_DATE_ANALYSIS.md`](analysis/chronology/ZONE_AND_DATE_ANALYSIS.md).

**Open source questions:** whether Farrar's 09:45 and 09:46 copies are
separate sends or renderings; the timezone of Rambaut's quoted 4:16 PM stamp;
OCR/time-label mismatches on Slack Part 1 PDF pp.21-24; and two unresolved
Slack Part 1 time-check items (pp.35 and 52-55). The p.64-65 item has a likely
14:44 correction in an OCR status note, but the app and generated time-check
CSV still contain 01:44 and need reconciliation. A fresh app-data check also
found that PO idx 92's page map spans pp.70-145; its correct page was not
reverified against the PDF during the documentation pass. These should not be
treated as settled by the article edits.

See [`README.md`](README.md) for the application overview,
[`docs/SPEC.md`](docs/SPEC.md) for current data and parser rules, and
[`docs/history/DEVELOPMENT_LOG.md`](docs/history/DEVELOPMENT_LOG.md) for the
preserved implementation history.
