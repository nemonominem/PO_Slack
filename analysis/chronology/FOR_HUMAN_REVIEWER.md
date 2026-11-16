# Current review: source questions, open issues, and article alignment

| Area | Current status |
|---|---|
| App/data | February 8 corrections are in the current branch. The inferred Feb. 20 rollover across Slack pp.54-55 and visible Garry times on pp.43 and 47 are corrected in the app. The regenerated Part 1 time-check has three rows, all involving redaction-placement estimates; see U4. |
| Medium article | Earlier Part 1 edits were reported applied; the live [article](https://gillesdemaneuf.medium.com/summary-proximal-origin-a-tragicomedy-of-our-times-1ed5b4dae506) has not been independently checked. Remaining edits are listed below. |
| Review scope | Two unresolved source/time groups (U2 and U4), one open non-datetime issue (O), the applied app date inference, and article edits are kept separate. Detailed evidence: [chronology audit](ZONE_AND_DATE_ANALYSIS.md). |

## U. Still unresolved: source/time questions needing human review

| Code | Current question | What would resolve it |
|---|---|---|
| **U2** | What timezone applies to Rambaut's nested 4:16 PM on [PO p.51](../../page_based/main_sources/po-emails.pdf)? The quote-clock rule and the potentially too-early CET reading are detailed below. | An offset-bearing copy or independent evidence of the client clock that generated the quote header. |
| **U4** | Three Slack time-check rows remain, but the visible Garry labels on pp.43 and 47 are corrected. The rows now involve estimated redaction placements, not verified source timestamps. Details are below. | Only source evidence for the obscured messages could resolve their actual times or dates. Do not infer a redacted sender or timestamp from an estimated placement. |

### U2: Why the quote clock remains uncertain

| Evidence | What it shows |
|---|---|
| [PO p.51](../../page_based/main_sources/po-emails.pdf) | Fouchier's top-level REV stamp is 2:50 PM, supported as Pacific / 22:50 UK. His reply quotes Rambaut at 4:16 PM. If Fouchier's reply client generated that quote header, the quote-clock rule uses that client's clock, not the REV clock. |
| Rotterdam hypothesis | If that client used CET, 4:16 PM would be 15:16 UK / 10:16 ET. The page supplies no offset or client configuration; Fouchier's location alone does not establish it. Eastern would give 21:16 UK, but is also unproven. |
| Potentially too early | Rambaut's [PO p.51](../../page_based/main_sources/po-emails.pdf) message disputes a no-lab assertion and an argument about other outbreaks; Fouchier's [PO p.55](../../page_based/main_sources/po-emails.pdf) email makes closely related points. Its 11:36:30 AM REV stamp is supported as 19:36:30 UK, over four hours after the proposed 15:16 UK. |
| [Slack p.23](../../page_based/main_sources/slack-part1.pdf) | Garry announces Ron's email at 14:47 ET; Holmes comments at 15:32, Rambaut critiques the other-outbreak argument at 15:43, and Andersen quotes Ron's no-lab claim at 15:53. This is consistent with the later sequence, not proof that the points never appeared earlier. |
| Conclusion | The CET reading creates a chronology tension, not a strict contradiction unless the arguments first appeared in the p.55 email. U2 remains open; see [detailed audit](ZONE_AND_DATE_ANALYSIS.md#u2-quote-clock-and-chronology). |

### U4: Slack time-check details

| Case | Printed source and current app/check data | Review needed |
|---|---|---|
| **U4a — 15 Feb in check, [pp.42-43](../../page_based/main_sources/slack-part1.pdf)** | The regenerated check compares a redacted **19:14** (app idx 432, placement estimate, not a visible stamp) with Garry **13:34** (idx 442). The redaction is at the top of p.42, before Holmes **22:44** and the Feb. 15 chip; p.42 ends with Rambaut **13:31** on figure numbering. Garry's p.43 continuation “Ok - that confused me” visibly says **13:34**; the app now matches the page. | The obscured sender, content and actual time cannot be read from the PDF. Keep 19:14 labeled as an estimate; do not infer a real timestamp or use the resulting backwards check row as proof of chronology. |
| **U4b — 17 Feb, [p.47](../../page_based/main_sources/slack-part1.pdf)** | The regenerated check compares Garry **16:02** (idx 508, “I think that's an artifact”) with redacted **12:15** (idx 510, placement estimate). The image shows Garry **16:02**, then Holmes **16:08** on pangolin sequences; the redacted block follows before Andersen **16:20**. The app now matches Garry's visible label; no redacted time or sender is visible. | Keep 12:15 labeled as an estimate, not a printed timestamp. The obscured sender, content and actual time cannot be read from the PDF. |
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
| **§§13.8-13.10** | Remove exact ordering/simultaneity claims depending on Rambaut's timezone; qualify the Andersen-copy one-minute variance (about 21:15-21:16 UK). | Rambaut's nested 4:16 PM on [PO p.51](../../page_based/main_sources/po-emails.pdf) has no established timezone. |
| **§13.14 caption** | Treat p.61 as annotation; cite p.57 for Ferguson's sender and time. | [Farrar-Fauci p.61](../../page_based/other_sources/farrar-fauci-comms.pdf) is the annotated draft; [PO p.57](../../page_based/main_sources/po-emails.pdf) gives 9 Feb 12:00:46 PM REV, supported as 20:00:46 UK. |
| **§14.4** | Retain approximate/inferred “around 9 pm”; do not state an exact call time. | Farrar's 21:27:14 UK message says they had just come off the call, so 21:27 is an end bound. |
| App guide | No article edit: the section-numbering mismatch is resolved in the app. | Current app branch. |

## Historical context

| Reference | Contents |
|---|---|
| [Chronology audit](ZONE_AND_DATE_ANALYSIS.md), Parts 1-2 and 5 | Broader method, prior classifications, and source-specific history; resolved former-U items are not repeated above. |
| [Chronology README](../README.md) and [tools README](../../tools/README.md) | Generated check locations. |
