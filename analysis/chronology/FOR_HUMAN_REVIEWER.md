# Current review: source questions, open issues, and article alignment

**Status snapshot: 16 November 2026.** This is a current-state decision sheet.
The app's February 8 records, reply links, page maps, guide links, and
source-read Slack labels on pp.21-24, p.35, and pp.64-65 are corrected in the
current po-sources-and-boxes branch. The current Part 1 time-check output
still has four rows, detailed in U3-U4 below. The user reported that earlier
Part 1 Medium edits were applied; the live article has not been independently
checked. Current cross-check edits to the article are listed separately below,
not as source uncertainties or app issues.

Only active questions and decisions are listed in U and O. Earlier U numbers,
resolved items, and rebuild history are not current action items. The detailed
evidence and prior classifications are preserved in
[the chronology audit](ZONE_AND_DATE_ANALYSIS.md), especially Part 3.1.
The current app records and page maps were checked in this branch; cited
source-image readings were rechecked on 15 November unless marked otherwise.

## U. Still unresolved: source/time questions needing human review

**U1 — Farrar's 09:45 and 09:46 request copies.** The copies in
[PO email pages 55-57](../../page_based/main_sources/po-emails.pdf) and
[Farrar-Fauci pages 59-62](../../page_based/other_sources/farrar-fauci-comms.pdf)
show a one-minute difference, but do not establish whether these are two sends
or different renderings. Resolve only with an original-message identifier,
mailbox/export metadata, or another independent copy; do not claim identity or
separate sending as fact without it.

**U2 — Rambaut's quoted 4:16 PM clock.** [PO email p.51](../../page_based/main_sources/po-emails.pdf)
places the stamp inside Fouchier's top-level REV message. That does not establish
Rambaut's clock for the nested quote; Eastern is plausible but unproven, and the
app leaves its normalized time unresolved. An exact copy with an offset or
independent evidence of the quoting client's clock would resolve this.

**U3 — Holmes's p.55 date.** The
[Part 1 time-check list](../slack_part1_time_check.csv) places Garry's Feb. 19
post on p.52 and Holmes's 02:16 post on p.55, with an attachment on pp.53-54.
There is no day chip above Holmes, and the later Feb. 20 chip does not settle
whether this post belongs to Feb. 19 or 20. An independent date anchor is
needed; do not infer the date from divider placement alone.

**U4 — Three remaining Slack time checks.** The
[Part 1 time-check list](../slack_part1_time_check.csv) flags pp.42-43, p.47,
and pp.134-135. The exact labels and page-to-page sequence still need source
image review; these rows were not settled by the 15 November recheck.

## O. Open non-datetime issues

**O1 — Section 4.11 chapter citation.** Its title gives Farrar's WHO proposal as
1 February at 3:59 pm EST, but the linked
[Farrar-Fauci p.137](../../page_based/other_sources/farrar-fauci-comms.pdf)
shows a 15:50 message about including Francis Collins, not the WHO proposal.
The candidate message on p.108 is stamped 4:48 AM on 2 February (23:48 ET on
1 February), also inconsistent with the title. Identify the intended message
or confirm the title time is wrong, then correct the link/title.

No other open non-datetime reviewer decision is identified in the current
audit. The February 8 §15.2 link and the affected app record/page-map links are
corrected in the current branch; see Part 3.1 for the evidence.

## Current article alignment

These are the remaining wording/caption checks for the live [Medium
article](https://gillesdemaneuf.medium.com/summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506),
not unresolved source questions. The live text has not been independently
checked; see
[the detailed article-claim cross-check](ZONE_AND_DATE_ANALYSIS.md#original-article-claims-checked-and-correction-evidence)
for the source evidence.

**§13.2.** Qualify Vallance as the earliest documented feedback in the checked
copies, not definitively first overall. His 12:03 UK stamp is on
[Farrar-Fauci pp.61-62](../../page_based/other_sources/farrar-fauci-comms.pdf);
an earlier or unproduced reply is not excluded.

**§§13.8-13.10.** Remove exact ordering or simultaneity claims that depend on
assigning a timezone to Rambaut's nested 4:16 PM on
[PO email p.51](../../page_based/main_sources/po-emails.pdf). Describe the Andersen copies
as approximately 21:15-21:16 UK and acknowledge their one-minute variance,
rather than asserting an exact match.

**§13.14 caption.** Treat
[Farrar-Fauci p.61](../../page_based/other_sources/farrar-fauci-comms.pdf)
as the annotated draft, not Ferguson's sent-message header. Attribute
Ferguson's sender and time to [PO email p.57](../../page_based/main_sources/po-emails.pdf):
the stamp is 9 February at 12:00:46 PM on REV, supported as 20:00:46 UK.

**§14.4.** Retain the approximate/inferred “around 9 pm” formulation.
Farrar's 21:27:14 UK message says they had just come off the call, so 21:27
is an end bound, not the call's start or exact time.

The section-numbering mismatch is resolved in the app guide; it is not an
additional Medium article task.

## Historical context

This file intentionally does not repeat resolved former-U questions or their
old item numbers. For the broader method, prior classifications, and
source-specific history, see Parts 1-2 and 5 of
[the chronology audit](ZONE_AND_DATE_ANALYSIS.md). Generated check locations
are listed in the [chronology README](../README.md) and
[tools README](../../tools/README.md).
