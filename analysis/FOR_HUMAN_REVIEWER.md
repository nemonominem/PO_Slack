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
| **2. Freeze rule** (a quoted block is on the clock of the person who quoted it) | Likely only | Needs to know where the quoter is: a lookup of where people live, in the parser (5.9). Nothing in the stamp proves it. |
| **3/4. Mailbox rule** (a top-level stamp is on the clock of the mailbox that shows it: REV Pacific, GARRY Chicago, LIP Eastern; the convener's mailbox London) | Likely only | The owner's clock; reply order cannot catch a stamp that is simply too early. |
| **Sender's institution** (where the sender works) | Likely only if the reply-order test passes with enough pairs; otherwise Unknown | A stand-in for the sender's clock. |
| **Reply-order test** | Never settles | Rules zones out (a reply cannot precede its parent). |
| **An unquoted message with no other support** (the last message of a thread, or only an inferred “same conversation” link) | **Nothing works** | The freeze rule needs a quote and an inferred link does not prove one. The time is Unknown until an anchor turns up. |

# 3. Where we stand

| Level | Emails | Slack |
|---|---|---|
| **Settled** | 115 | Part 1 (1,256 messages): Eastern; Part 2 (11,351): Pacific, converted to ET |
| **Likely** | 258 | none |
| **Unknown** | 14 | the 74 backwards times in Part 1 (see U15 to U17) |

---

# S. Settled: nothing for you to do

### S1. Zone written in the stamp (53 emails: 45 Farrar-Fauci, 8 P.O.)
The stamp carries the zone. Rule 1.

### S2. One exact copy with an explicit offset
`po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]”, equals `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”. Rule 1b. It also anchors REV (S4).

### S3. Verified from the page image, the message text or a calendar (15 emails)
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
| `farrar-fauci-comms.pdf` p.80, Farrar | Sent: Tuesday, February 4, 2020 6:08 AM | 4 Feb 06:08 | Read from the page; quoted in Collins's 6:12 AM reply (Eastern) |
| `farrar-fauci-comms.pdf` pp.169-172, GPMB Secretariat | Sent: martes, 28 de enero de 2020 9:09 | 28 Jan 07:09 | Read from the page; Vega Morales is based in Santiago de Chile (UTC-3 in January), you confirmed |

### S4. REV top-level stamps: Pacific (46 emails)
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
| **L1** | 164 (151 P.O., 13 Farrar-Fauci) | **Freeze rule**: a quoted block is on the quoter's clock | Every reply pair it touches is in order (179 pairs, only shift 0 allowed). Quoters: Farrar London, Koopmans/Fouchier Rotterdam, Holmes Sydney, Andersen Pacific and the rest by where they work | An exact copy with a zone, or a time/remark in the text |
| **L2** | 32 (Farrar-Fauci) | Farrar's top-level stamps: London (you: he is based in London) | 41 pairs, only shift 0 allowed | An exact copy with a zone |
| **L3** | 17 (15 FF, 2 P.O.) | Wellcome convener's mailbox: London | 13 pairs, only shift 0 allowed | The same |
| **L4** | 26 (Farrar-Fauci) | NIH, Bethesda: Eastern | 39 pairs, only shift 0 allowed | The same |
| **L5** | 8 (P.O. pages LIP) | Lipkin's mailbox: Eastern (Columbia) | 10 pairs, only shift 0 allowed | The same |
| **L6** | 11 (P.O. pages GARRY) | Garry's mailbox: Chicago, Central (Tulane, New Orleans; you gave this) | 10 pairs, only shift 0 allowed; the 10 Feb chain favours Chicago (16:51 ET; Eastern would put it before the message it answers) but the link is only inferred | An exact copy on a GARRY page |

Filter `zone_format_audit.csv` on `zone_status` = Supported, then on `rule`. Bracketing could not choose between Chicago and Eastern for GARRY or LIP (too few bracketed stamps).

---

# U. Unknown: the present list

### Emails (14): no rule that gives a clock could be used

Why: either **A. nothing quotes it** (the last message of its thread, or alone on its page: the freeze rule cannot apply), or **B. only an inferred “same conversation” link points at it**, which does not prove a quote exists. The time shown is a guess from where the sender works. Not one has an anchor.

| Code | Where | Header as printed | Sender | Subject | Reason | Clock used (guess) |
|---|---|---|---|---|---|---|
| **U1** | `po-emails.pdf` p.142 | 3/31/2020 8:59:49 PM | Kristian G. Andersen | Re: Furin... | A | Los Angeles |
| **U2** | `farrar-fauci-comms.pdf` pp.137-138 | Saturday, February 1, 2020 10:49 AM | Robert Garry | Re: Teleconference | B | Chicago |
| **U3** | `farrar-fauci-comms.pdf` p.116 | Saturday, 1 February 2020 at 19:43 | Marion Koopmans | Re: Teleconference | B | Rotterdam |
| **U4** | `farrar-fauci-comms.pdf` p.122 | Saturday, 1 February 2020 at 19:43 | Marion Koopmans | Re: Teleconference Re the pangolin sequences | A | Rotterdam |
| **U5** | `farrar-fauci-comms.pdf` pp.55-56 | Sunday, 9 February 2020 at 20:07 | Marion Koopmans | Re: [ext] 2019 N-CoV | B | Rotterdam |
| **U6** | `farrar-fauci-comms.pdf` pp.76-103 | Tuesday, 4 February 2020 at 06:33 | Edward Holmes | Re: Prevalence of infection and stage of the epidemic in Wuhan | A | Sydney |
| **U7** | `farrar-fauci-comms.pdf` p.58 | Saturday, 8 February 2020 at 20:11 | Edward Holmes | Re: [ext] 2019 N-CoV | A | Sydney |
| **U8** | `farrar-fauci-comms.pdf` pp.61-62 | Saturday, 8 February 2020 at 12:03 | Patrick Vallance | RE: 2019 N-CoV | A | London |
| **U9** | `farrar-fauci-comms.pdf` pp.47-49 | 03 March 2020 23:06 | Alex Harris | RE: GPMB: COVID-19 FUNDING NOTE | A | London |
| **U10** | `farrar-fauci-comms.pdf` p.43 | 06 March 2020 10:34 | Marja Esveld | RE: URGENT - GPMB COVID-19 FUNDING NOTE | B | London (see below) |
| **U11** | `farrar-fauci-comms.pdf` pp.42-43 | Freitag, 6. Marz 2020 11:56 | Alex Harris | RE: URGENT - GPMB COVID-19 FUNDING NOTE | B | London |
| **U12** | `farrar-fauci-comms.pdf` pp.7-13 | Tuesday, 12 May 2020 at 13:16 | Russell Viner | confidential - update on Paediatric Multisystem Inflammatory | B | London |
| **U13** | `farrar-fauci-comms.pdf` pp.6-7 | Tuesday, May 12, 2020 6:12 PM | Russell Viner | Re: confidential - update on Paediatric Multisystem Inflammatory Syndrome (PIMS) | B | London |
| **U14** | `farrar-fauci-comms.pdf` p.5 | Wednesday, 13 May 2020 at 22:22 | Russell Viner | Re: confidential - update on Paediatric Multisystem Inflammatory Syndrome (PIMS) | A | London |

The Rotterdam group (Koopmans) has 4 reply pairs and the test allows shifts 0 to +8: it cannot decide.

**What would settle one:** a time or remark in the message or a neighbour (like the NAS panel for Gao and Dzau), an exact copy with an explicit offset, or a link that proves who quoted it.
**Send me:** such an anchor for any of them, or “accept” (keep the guess, still Unknown).

**U10, Esveld p.43, in detail (London or Netherlands time: up to 1 hour).** The parser files her with Alex Harris as “Wellcome Trust / UK” and reads the 10:34 as London (05:34 ET). That label is wrong for her: she writes from the Dutch Ministry of Foreign Affairs.
London may still be right: this reply is top-level, so its stamp is on the clock of the mailbox that shows it, not hers; it is English-format, while her own earlier message below it prints in Dutch (“vrijdag 6 maart 2020 09:23”), so the 10:34 did not come from her client, and the mailbox (Wellcome) is in London.
It cannot be proven: London gives 10:34 UTC, the Netherlands 09:34 UTC, and both fit the thread (her 09:23 Dutch message = 08:23 UTC; Harris 11:56; Farrar 14:33:45 +0000). **Send me:** “keep London” or “Netherlands” (the entry moves to 04:34 ET).

### Flagged by my checks (not time errors that I can place)

| Code | What | Why it is unknown |
|---|---|---|
| **U15** | Three reply pairs that my separate freeze check flags as backwards: `po-emails.pdf` pp.22-29 (Garry “5 Feb 2020 1:03 pm”, then Holmes “2/5/2020 1:23:41 AM”), p.28 and pp.28-45 (Holmes “5 Feb 2020 9:04 pm”, then Holmes “2/5/2020 4:22:24 AM”), and pp.57-65 and 55-57 (Farrar “08 February 2020 09:45”, then Fouchier “2/8/2020 11:36:30 AM”, inferred link only) | The app's own data has no reply before its parent. In each pair one stamp is on a clock I read wrongly, or the link is wrong. **Send me:** whether the headers show the second message answers the first, and the stamps as you read them, or “skip” |
| **U16** | Slack Part 1: 6 evening-then-small-hours rows left (p.19 19:44, p.24 21:17, p.60 21:05, p.121 19:57, p.134 18:30 and 19:51) | Not the divider fault (the evening run is long, or the dates jump): probably misread digits. On p.19 the printed times rise steadily, so “01:49” is a misread. Fixing them needs each page image |
| **U17** | Slack Part 1: the other 68 backwards times | Probably misread digits (Part 1 has no AM/PM and times only the first message of a run). Listed in `slack_part1_time_check.csv`. Part 2 has none |

---

# O. Other open points (not datetimes)

| Code | What | What I need |
|---|---|---|
| **O1** | Chapter link for section 4.11 (“Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)”): it points at Fauci's `farrar-fauci-comms.pdf` p.137, 15:50 (“Please include Francis Collins…”), which is not about the WHO. The Farrar message that proposes WHO contact is p.108, “Sunday, February 2, 2020 4:48 AM” (now 23:48 ET, 1 Feb); neither is at 3:59 pm | Which message you mean, or whether the caption time is off; then I fix the link |
| **O2** | A few old bookmark keys now name a different message and cannot be re-mapped (list in analysis A10) | Nothing, unless you or others bookmarked emails on those dates |
| **O3** | P1 to P4: issues in your P.O. piece, in `TRAGICOMEDY_ISSUES.md` (private, git-ignored). The times have moved since I last checked them | “re-check them” |
| **O4** | Should `analysis/` stay in the public repository? | “ignore the folder” or “fine as it is” |
| **O5** | My edits to your own `README.md` (six paths) and `STATUS.md` (one path) | “fine” or what to put back |
| **O6** | `PO_Slack.code-workspace` is untracked | “commit”, “ignore” or “delete” |

---

# Fixed in this rebuild (no action)

Found and fixed by me: Folkers 8:43 PM (S3); the 22:34 message's sender label and reply link and the “Phone call” body (S3); six Slack day errors (S7); a swap of two overrides that I had made after the 29 Oct rerun (analysis A9); Farrar, Koopmans and Fouchier clocks (L1, L2); the cross-release quote check is run, with no violation (analysis A8).

# Files

| File | Use it? | For |
|---|---|---|
| `zone_format_audit.csv` | Optional | One row per email: rule, status (Settled / Supported / Not settled), reason |
| `slack_part1_time_check.csv` | For U16, U17 | The 74 places where Slack Part 1 times run backwards |
| `freeze_bracket_check.csv` | For U15 | Clock and bracketing test per email |
| `cross_release_check.csv` | No | Quoted-later-than-quoter test across the two releases (empty: no violation) |
| `reply_order_check.csv`, `owner_zone_check.csv` | No | My test output |
| `zone_rule_dedupe.log` | Only if an email looks missing | The copies I removed as duplicates |
| `chapter_links_report.txt`, `bookmark_rekey_report.txt` | No | Link and bookmark housekeeping |
