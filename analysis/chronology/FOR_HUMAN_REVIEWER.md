# Current review: unresolved chronology and open issues

**Status snapshot: 15 November 2026.** This is a current-state decision sheet.
The app's February 8 records, reply links, page maps, guide links, and
source-read Slack labels on pp.21-24, p.35, and pp.64-65 are corrected in the
current `po-sources-and-boxes` branch. The current Part 1 time-check output
still has four rows, detailed in U3-U4 below. The user reported that the Part
1 Medium edits were applied and Part 2/cross-reference edits were in progress;
the live article has not been independently checked.

Only active questions and decisions are listed in U and O. Earlier U numbers,
resolved items, and rebuild history are not current action items. The detailed
evidence and prior classifications are preserved in
[`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md), especially Part 3.1.
The current app records and page maps were checked in this branch; cited
source-image readings were rechecked on 15 November unless marked otherwise.

## U. Still unresolved: source/time questions needing human review

| Code | Current unresolved item and evidence | What would resolve it |
|---|---|---|
| **U1** | **Farrar's 09:45/09:46 request copies.** `po-emails.pdf` p.57 quotes `Sent: 08 February 2020 09:45` inside Ferguson's reply; the Dutch quote inside Fouchier's p.55 reply and the German copy in `farrar-fauci-comms.pdf` pp.59-60 print 10:45. Vallance quotes a near-identical 09:46 copy on `farrar-fauci-comms.pdf` p.62. The minute difference and similar text do not establish whether these are separate sends or different renderings. | An original-message identifier, mailbox/export metadata, or another independent copy that establishes whether they are one message or two. Without that evidence, do not claim either identity or separate sending as fact. |
| **U2** | **Rambaut's quoted 4:16 PM clock.** `po-emails.pdf` p.51 prints `Saturday, February 8, 2020 4:16 PM` inside Fouchier's top-level REV message. The quote is nested, so REV's page-owner clock does not establish Rambaut's quoted clock. Eastern is plausible but not proven. The app preserves the printed date and leaves the normalized time unresolved. | An exact copy with an offset or other independent evidence of the client clock that rendered the quoted block. Until then, preserve the printed time without assigning a timezone. |
| **U3** | **Holmes's p.55 date.** `slack_part1_time_check.csv` records Garry 05:05 on 19 Feb at p.52 followed by Holmes 02:16 at p.55. The intervening pp.53-54 are an attachment. There is no day chip above Holmes on p.55; the later Feb. 20 chip does not establish whether this post is Feb. 19 or 20. The screenshot label was rechecked, but the date remains unresolved. | An independent date anchor for Holmes's post. Do not assign Feb. 19 or 20 solely from the current page divider placement. |
| **U4** | **Three remaining Slack Part 1 time-check rows.** The current `slack_part1_time_check.csv` lists: p.42→43 (15 Feb), redacted 19:14 → Garry 01:34; p.47 (17 Feb), Garry 14:02 → redacted 12:15; and p.134→135 (21 Apr), Holmes 23:42 → redacted 13:36. These rows have not been independently settled by the 15 November source-page recheck. | Check the relevant page images for exact labels, message order, and any day divider across the page boundary; update only readings confirmed by the source. |

## O. Open non-datetime issues

| Code | Current issue and evidence | Decision or action needed |
|---|---|---|
| **O1** | **Section 4.11 chapter citation.** Its title says “Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)” but the current link points to `farrar-fauci-comms.pdf` p.137, 15:50 (“Please include Francis Collins…”), which is not the WHO proposal. The candidate Farrar message is p.108, `Sunday, February 2, 2020 4:48 AM` (23:48 ET on 1 Feb), also inconsistent with 3:59 pm. | Identify the intended message, or confirm that the title's time is wrong; then correct the chapter link/title. |

No other open non-datetime reviewer decision is identified in the current
audit. The February 8 §15.2 link and the affected app record/page-map links are
corrected in the current branch; see Part 3.1 for the evidence.

## Historical context

This file intentionally does not repeat resolved former-U questions or their
old item numbers. For the broader method, prior classifications, and
source-specific history, see Parts 1-2 and 5 of
[`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md). Generated check
locations are listed in [`../README.md`](../README.md) and
[`../../tools/README.md`](../../tools/README.md).
