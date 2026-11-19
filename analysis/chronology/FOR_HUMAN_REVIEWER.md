# Current review: source questions, open issues, and article alignment

| Area | Current status |
|---|---|
| App/data | February 8 corrections are in the current branch. Slack p.42 and p.47 redactions use estimated placements, and source-visible times on pp.47-48 and dates on p.49 have been corrected. The regenerated Part 1 time-check has one row, involving a redaction-placement estimate; see U4. |
| Medium article | Earlier Part 1 edits were reported applied; the live [article](https://gillesdemaneuf.medium.com/summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506) has not been independently checked. Remaining edits are listed below. |
| Review scope | The user-directed U2 inference and its outstanding source caveat, U4, one open non-datetime issue (O), and article edits are kept separate. Detailed evidence: [chronology audit](ZONE_AND_DATE_ANALYSIS.md). |

## U. Still unresolved: source/time questions needing human review

| Code | Current question | What would resolve it |
|---|---|---|
| **U2** | The user directs the quote-clock rule: the app now treats Rambaut's nested 4:16 PM on [PO p.51](../../page_based/main_sources/po-emails.pdf) as **inferred CET / 15:16 UK / 10:16 ET**. The client setting is not independently established and the contextual timing tension remains. | An offset-bearing copy or independent evidence of the client clock would verify or challenge the inference. |
| **U4** | One Slack time-check row remains, on pp.134-135. The p.42 and p.47 placements are corrected below. The date of the Garry 09:46 message after the large p.48 redaction also remains unverified. | Only source evidence for the obscured messages could resolve their actual times or senders. Do not infer either from an estimated placement. |

### U2: User-directed quote-clock inference and evidence caveat

| Evidence | What it shows |
|---|---|
| [PO p.51](../../page_based/main_sources/po-emails.pdf) | Fouchier's top-level REV stamp is 2:50 PM, supported as Pacific / 22:50 UK. His reply quotes Rambaut at 4:16 PM. If Fouchier's reply client generated that quote header, the quote-clock rule uses that client's clock, not the REV clock. |
| User decision | The user directed: “We use the quopte rule, so captured in Fouchier's timezone.” The app applies the presumed Rotterdam CET client clock: 4:16 PM CET = 15:16 UK / 10:16 ET. The page supplies no offset or client configuration; this is an inference, not a verified offset. Eastern would give 21:16 UK, but is also unproven. |
| Potentially too early | Rambaut's [PO p.51](../../page_based/main_sources/po-emails.pdf) message disputes a no-lab assertion and an argument about other outbreaks; Fouchier's [PO p.55](../../page_based/main_sources/po-emails.pdf) email makes closely related points. Its 11:36:30 AM REV stamp is supported as 19:36:30 UK, over four hours after the proposed 15:16 UK. |
| [Slack p.23](../../page_based/main_sources/slack-part1.pdf) | Garry announces Ron's email at 14:47 ET; Holmes comments at 15:32, Rambaut critiques the other-outbreak argument at 15:43, and Andersen quotes Ron's no-lab claim at 15:53. This is consistent with the later sequence, not proof that the points never appeared earlier. |
| Conclusion | The inferred CET reading creates a chronology tension, not a strict contradiction unless the arguments first appeared in the p.55 email. The user-directed reading is applied; the client clock remains unverified. See [detailed audit](ZONE_AND_DATE_ANALYSIS.md#u2-quote-clock-and-chronology). |

### U4: Slack time-check details

| Case | Printed source and current app/check data | Review needed |
|---|---|---|
| **U4a — corrected placement, [pp.41-43](../../page_based/main_sources/slack-part1.pdf)** | The user confirms Garry's p.43 **13:34** is in Slack Part 1's Eastern timezone. The blacked-out block at the top of p.42 follows Garry **15:44 on Feb. 14** (p.41) and precedes Holmes **22:44 on Feb. 14** (p.42), before the Feb. 15 chip and Garry **08:11**. The pre-existing **19:14** placement equals the midpoint of the two neighboring visible times; its selection rationale is not documented. The parser incorrectly assigned it Feb. 15 by choosing another message on p.42. The app now places idx 432 on **inferred Feb. 14**, retaining **19:14** as an estimated placement; the date and time are both labeled estimated. Holmes 22:44 and Garry 08:11 are restored from the visible headers. | No further user decision is needed for placement. The obscured sender, content, actual time, and any date marker inside the blacked-out area remain unknown; the estimated date/time is not a source-visible stamp. |
| **U4b — 17 Feb, [pp.47-49](../../page_based/main_sources/slack-part1.pdf)** | The records were present, but untimed messages sorted to the end of Feb. 17 and the redaction's old **12:15** estimate sorted before Garry **16:02**. P.47 shows Holmes **16:08**, the blacked-out block, Andersen **16:20**, Garry **16:21**, Holmes **16:22** and **16:39**, and Andersen **16:46**. Their visible times are restored; the redaction now uses **16:14**, the midpoint of 16:08 and 16:20, explicitly as a placement estimate. Other visible p.47 and early p.48 times are restored. On p.49, the visible Feb. 18 chips and sequence support correcting idx 522-528 from Feb. 17 to Feb. 18, and Rambaut idx 529 to **18:52**. | The redacted sender, content and actual time remain unknown; 16:14 is not a source timestamp. The p.48 blacked-out area may conceal a date transition before Garry's visible **09:46**; its date is not established by the visible chips, so app idx 521 remains unchanged and needs source review. |
| **U4c — 21-22 Apr, [pp.134-135](../../page_based/main_sources/slack-part1.pdf)** | The check compares Holmes **23:42** on 21 Apr (idx 1292, “I was just about to send that to you!”) with redacted **13:36** (idx 1296, placement estimate). The image continues with Holmes **23:59**, then p.135 Andersen **00:05** and Garry **07:47**, followed by a redacted block; an Apr. 27 chip appears later. | Review the inferred rollover and placeholder date/placement. The redacted sender and actual time are not visible; 13:36 is not a printed stamp. |

## Applied date inference and app corrections

| Source finding | App action |
|---|---|
| Former U3: [Slack pp.54-55](../../page_based/main_sources/slack-part1.pdf) show the Feb. 19 sequence ending with Andersen **19:32**, followed on p.55 by Holmes **02:16**, Rambaut **05:53**, Garry **06:27/06:40**, Rambaut **06:45/06:57**, and Garry **07:06** near a Feb. 20 chip. Comparing the preceding evening, ordered small-hours messages, page continuity, and chip supports **Feb. 20** for Holmes and the following posts; this is an inference, not a date printed beside Holmes. | Applied: app Part 1 idx **602-607** now use Feb. 20, and idx **608** now carries the visible **07:06**. The p.54-55 time-check row is gone. The rule is documented in [the Slack/date-handling spec](../../docs/SPEC.md#slack-part-1-date-assignment); a backwards time by itself does not establish a rollover. |

## O. Open non-datetime issues

| Code | Current issue | Decision needed |
|---|---|---|
| **O1** | Section 4.11's WHO proposal title says 1 Feb, 3:59 pm EST, but linked [Farrar-Fauci p.137](../../page_based/other_sources/farrar-fauci-comms.pdf) is a 15:50 message about Francis Collins. Candidate p.108 is 4:48 am on 2 Feb (23:48 ET on 1 Feb). | Identify the intended message or confirm the title time is wrong; correct the chapter link/title. |

## Current article alignment

| Section | Required edit | Evidence/status |
|---|---|---|
| **§13.2** | Call Vallance the earliest documented feedback in checked copies, not definitively first overall. | 12:03 UK stamp: [Farrar-Fauci pp.61-62](../../page_based/other_sources/farrar-fauci-comms.pdf); earlier/unproduced replies are not excluded. |
| **§§13.8-13.10** | Reconcile Rambaut's stated 21:16 UK and ordering with the user-directed inferred **15:16 UK** reading; qualify the inference and avoid treating the chronology tension as a proven contradiction. Qualify the Andersen-copy one-minute variance (about 21:15-21:16 UK). | Rambaut's nested 4:16 PM on [PO p.51](../../page_based/main_sources/po-emails.pdf) has no printed offset; inferred CET places it before the other messages in §13.8's current 20:11–21:16 UK heading. The live Medium text needs checking. |
| **§13.14 caption** | Treat p.61 as annotation; cite p.57 for Ferguson's sender and time. | [Farrar-Fauci p.61](../../page_based/other_sources/farrar-fauci-comms.pdf) is the annotated draft; [PO p.57](../../page_based/main_sources/po-emails.pdf) gives 9 Feb 12:00:46 PM REV, supported as 20:00:46 UK. |
| **§14.4** | Retain approximate/inferred “around 9 pm”; do not state an exact call time. | Farrar's 21:27:14 UK message says they had just come off the call, so 21:27 is an end bound. |
| App guide | No article edit: the section-numbering mismatch is resolved in the app. | Current app branch. |

## Historical context

| Reference | Contents |
|---|---|
| [Chronology audit](ZONE_AND_DATE_ANALYSIS.md), Parts 1-2 and 5 | Broader method, prior classifications, and source-specific history; resolved former-U items are not repeated above. |
| [Chronology README](../README.md) and [tools README](../../tools/README.md) | Generated check locations. |
