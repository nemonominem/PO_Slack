# Zone and date analysis: P.O. Record Search and the email releases

Status as of 2026-11-01 (the quote/forward rule is now implemented; see 5.6 and 5.8). Internal; not published. This file is only about getting the dates and
times right and about what is wrong in the P.O. piece and the web app because of them. Every
instruction and decision for you is in `FOR_HUMAN_REVIEWER.md`.

**How entries are named.** Entries are never given by a number. Each is written as: PDF file and pages,
the date and time exactly as printed in its header, the sender, and the subject. (`tools/entry_ref.py`
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

---|---|---|---|
| Sender, small groups (`FOR_HUMAN_REVIEWER.md`, U11) | 1 | by sender | Harris `farrar-fauci-comms.pdf` pp.42-43, “Freitag, 6. Marz 2020 11:56”, is quoted in a message whose author the lookup does not know (the OCR gives the name as “ee”) |

---|---|---|---|
| Sender, small groups (`FOR_HUMAN_REVIEWER.md`, U11, U18, U19) | 3 | by sender | U11, U18 and U19 are quoted in messages whose authors the lookup does not know (the OCR gives one as “ee”, the others are Kimberly Barasch and Teresa Miller de Vega) |

---|---|---|---|
| Sender, small groups (list in `FOR_HUMAN_REVIEWER.md`, items U5 to U14) | 10 | by sender | No quote rule possible: 5 are not quoted by anything, 5 only by an inferred link (which proves no quote); each has one to four linked replies to test. One of them, Esveld p.43, is a separate question (item U5): London (mailbox clock) or Amsterdam |

---

# Part 3. Issues in your P.O. piece

These are in `TRAGICOMEDY_ISSUES.md` (private, git-ignored, not pushed). Nothing in the article has been changed.

---

# Part 4. Issues in the web app: what was found and fixed (2026-11-01)

Everything that had a known problem and a known answer has been fixed. What is still open is in `FOR_HUMAN_REVIEWER.md`.

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
- **A quoted block takes the zone of the quoting message's author (from the author's institution).** On 150
  candidates it would change 59 and create 11 reply-order violations (shifts of -17, -19 hours). Rejected.

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

- `analysis/`: this file, `FOR_HUMAN_REVIEWER.md`, `zone_format_audit.csv`, `reply_order_check.csv`,
  `owner_zone_check.csv`, the dedupe and report logs.
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
