# Current review: source questions, open issues, and article alignment

**Status snapshot: 16 November 2026.** This is a current-state decision sheet.
App records, page maps, guide links, and source-read Slack labels are corrected
in the current po-sources-and-boxes branch. The live Medium article has not
been independently checked.

The tables below separate unresolved source questions (U), open non-datetime
issues (O), and article edits. Detailed evidence is in the
[chronology audit](ZONE_AND_DATE_ANALYSIS.md), Part 3.1.

## U. Still unresolved: source/time questions needing human review

| Code | Current question | What would resolve it |
|---|---|---|
| **U1** | Are Farrar's 09:45 and 09:46 request copies separate sends or different renderings? The checked copies differ by one minute. ([PO pp.55-57](../../page_based/main_sources/po-emails.pdf); [Farrar-Fauci pp.59-62](../../page_based/other_sources/farrar-fauci-comms.pdf)) | An original-message identifier, mailbox/export metadata, or another independent copy. |
| **U2** | What timezone applies to Rambaut's nested 4:16 PM stamp on [PO p.51](../../page_based/main_sources/po-emails.pdf)? Eastern is plausible, not established; the app leaves normalized time unresolved. | An exact copy with an offset or independent evidence of the quoting client's clock. |
| **U3** | Is Holmes's Slack post on p.55 dated Feb. 19 or 20? There is no day chip above it; pp.53-54 are an attachment. ([Time-check list](../slack_part1_time_check.csv)) | An independent date anchor; do not infer the date from divider placement alone. |
| **U4** | Three Slack time checks remain unsettled: pp.42-43, p.47, and pp.134-135. ([Time-check list](../slack_part1_time_check.csv)) | Review source images for labels, ordering, and any day divider across the page boundary. |

## O. Open non-datetime issues

| Code | Current issue | Decision needed |
|---|---|---|
| **O1** | Section 4.11's WHO proposal title says 1 Feb, 3:59 pm EST, but linked [Farrar-Fauci p.137](../../page_based/other_sources/farrar-fauci-comms.pdf) is a 15:50 message about Francis Collins. Candidate p.108 is 4:48 am on 2 Feb (23:48 ET on 1 Feb). | Identify the intended message or confirm the title time is wrong; correct the chapter link/title. |

No other open non-datetime reviewer decision is identified in the current
audit. The February 8 §15.2 link and the affected app record/page-map links are
corrected in the current branch; see Part 3.1 for the evidence.

## Current article alignment

These are current cross-check edits for the live [Medium article](https://gillesdemaneuf.medium.com/summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506),
not unresolved source questions. The live text has not been independently
checked. See the [detailed article-claim cross-check](ZONE_AND_DATE_ANALYSIS.md#original-article-claims-checked-and-correction-evidence).

| Section | Required edit | Evidence/status |
|---|---|---|
| **§13.2** | Call Vallance the earliest documented feedback in checked copies, not definitively first overall. | 12:03 UK stamp: [Farrar-Fauci pp.61-62](../../page_based/other_sources/farrar-fauci-comms.pdf); earlier/unproduced replies are not excluded. |
| **§§13.8-13.10** | Remove exact ordering/simultaneity claims depending on Rambaut's timezone; qualify the Andersen-copy one-minute variance (about 21:15-21:16 UK). | Rambaut's nested 4:16 PM on [PO p.51](../../page_based/main_sources/po-emails.pdf) has no established timezone. |
| **§13.14 caption** | Treat p.61 as annotation; cite p.57 for Ferguson's sender and time. | [Farrar-Fauci p.61](../../page_based/other_sources/farrar-fauci-comms.pdf) is the annotated draft; [PO p.57](../../page_based/main_sources/po-emails.pdf) gives 9 Feb 12:00:46 PM REV, supported as 20:00:46 UK. |
| **§14.4** | Retain approximate/inferred “around 9 pm”; do not state an exact call time. | Farrar's 21:27:14 UK message says they had just come off the call, so 21:27 is an end bound. |

The section-numbering mismatch is resolved in the app guide; it is not an
additional Medium article task.

## Historical context

This file intentionally does not repeat resolved former-U questions or their
old item numbers. For the broader method, prior classifications, and
source-specific history, see Parts 1-2 and 5 of
[the chronology audit](ZONE_AND_DATE_ANALYSIS.md). Generated check locations
are listed in the [chronology README](../README.md) and
[tools README](../../tools/README.md).
