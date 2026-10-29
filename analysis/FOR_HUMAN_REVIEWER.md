# For the human reviewer: everything you need to do

This is the only file with instructions for you. The evidence is in `ZONE_AND_DATE_ANALYSIS.md`.

**How to answer:** reply in chat with the item code and your answer, for example “U1: accept Chicago”,
“U3: both match”, “A1: apply”, “P1: change all”. Any order; skip what you like. Nothing changes until you answer.

**How entries are named.** Never by number. Each is: PDF file and pages (PDF page numbers), the date and time
exactly as printed in its header, the sender, and the subject. Slack messages: PDF page, printed time, sender,
first words.

The items are in four parts, matching the analysis file:

| Part | What | Items |
|---|---|---|
| 1 | Settled datetimes | S1 to S4: nothing for you to do |
| 2 | Unsettled datetimes | U1, U2 and U4: your decisions (U3 is now done in the code) |
| 3 | Issues in your P.O. piece | P1 to P4, in `TRAGICOMEDY_ISSUES.md` (private, git-ignored) |
| 4 | Issues in the web app | A1 to A8: what I should fix |
| 5 | Housekeeping | H1 to H3 |

## Do you need to open any CSV or log?

**No file is required.** Every item gives the PDF and pages.

| File | Use it? | For |
|---|---|---|
| `zone_format_audit.csv` | Optional, not needed now | One row per email, with the rule and status. Filter `rule` = “4. Page owner GARRY” to see the Garry-page entries (now Supported) |
| `slack_part1_time_check.csv` | Optional, for A3 only | The 80 places where Slack Part 1 times run backwards; the 12 `late_to_early` rows are the useful ones |
| `reply_order_check.csv`, `owner_zone_check.csv` | No | My test output. Nothing to check |
| `zone_rule_dedupe.log` | Only if an email looks missing | Which copies I removed as duplicates |
| `chapter_links_report.txt`, `bookmark_rekey_report.txt` | No | Link and bookmark housekeeping |

---

**Standard time.** The web app shows every date and time in New York time (ET) first, followed by the local
time as printed, for emails, Slack and everything else. ET stays the standard while local times are sorted out.

# Part 1. Settled datetimes: nothing for you to do

### S1. The Farrar 22:34 reply: done
`po-emails.pdf` p.3, “Friday, 31 January 2020 at 22:34”, Fauci, Anthony, “RE: Phone call”. You answered on 2026-10-26 that Farrar's “Phone call” went out at 22:23 UK (“It is 10pm now UK”), that
Conrad's reply froze it as 5:23 PM on her East Coast clock, and that Farrar's answer carries his own UK clock,
22:34. It is now **17:34 Eastern on 31 Jan**, as a verified correction for this message only.

### S2. REV (P.O. emails) is Pacific time: done
Andersen's mailbox, Scripps Research, La Jolla, San Diego: UTC-8 in winter, UTC-7 in summer. I switched to
Arizona on 2026-10-28 and reverted it the same day. The data is identical to before, except S1. Evidence:
`po-emails.pdf` pp.1-2, “Jan 31, 2020 4:38 PM”, Fauci, Anthony, “[NA]” is an exact copy, sent 00:38 UTC, printed 4:38 PM (UTC-8), quoted inside Andersen's own reply
`po-emails.pdf` p.1, “Friday, January 31, 2020 8:05 PM”, Kristian G. Andersen, “Re: Phone call”; your article's footnote says REV is “UK -8”; the Slack Part 2 anchors agree. Details:
`ZONE_AND_DATE_ANALYSIS.md` 1.2.

### S3. Slack Part 2 is Pacific time: found, nothing to decide
Two Slack messages state the sender's local clock (Holmes, `slack-part2.pdf` p.706, “it's 1 am here”; Garry,
`slack-part2.pdf` p.1090, “It's 4:15 am in Sydney”) and the sleeping hours of all four authors over 11,000
messages agree. **Applied:** Slack Part 2 is now converted to ET in the app, with the printed Pacific time in the
🕑 chip. Details: analysis 1.3. If you disagree, tell me.

### S4. Slack Part 1 is Eastern time: settled by you (2026-10-28)
One anchor (`slack-part1.pdf` p.61, Rambaut, printed 21:26, “Jeez it is 2.30 am”) and your own captions agree.
The app shows Part 1 as printed, labelled ET. Details: analysis 1.4.

---

# Part 2. Unsettled datetimes: your decisions

### U1. GARRY pages (11 top-level emails; the quoted ones now follow the quote rule): Chicago or Eastern? — mostly answered
- **Answer received:** Garry works at Tulane University School of Medicine, New Orleans, so his mailbox is on
  Central time. The app already uses Chicago (Central), so no time changes. The 40 emails move from
  “Not settled” to “Supported”.
- **Still open (optional):** no exact copy with an explicit offset proves it, and a trip away from Central
  would not show. If you find one on a GARRY page, send both page references.
- **CSV:** no.

### U2. Small sender groups (14 emails): accept the sender rule?
- **Problem:** each email's zone comes from the sender's institution. Each group has too few linked replies to
  test. The Sydney group (Holmes) is the most doubtful.
- **Send me:** “accept” for all or for named groups, or one exact copy with an explicit offset per group.
- **CSV:** no.

**Beijing** (1)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `farrar-fauci-comms.pdf` pp.23-31 | Apr 25, 2020 1:22 PM | George Gao (Gao Fu) | [NA] |

**Chicago** (1)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `farrar-fauci-comms.pdf` pp.137-138 | Saturday, February 1, 2020 10:49 AM | Robert Garry | Re: Teleconference |

**London** (7)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `farrar-fauci-comms.pdf` pp.61-62 | Saturday, 8 February 2020 at 12:03 | Patrick Vallance | RE: 2019 N-CoV Jeremy Thanks for sharing, and thanks to those involved for a really important piece of work. I think this looks pretty balanced and is useful. I do think it would be helpful to make sure that the sequence data from the pangolins is included and to indicate what that might mean in terms of a potential prolonged period of adaptation in animals. The glycan point is important and could be given further weight against an passage origin. Once complete I think it would be helpful to publish this |
| `farrar-fauci-comms.pdf` pp.47-49 | 03 March 2020 23:06 | Alex Harris | RE: GPMB: COVID-19 FUNDING NOTE |
| `farrar-fauci-comms.pdf` p.43 | 06 March 2020 10:34 | Marja Esveld | RE: URGENT - GPMB COVID-19 FUNDING NOTE |
| `farrar-fauci-comms.pdf` pp.42-43 | Freitag, 6. Marz 2020 11:56 | Alex Harris | RE: URGENT - GPMB COVID-19 FUNDING NOTE |
| `farrar-fauci-comms.pdf` pp.7-13 | Tuesday, 12 May 2020 at 13:16 | Russell Viner | confidential - update on Paediatric Multisystem Inflammatory |
| `farrar-fauci-comms.pdf` pp.6-7 | Tuesday, May 12, 2020 6:12 PM | Russell Viner | Re: confidential - update on Paediatric Multisystem Inflammatory Syndrome (PIMS) |
| `farrar-fauci-comms.pdf` p.5 | Wednesday, 13 May 2020 at 22:22 | Russell Viner | Re: confidential - update on Paediatric Multisystem Inflammatory Syndrome (PIMS) |

**Los Angeles** (2)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `po-emails.pdf` p.142 | 3/31/2020 8:59:49 PM | Kristian G. Andersen | Re: Furin... |
| `farrar-fauci-comms.pdf` p.56 | 8 Feb 2020 22:15 | Kristian G. Andersen | [NA] |

**Paris** (1)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `farrar-fauci-comms.pdf` pp.110-113 | 2 Feb 2020 08:30 | R.A.M. Fouchier | [NA] |

**Sydney** (2)

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `farrar-fauci-comms.pdf` pp.76-103 | Tuesday, 4 February 2020 at 06:33 | Edward Holmes | Re: Prevalence of infection and stage of the epidemic in Wuhan |
| `farrar-fauci-comms.pdf` p.58 | Saturday, 8 February 2020 at 20:11 | Edward Holmes | Re: [ext] 2019 N-CoV |

### U3. The quote/forward rule is now in the code: nothing for you to answer
- The 152 quoted blocks (143 P.O. emails, 9 Farrar-Fauci) now take the clock of the quoting message's author.
  The two copies that used to be listed here (`farrar-fauci-comms.pdf` p.157, “Jan 30, 2020 7:13 AM”,
  Jeremy Farrar, “[NA]” and p.10, “May 12, 2020 12:57 PM”, Jeremy Farrar, “[NA]”) are among them.
- **If you want to check:** filter `rule` = “2. Quoted block” in `zone_format_audit.csv`.

### U4. Seven emails with no date or time: what are they?
- **Done 2026-10-30:** `po-emails.pdf` pp.17-18, Pope, “Sent: Tuesday, February 4, 2020 9:11 AM”, read from the page
  image by you. Same message as the p.19 copy (9:10:35 AM, UTC-05:00); it is now 09:11 ET on 4 Feb, a verified correction.
- **Problem:** the data has no date or time for them, so they sit outside the timeline. Look at the pages and
  read the header.
- **Send me:** “page, subject, date, time” for each, or “skip”. Some may copy dated emails (the Farrar forward
  on pp.59-60 looks like the 8 Feb forward; the Farrar reply on p.80 looks like the 4 Feb message on that page).
  Not checked.
- **CSV:** no.

| Where | Header as printed | Sender | Subject |
|---|---|---|---|
| `po-emails.pdf` pp.78-80 | (no date or time printed or recovered) | (unknown sender) | Interest in commentary/hypothesis on SARS-CoV-2 origins? |
| `farrar-fauci-comms.pdf` pp.43-44 | (no date or time printed or recovered) | Marja Esveld | RE: URGENT - GPMB COVID-19 FUNDING NOTE |
| `farrar-fauci-comms.pdf` pp.44-47 | (no date or time printed or recovered) | Alex Harris | URGENT - GPMB COVID-19 FUNDING NOTE |
| `farrar-fauci-comms.pdf` p.57 | (no date or time printed or recovered) | Jeremy Farrar | Re: [ext] 2019 N-CoV |
| `farrar-fauci-comms.pdf` pp.59-60 | (no date or time printed or recovered) | Jeremy Farrar | [ext] FW: 2019 N-CoV |
| `farrar-fauci-comms.pdf` p.80 | (no date or time printed or recovered) | Jeremy Farrar | Re: Prevalence of infection and stage of the epidemic in Wuhan |
| `farrar-fauci-comms.pdf` pp.169-172 | (no date or time printed or recovered) | GPMB | TIME SENSITIVE Message from GPMB Co-Chairs: review of draft GPMB… |

---

# Part 3. Issues in your P.O. piece

These are in `TRAGICOMEDY_ISSUES.md` (items P1 to P4). That file is kept out of the repository
(`.gitignore`), so it is not pushed. Nothing in the article has been changed.

---

# Part 4. Issues in the web app

### A1. Folkers' 8:43 PM is on the wrong clock
- `po-emails.pdf` pp.4-11, “Friday, January 31, 2020 8:43 PM”, Folkers, Greg, “Science: Mining coronavirus genomes for clues to the…” is Folkers' message quoted inside Fauci's forward `farrar-fauci-comms.pdf` p.147, “Sat, 1 Feb 2020 02:47:39 +0000”, Anthony Fauci, “FW: Science: Mining coronavirus genomes for clues to the…” (9:47 PM Eastern), so it is on Fauci's
  Eastern clock. The app shows **23:43 Eastern**, later than the forward that quotes it; it should be
  **20:43 Eastern**.
- **Send me:** “apply” (I add a verified correction with this evidence) or “no”.

### A2. A Slack message was on the wrong day: fixed
- `slack-part1.pdf` p.4, Andersen, 22:42, “@Eddie Holmes and @Andrew Rambaut - here's a document I have been
  working on” was dated 2 Feb 2020. It is the evening of **1 Feb** (after the 15:05 Zoom message, before the 01:00
  message of 2 Feb; your article, 5.6a, agrees). Corrected, with the evidence in `tools/slack_date_fixes.json`.
  Nothing for you to do.

### A3. Slack Part 1: times run backwards in 80 places (listed)
- Listed in `slack_part1_time_check.csv` (page, printed times, senders, first words). Example: 12:47, then 01:28,
  then 12:50. 12 of them (evening, then small hours, same date) look like day dividers in the wrong place, like A2;
  the other 68 look like misread digits. Part 2 has none.
- **Optional CSV:** open it and look at the 12 rows with `pattern` = `late_to_early` against the page images. For
  each, tell me which message is on the wrong day, and I add it to `slack_date_fixes.json`. The 68 others can wait.
- **Send me:** the rows you want fixed, or “skip”.

### A4. Slack times carry no zone: done
- Slack Part 2 (Pacific) is now shown in ET with the printed Pacific time in the 🕑 chip; Part 1 (Eastern) is
  labelled ET. 11,293 Part 2 messages changed, 591 of them to another date. Nothing for you to do unless
  something looks off in the timeline.

### A5. Chapter link for section 4.11
- `farrar-fauci-comms.pdf` p.112: your caption “3:59 pm EST” is linked to Fauci's `farrar-fauci-comms.pdf` p.137, “Saturday, 1 February 2020 at 15:50”, Anthony Fauci, “RE: Teleconference”, 9 minutes away. It may
  be a different message.
- **Send me:** whether they are the same message (the app then keeps or removes the link).

### A6. Farrar's original “Phone call” has no body text
- `po-emails.pdf` pp.3-4, “Friday, January 31, 2020 5:23 PM”, Jeremy Farrar, “Phone call”. OCR kept the header and lost the body.
- **Send me:** “re-run OCR on pages 2 and 3”, “I will type it”, or “leave it”.

### A7. The Farrar 22:34 message
- `po-emails.pdf` p.3, “Friday, 31 January 2020 at 22:34”, Fauci, Anthony, “RE: Phone call”: the sender label reads “Fauci, Anthony” (the header says “on behalf of”), and the message now has no
  reply link (the old link, to Andersen, ran backwards and was dropped).
- **Send me:** the right sender label and what it replies to, or “leave”.

### A8. Possible similar errors elsewhere
- A1 was found by a rule not yet automated: a quoted message cannot be later than the message that quotes it,
  even when they sit in different releases. **Send me:** “run it across both releases” and I list every violation.

---

# Part 5. Housekeeping

### H1. Commit and push: when?
- Everything is committed locally; nothing is pushed.
  - `PO_Slack` (branch `po-sources-and-boxes`): the Slack-to-ET change is committed but not pushed. Pushing redeploys the P.O. site.
  - `Edition_Toolkit` (branch `nested-header-split`): 1 commit ahead, with the shared parser changes and the
    skill `foia-datetime-resolution`.
- **Send me:** “push `PO_Slack`”, “push `Edition_Toolkit`”, “push both”, or “wait”.

### H2. Should `analysis/` stay out of the public repository?
- The repository is public. `analysis/` is pushed, **except `TRAGICOMEDY_ISSUES.md`** (your piece's problems),
  which is git-ignored. The rest is visible on GitHub.
- **Send me:** “ignore the whole folder” (I stop tracking it), or “fine as it is”.

### H3. Check my edits to your own files
- `README.md`: six paths changed to the new layout. `STATUS.md`: one path changed (`tools/tests/test_browser.mjs`).
- **Send me:** “fine”, or what to put back.
