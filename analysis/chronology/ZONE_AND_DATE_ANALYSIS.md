# Zone and date analysis: P.O. Record Search and the email releases

Baseline email and Slack audit: 2026-11-01 to 2026-11-05 (see Parts 1-2
and 5). The February 8 thread was re-audited on 2026-11-12. Its source findings
and current app discrepancies are in Part 3; they qualify the older counts,
links, and clean-check claims. The February 8 correction commit is now an
ancestor of `po-sources-and-boxes` at `c0f6933`; the data still has residual
errors described below.
Internal; not published. This file is only about getting the dates and
times right and about what is wrong in the P.O. piece and the web app because of them. Every
instruction and decision for you is in `FOR_HUMAN_REVIEWER.md`.

**How entries are named.** Use PDF file and pages, the date and time exactly as
printed in the header, the sender, and the subject; the February 8 audit also
gives record indices and keys to identify the affected app entries. (`tools/entry_ref.py`
turns the internal entry numbers into this form; `zone_format_audit.csv` has one row per entry with the
same fields.) "P.O. emails" is `po-emails.pdf`; "Farrar-Fauci" is `farrar-fauci-comms.pdf`; the
Slack PDFs are `slack-part1.pdf` and `slack-part2.pdf`.

**Standard time.** Every date and time in the web app, whatever the source (emails, Slack, drafts), is shown
in **New York time (ET)**, followed by the local time as printed. ET is the standard while the local times are
being sorted out; where a local zone is unknown the entry says so. Slack Part 2 is converted to ET
(`tools/parse_part2.py`); Slack Part 1 is already Eastern.

The file has five parts:
1. **Settled datetimes**
2. **Unsettled datetimes**
3. **Issues in your P.O. piece**
4. **Issues in the web app**
5. **Method**: the rules, the tests, the anchors

---

# Part 1. Settled datetimes (123 emails, plus Slack Part 1 and Part 2)

Settled means: fixed by the stamp itself, by an exact copy, by the page image, or by a decision of yours
backed by evidence. `zone_format_audit.csv` marks each email `Settled`.

| Zone source | Emails | Zone used | Evidence |
|---|---|---|---|
| Zone written in the stamp (`+0000`, `UTC+11:00`, `AEDT`, `EST`) | 53 (45 Farrar-Fauci, 8 P.O. emails) | as written | The stamp |
| Exact copy with an explicit offset | 1 | from the copy | `po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]” equals the Farrar-Fauci copy `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”, Anthony Fauci, “RE: Phone call” |
| Verified from the page image or the message text | 24 | per entry (Eastern, London, Pacific, Amsterdam, Berlin, Santiago) | 4 corrections in 1.1; 8 headers that were undated, read from the page images; 2 corrected from the message text (Gao and Dzau, 25 Apr 2020); Folkers 8:43 PM; and the 22:34 reply (list in FOR_HUMAN_REVIEWER.md, S3) |
| Page owner **REV**, top-level stamps only (P.O. emails) | 45 | Pacific | Section 1.2. The 95 other REV-page entries are quoted blocks, which now take the quoting author's clock (Supported) |

## 1.1 The verified corrections (25 entries; first four, then the others in FOR_HUMAN_REVIEWER.md S3)

- `po-emails.pdf` p.2, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call”: quoted in Fauci's reply, so on Fauci's Eastern clock. The same message appears in the
  Farrar-Fauci release as `farrar-fauci-comms.pdf` pp.154-155, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call”, inside Fauci's reply stamped `00:38:35 +0000`: also a verified correction.
- `po-emails.pdf` pp.3-4, “Friday, January 31, 2020 5:23 PM”, Jeremy Farrar, “Phone call”: Farrar's text says “It is 10pm now UK”, so 5:23 PM is Eastern (22:23 UK).
- `po-emails.pdf` p.3, “Friday, 31 January 2020 at 22:34”, Fauci, Anthony, “RE: Phone call”: decided by you on 2026-10-26. Farrar's “Phone call” left at 22:23 UK; Conrad's reply froze it
  as 5:23 PM on her East Coast clock; Farrar's answer to her carries his own UK clock, 22:34 (11 minutes
  later) = 17:34 Eastern. A decision for this message only, not a rule for the day-first 24-hour format.

## 1.2 REV: the P.O. emails' mailbox is on Pacific time

REV pages (50 top-level stamps; the quoted blocks on these pages follow the freeze rule) are on Pacific time (UTC-8 in winter, UTC-7 in summer), which fits Kristian
Andersen's mailbox: he is at Scripps Research in La Jolla, San Diego. (On 2026-10-28 the code was switched
to Arizona for a few hours and reverted when the evidence below and your correction showed Andersen is in
San Diego. The data is identical to its state before the switch, except for the Farrar 22:34 message.)

The evidence:
- `po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]” is an exact copy. The Farrar-Fauci release has it as `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”, Anthony Fauci, “RE: Phone call”: sent 00:38 UTC = 7:38 PM Eastern.
  It prints 4:38 PM, which is UTC-8.
- It is quoted inside Andersen's own reply, `po-emails.pdf` p.1, “Friday, January 31, 2020 8:05 PM”, Kristian G. Andersen, “Re: Phone call”. By your footnote rule, a frozen quote carries the clock of
  the client that quoted it, so Andersen's client was on UTC-8 on 31 Jan 2020.
- Your article says “~4 pm CA” for that call (3.11), and its footnote says REV “is UK -8”.
- Slack Part 2 (1.3): a Garry message (16 Feb 2022) fits UTC-8 to the minute; Andersen wrote “it's 85
  degrees in San Diego today” (15 Jan 2021).
- Reply order allows REV to shift by -3 to 0 hours, so it neither proves nor excludes Pacific alone.
- **REV is Andersen's collection throughout (your point, 2026-11-01).** `slack-part1.pdf` is itself REV: its 140
  pages are numbered REV0002899 to REV0003038. Its first page reads “You created this private channel on
  February 1st, 2020”, so “you” is Kristian Andersen (he is the first to join, 12:11, then Rambaut 12:13). So the
  REV series, emails and Slack Part 1 alike, is Andersen's own material, and REV time is Andersen's timeline.

Remaining limit: only one exact copy tests the clock, and it is a quote, not one of Andersen's top-level
stamps. Status stays Settled (your decision) with that test as support.

**Caveat:** Pacific is the owner's own clock. A block quoted on a REV page can be frozen on someone else's
clock. Farrar's 5:57 PM and 5:23 PM messages were (Fauci's Eastern clock), and the Folkers message below is
(Part 4, item A1). If a REV time looks hours out, suspect a quoted block; each needs its own evidence.

## 1.3 Slack Part 2 is on Pacific time (with daylight saving)

Three messages state the sender's local clock. Two are in Part 2:

| Slack message | Stated | Place | The stamp must be on |
|---|---|---|---|
| `slack-part2.pdf` p.706, Holmes, 2021-04-15 07:58:54, “it's 1 am here and I need to sleep” | 1 am | Sydney (UTC+10) | UTC-7, Pacific daylight (07:58 = 00:58 Sydney) |
| `slack-part2.pdf` p.1090, Garry, 2022-02-16 09:15:51, “It's 4:15 am in Sydney” | 4:15 am | Sydney (UTC+11) | UTC-8, Pacific standard (09:15 = 04:15 Sydney next day, to the minute) |

Independent check, from sleeping hours: for each main author the quietest six-hour window of the day,
taken as 03:30 local. Over 11,000 Part 2 messages every author gives the same stamp zone, about UTC-8.5:
Andersen is quiet 00:00-06:00; Holmes (Sydney) 05:00-11:00; Rambaut (UK) 17:00-23:00; Garry (Chicago)
21:00-03:00. That is Pacific. So Slack Part 2 times are Pacific (settled: two anchors and the histogram).
**Applied:** `tools/parse_part2.py` now converts Part 2 to ET (Pacific + 3 hours; US Pacific and Eastern change
clocks at the same instant). The app shows the ET date and time, and the 🕑 chip gives the printed Pacific time
(“07:58:54 Pacific -> 10:58:54 ET”). 11,293 timed messages changed; 591 moved to another date.

## 1.4 Slack Part 1 is Eastern time

Decided by you on 2026-10-28. Evidence: `slack-part1.pdf` p.61, Rambaut, 22 Feb 2020 printed 21:26, “Jeez it is
2.30 am. Going to bed.” (Edinburgh, UTC+0): 21:26 Eastern = 02:26 UK. Your own captions treat Part 1 Slack times
as Eastern and add 5 hours for UK; of 67 Slack captions I could check, 16 match a stamp to the minute and most
others fall within a few minutes of the nearest timed message (only the first message of a run is timed in Part 1).
The sleeping-hours method on Part 1 is too noisy (UTC-4 to UTC-7) to add anything. The app shows Part 1 times as
printed, labelled ET in the 🕑 chip.

**Second anchor (2026-11-01, your point).** The 1 Feb 2020 call with Fauci ran 2 to 3 pm Eastern; Fauci's
calendar shows it, and your article uses it (see the P.O. piece, 3.11). On `slack-part1.pdf` (first pages, 1 Feb 2020)
Andersen writes “Yes, call.” at 13:59 and Rambaut “Stay on here in case we need to message” at 13:59; the
messages typed during the call run from 14:13 (“Just FYI - o-linked glycan also present in bat”) to 15:01, and
“Can we do a zoom?” follows at 15:01, with the Zoom link at 15:05, the “after-call” by your caption. Read as Eastern, the
call fills exactly 14:00 to 15:00; read as Pacific it would be 17:00 to 18:00 Eastern, outside Fauci's calendar. So
Part 1 is Eastern on two independent anchors (Rambaut 22 Feb and the 1 Feb call), not one.

**Note (2026-11-01).** Part 1 is Andersen's own collection (REV0002899 to REV0003038; the first page says “You
created this private channel”), yet its times are Eastern, while his P.O. emails are Pacific (1.2) and Part 2 is
Pacific (1.3). Slack prints times in the zone of the session that produced the capture, so Part 1 was captured in an
Eastern session. Who or why is not known: you suggest the investigators who acquired it; another setting on his
account is also possible. Either way Part 1's Eastern time says nothing about Andersen's own clock. The two anchors
above decide Part 1; the REV numbering does not.

---

# Part 2. Not settled and only supported datetimes (260 emails)

## 2.1 Supported but not proven (260 emails)

Consistent with every test (every reply pair it touches is in order), but reply order cannot catch a copy that
is simply too early; the Farrar message `farrar-fauci-comms.pdf` pp.154-155, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call” was five hours early and the test passed. Marked `Supported`.

| Zone source | Emails | Zone used |
|---|---|---|
| Quoted block: clock of the quoting message's author (the freeze rule, 5.6) | 231 (151 P.O. emails, 80 Farrar-Fauci; the Farrar-Fauci ones include every block physically nested under another block on the same page, see 5.10) | the author's institution zone |
| Sender: Jeremy Farrar, top-level (Farrar-Fauci release) | 1 | London (he is based in London, reviewer, 2026-11-01) |
| Sender: Wellcome convener (other unzoned stamps) | 5 (3 Farrar-Fauci, 2 P.O. emails) | London |
| Sender: NIH, Bethesda (Farrar-Fauci release) | 2 | Eastern |
| Page owner **LIP**, top-level (P.O. emails) | 8 | Eastern |
| Page owner **FARZAN**, top-level (P.O. pp.142-143) | 2 | Eastern: Farzan works at Scripps Research, Jupiter, Florida (reviewer, 2026-11-02); the pages end “HIGHLY CONFIDENTIAL AND PROPRIETARY FARZAN-0000102/103”. Found 2026-11-02; before that these pages were read as Scripps Los Angeles. |
| Page owner **GARRY**, top-level (P.O. emails) | 11 | Chicago (Central): Garry works at Tulane University School of Medicine, New Orleans (Central time), per the reviewer, 2026-10-29. Reply order excludes Pacific. No exact copy proves it; a trip away from Central would not show. |

## 2.2 Not settled (0 emails)

None. The last one (Harris pp.42-43) was cleared on 2026-11-02 when the lookup learned who quotes it: Ilona Kickbusch (Geneva), whose name the OCR had read as “ee” (a redaction code).

| Historical category | Emails | Zone used | Notes |
|---|---|---|---|
| Sender, small groups (`FOR_HUMAN_REVIEWER.md`, U11) | 1 | by sender | Harris `farrar-fauci-comms.pdf` pp.42-43, “Freitag, 6. Marz 2020 11:56”, is quoted in a message whose author the lookup does not know (the OCR gives the name as “ee”) |
| Sender, small groups (`FOR_HUMAN_REVIEWER.md`, U11, U18, U19) | 3 | by sender | U11, U18 and U19 are quoted in messages whose authors the lookup does not know (the OCR gives one as “ee”, the others are Kimberly Barasch and Teresa Miller de Vega) |
| Sender, small groups (list in `FOR_HUMAN_REVIEWER.md`, items U5 to U14) | 10 | by sender | No quote rule possible: 5 are not quoted by anything, 5 only by an inferred link (which proves no quote); each has one to four linked replies to test. One of them, Esveld p.43, is a separate question (item U5): London (mailbox clock) or Amsterdam |

---

# Part 3. Issues in your P.O. piece

Other article issues were recorded in `TRAGICOMEDY_ISSUES.md` (private,
git-ignored; not present in this worktree). This audit covers the 8 February
correspondence and its directly dependent passages. The correction commit
`d311367` is an ancestor of `po-sources-and-boxes` at `c0f6933`; its 160/160
test result covered only that earlier change. On 2026-11-15, source images for
the residual PO email records and Slack pages were reopened, and the current
app records, page maps, reply graph and chapter links were corrected in this
branch. The live Medium article has not been independently checked; the user
is handling those edits. The remaining source uncertainties are identified
below, and the app test/push status is recorded in the handoff.
The user reports that the Part 1 Medium article reordering and text corrections
for §§13.1-13.14 have been applied, including the Drosten attribution and
Ferguson's 9 Feb 20:00 UK response. Cross-references and Part 2 §§14.4, 15.2
and 15.3 were still in progress at the last update. The live Medium article
was not independently checked.

## 3.1 The February 8 correspondence: evidence and chronology

**Scope and confidence.** The article's Part 1 sections 13.1-13.14 and
dependent Part 2 sections 14.4, 15.2-15.3 and footnote 49 were checked against
the page images, both email JSONs, their page maps, Slack p.23 and the chapter
links. PDF page numbers below are physical PDF pages, not Bates numbers. UK is
UTC in February 2020; Eastern is UTC-5, Pacific UTC-8, Rotterdam and Berlin
UTC+1, and Sydney UTC+11. A printed stamp is **verified** by the page image;
its conversion is **supported** when it relies on a mailbox/client clock
without a printed offset. In particular, a recipient address by itself does
not prove the clock. The previously accepted REV-Pacific rule is supported by
the independent anchors in 1.2, not by the fact that `kga1978` is Andersen.

**Which response was first?** Vallance is the earliest feedback documented in
the checked copies, at 12:03 UK on 8 February, before Fouchier's 19:36 UK on
8 February and Ferguson's 20:00 UK on 9 February. This does not establish
that Vallance was the earliest response overall; an earlier or unproduced
reply may exist. Farrar's
09:45 and 09:46 forwards have the same visible text and substantially
overlapping recipients, but their one-minute difference and redactions do not
prove whether they are two sends or two renderings. Vallance quotes the 09:46
copy, while Fouchier and Ferguson quote the 09:45 copy. Do not assert that
Fouchier was first even if the discussion is described as the 09:45 thread.

| UK time, 2020 | Event and direct source | Reading and certainty |
|---|---|---|
| 8 Feb 09:45 | Farrar's request, quoted inside Ferguson's top-level message, `po-emails.pdf` p.57: `Sent: 08 February 2020 09:45`. A Dutch copy inside Fouchier's p.55 reply prints 10:45; Drosten's German copy is `farrar-fauci-comms.pdf` pp.59-60, also 10:45. | **Supported 09:45 UK / 04:45 ET**: the Dutch/German copy and UK-rendered copy agree under the clients' expected zones. The app correction for PO idx 84 now updates the stale key and thread label too. The 09:45/09:46 copies' relationship remains unresolved. |
| 8 Feb 09:46 | Same visible request quoted in Vallance's reply, `farrar-fauci-comms.pdf` p.62, `Sent: 08 February 2020 09:46`. | **Supported 09:46 UK / 04:46 ET**, in Vallance's UK-client quote. App `farrar-fauci` idx 82. The difference from 09:45 is real in the printed copies; their identity is unresolved. |
| 8 Feb 12:03 | Vallance, `farrar-fauci-comms.pdf` pp.61-62, header `Date: Saturday, 8 February 2020 at 12:03`, body on p.62. Quoted inside Farrar's message, itself inside Fauci's explicitly timed p.61 reply. | **Supported 12:03 UK / 07:03 ET**, assuming Farrar's quoting client was in London; app `farrar-fauci` idx 83 agrees. Not an explicit-offset stamp. |
| 8 Feb 15:13; 17:36:34 | Farrar's `10:13 AM` quoted in Fauci's reply, then Fauci's top-level `Sat, 8 Feb 2020 17:36:34 +0000`, `farrar-fauci-comms.pdf` p.61. | Farrar **supported 15:13 UK / 10:13 ET** on Fauci's Eastern client; Fauci **verified 17:36:34 UK / 12:36:34 ET** by offset. App idx 84-85 agree. Slack p.23 prints Garry 12:42 ET, six minutes after Fauci, consistent with article 13.6. |
| 8 Feb 19:36:30 | Fouchier, `po-emails.pdf` p.55, top-level `Message / From: R.A.M. Fouchier / Sent: 2/8/2020 11:36:30 AM`, `Summary.Feb7 RF.pdf`. The 10:45 Dutch header below belongs to **Farrar's quoted request**, not to Fouchier. | **Supported 19:36:30 UK / 14:36:30 ET / 20:36:30 Rotterdam**, on the REV-Pacific export rule; the app's idx 85 record and page map have been corrected. Slack p.23 prints Garry's notice of Ron's email at 14:47 ET, 11 minutes later. |
| 8 Feb 19:52; 20:11; 20:21 | Drosten's 9 Feb `6:52 am` is quoted by Holmes, `po-emails.pdf` p.53 and `farrar-fauci-comms.pdf` p.59; Holmes's `8 February ... 20:11` is quoted by Farrar, `po-emails.pdf` p.52 and Farrar-Fauci p.58; Farrar's `20:21` is quoted on PO p.52 and appears as German `21:21` on Farrar-Fauci p.57. | **Supported 19:52, 20:11 and 20:21 UK**, respectively, from Sydney, London and Berlin/London clients. Holmes addresses **Drosten**, not Fouchier. PO idx 86-88 and FF idx 86-87/150 have the corresponding values. The p.53 source image shows Drosten's message quoting Farrar's request; app idx 86 now links to Farrar idx 84, not Fouchier idx 85. |
| 8 Feb approximately 21:15-21:16; 21:27:14 | Andersen's `21:16` UK-client header is nested inside Farrar's top-level `2/8/2020 1:27:14 PM` REV message, `po-emails.pdf` p.144. The same Andersen text appears in Koopmans's copy as `22:15` inside her message, `farrar-fauci-comms.pdf` p.56. | **Supported Andersen 21:15-21:16 UK / 16:15-16:16 ET**, with a one-minute difference between copies (Koopmans's 22:15 Netherlands time is 21:15 UK), and Farrar **21:27:14 UK / 16:27:14 ET** on REV-Pacific. Farrar explicitly quotes Andersen, not Holmes. Slack p.23 prints Rambaut 16:19, Andersen 16:21 and Garry 16:30 ET; the last quotes Farrar's message. App idx 92 now maps to pp.144-145 and retains the PO copy's 21:16 time. |
| 8 Feb 21:16?; 22:50 | `po-emails.pdf` p.51: Rambaut's `Saturday, February 8, 2020 4:16 PM` is quoted under Fouchier's top-level REV `2/8/2020 2:50:00 PM`. Fouchier's message quotes Rambaut's argument. Slack p.23 prints Andersen quoting Fouchier at 17:52 ET. | Fouchier **supported 22:50 UK / 17:50 ET** on REV-Pacific, consistent with Slack two minutes later; app idx 83 is corrected and linked to Rambaut idx 91. The article's 21:16 UK for Rambaut assumes the quoted `4:16 PM` is Eastern, but the page and matching copies do not establish that clock. App idx 91 now preserves 8 Feb, leaves normalized time unresolved, and has no unsupported parent reply link. |
| 9 Feb 20:00:46 | Ferguson, `po-emails.pdf` p.57, top-level `Message / From: Mike Ferguson / Sent: 2/9/2020 12:00:46 PM`, with `Summary.Feb7_MF.pdf`; the annotated draft includes p.61. | **Supported 20:00:46 UK / 15:00:46 ET** on REV-Pacific, not noon UK on 8 Feb. PO idx 93 now has the verified sender and an explicit quote link to Farrar's 09:45 request (idx 84). No earlier copy of this email at 12:00 UK on 8 Feb was verified; do not infer one from the attachment. |
| 9 Feb 20:07; 10 Feb 09:26:57 | Koopmans is quoted under Farrar's top-level reply on `po-emails.pdf` p.69: `Sunday, 9 February 2020 at 20:07`; the same pair on `farrar-fauci-comms.pdf` p.55 has Farrar `Mon, 10 Feb 2020 09:26:57 +0000`. | Koopmans **supported 20:07 UK / 15:07 ET**; Farrar **verified 09:26:57 UK / 04:26:57 ET** by explicit offset, which also confirms the REV top-level `2/10/2020 1:26:57 AM` is Pacific. App idx 94 now identifies Koopmans and is linked as an inferred same-conversation reply; idx 95 now has the Feb. 10 ET date/key and explicitly quotes Koopmans. §15.2 links to idx 94. |

### Original article claims checked and correction evidence

The bullets below describe the audited original passages and the source-based
correction. The user reports that Part 1 text corrections were applied, but
the live Medium article was not checked; do not read these descriptions as
claims that the article still contains the original errors.

- **13.1 (Part 1 PDF p.145):** the 09:45 UK value is supported and the
  request is on PO p.57, continuing on p.58. Do not equate it uncritically
  with the 09:46 copy or assert it is the only send.
- **13.2 (pp.145-147, both captions):** replace 10:36 UK / 11:36 Rotterdam
  and “first” with the supported 19:36 UK / 20:36 Rotterdam and avoid a
  first-response claim. Footnote 49 (Part 2 p.190) interprets “Andrew's
  comments”; this does not prove when those earlier comments were sent, to
  whom, or whether the later Rambaut reply on p.51 is the same material.
- **13.3 (pp.147-148):** the heading, “second”, “12:00 pm UK”, and “less
  than two hours” are unsupported for the p.57 Ferguson email and its
  attachment. P.61 is an annotated draft page, not its timestamp; p.56
  continues Fouchier's quoted Farrar request, not Ferguson's email. Cite
  p.57 for the header/body and p.61 for the annotation. Under the accepted
  clock Ferguson's reply followed the request by about 34 hours 16 minutes,
  not less than two hours.
- **13.4 (p.148):** 12:03 UK is supported, but not “a few minutes after
  Mike Ferguson”; this documented Ferguson email came the following day.
  Cite Farrar-Fauci pp.61-62 for header and body, not p.62 alone for the
  header. The reply shown is to the 09:46 rendering.
- **13.5 (pp.149-150):** Slack p.21 prints Garry 08:09 ET and Rambaut
  08:30 ET, supporting the article's 13:09 and 13:30 UK and its approximate
  “one hour later” relative to Vallance's 12:03. These labels do not establish
  whether Garry or Rambaut had read Vallance's email.
- **13.6-13.8 (pp.150-155):** Slack pp.21-22 print Rambaut 08:30 ET and
  Garry 08:43 ET, supporting the 13:30 and 13:43 UK labels. The cited
  Vallance, Farrar, Fauci, Drosten
  and Holmes times are consistent with the source readings above. They do
  not establish that Drosten replied to Fouchier.
- **13.9 (pp.155-158):** p.52 shows Holmes addressing Drosten, so “answer
  to Fouchier” and Farrar “jumping on Holmes's answer to Fouchier” are
  misattributions. The p.51 caption `8 Feb 2030` must be 2020. The source
  prints Rambaut's 4:16 PM without a zone; 9:16 UK / 4:16 EST is plausible
  but needs a clock anchor, not merely the existing app record. Other 20:11
  and 20:21 readings are supported.
- **13.10-13.13 (pp.159-164):** Slack p.23 shows Garry 14:47 ET and
  Andersen 15:53 ET, consistent with 19:47 and 20:53 UK, after Fouchier's
  first email. The PO copy of Andersen is 21:16 UK and the Netherlands
  rendering is 21:15 UK, so an exact simultaneous “precise time” with
  Rambaut is not established; Farrar 21:27 follows either. For 13.11 the
  9:19 caption refers to Rambaut's Slack question, while Andersen's answer
  prints 16:21 ET = 21:21 UK. The 13.13 22:50 and Slack 22:52 sequence is
  supported.
- **13.14 (pp.164-165):** Slack p.24 prints Holmes at 18:42 ET, supporting
  23:42 UK. This is 2 hours 15 minutes after Farrar's 21:27 message; the
  “about two hours” description is consistent.
- **Part 2 14.4 (p.4):** the 21:27 message says Farrar and Holmes had
  **just come off** the NASEM call. It establishes an upper bound for the
  end, not that the call took place at 21:27; its start and exact duration
  are not established by that email.
- **Part 2 15.2-15.3 (pp.13-14):** Koopmans's 9 Feb 20:07 and Farrar's
  10 Feb 09:26 are supported; the 15.3 image caption says **9 Feb** for
  Farrar, contradicting both its heading and the explicit-offset source. The
  user is finishing these Part 2 edits and the related cross-references.

### App records, links and display: implemented corrections and remaining uncertainty

| Record / surface | Audit finding and current status |
|---|---|
| PO idx 83-95 | **Corrected in this branch.** Idx 83 is Fouchier 17:50 ET / 22:50 UK on p.51 and explicitly quotes idx 91; idx 91 retains its printed 8 Feb date but has no normalized time or unsupported parent link. Idx 84 remains 04:45 ET; idx 85 remains 14:36 ET and quotes idx 84; idx 86 now links to the quoted Farrar request (idx 84), not Fouchier. Idx 92 is 16:16 ET on 8 Feb and maps to pp.144-145; its explicit Drosten quote link is retained. Idx 93 identifies Mike Ferguson at 15:00 ET on 9 Feb and quotes idx 84. Idx 94 identifies Marion Koopmans at 15:07 ET and has only an inferred conversation link to idx 92; idx 95 is 04:26 ET on 10 Feb and explicitly quotes idx 94. |
| Page maps, guide and chapter links | **Corrected in the app.** Idx 92 maps to pp.144-145 (not pp.70-145); the other affected entries' maps follow their corrected keys. The app guide now places Fouchier, Ferguson and Vallance in §§13.2-13.4 with the verified records and pages; §13.9's former 2030 typo is corrected to 2020, while Rambaut's nested 4:16 pm zone remains explicitly unresolved. Part 2 §15.2 now links to Koopmans idx 94; Ferguson idx 93 links to §13.3. The live Medium article has not been checked here. |
| Slack pp.21-24, 35, 64-65 / app | **Source-read labels applied.** Part 1 now records p.21 Garry 08:09 and Rambaut 08:30 (app idx 245-246), p.22 Garry 08:43 (idx 247), p.23 Garry 14:47, Holmes 15:32, Andersen 15:53, Andersen 16:21 and Garry 16:30 (idx 261-262, 265, 269-270), and p.24 Holmes 18:42 (idx 277). P.35 now reads 18:18, 18:20, 18:21 and 18:22 in page order (idx 376-379). P.64 Garry 10:59 is confirmed; p.65 is Garry 14:44 followed by Andersen 14:45 (idx 727-728). |
| Remaining source uncertainty | The printed 09:45 and 09:46 forward copies differ by one minute; whether they are separate sends or renderings remains unresolved. Rambaut's nested `4:16 PM` on PO p.51 has no independently established time zone. On Slack p.55, Holmes's 02:16 post has no day chip above it; the later Feb. 20 chip does not establish whether the post belongs to Feb. 19 or 20. The current Part 1 time-check CSV retains four rows (pp.42-43, 47, 54-55 and 134-135); they have not been independently settled in this pass. |
| Pipeline and UI | Source corrections are kept in the override/fix inputs and regenerated app data, with focused regression coverage. The user is handling the Medium article; its live text has not been independently checked and no article source was edited. The daily chart still does not show within-day order. |

The existing “all reply pairs in order” and “zero cross-release violations”
reports were historical checks of the generated graph, not independent proof.
The merged app corrections address some identified February 8 record and
navigation defects, but the residual discrepancies in the table above remain,
along with the source ambiguities and Slack OCR discrepancies. The audit's
`zone_format_audit.csv` findings describe an earlier data state and should not
be read as a current app status report.

---

# Part 4. Issues in the web app: what was found and fixed (2026-11-01)

The items below are historical fixes from earlier rebuilds. The February 8
app status is updated in Part 3.1.

## A1. Folkers' 8:43 PM: fixed
`po-emails.pdf` pp.4-11, “Friday, January 31, 2020 8:43 PM”, Folkers, Greg, was shown as 23:43 Eastern (REV rule, Pacific), later than the Fauci forward that quotes it (`farrar-fauci-comms.pdf` p.147, stamped `Sat, 1 Feb 2020 02:47:39 +0000` = 21:47 Eastern). It is on Fauci's Eastern clock: **20:43 Eastern**. Now a verified correction.

## A2. A Slack message on the wrong day: fixed
`slack-part1.pdf` p.4, Andersen, 22:42, was dated 2 Feb; it is the evening of 1 Feb (the day divider had been applied one message too early). Corrected through `tools/slack_date_fixes.json`.

## A3. Slack Part 1: times run backwards (80 at first, 3 after the readings of 2026-11-03/05): 6 of the 12 evening-then-small-hours cases fixed
Of the 12 cases where an evening message is followed by a small-hours message on the same date, **6 are the same fault as A2** (a single evening message whose date is one day too late, because the divider was applied one message early). In each, the previous timed message belongs to the previous day with an earlier time, and the next one is a small-hours message of the day. Checked on the page image for `slack-part1.pdf` p.9 (the “February 3rd” divider sits below the 22:35 message). Fixed: p.9 (22:35, 2 Feb), p.16 (20:11, 5 Feb), p.21 (19:11, 7 Feb), p.35 (19:45, 11 Feb), p.39 (22:26, 12 Feb), p.134 (23:56, 20 Apr). The other 6 are not that pattern (the evening run is long and contiguous with the same date, or the dates jump: p.60, 22 Feb vs 24 Feb); on the page image of p.19 the times rise steadily, so the “01:49” is a misread digit. They stay in `slack_part1_time_check.csv`, together with the other backwards times, as probable misread digits. Update 2026-11-04: the reviewer's six readings and 59 labels from an external OCR pass (`tools/slack_time_fixes.json`) and 26 more from its STATUS file and 10 more readings by the reviewer (2026-11-05) leave 3 backwards pairs; see FOR_HUMAN_REVIEWER U17.

## A4. Slack times carry no zone: done
Slack Part 2 (Pacific) is converted to ET, Part 1 (Eastern) is labelled ET; both show the printed local time in the 🕑 chip.

## A5. Chapter link for section 4.11: open
The article caption “Farrar proposes a way out via the WHO (1 Feb, 3:59 pm EST)” is linked to Fauci's `farrar-fauci-comms.pdf` p.137, “Saturday, 1 February 2020 at 15:50”, “RE: Teleconference” (“Please include Francis Collins…”), which is not about the WHO. The Farrar message that proposes WHO contact is `farrar-fauci-comms.pdf` p.108, “Sunday, February 2, 2020 4:48 AM” (now 23:48 ET on 1 Feb). Neither is at 3:59 pm Eastern, so the link is probably wrong and the caption time may be off too. Needs your decision (FOR_HUMAN_REVIEWER.md, O1).

## A6. Farrar's original “Phone call” body: fixed
`po-emails.pdf` pp.3-4, “Friday, January 31, 2020 5:23 PM”: the body (“Tony / Really would like to speak with you this evening / It is 10pm now UK / Can you phone me on +44 … / Jeremy”) is typed from the page image into the override. The header's Sent line, cut by OCR, is also restored.

## A7. The Farrar 22:34 message: fixed
`po-emails.pdf` p.3: the page image shows “From: Conrad, Patricia (NIH/NIAID) on behalf of Fauci, Anthony”, to Jeremy Farrar, “RE: Phone call”, “Will call shortly…”, signed Patricia L. Conrad. The sender label is now “Conrad, Patricia (on behalf of Fauci, Anthony)”, and it replies (explicit, quoted inline on the same page) to Farrar's 5:23 PM “Phone call”, 11 minutes earlier.

## A8. Cross-release quote check: run, no violation
`tools/cross_release_check.py` looks for the body of each entry of one release inside an entry of the other release and tests that the quoted message is not later than its quoter. 6 quoted pairs found, 0 violations (the Folkers one, A1, was the case that prompted it). Signature blocks are excluded. Output: `cross_release_check.csv`.

## A9. A bug of mine, found and fixed: two verified overrides were swapped
After the 2026-10-29 rerun I re-pointed the “Phone call” 5:23 PM override to the wrong key, so the p.2 message (“Re: Phone call”, 5:57 PM) showed 5:23 PM and the pp.3-4 message (“Phone call”, 5:23 PM) showed 5:57 PM. Both are now on the right entries (keys `po-emails|2020-01-31|1200` for p.2, `|1500` for pp.3-4). Lesson: when keys change, re-check every override target by its page, not by its time.

## A10. Bookmarks
268 old bookmark keys are re-mapped. A few old keys now name a different message and cannot be re-mapped (the old key is still live): `po-emails|2020-01-31|1500` (now the pp.3-4 message), `|2020-02-04|2008`, `|2020-02-05|1500|1`, `|1500|2`, `|1500|3`, `|2020-02-16|1750`, `|2020-02-16|1806`, `|2020-02-17|1641`, and one with no unique match, `farrar-fauci|2020-02-01|1343|1`. Anyone who bookmarked one of those will see the wrong message.

---

# Part 5. Method

## 5.1 Rules in use (the first that applies wins)

- **Rule 1. Zone written in the stamp** (numeric offset or named zone).
- **Rule 1b. Exact copy with an explicit offset.** Text match (similarity >= 0.95, same or adjacent day) with a
  copy that has an explicit offset takes that copy's instant. `tools/anchor_copies.py`.
- **Rule 1c. Verified from the page image or the message text.** Hand-checked, with the evidence in
  `tools/verified_overrides.json`, applied by `tools/apply_verified_overrides.py`. The thread key is unchanged.
- **Rule 2. Quoted copy takes the replier's zone** (your footnote rule), where the quoting link is known.
  Not always the replier's own clock. Stated in full, with examples, in 5.6.
- **Rule 3. Unzoned top-level stamp, Farrar-Fauci release:** the sender's institution.
- **Rule 4. Unzoned top-level stamp, P.O. emails:** the page owner (REV Pacific, GARRY Chicago, LIP Eastern).

After the rules: same instant and same text, one copy kept (explicit offset first, then the fuller sender name;
never on a partial or unparsed stamp, whose time is a default); header-only fragments matching a full entry are
removed under the same condition; an inferred link that the corrected times put backwards is dropped (explicit
links are never touched).

## 5.2 Rules considered and not used

- **A 24-hour day-month-year stamp is London time.** Too flaky: format is a proxy for locale, US clients can use
  day-first formats. Kept as a hypothesis only.
- **A long-format (US) stamp is Eastern.** The US zone depends on the mailbox.
- **Eastern as the default for unzoned Farrar-Fauci stamps.** Removed.
- **Page owner decides every stamp on its pages.** Kept only as rule 4.
- **An early global sender-affiliation interpretation of quoted blocks.** On 150
  candidates it would change 59 and create 11 reply-order violations (shifts of -17, -19 hours). Rejected.
  This historical experiment did not settle the clock of each physical quote;
  the later nesting approach in 5.10 and the exceptions in 3.1 supersede it.

## 5.3 Checks and their limits

- **Exact copies** (`tools/anchor_copies.py`, `tools/owner_zone_check.py`): few exist; one anchor, one REV pair.
- **Reply order** (`tools/reply_order_check.py`): each zone group is shifted by whole hours; a shift that puts a
  reply before its parent is ruled out. It cannot catch a quoted copy that is simply too early, and it depends
  on the reply links being right. “Only the current zone is allowed” means consistent, not proven.
- **Cross-release bound** (new): a quoted message cannot be later than the message that quotes it, even when
  the two sit in different releases (this is how the Folkers error in A1 was found). Not automated yet.

## 5.4 Anchors in the message text

I searched every email and Slack message for sentences stating the sender's local time (“it is 2 am here”),
then for looser phrasings. Usable: the Farrar “It is 10pm now UK” (emails; used), and the three Slack
messages above. Not usable: statements about the future (“starting at 5am my time”), the Farrar UK-time
sentences of 26 Feb 2020 (meeting times, not the time of writing), sentences with no number, and Slack
messages that have no time. A few email bodies were lost by OCR (the Farrar message was one), so a similar
sentence could be hidden in the page images; the 386 pages have not all been read.

## 5.5 Where the files are

- `analysis/chronology/`: this file and `FOR_HUMAN_REVIEWER.md`. Generated
  CSVs and report logs remain in `analysis/`; OCR review notes are in
  `analysis/slack-qa/`.
- `tools/`: scripts, `verified_overrides.json`, `entry_ref.py` (see `tools/README.md`).
- `docs/`: project notes. `source_ocr/`: OCR text. `page_based/`: the published app and its data.

## 5.6 The freeze rule (quote and forward), with examples

**The rule.** An email program stamps a message in the clock of the program that shows it. When someone
replies to or forwards a message, the program copies the original's header into the new message, and the stamp
in that copy is frozen on the clock of the person who replied or forwarded. It no longer follows anyone's
clock. So the time printed on a message depends on where we see it:

1. **A top-level message** (the message itself, not inside another) is on the clock of the mailbox that holds
   it. In a page-owner export (REV, GARRY, LIP, FARZAN) that is the owner's clock.
2. **A quoted or forwarded message** is on the clock of the person who quoted or forwarded it, not the
   clock of its own author.
3. **Several copies of one message** can therefore print different times. Each copy is right for its own clock.
4. **The last message of a thread has nothing quoting it**, so rule 2 cannot be applied to it. It is
   top-level and sits on the clock of the mailbox it was exported from. If we cannot find a quote or forward of
   a message, we must not invent one. A reply link that the parser only inferred (“same conversation”) does
   not prove that a quote exists.

**Example (illustrative; Sydney is 11 hours ahead of Edinburgh).** Holmes (Sydney) and Rambaut (Edinburgh)
reply to each other, one hour apart. In absolute time (UTC) the chain is H1 21:00, R1 22:00, H2 23:00,
R2 00:00. On their own clocks:

| Message | Holmes's clock (UTC+11) | Rambaut's clock (UTC+0) |
|---|---|---|
| H1 Holmes, first | 08:00 | 21:00 |
| R1 Rambaut replies | 09:00 | 22:00 |
| H2 Holmes replies | 10:00 | 23:00 |
| R2 Rambaut replies | 11:00 | 00:00 |

Each reply quotes its parent, so in the final printed thread:

- H1 is quoted by R1 (Rambaut), so it prints on Rambaut's clock: **21:00**.
- R1 is quoted by H2 (Holmes), so it prints on Holmes's clock: **09:00**.
- H2 is quoted by R2 (Rambaut), so it prints on Rambaut's clock: **23:00**.
- R2 is the last message. Nothing quotes it, so it prints on the clock of the mailbox it is shown in, for
  example Rambaut's own, **00:00**.

The printed order is 21:00, 09:00, 23:00, 00:00. It looks scrambled, yet every stamp is correct for its clock.
So a reply that prints earlier than the message it answers, or later by many hours, is not by itself an
error. The check is: convert each stamp to one clock using the clock that froze it, then test the order.
Whoever is far ahead or behind the others (Holmes, Sydney) makes the largest jumps.

**Using it.** To read a quoted stamp, find who quoted it: the quoting message sits immediately above the
quote, and its author's clock is the one to use. To read a top-level stamp, use the mailbox owner's clock. The
quoting link must be explicit (the quote is visible in the page), not just a guessed same-conversation link.

## 5.7 Tricks for fixing a zone

1. **Anchor sentences.** “It's 1 am here”, “it is 10pm now UK” give the sender's clock at that moment (5.4).
2. **Exact copy with an explicit offset** (rule 1b).
3. **Reply order under the freeze rule.** Convert with the clock that froze each stamp (5.6), then test the
   order. A zone that puts a reply before its parent is ruled out. A zone that fits every pair is only
   supported, not proven.
4. **Page code continuity.** Every page of a mailbox export carries a code at the bottom right (for example
   GARRY0000nnn or REV0000nnn). If page n has code N, the natural previous page has code N-1. If the previous
   PDF page does not carry N-1, the export was spliced there and the two pages are probably not the same
   conversation. If it does, and the subject continues, the messages belong to one thread, which tells us which
   mailbox, and so which clock, froze each stamp. Used to decide whether a quote or forward exists across a
   page break. Not automated; check on the page images.
5. **Bracketing.** If a person's message sits, in the true reply order, between two messages whose absolute
   times are exactly known (explicit zone, exact copy or verified), and those two are at most an hour apart,
   then the middle message was sent inside that hour. Its printed stamp then fixes the offset of the clock
   that froze it: the offset is the whole number of hours (or half hours) that moves the printed time into the
   window. Example (illustrative): A is 14:00 UTC and B is 14:40 UTC, both exact. In between, M prints
   “9:20 AM”. Moving 9:20 into 14:00-14:40 UTC takes +5 hours, so M's clock is UTC-5 (Eastern, winter). The
   narrower the window, the surer; a window wider than an hour allows two whole-hour answers. It needs the
   reply order to be right and the stamp's freezing clock to be known (5.6).
   Not yet run across the data.
6. **Dangling last message.** Rule 4 of 5.6: the last message of a thread cannot be tested by quote or forward.
   Use only mailbox-owner evidence for it, and say so.

Order of preference: exact evidence (1, 2) first; then bracketing (5); then reply order (3); page continuity
(4) decides which of these may be used; the owner and institution defaults only last.

## 5.8 The freeze rule in the code, and the checks (2026-10-29)

**Code change.** In `foia_parser/core.py` (`reconcile_zones`) a quoted block now takes the clock of the AUTHOR of
the message that quotes it, read from the affiliation table (new profile option `freeze_rule_author_zone`).
Before, a block on a GARRY, REV or LIP page was given the page owner's clock before the quote rule ran, and
the rule then skipped it. Where the quoting message was top-level, the rule also used the mailbox clock
and not the author's. An explicit zone in the stamp is never overridden. Lipkin (Columbia, Eastern) was added to
the affiliation table. `tools/build_bookmark_rekey.py` now matches within 24 hours (Sydney moves an entry by
up to 16 hours).

**Effect.** 104 P.O. emails and 9 Farrar-Fauci emails changed time (by up to 16 hours). Explicit quote links that
survive the parser's "no quote before it was sent" test went from 108 to 144 (P.O. emails): 36 links that the old
clocks put backwards are now in order. The reply-order test still allows only the current clock for every group.
The app tests (8) and the app audit (66 checks) pass.

**Checks with `tools/freeze_bracket_check.py`** (changes nothing; writes `freeze_bracket_check.csv`):
- **Bracketing on REV, a test of the method:** 24 top-level REV stamps are bracketed by exact anchors; the
  offsets allowed by all of them are exactly -8 and -7 (Pacific winter and summer). Method and rule agree.
- **Bracketing on GARRY:** 8 top-level Garry-mailbox stamps, 2 bracketed, none narrow. It cannot choose
  between Chicago and Eastern yet.
- **Bracketing on LIP:** 9 top-level stamps, 2 bracketed, none narrow.
- **Two pairs still reversed under the author-home-clock reading** (checked by the script, not applied by the
  parser, which keeps the link only when the times agree): `po-emails.pdf` pp.22-29, “5 Feb 2020 1:03 pm”, Robert Garry
  and “2/5/2020 1:23:41 AM”, Edward Holmes; and p.28, “5 Feb 2020 9:04 pm”, Edward Holmes and pp.28-45, “2/5/2020 4:22:24 AM”,
  Edward Holmes. Page images to read.
- **Feb 10 chain (pp.65-67):** with the rule, Holmes's “10 Feb 2020 21:11” (quoted by Rambaut, London) is 16:11 ET,
  Holmes sends the document to Lipkin at 16:33 ET (22 minutes later) and Garry's “2/10/2020 3:51:18 PM” is 16:51 ET
  under Chicago. Under Eastern it would be 15:51 ET, before the 16:11 ET message about Lipkin's call. This
  supports Chicago, but it assumes that Garry's message is a reply to that report (his link is only inferred).
- **11-12 Feb chain (pp.75-77):** the order is now consistent: Lipkin 09:40 ET on 11 Feb, Garry's first reply
  (“12 Feb 2020 1:00 pm”, read on Holmes's Sydney clock) 21:00 ET, Holmes's forward 02:15 ET on 12 Feb.
- **Page-code continuity:** Garry runs pp.65-66 (GARRY 263-264), pp.75-77 (272-274) and pp.83-87 (306-310);
  the neighbouring pages are REV.

GARRY stays **Supported** (Tulane, Central; reply order excludes Pacific; the Feb 10 chain favours Chicago), not Settled.

## 5.9 Whose clock the code assumes for a quoter (2026-11-01)

The freeze rule needs the clock of the person who quoted a block. The documents rarely state it, so the parser
carries a lookup, name pattern to zone, in `ZONE_BY_AFFILIATION` (`tools/parse_po_emails.py`, `tools/parse_farrar_fauci.py`). It is only the
code's way of knowing where each person is; when a quoter is missing from it the rule is silently skipped for the blocks that person quoted.
On 2026-11-01 the reviewer gave three facts, now in the lookup: **Jeremy Farrar: London; Marion Koopmans and Ron Fouchier: Rotterdam (Erasmus MC; the zone is
`Europe/Amsterdam`, the only Dutch zone); Edward Holmes: Sydney (already there).** Effect: 15 times moved (8 P.O. emails, 7 Farrar-Fauci), most by one to
five hours (one by 9 hours: Andersen, 8 Feb 22:15, quoted by Koopmans, now 16:15 ET); reply order still allows only the current clock for every group;
app tests 8 PASS, audit 66/66. Fouchier and Koopmans now have their own group (`Erasmus MC, Netherlands`, 5 linked pairs, only shift 0 allowed) and Farrar his own
(`Jeremy Farrar, Wellcome Trust (London)`, 41 pairs, only shift 0 allowed), so the small London senders are not given Farrar's pairs as support.
Dzau is not in the lookup; his two stamps are verified from the message text (FOR_HUMAN_REVIEWER.md, S3).

## 5.10 Physical nesting = quote (2026-11-02, reviewer's decision)

In the Farrar-Fauci release every top-level message prints a stamp with an explicit offset (`Sent: Sat, 1 Feb 2020 22:06:26 +0000`). Any other header (`Sent: Saturday, February 1, 2020 4:00 PM`, `Date: Saturday, 1 February 2020 at 20:50`) is therefore a block printed inside the body of the message above it. **A header that sits on the same page as body text of the block above it is quoted by that block**; a header that opens a page is not linked, because a page break may be a different extract, unless the reviewer has read the page image and declared that page's first header nested (`nested_page_starts`; p.58, Holmes, 2026-11-02: no top-level separator above it). The block above is the quoter, so the freeze rule gives the block the clock of that quoter's author.

Example (pp.115-116, 1 Feb 2020): Fauci `22:06:26 +0000` quotes Farrar `4:00 PM` (Eastern, Fauci's clock) which quotes Collins `20:50` (London, Farrar's clock) which quotes Farrar's `3:07 PM` (Eastern, Collins's iPhone) ... and the 19:56 message with Koopmans's `19:43` under it (London, Farrar's clock). Every time is then in order and the call (2 to 3 pm ET) is bracketed by them.

The rule found by itself every correction I had made by hand for that chain (14:56, 16:00, 15:50, 15:12, 14:43, 10:49, 10:48, 10:50), moved about 45 more Farrar-Fauci times by ±5 h (Outlook-style `Sent: ... AM/PM` blocks quoted by Fauci or Collins are Eastern, not London; Apple-style `Date: ... at HH:MM` blocks quoted by Farrar are London, not Eastern), and left the reply-order test clean (250 quoted pairs, only shift 0 allowed). The same release has a fallback: when the quoting author is not in the lookup of where people live, the block takes the quoting message's own reading (a default guess), and is marked Not settled.

It is switched on only where a profile gives a `top_level_stamp_re` (Farrar-Fauci). The P.O. emails do not have one: a top-level message there can carry an attached document, and the Pope/NASEM case showed that physical order alone links unrelated text.
