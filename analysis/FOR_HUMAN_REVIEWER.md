# Where the dates and times stand: what is settled, what is likely, what is unknown

Status 2026-11-01, after the last rebuild. This is the only file with things for you to look at.
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
| **Unknown** | 0 | the 74 backwards times in Part 1 (see U16 and U17) |

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

### S7. Slack day corrections (7 messages)
`slack_date_fixes.json`: the 22:42 message of 1 Feb, and six more evening messages that had the next day's date (p.9 22:35, p.16 20:11, p.21 19:11, p.35 19:45, p.39 22:26, p.134 23:56). Same fault each time (the day divider applied one message too early); p.9 checked on the page image.

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

Every email now has a rule that gives a clock. Since your decision of 2026-11-02 (**physically nested under a block on the same page = quoted by it**, rule 2 above; a header that opens a page is not linked unless you declared it nested from the page image, as for p.58), the freeze rule applies to every Farrar-Fauci block, and the quoters were added to the lookup of where people live: Barasch (NIAID, Bethesda), Miller de Vega (GPMB Secretariat at WHO, Geneva), Kickbusch (Global Health Centre, Geneva; the “From: ee” on p.41 is the OCR of a redaction code, you identified her) and Dzau (Washington DC). Nothing is Unknown among the emails; the Slack items U15 to U17 below remain.

**Esveld (old U10) and the others.** Esveld p.43, “06 March 2020 10:34”, is now read as nested under Alex Harris's block, so on Harris's London clock (05:34 ET). Her earlier Dutch-format message below it is already Settled (S3). The old question “London or Netherlands, up to 1 h” remains open in substance: Harris is Head of Global Policy & Advocacy at Wellcome, London (you confirmed, 2026-11-02), so London is right. Harris's own 11:56 is on Kickbusch's Geneva clock (10:56 UTC), 22 minutes after Esveld's 10:34 UTC.

**Old U7** (Holmes p.58) is now Likely: your reading of the page image (no top-level separator above it) makes it quoted by Farrar's block at the end of p.57, so London (15:11 ET); the profile lists p.58 in `nested_page_starts`. **Old U1** (Farzan p.142) is L7. **Old U2 to U4** are S3. **Old U5, U6, U8, U9, U12, U13, U14** are now Likely (L1): Koopmans 9 Feb is London (Farrar's block above), Holmes 4 Feb is London (Farrar's), Vallance 8 Feb London, Harris 3 Mar London, Viner 12 May 13:16 and 13 May 22:22 London (Farrar's), Viner 12 May 6:12 PM Eastern (Collins's).

### Flagged by my checks (not time errors that I can place)

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

#### U16. Slack Part 1: six evening-then-small-hours rows that are not the divider fault

Each is an evening message followed on the same printed date by a small-hours message. Six other cases like this were the divider fault (S7) and are fixed; these six are not (the evening run is long, or the dates jump), so they look like **misread digits**.

| Page | Date | Evening message | Next message (small hours) |
|---|---|---|---|
| p.19 | 6 Feb 2020 | 19:44 Garry, “I've known Don for 30 years...” | 01:49 Holmes, “Nailedit. Andrew - thanks!...” (the times on this page rise steadily, so 01:49 is most likely a misread of something like 10:49 or 19:49) |
| p.24 | 8 Feb 2020 | 21:17 Andersen, “Guys, one thing that occurs to me...” | 05:16 Rambaut, “Swine flu 2009 cid though.” |
| p.60 | 22 Feb 2020 | 21:05 Andersen, “Just in case people think it's difficult...” | 04:15 Rambaut, “4. I think VR's piece is supposed to be...” |
| p.121 | 10 Apr 2020 | 19:57 Andersen, “Still trying to work through this...” | 01:50 Andersen, “Very sow going...” |
| p.134 | 20 Apr 2020 | 18:30 Holmes, “Catching up. The bats are not special...” | 01:36 Holmes, “I've spent most of my waking hours...” |
| p.134 | 21 Apr 2020 | 19:51 Andersen, “I think 3-factor authentication...” | 02:32 Holmes, “I was just about to send that to you!” |

**Why it is open.** Slack Part 1 prints times in a small font with no AM/PM, only on the first message of each run, and my OCR reads digits badly there (see U17). I cannot tell which of the two times is wrong without the page image.
**What would settle it:** reading each of the six times off the page image (a second OCR pass at 400 dpi of the time labels, as I did for the email headers, would do it). **Send me:** “do the second pass” (my recommendation), or the six times as you read them.

#### U17. Slack Part 1: the other 68 backwards times

Same test, 68 more places where a message prints an earlier time than the one before it (listed in `slack_part1_time_check.csv`, column `pattern` = `other`). Spread: 23 are 1 to 3 hours backwards, 18 are 3 to 6 hours, 33 are more than 6 hours; none is under an hour. The worst pages are p.2 (4), p.57 (4), p.13, p.43 and p.134 (3 each).

**Why I think they are OCR errors, not real order problems.** The first page of the OCR text shows what the digits look like: “12:90” and “15.95” for what are times, “13.7” and “13.42” with a dot, “1595” and “1997” with no colon. A time of that kind cannot be compared with its neighbours. The second cause is reading order: where two columns or a thread sit side by side, the OCR can read a reply before the message above it. Neither is a problem in the PDF itself, and Part 2 (a different, cleaner export) has no such cases.
**What would settle it:** the same second OCR pass of the time labels (it would also resolve U16), then rerunning the check. Whatever is still backwards after that is a real question about the PDF.
**Send me:** “do the second pass” (it needs no decision from you) or “skip” (the 74 rows stay as they are; the app shows each Slack message with the time as OCR read it, which can be wrong by a digit).

---

# O. Other open points (not datetimes)

| Code | What | What I need |
|---|---|---|
| **O1** | Chapter link for section 4.11 (“Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)”): it points at Fauci's `farrar-fauci-comms.pdf` p.137, 15:50 (“Please include Francis Collins…”), which is not about the WHO. The Farrar message that proposes WHO contact is p.108, “Sunday, February 2, 2020 4:48 AM” (now 23:48 ET, 1 Feb); neither is at 3:59 pm | Which message you mean, or whether the caption time is off; then I fix the link |
| **O2** | A few old bookmark keys now name a different message and cannot be re-mapped (list in analysis A10) | Nothing, unless you or others bookmarked emails on those dates |
| **O3** | P1 to P4: issues in your P.O. piece, in `TRAGICOMEDY_ISSUES.md` (private, git-ignored). The times have moved since I last checked them | “re-check them” |
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
| `slack_part1_time_check.csv` | For U16, U17 (columns: page, date, first and second time, senders, first words, pattern) | The 74 places where Slack Part 1 times run backwards |
| `freeze_bracket_check.csv` | For U15 | Clock and bracketing test per email |
| `cross_release_check.csv` | No | Quoted-later-than-quoter test across the two releases (empty: no violation) |
| `reply_order_check.csv`, `owner_zone_check.csv` | No | My test output |
| `zone_rule_dedupe.log` | Only if an email looks missing | The copies I removed as duplicates |
| `chapter_links_report.txt`, `bookmark_rekey_report.txt` | No | Link and bookmark housekeeping |
