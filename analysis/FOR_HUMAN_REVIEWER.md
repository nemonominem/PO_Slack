# Where the dates and times stand: what is settled, what is likely, what is unknown

Status 2026-11-05 (emails: last rebuild of 2026-11-01; Slack Part 1 times: 2026-11-05). This is the only file with things for you to look at.
The evidence and the method are in [`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md).

**How to answer:** reply in chat with the code and your answer (for example “U10: keep London”, “O1: it is p.108”).
Any order; skip what you like. Nothing changes until you answer.

**How entries are named.** Never by number: PDF file and pages, the header exactly as printed, the sender, the subject.
Slack messages: PDF page, printed time, sender, first words.

**Standard time.** The web app shows every date and time in New York time (ET) first, then the local time as printed.

---

# 1. Definitions

| Level | Code | Meaning |
|---|---|---|
| **Settled** | S | Something in the documents, or your decision, fixes the clock. The time is as good as the source. |
| **Likely** (= *Supported*) | L | A rule gives the clock, and every test passes (no reply before the message it answers, no time travel), but nothing proves it. Consistency only rules zones out. Moves to Settled if an anchor turns up. |
| **Unknown** (= *Not settled*, right now) | U | No rule that gives a clock can be used, or the test cannot decide: the time is a guess from where the sender works. |

In `zone_format_audit.csv` the column `zone_status` says Settled, Supported (= Likely) or Not settled (= Unknown).

# 2. Rules: what settles, what only gives “likely”, and where nothing works

The full text, with examples, is in [`ZONE_AND_DATE_ANALYSIS.md`](ZONE_AND_DATE_ANALYSIS.md) section 5
(5.1 the rules in order, 5.6 the freeze rule with the Holmes/Rambaut example, 5.7 the tricks, 5.9 the quoter lookup) and, for reuse on other releases, in the toolkit:
[`SKILL.md`](https://github.com/nemonominem/Edition_Toolkit/blob/nested-header-split/skill/foia-datetime-resolution/SKILL.md) and
[`freeze-rule-and-tricks.md`](https://github.com/nemonominem/Edition_Toolkit/blob/nested-header-split/skill/foia-datetime-resolution/freeze-rule-and-tricks.md).

| Rule | Can it settle? | What it does |
|---|---|---|
| **1. Zone written in the stamp** (`+0000`, `AEDT`, `UTC-05:00`) | **Settles** | The stamp says which clock. |
| **1b. Exact copy with an explicit offset** | **Settles** | The same message elsewhere carries a zone: take its instant. |
| **1c. Anchor in the page or the message** (page image, “It is 10pm now UK”, a calendar such as the NAS panel 2:00-3:30 pm ET, the 1 Feb call) | **Settles** | The text or a known event fixes the time and its clock. |
| **Bracketing** (a message lying between two exactly timed ones less than 1 h apart) | **Settles** if one whole-hour offset survives; otherwise narrows | The message was sent inside that hour. |
| **Your decision** (e.g. REV is Pacific, Slack Part 1 is Eastern) | **Settles** | Recorded with its evidence. |
| **2. Freeze rule** (a quoted block is on the clock of the person who quoted it; **physically nested under a block on the same page counts as quoted**, a header that opens a page does not) | Likely only | Needs to know where the quoter is: a lookup of where people live, in the parser (5.9). Nothing in the stamp proves it. |
| **3/4. Mailbox rule** (a top-level stamp is on the clock of the mailbox that shows it: REV Pacific, GARRY Chicago, LIP Eastern; the convener's mailbox London) | Likely only | The owner's clock; reply order cannot catch a stamp that is simply too early. |
| **Sender's institution** (where the sender works) | Likely only if the reply-order test passes with enough pairs; otherwise Unknown | A stand-in for the sender's clock. |
| **Reply-order test** | Never settles | Rules zones out (a reply cannot precede its parent). |
| **An unquoted message with no other support** (the last message of a thread, or only an inferred “same conversation” link) | **Nothing works** | The freeze rule needs a quote; a header that opens a page may be a different extract, and an inferred link does not prove a quote. The time is Unknown until an anchor turns up. |

# 3. Where we stand

| Level | Emails | Slack |
|---|---|---|
| **Settled** | 123 | Part 1 (1,256 messages): Eastern; Part 2 (11,351): Pacific, converted to ET |
| **Likely** | 260 | none |
| **Unknown** | 0 | the 3 backwards times in Part 1 (see U17) |

---

# S. Settled: nothing for you to do

### S1. Zone written in the stamp (53 emails: 45 Farrar-Fauci, 8 P.O.)
The stamp carries the zone. Rule 1.

### S2. One exact copy with an explicit offset
`po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]”, equals `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”. Rule 1b. It also anchors REV (S4).

### S3. Verified from the page image, the message text or a calendar (25 entries; the Koopmans and notice copies count once each below)
Rule 1c. Each is in `tools/verified_overrides.json` with its evidence.

| Where | Header as printed | Now (ET) | Evidence |
|---|---|---|---|
| `po-emails.pdf` p.2, Farrar, “Re: Phone call” | Friday, January 31, 2020 5:57 PM | 31 Jan 17:57 | Quoted in Fauci's reply, so Eastern; same message in `farrar-fauci-comms.pdf` p.154 |
| `po-emails.pdf` pp.3-4, Farrar, “Phone call” | Friday, January 31, 2020 5:23 PM | 31 Jan 17:23 | “It is 10pm now UK” (22:23 UK); the body is now typed from the page |
| `po-emails.pdf` p.3, Conrad on behalf of Fauci, “RE: Phone call” | Friday, 31 January 2020 at 22:34 | 31 Jan 17:34 | Your decision 2026-10-26: Farrar's UK clock, 11 min after his 22:23; sender label and reply link corrected from the page |
| `po-emails.pdf` pp.4-11, Folkers | Friday, January 31, 2020 8:43 PM | 31 Jan 20:43 | Quoted in Fauci's forward stamped 21:47 ET (`farrar-fauci-comms.pdf` p.147), so on Fauci's Eastern clock |
| `po-emails.pdf` pp.17-18, Pope | Sent: Tuesday, February 4, 2020 9:11 AM | 4 Feb 09:11 | Read from the page; copy on p.19: 9:10:35 AM UTC-05:00 |
| `po-emails.pdf` p.78, Andersen | Sent: 12 February 2020 23:09 | 13 Feb 02:09 | Read from the page; Pacific by equality with the p.80 copy (assumed) |
| `farrar-fauci-comms.pdf` pp.154-155, Farrar | Friday, January 31, 2020 5:57 PM | 31 Jan 17:57 | Quoted in Fauci's reply stamped `00:38:35 +0000` |
| `farrar-fauci-comms.pdf` pp.23-31, Gao | Apr 25, 2020 1:22 PM | 25 Apr 13:22 | NAS panel “2:00-3:30 pm ET” in Dzau's quoted invitation; Gao “waiting for being connected” |
| `farrar-fauci-comms.pdf` pp.22-30, Dzau | Saturday, April 25, 2020 3:59 PM | 25 Apr 15:59 | “It was a spectacular session”, after the panel ended |
| `farrar-fauci-comms.pdf` pp.43-44, Esveld | vrijdag 6 maart 2020 09:23 | 6 Mar 03:23 | Read from the page; Dutch client, Netherlands time |
| `farrar-fauci-comms.pdf` p.44, Harris | donderdag 5 maart 2020 15:29 | 5 Mar 09:29 | Read from the page; quoted in Esveld's Dutch client |
| `farrar-fauci-comms.pdf` p.57, Farrar | Datum: Samstag, 8. Februar 2020 um 21:21 | 8 Feb 15:21 | Read from the page; Drosten's German client (Berlin); 20:21 UTC is after Drosten's reply |
| `farrar-fauci-comms.pdf` pp.59-60, Farrar | Datum: Samstag, 8. Februar 2020 um 10:45 | 8 Feb 04:45 | Read from the page; Berlin |
| `po-emails.pdf` pp.57-65, Farrar “FW: 2019 N-CoV” | Sent: 08 February 2020 09:45 | 8 Feb 04:45 | Quoted inside Ferguson's reply, so London (UK date format, 24 h), not REV Pacific; Drosten's German client prints the same message at 10:45 Berlin (U15c) |
| `farrar-fauci-comms.pdf` p.80, Farrar | Sent: Tuesday, February 4, 2020 6:08 AM | 4 Feb 06:08 | Read from the page; quoted in Collins's 6:12 AM reply (Eastern) |
| `farrar-fauci-comms.pdf` pp.169-172, GPMB Secretariat | Sent: martes, 28 de enero de 2020 9:09 | 28 Jan 07:09 | Read from the page; Vega Morales is based in Santiago de Chile (UTC-3 in January), you confirmed |
| `farrar-fauci-comms.pdf` pp.115-122, Farrar “shut down the call” | Saturday, February 1, 2020 2:56 PM | 1 Feb 14:56 | Quoted in Fauci's 20:03:12 +0000 reply and Collins's 20:12; the p.115 copy prints 19:56 in Farrar's London client: same minute |
| `farrar-fauci-comms.pdf` p.115, Farrar “We are altogether” | Saturday, February 1, 2020 4:00 PM | 1 Feb 16:00 | Quoted in Fauci's 22:06:26 +0000 reply, so Eastern; on London time it would come before the message it answers |
| `farrar-fauci-comms.pdf` p.115, Collins “24/7 for the call with Tedros” | Saturday, 1 February 2020 at 20:50 | 1 Feb 15:50 | Quoted in Farrar's 4:00 PM ET reply, so London; it answers Farrar's “I have rejoined” (3:07 PM ET) |
| `farrar-fauci-comms.pdf` p.119, Collins “Just saw this” | Saturday, 1 February 2020 at 20:12 | 1 Feb 15:12 | Quoted in Farrar's “sure” (20:13:15 +0000), so London, one minute before it |
| `farrar-fauci-comms.pdf` pp.116, 119, 122, Koopmans “Re the pangolin sequence” (three copies) | Saturday, 1 February 2020 at 19:43 | 1 Feb 14:43 | Quoted in Farrar's 19:56 London message: 2:43 PM ET, during the 2-3 pm ET call |
| `farrar-fauci-comms.pdf` p.140, Farrar's “Teleconference” notice (two copies) | Saturday, February 1, 2020 10:34 AM / at 15:34 | 1 Feb 10:34 | Quoted in Fauci's reply (Eastern) and printed 15:34 in Farrar's London client; Garry's iPhone quote 9:34 AM Central: all the same instant |
| `farrar-fauci-comms.pdf` pp.137-138, Garry “I will be on the call” | Saturday, February 1, 2020 10:49 AM | 1 Feb 10:49 | Quoted in Fauci's 15:50 (London) reply, so Eastern: 15:49 UTC, one minute before it |
| `farrar-fauci-comms.pdf` pp.137, 140, Fauci “Francis will be on the call” and “Please include Francis Collins” | Saturday, 1 February 2020 at 15:48 and 15:50 | 1 Feb 10:48 and 10:50 | Quoted in Farrar's 15:50:28 and 15:51:54 +0000 replies, so London |

### S4. REV top-level stamps: Pacific (44 emails)
Your decision, with evidence: REV is Kristian Andersen's collection (the REV0000nnn numbering also covers `slack-part1.pdf`, REV0002899 to REV0003038, whose first page reads “You created this private channel”).
He is at Scripps Research, La Jolla, San Diego. Anchors: S2 (4:38 PM = UTC-8), a Garry message (16 Feb 2022) that fits UTC-8 to the minute, “it's 85 degrees in San Diego today”, and 24 bracketed stamps that all allow only -8 and -7.
Details: analysis 1.2. Quoted blocks on REV pages follow the freeze rule instead (L1).

### S5. Slack Part 1 is Eastern
Settled by you (2026-10-28) on two independent anchors: Rambaut's 21:26 “Jeez it is 2.30 am” (22 Feb), and the 1 Feb 2020 call with Fauci, 2 to 3 pm ET per Fauci's calendar, whose Slack messages run 13:59 to 15:01 with the Zoom link at 15:05.
Part 1 is Andersen's collection but prints Eastern because of the session that captured it (who or why is unknown; you suggest the investigators). That says nothing about his own clock. Details: analysis 1.4.

### S6. Slack Part 2 is Pacific
Anchors: Holmes (“it's 1 am here”), Garry (“It's 4:15 am in Sydney”), and the sleeping hours of all four authors over 11,000 messages. Converted to ET, the printed Pacific time is in the 🕑 chip. Details: analysis 1.3.

### S7. Slack day corrections (67 messages, now by the parser)
The parser now gives each message the day in force when its header was read (2026-11-03, see U16), which corrects 67 messages whose day divider sat just below them, including the seven below. The hand list `slack_date_fixes.json` is kept as evidence but no longer needed. The seven: the 22:42 message of 1 Feb, and six more evening messages that had the next day's date (p.9 22:35, p.16 20:11, p.21 19:11, p.35 19:45, p.39 22:26, p.134 23:56). Same fault each time (the day divider applied one message too early); p.9 checked on the page image.

### S8. Slack Part 1 time labels (16 read by you, 85 by an external OCR pass)
On 2026-11-04 a first external OCR pass (`grok_slack_part1_times_partial.csv`, notes in `grok_slack_part1_times_STATUS.md`) was matched to messages by page, sender and first words, and 59 labels were applied (commit a38bcf9); each is in `slack_time_fixes.json` marked as not yet checked by you. The corrections in its STATUS file were applied in a second step (U17). Your six: `slack_time_fixes.json`: p.19 Holmes 19:49; p.121 Andersen 15:40 and “slow”; p.134 Holmes 18:36, Andersen 18:51, Andersen 22:44, Holmes 23:42. Read from the page images on 2026-11-03.

---

# L. Likely: nothing to do unless you have an anchor

Each is consistent with every test. What would move one to Settled is in the last column.

| Code | Emails | Rule and the clock | Why it holds | What would settle it |
|---|---|---|---|---|
| **L1** | 231 (151 P.O., 80 Farrar-Fauci) | **Freeze rule**: a quoted block is on the quoter's clock | Every reply pair it touches is in order (250 pairs, only shift 0 allowed). Quoters: Farrar London, Koopmans/Fouchier Rotterdam, Holmes Sydney, Andersen Pacific and the rest by where they work | An exact copy with a zone, or a time/remark in the text |
| **L2** | 1 (Farrar-Fauci) | Farrar's last top-level stamp: London (you: he is based in London) | 2 pairs, only shift 0 allowed | An exact copy with a zone |
| **L3** | 5 (3 FF, 2 P.O.) | Wellcome convener's mailbox: London | 3 pairs, only shift 0 allowed | The same |
| **L4** | 2 (Farrar-Fauci) | NIH, Bethesda: Eastern | 2 pairs, not decided | The same |
| **L5** | 8 (P.O. pages LIP) | Lipkin's mailbox: Eastern (Columbia) | 10 pairs, only shift 0 allowed | The same |
| **L6** | 11 (P.O. pages GARRY) | Garry's mailbox: Chicago, Central (Tulane, New Orleans; you gave this) | 10 pairs, only shift 0 allowed; the 10 Feb chain favours Chicago (16:51 ET; Eastern would put it before the message it answers) but the link is only inferred | An exact copy on a GARRY page |
| **L7** | 2 (P.O. pp.142-143, stamp FARZAN) | Farzan's own mailbox: Eastern (Scripps, Jupiter, Florida; you gave this) | Leaf-level: nothing quotes the 31 Mar message, so the freeze rule cannot apply. Eastern gives 20:59 ET for “Re: Furin...” (31 Mar) and 23:07 ET for Farzan's 6 Feb “RE: Furin...”; the 6 Feb one used to sit in the REV run (Pacific, 02:07 ET on 7 Feb) and moved when the FARZAN stamp was found. Andersen's “SoCal” fixes where he wrote, not whose clock the export shows. A third P.O. entry on these pages (Andersen, 16 Feb 21:45) is a block quoted in Farzan's own message, so it takes his Eastern clock too (21:45 ET instead of 00:45 ET on the 17th); it is counted in L1 | An exact copy with a zone, or a remark in the text. If the export were rendered in a fixed zone (as the REV run may be), the 31 Mar time would be 17:59 ET instead |

Filter `zone_format_audit.csv` on `zone_status` = Supported, then on `rule`. Bracketing could not choose between Chicago and Eastern for GARRY or LIP (too few bracketed stamps).

---

# U. Unknown: the present list

### Emails (0): none

Every email now has a rule that gives a clock. Since your decision of 2026-11-02 (**physically nested under a block on the same page = quoted by it**, rule 2 above; a header that opens a page is not linked unless you declared it nested from the page image, as for p.58), the freeze rule applies to every Farrar-Fauci block, and the quoters were added to the lookup of where people live: Barasch (NIAID, Bethesda), Miller de Vega (GPMB Secretariat at WHO, Geneva), Kickbusch (Global Health Centre, Geneva; the “From: ee” on p.41 is the OCR of a redaction code, you identified her) and Dzau (Washington DC). Nothing is Unknown among the emails; the Slack item U17 below is the only open one (U15 and U16 are resolved).

**Esveld (old U10) and the others.** Esveld p.43, “06 March 2020 10:34”, is now read as nested under Alex Harris's block, so on Harris's London clock (05:34 ET). Her earlier Dutch-format message below it is already Settled (S3). The old question “London or Netherlands, up to 1 h” remains open in substance: Harris is Head of Global Policy & Advocacy at Wellcome, London (you confirmed, 2026-11-02), so London is right. Harris's own 11:56 is on Kickbusch's Geneva clock (10:56 UTC), 22 minutes after Esveld's 10:34 UTC.

**Old U7** (Holmes p.58) is now Likely: your reading of the page image (no top-level separator above it) makes it quoted by Farrar's block at the end of p.57, so London (15:11 ET); the profile lists p.58 in `nested_page_starts`. **Old U1** (Farzan p.142) is L7. **Old U2 to U4** are S3. **Old U5, U6, U8, U9, U12, U13, U14** are now Likely (L1): Koopmans 9 Feb is London (Farrar's block above), Holmes 4 Feb is London (Farrar's), Vallance 8 Feb London, Harris 3 Mar London, Viner 12 May 13:16 and 13 May 22:22 London (Farrar's), Viner 12 May 6:12 PM Eastern (Collins's).

### Resolved checks (U15, U16: nothing to do)

These come from tests that run outside the app. The app's own data has **no reply before the message it answers**; they are about readings that might be wrong.

#### U15. Resolved (2026-11-03): three reply pairs, no conflict; one real fix (U15c)

`tools/freeze_bracket_check.py` re-reads every message on the clock of whoever quotes it. For three pairs in `po-emails.pdf` that reading put the reply before its parent. The cause was in the check, not in the times: each reply is one merged entry with **one** kept stamp (the top-level copy's), and the check applied the quoter's clock to that stamp instead of to the stamp the quoted copy prints. Reading the quoted copies themselves settles all three.

| Pair | Top-level copy (kept) | The quoted copy, as printed | Same instant? |
|---|---|---|---|
| **U15a** Holmes, “Re: Summary - Invitation to edit” (pp.22, 28-29) | REV p.22: “2/5/2020 1:23:41 AM” Pacific = 09:23 UTC = 04:23 ET | Quoted in Rambaut's reply (iPhone, London): “On 5 Feb 2020, at 09:23, Edward Holmes wrote” | **Yes** (Pacific 01:23 = London 09:23, the 8 h gap) |
| **U15b** Holmes, “Region 6 is the RBD” (pp.28, 45) | GARRY page: “2/5/2020 4:22:24 AM” Chicago = 10:22 UTC = 05:22 ET | Quoted in Rambaut's reply: “On 5 Feb 2020, at 10:22, Edward Holmes wrote” | **Yes** (Chicago 04:22 = London 10:22, the 6 h gap) |
| **U15c** Farrar, “FW: 2019 N-CoV” (pp.57-65) | none: the only copy in the REV release is the block “From: Jeremy Farrar / Sent: 08 February 2020 09:45” **inside Mike Ferguson's reply** (REV0000827) | Drosten's German client: “Datum: Samstag, 8. Februar 2020 um 10:45” (S3, `farrar-fauci-comms.pdf` pp.59-60) = 09:45 UTC | **Yes**, but the app had read 09:45 as REV Pacific (12:45 ET) |

**U15a and U15b: nothing to change.** The two pairs give a minute-exact match between two printed clocks that differ by exactly the whole-hour offset we assume (Pacific to London, Chicago to London). That is also the best evidence yet for the REV (Pacific) and GARRY (Chicago) clocks, and for Rambaut's London iPhone. The Holmes “On ... wrote:” attribution lines are Apple Mail's way of writing a quoted header; they carry **no separator line**, unlike Outlook's header block. That changes nothing for the quote rule: what decides the clock is that the block is nested in another message and that the quoting client wrote its date line (the attribution line is written by Holmes's client, so Sydney: “1:03 pm” = 21:03 ET the evening before; Andersen's “Tuesday, February 4, 2020 at 7:08 PM” inside Garry's message is Garry's Outlook, Central = 20:08 ET). The check should read the quoted copy's own stamp. It does not yet; hence these two still show as “newly broken” in `analysis/freeze_bracket_check.csv`.
**U15c: fixed.** Farrar's block is quoted, not top-level, so it is on Ferguson's London clock: 09:45 London = **04:45 ET** (it was 12:45 ET). It is now a verified override (S3), consistent with the German copy. Reply order: Farrar 04:45, Fouchier (REV top-level, Pacific) 14:36, Drosten's quoted copy of Fouchier 05:36 on the Berlin clock: all in order. The inferred “same conversation” link Farrar to Fouchier stays.
**Lesson, for anyone who reads P.O. emails:** a header printed in the format “Sent: 08 February 2020 09:45” (day, month name, year, 24 h, no seconds) is a UK client's rendering, so it is **not** a REV export stamp even when the page is a REV page. A true REV top-level stamp has the form “Sent: 2/8/2020 11:36:30 AM” (month/day, seconds, AM/PM) under a “Message” line. The parser's page-owner rule for the P.O. release has no such test (the P.O. release has no `top_level_stamp_re`, because of the attached-document risk, e.g. Pope's “Tue 2/4/2020 9:10:35 AM (UTC-05:00)”); a search for other REV-page entries whose stamp is not in the REV export form is the obvious next check.

#### U16. Resolved (2026-11-03)

Six evening-then-small-hours rows. Two were a missed day divider (p.24 and p.60; the divider “February 9th. 2020” had a period the pattern did not accept, and a message took the day of the divider printed **below** it: now fixed in `parse_part1.py`, 67 messages changed day, see S7). The other four were digits lost from the time label, which you read off the page images and I entered in `tools/slack_time_fixes.json`: p.19 Holmes `19:49` (was 01:49); p.121 Andersen `15:40` and “Very **slow** going” (was 01:50, “sow”); p.134 Holmes `18:36` (was 01:36), Andersen `18:51` (was 19:51), Andersen's “It's an eel! Eel!!!” `22:44` (had no label), Holmes `23:42` (was 02:32), in reply to it. See S8. The check then listed 30 backwards pairs (now 3, U17), all in U17.

### Open: the only Unknown left

#### U17. Slack Part 1: backwards times, 3 left (80 at first)

The test: two consecutive timed messages on the same day where the second prints a time more than an hour earlier. Part 1 has no AM/PM and shows a time only for the first message of a run, so these are OCR slips (a dropped or swapped digit) or reading-order slips; Part 2 (a cleaner export) has none. Listed in `slack_part1_time_check.csv`.

**How it came down.**
1. Divider fix in the parser, and your six readings (U16, S8): 74 → 60.
2. A first external OCR pass (Grok partial CSV, 2026-11-04) matched to messages by page, sender and first words: 59 labels, 60 → 30 (commit a38bcf9).
3. A second pass from the corrections in `grok_slack_part1_times_STATUS.md`, matched by page, sender and printed time: 26 labels (table below), 30 → 11.
4. Your readings of 2026-11-05 on the other 8 pairs (p.35, 36, 43, 49, 57, 102, 104, 115): 11 → 3. p.115 was a missed date chip: “This whole furin site…” and the 11 messages after it, up to the April 4th divider, are 3 April, not 2 April (`slack_date_fixes.json`). One of my inferences needs a check: p.43 Rambaut's “Eddie is colour blind too” is set to 13:56 (it printed 19:56, which would put it after Garry's 13:57). No new visual OCR in this step. A fix applies only if the entry still carries that sender and that exact wrong time. p.102 (a day divider, not a time) is left out, and so are p.7 and p.52, which may be printed backwards.

All of these are marked in `tools/slack_time_fixes.json` as not checked by you.

**The 3 that remain**, and what I need:

| page | pair | what is open |
|---|---|---|
| p.35 | Garry 18:22 → Andrew 16:21 (“fair enough I just have heard…”) | Andrew's label is probably 18:2x; please read it |
| p.52 → p.55 | Garry 05:05 (19 Feb) → Holmes 02:16 (“Thanks for that. However this outbreak…”, first message on p.55) | I cited it as a p.52 pair and you could not find it: it is Garry's last message on p.52 and Holmes's first on p.55 (pp.53-54 are the attached document). Is there a day chip above Holmes on p.55 (then 02:16 is 20 Feb and nothing is wrong)? |
| p.64 → p.65 | Garry 10:59 (p.64) → “No polybasic site, HOWEVER…” 01:44 (top of p.65, shown as Andersen) | Your p.64 image is in order (10:59, 11:07, 11:11, 11:21, 14:41); the odd one is the p.65 label. The external pass read it as Garry 14:44, after Holmes's 14:41. I did not apply it: is it 14:44, and is the sender Garry? |

**What would settle the rest:** a visual read of these pages (prompt: `GROK_PROMPT_SLACK_PART1_TIMES.md`), then rerun `slack_time_check.py`. Whatever is still backwards after that is a real question about the PDF.
**Send me:** the readings, or “skip” (the 3 rows stay; the app shows each time as OCR read it, which can be wrong by a digit).

<details><summary>The 26 labels from the STATUS file (2026-11-04)</summary>

| idx | page | sender | wrong -> corrected | source |
|---|---|---|---|---|
| 13 | p.2 | Andrew Rambaut | 15:00 -> 13:30 | Grok partial CSV (cluster 13:28-13:42) |
| 17 | p.2 | Andrew Rambaut | 15:59 -> 13:33 | Grok partial CSV |
| 23 | p.2 | Andrew Rambaut | 19:08 -> 13:38 | Grok partial CSV |
| 145 | p.13 | Kristian Andersen | 16:26 -> 18:26 | STATUS line 54 |
| 246 | p.22 | Robert Garry | 00:57 -> 08:57 | STATUS line 56 |
| 366 | p.35 | Robert Garry | 19:04 -> 18:04 | STATUS line 61 |
| 367 | p.35 | Andrew Rambaut | 16:16 -> 18:21 | STATUS line 61 |
| 376 | p.36 | Eddie Holmes | 09:32 -> 03:32 | STATUS line 62 |
| 378 | p.36 | Eddie Holmes | 09:36 -> 03:36 | STATUS line 62 |
| 397 | p.39 | Kristian Andersen | 19:10 -> 18:10 | STATUS line 64 |
| 398 | p.39 | Robert Garry | 16:20 -> 18:20 | STATUS line 64 |
| 413 | p.40 | Kristian Andersen | 01:19 -> 11:31 | STATUS line 65 |
| 435 | p.43 | Andrew Rambaut | 12:00 -> 13:40 | STATUS line 66 |
| 439 | p.43 | Andrew Rambaut | 19:57 -> 13:57 | STATUS line 66 |
| 440 | p.43 | Robert Garry | 14:00 -> 13:40 | STATUS line 66 |
| 462 | p.45 | Robert Garry | 00:52 -> 08:52 | STATUS line 67 |
| 515 | p.49 | Robert Garry | 01:00 -> 18:09 | STATUS line 68 |
| 779 | p.69 | Andrew Rambaut | 06:19 -> 06:13 | STATUS line 35 |
| 780 | p.69 | Robert Garry | 04:21 -> 06:17 | STATUS line 35 |
| 995 | p.103 | Kristian Andersen | 09:31 -> 03:31 | STATUS line 38 |
| 996 | p.103 | Andrew Rambaut | 02:52 -> 03:32 | STATUS line 38 |
| 1001 | p.104 | Eddie Holmes | 01:00 -> 05:31 | Grok partial CSV |
| 1007 | p.104 | Kristian Andersen | 10:49 -> 10:41 | Grok partial CSV |
| 1126 | p.121 | Kristian Andersen | 19:57 -> 13:37 | STATUS line 69 |
| 1218 | p.134 | Eddie Holmes | 01:49 -> 18:43 | STATUS line 70 |
| 1248 | p.139 | Kristian Andersen | 10:25 -> 16:25 | STATUS line 42 |

</details>

---

# O. Other open points (not datetimes)

| Code | What | What I need |
|---|---|---|
| **O1** | Chapter link for section 4.11 (“Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)”): it points at Fauci's `farrar-fauci-comms.pdf` p.137, 15:50 (“Please include Francis Collins…”), which is not about the WHO. The Farrar message that proposes WHO contact is p.108, “Sunday, February 2, 2020 4:48 AM” (now 23:48 ET, 1 Feb); neither is at 3:59 pm | Which message you mean, or whether the caption time is off; then I fix the link |
| **O2** | A few old bookmark keys now name a different message and cannot be re-mapped (list in analysis A10) | Nothing, unless you or others bookmarked emails on those dates |
| **O3** | P1 to P4: issues in your P.O. piece, in `TRAGICOMEDY_ISSUES.md` (private, git-ignored). Re-checked 2026-11-05: all still valid; one new real question, 13.2 (Fouchier 10:36 UK in the article against 19:36 UK in the data) | Your reading of that page (see the file, P1.3) |
| **O4** | Should `analysis/` stay in the public repository? | “ignore the folder” or “fine as it is” |
| **O5** | My edits to your own `README.md` (six paths) and `STATUS.md` (one path) | “fine” or what to put back |
| ~~O6~~ | `PO_Slack.code-workspace` | done: added to `.gitignore` (2026-11-02) |

---

# Fixed in this rebuild (no action)

Found and fixed by me: the physical-nesting rule for the Farrar-Fauci release (about 60 times moved; the Feb 1 chain and the Gao/Dzau chain agree with your hand reading; analysis 5.10); the Farzan mailbox stamp (L7); Folkers 8:43 PM (S3); the 22:34 message's sender label and reply link and the “Phone call” body (S3); six Slack day errors (S7); a swap of two overrides that I had made after the 29 Oct rerun (analysis A9); Farrar, Koopmans and Fouchier clocks (L1, L2); the cross-release quote check is run, with no violation (analysis A8).

# Files

| File | Use it? | For |
|---|---|---|
| `zone_format_audit.csv` | Optional | One row per email: rule, status (Settled / Supported / Not settled), reason |
| `slack_part1_time_check.csv` | For U17 (columns: page, date, first and second time, senders, first words, pattern) | The 3 places where Slack Part 1 times run backwards |
| `freeze_bracket_check.csv` | For U15 | Clock and bracketing test per email |
| `cross_release_check.csv` | No | Quoted-later-than-quoter test across the two releases (empty: no violation) |
| `reply_order_check.csv`, `owner_zone_check.csv` | No | My test output |
| `zone_rule_dedupe.log` | Only if an email looks missing | The copies I removed as duplicates |
| `chapter_links_report.txt`, `bookmark_rekey_report.txt` | No | Link and bookmark housekeeping |
