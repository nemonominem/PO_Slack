# Current review: unresolved chronology and open issues

**Status snapshot: 15 November 2026.** This is a current-state decision sheet.
The items below are the only open questions being carried here; resolved
questions, previous U numbers, test history, and rebuild narratives are
intentionally excluded. The detailed source audit is in
[`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md), especially Part 3.1
for the February 8 chain.

The app's JSON, chapter links, and page maps were checked at commit
`0dff257` on `po-sources-and-boxes`. PDF-image interpretations and cross-release
comparisons identified below come from the earlier chronology audit and were
not reopened during this document revision. The user reported that the Part 1
Medium edits were applied and Part 2/cross-reference edits were in progress;
the live article has not been independently checked.

## U. Still unresolved: source/time questions needing human review

Only items whose source reading or interpretation can still be clarified are
listed here. A printed stamp is not the same as a verified timezone.

| Code | Unresolved item and evidence | What would resolve it |
|---|---|---|
| **U1** | **Farrar's 09:45/09:46 request copies.** `po-emails.pdf` p.57 quotes `Sent: 08 February 2020 09:45` inside Ferguson's reply; the Dutch quote inside Fouchier's p.55 reply and the German copy in `farrar-fauci-comms.pdf` pp.59-60 print 10:45. Vallance quotes a near-identical 09:46 copy on `farrar-fauci-comms.pdf` p.62. The minute difference and similar text do not establish whether these are separate sends or different renderings. | An original-message identifier, mailbox/export metadata, or another independent copy that establishes whether they are one message or two. Without that evidence, do not claim either identity or separate sending as fact. |
| **U2** | **Rambaut's quoted 4:16 PM clock.** `po-emails.pdf` p.51 prints `Saturday, February 8, 2020 4:16 PM` inside Fouchier's top-level REV message. The quote is nested, so REV's page-owner clock does not establish Rambaut's quoted clock. Eastern is plausible but not proven. | An exact copy with an offset or other independent evidence of the client clock that rendered the quoted block. Until then, preserve the printed time and mark its timezone unresolved. |
| **U3** | **Slack Part 1 time labels around pp.21-24.** The app/source records disagree with the previously audited screenshot labels: p.21 Garry 08:09 is absent at idx 245 and Rambaut 08:30 is stored as 05:20 at idx 246; p.22 Garry 08:43 is absent at idx 247; p.23 Garry 14:47 and Holmes 15:32 are absent at idxs 261-262 and Andersen 15:53 is stored as 15:59 at idx 265; p.23 Andersen 16:21 and Garry 16:30 are absent at idxs 269-270. P.24 Holmes 18:42 is present at idx 277. | Re-read the cited screenshots and reconcile the message labels/record associations. These are source/OCR checks, not timezone choices. |
| **U4** | **Remaining Slack Part 1 backward-time checks.** `slack_part1_time_check.csv` still lists p.35 Garry 18:22 followed by Rambaut 16:21, and p.52 Garry 05:05 followed by Holmes 02:16 at the top of p.55; pp.53-54 are an attached document. The latter may be a day-divider issue. The same CSV still labels the p.65 “No polybasic site, HOWEVER…” line as Andersen 01:44, while `analysis/slack-qa/grok_slack_part1_times_STATUS.md` reports Robert Garry 14:44. | Check p.35's label and the p.55 day divider; verify p.65's printed time and sender. Apply only page-confirmed corrections, then regenerate the time-check report. |

## O. Open non-datetime issues

| Code | Current issue and evidence | Decision or action needed |
|---|---|---|
| **O1** | **Section 4.11 chapter citation.** Its title says “Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)” but the current link points to `farrar-fauci-comms.pdf` p.137, 15:50 (“Please include Francis Collins…”), which is not the WHO proposal. The candidate Farrar message is p.108, `Sunday, February 2, 2020 4:48 AM` (23:48 ET on 1 Feb), also inconsistent with 3:59 pm. | Identify the intended message, or confirm that the title's time is wrong; then correct the chapter link/title. |
| **O2** | **Section 15.2 chapter link.** Current `page_based/chapter_links.json` links Part 2 §15.2 to Ferguson, PO idx 93 (`2020-02-09 15:00 ET`). The section is about Koopmans's 9 Feb 20:07 UK message, currently PO idx 94 (`2020-02-09 23:07 ET`) with a blank sender. The earlier source audit places Koopmans on `po-emails.pdf` p.69. | Correct the target to the verified Koopmans record after fixing its sender/time normalization; do not leave the link on Ferguson. |

## App/data follow-up (not user decisions)

These are known maintenance defects, not questions for the reviewer to guess
at. The underlying source interpretations are from the earlier audit; current
record fields were checked at `0dff257`.

| Record/surface | Current checked state |
|---|---|
| PO idx 83 | p.51; Fouchier's top-level `2/8/2020 2:50:00 PM` is normalized to 09:50 ET using Farrar/London. The earlier source audit identifies it as a top-level REV stamp, for which Pacific would give 17:50 ET / 22:50 UK. |
| PO idx 84-85 | Idx 84 has the corrected 04:45 ET key and pp.57-58 map; idx 85 has the 14:36 ET key and pp.55-56 map. These were confirmed in current app data. |
| PO idx 91-92 | Idx 91 is Rambaut's p.51 4:16 PM quote and remains covered by U2. Idx 92 is Andersen's 21:16 quote, currently normalized to 00:16 ET on 9 Feb; the earlier audit's parallel Koopmans copy supports about 16:15-16:16 ET / 21:15-21:16 UK on 8 Feb. Its current page map spans pp.70-145, which is an evident mapping defect; its exact replacement range still needs a source-page check. |
| PO idx 93-95 | Idx 93 identifies Ferguson at 15:00 ET on p.57 but has no `reply_to`. Idx 94 is Koopmans's p.69 20:07 quote, but its sender is blank and it is normalized to 23:07 ET. Idx 95 is Farrar's p.69 `2/10/2020 1:26:57 AM`, normalized to 01:26 ET with `zone_assumed` incorrectly naming Lipkin; the earlier audit's explicit-offset copy in `farrar-fauci-comms.pdf` p.55 gives 04:26:57 ET / 09:26:57 UK. |
| Article/app status | The February 8 correction commit `d311367` is an ancestor of `po-sources-and-boxes`; its source branch reported 160/160 tests passing. That prior test result does not establish that the current residuals above are fixed. The reported Part 1 article edits, remaining Part 2 §§14.4/15.2/15.3 and cross-references, and the live Medium state have not been independently verified here. |

## Historical material

Earlier classifications and resolved former-U questions are not current
requests and are not repeated here. See Parts 1-2 and 5 of
[`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md) for the broader
datetime method and prior evidence. Generated checks and their locations are
listed in [`../README.md`](../README.md) and [`../../tools/README.md`](../../tools/README.md).
