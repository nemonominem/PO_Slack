# Zone and date analysis: P.O. Record Search and the email releases

Status as of 2026-10-28. Internal; not published. This file is only about getting the dates and
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

# Part 1. Settled datetimes (203 emails, plus Slack Part 1 and Part 2)

Settled means: fixed by the stamp itself, by an exact copy, by the page image, or by a decision of yours
backed by evidence. `zone_format_audit.csv` marks each email `Settled`.

| Zone source | Emails | Zone used | Evidence |
|---|---|---|---|
| Zone written in the stamp (`+0000`, `UTC+11:00`, `AEDT`, `EST`) | 53 (45 Farrar-Fauci, 8 P.O. emails) | as written | The stamp |
| Exact copy with an explicit offset | 1 | from the copy | `po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]” equals the Farrar-Fauci copy `farrar-fauci-comms.pdf` p.154, “Sat, 1 Feb 2020 00:38:35 +0000”, Anthony Fauci, “RE: Phone call” |
| Verified from the page image or the message text | 4 | Eastern or London, per entry | Listed below |
| Page owner **REV** (P.O. emails) | 145 | Pacific | Section 1.2 |

## 1.1 The four verified corrections

- `po-emails.pdf` p.2, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call”: quoted in Fauci's reply, so on Fauci's Eastern clock. The same message appears in the
  Farrar-Fauci release as `farrar-fauci-comms.pdf` pp.154-155, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call”, inside Fauci's reply stamped `00:38:35 +0000`: also a verified correction.
- `po-emails.pdf` pp.3-4, “Friday, January 31, 2020 5:23 PM”, Jeremy Farrar, “Phone call”: Farrar's text says “It is 10pm now UK”, so 5:23 PM is Eastern (22:23 UK).
- `po-emails.pdf` p.3, “Friday, 31 January 2020 at 22:34”, Fauci, Anthony, “RE: Phone call”: decided by you on 2026-10-26. Farrar's “Phone call” left at 22:23 UK; Conrad's reply froze it
  as 5:23 PM on her East Coast clock; Farrar's answer to her carries his own UK clock, 22:34 (11 minutes
  later) = 17:34 Eastern. A decision for this message only, not a rule for the day-first 24-hour format.

## 1.2 REV: the P.O. emails' mailbox is on Pacific time

REV pages (145 emails) are on Pacific time (UTC-8 in winter, UTC-7 in summer), which fits Kristian
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

# Part 2. Unsettled datetimes (183 emails)

## 2.1 Supported but not proven (114 emails)

Consistent with every test (reply order allows only this zone), but reply order cannot catch a copy that
is simply too early; the Farrar message `farrar-fauci-comms.pdf` pp.154-155, “Friday, January 31, 2020 5:57 PM”, Jeremy Farrar, “Re: Phone call” was five hours early and the test passed. Marked `Supported`.

| Zone source | Emails | Zone used |
|---|---|---|
| Sender: Wellcome convener (Farrar-Fauci release) | 56 | London |
| Sender: Wellcome convener (P.O. emails) | 3 | London |
| Sender: NIH, Bethesda (Farrar-Fauci release) | 27 | Eastern |
| Page owner **LIP** (P.O. emails) | 28 | Eastern |

## 2.2 Not settled (69 emails)

| Zone source | Emails | Zone used | Why open |
|---|---|---|---|
| Page owner **GARRY** (P.O. emails) | 40 | Chicago | Reply order excludes Pacific; Chicago or Eastern remain. No exact copy. |
| Sender, small groups (list in `FOR_HUMAN_REVIEWER.md`, item U2) | 19 | by sender | Too few linked replies to test (one to four each) |
| Quoted copy takes the replier's zone | 2 | replier's | Footnote rule, not tested: `farrar-fauci-comms.pdf` p.157, “Jan 30, 2020 7:13 AM”, Jeremy Farrar, “[NA]” and `farrar-fauci-comms.pdf` p.10, “May 12, 2020 12:57 PM”, Jeremy Farrar, “[NA]” |
| No date or time in the data | 8 | none | Need the page image (list in `FOR_HUMAN_REVIEWER.md`, item U4) |

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
Eight emails have no date or time (item U4). The sender-institution groups were mislabelled by hand in an
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
  Not always the replier's own clock.
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
