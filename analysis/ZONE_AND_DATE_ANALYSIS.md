# Zone and date analysis: P.O. Record Search and the email releases

Status as of 2026-10-29 (the quote/forward rule is now implemented; see 5.6 and 5.8). Internal; not published. This file is only about getting the dates and
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

# Part 1. Settled datetimes (109 emails, plus Slack Part 1 and Part 2)

Settled means: fixed by the stamp itself, by an exact copy, by the page image, or by a decision of yours
backed by evidence. `zone_format_audit.csv` marks each email `Settled`.

| Zone source | Emails | Zone used | Evidence |
|---|---|---|---|
| Zone written in the stamp (`+0000`, `UTC+11:00`, `AEDT`, `EST`) | 53 (45 Farrar-Fauci, 8 P.O. emails) | as written | The stamp |
| Exact copy with an explicit offset | 1 | from the copy | `po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]” equals the Farrar-Fauci copy `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”, Anthony Fauci, “RE: Phone call” |
| Verified from the page image or the message text | 4 | Eastern or London, per entry | Listed below |
| Page owner **REV**, top-level stamps only (P.O. emails) | 50 | Pacific | Section 1.2. The 95 other REV-page entries are quoted blocks, which now take the quoting author's clock (Supported) |

## 1.1 The four verified corrections

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

---

# Part 2. Unsettled datetimes (278 emails)

## 2.1 Supported but not proven (256 emails)

Consistent with every test (every reply pair it touches is in order), but reply order cannot catch a copy that
is simply too early; the Farrar message `farrar-fauci-comms.pdf` pp.154-155, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call” was five hours early and the test passed. Marked `Supported`.

| Zone source | Emails | Zone used |
|---|---|---|
| Quoted block: clock of the quoting message's author (the freeze rule, 5.6) | 152 (143 P.O. emails, 9 Farrar-Fauci) | the author's institution zone |
| Sender: Wellcome convener | 53 (51 Farrar-Fauci, 2 P.O. emails) | London |
| Sender: NIH, Bethesda (Farrar-Fauci release) | 27 | Eastern |
| Page owner **LIP**, top-level (P.O. emails) | 13 | Eastern |
| Page owner **GARRY**, top-level (P.O. emails) | 11 | Chicago (Central): Garry works at Tulane University School of Medicine, New Orleans (Central time), per the reviewer, 2026-10-29. Reply order excludes Pacific. No exact copy proves it; a trip away from Central would not show. |

## 2.2 Not settled (21 emails)

| Zone source | Emails | Zone used | Why open |
|---|---|---|---|
| Sender, small groups (list in `FOR_HUMAN_REVIEWER.md`, item U2) | 14 | by sender | Too few linked replies to test (one to four each) |
| No date or time in the data | 7 | none | Need the page image (list in `FOR_HUMAN_REVIEWER.md`, item U4) |

---

# Part 3. Issues in your P.O. piece

These are in `TRAGICOMEDY_ISSUES.md` (private, git-ignored, not pushed). Nothing in the article has been changed.

---

# Part 4. Issues in the web app

## A1. Folkers' 8:43 PM is on the wrong clock (23:43 Eastern; should be 20:43 Eastern)
`po-emails.pdf` pp.4-11, “Friday, January 31, 2020 8:43 PM”, Folkers, Greg, “Science: Mining coronavirus genomes for clues to the…” is Folkers' message as quoted inside Fauci's forward (`farrar-fauci-comms.pdf` p.147, “Sat, 1 Feb 2020 02:47:39 +0000”, Anthony Fauci, “FW: Science: Mining coronavirus genomes for clues to the…”, 9:47 PM Eastern), so it is on Fauci's
Eastern clock. The REV rule gives it Pacific = 23:43 Eastern, later than the forward that quotes it. Proposed
fix: add it as a verified correction to `tools/verified_overrides.json`, with this evidence.

## A2. A Slack message was on the wrong day: fixed
`slack-part1.pdf` p.4, Andersen, 22:42, “@Eddie Holmes and @Andrew Rambaut - here's a document I have been
working on” was dated 2 Feb 2020 in the app. It is the evening of 1 Feb (it comes after the 15:05 Zoom message of
1 Feb and before the 01:00 message of 2 Feb; your article, 5.6a, has 1 Feb). The day divider “February 2” had been
applied one message too early. Corrected through `tools/slack_date_fixes.json` (with the evidence), applied by
`tools/parse_part1.py`. The chapter 5.6 button now also appears on this message.

## A3. Slack Part 1: times run backwards in 80 places (listed)
Timed messages whose time drops by more than an hour inside one date, for example 12:47, then 01:28, then 12:50.
Part 1 has no AM/PM and times only the first message of a run, so these are OCR slips or misplaced day dividers.
Part 2 has none. The 80 are in `slack_part1_time_check.csv` (page, printed times, senders, first words; made by
`tools/slack_time_check.py`). 12 follow the evening-then-small-hours pattern of a misplaced day divider (the same
pattern as A2) and need the page image to place; the other 68 look like misread digits. Not fixed.

## A4. Slack times carry no zone: done
Slack Part 2 (Pacific) is now converted to ET and Part 1 (Eastern) is labelled ET; both show the printed local
time in the 🕑 chip. Sorting and the timeline now compare like with like. Related data issues remain in A2 and A3.

## A5. Chapter link for section 4.11
The article caption “3:59 pm EST” (Farrar-Fauci p.112) is linked to Fauci's `farrar-fauci-comms.pdf` p.137, “Saturday, 1 February 2020 at 15:50”, Anthony Fauci, “RE: Teleconference”, 9 minutes away. It may
be a different message.

## A6. Farrar's original “Phone call” has no body text
`po-emails.pdf` pp.3-4, “Friday, January 31, 2020 5:23 PM”, Jeremy Farrar, “Phone call”: OCR kept the header and lost the body; the page image has it.

## A7. The Farrar 22:34 message
`po-emails.pdf` p.3, “Friday, 31 January 2020 at 22:34”, Fauci, Anthony, “RE: Phone call”: the sender label reads “Fauci, Anthony” (the header says “on behalf of”), and the message now has no
reply link (the old link, to Andersen, ran backwards and was dropped).

## A8. Undated and mis-grouped entries
Seven emails have no date or time (item U4; the Pope one, pp.17-18, was read from the page image on 2026-10-30). The sender-institution groups were mislabelled by hand in an
earlier version of the review file; they are now generated from the audit file.

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
   it. In a page-owner export (REV, GARRY, LIP) that is the owner's clock.
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

