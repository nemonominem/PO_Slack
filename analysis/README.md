# Internal analyses and generated reports

This directory contains audit evidence and working reports. It is not served
by the static app. Current product documentation lives in [`../docs/`](../docs/).

## Topics

| Folder | Contents |
|---|---|
| [`chronology/`](chronology/) | Source-based email/time-zone audit and reviewer index. Start with [`FOR_HUMAN_REVIEWER.md`](chronology/FOR_HUMAN_REVIEWER.md); detailed February 8 findings are in [`ZONE_AND_DATE_ANALYSIS.md`](chronology/ZONE_AND_DATE_ANALYSIS.md). |
| [`slack-qa/`](slack-qa/) | Preserved OCR review prompts, status notes, and page-specific Slack checks. These are historical work records; consult [`chronology/FOR_HUMAN_REVIEWER.md`](chronology/FOR_HUMAN_REVIEWER.md) for the latest unresolved items. |
| [`source-links/`](source-links/) | Generated unresolved-link report, plus any supporting scan data. Rebuild the Markdown report with `python3 tools/build_url_report.py`. |
| `_OldStuff/` | Locally archived, git-ignored private notes; not included in the repository. |

## Generated evidence

The scripts in [`../tools/README.md`](../tools/README.md) write CSV and text
reports directly here, including the datetime audit, reply-order checks,
Slack Part 1 time checks, and chapter-link reports. Do not edit generated
outputs by hand; make evidence-backed changes in the corresponding source
data, parser, or verified overrides and regenerate them.

The February 8 article/app audit is scoped to the correspondence chain and
directly dependent passages. It distinguishes verified source stamps from
timezone interpretations that remain supported or unresolved.
