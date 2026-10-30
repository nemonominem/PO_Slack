# For the human reviewer: everything you need to do

This is the only file with instructions for you. The evidence is in `ZONE_AND_DATE_ANALYSIS.md`.
Status as of 2026-10-31. Everything below has been re-read after the last rebuild.

**How to answer:** reply in chat with the item code and your answer, for example “U5: keep London”,
“A1: apply”, “A3: rows 3 and 7”. Any order; skip what you like. Nothing changes until you answer.

**How entries are named.** Never by number. Each is: PDF file and pages (PDF page numbers), the date and time
exactly as printed in its header, the sender, and the subject. Slack messages: PDF page, printed time, sender,
first words.

# REMAINING ISSUES AT A GLANCE

Every open item is in this table. Nothing else in this file needs an answer.

| Code | What is open | What I need from you | If you say nothing |
|---|---|---|---|
| **U1** | Garry's mailbox: Central (Chicago) is used and supported (Tulane, New Orleans), not proven | Optional: one exact copy with an explicit offset on a GARRY page | Stays “Supported”; no time changes |
| **U2** | 14 emails whose zone comes from the sender's institution only (Beijing 1, Chicago 1, London 7, Los Angeles 2, Paris 1, Sydney 2) | “accept” (all or named groups), or one exact copy per group | Stay “Not settled”; times as now |
| **U5** | Marja Esveld, `farrar-fauci-comms.pdf` p.43, “06 March 2020 10:34”: London or Amsterdam clock? (up to 1 hour) | “keep London” or “Amsterdam” | London stays |
| **U6** | Three reply pairs that my separate check flags as backwards (`po-emails.pdf` pp.22-29, p.28, pp.57-65); the app's own data has none | Read the headers and tell me whether the second message answers the first | Times unchanged |
| **A1** | Folkers' 8:43 PM shows 23:43 ET; should be 20:43 ET | “apply” or “no” | Stays wrong (23:43) |
| **A3** | 12 Slack Part 1 messages that look to be on the wrong day (and 68 misread times) | Rows from `slack_part1_time_check.csv` to fix, or “skip” | Stay as printed |
| **A5** | Chapter link for section 4.11 (p.112 “3:59 pm EST” to Fauci p.137, 15:50): same message? | “same” or “different” | Link stays |
| **A6** | Farrar's “Phone call” (`po-emails.pdf` pp.3-4) has no body text | “re-run OCR”, “I will type it”, or “leave it” | Stays empty |
| **A7** | The 22:34 Fauci message: sender label and what it replies to | Correct label and parent, or “leave” | Stays as is |
| **A8** | Quoted message later than its quoter, across the two releases: not yet run | “run it” | Not run |
| **A9** | 8 old bookmark keys now name a different message and cannot be re-mapped | Nothing, unless you or others bookmarked them (list in A9) | Those bookmarks point at the wrong message |
| **P1-P4** | Issues in your P.O. piece (`TRAGICOMEDY_ISSUES.md`, private). Times have moved since I last checked them | “re-check them” | Not re-checked |
| **H2** | Keep `analysis/` in the public repository? | “ignore the folder” or “fine as it is” | Stays public |
| **H3** | My edits to your `README.md` and `STATUS.md` | “fine” or what to put back | Stays |
| **H4** | `PO_Slack.code-workspace` is untracked | “commit”, “ignore” or “delete” | Left alone |

**Done since the last version of this file** (nothing to answer): the quote/forward rule is in the code (U3); all
eight undated emails are dated (U4, last one answered 2026-10-31); both repositories are pushed (H1).

## Do you need to open any CSV or log?

**No file is required.** Every item gives the PDF and pages.

| File | Use it? | For |
|---|---|---|
| `zone_format_audit.csv` | Optional | One row per email, with the rule and status. Filter `rule` = “4. Page owner GARRY” for the Garry pages |
| `slack_part1_time_check.csv` | Optional, for A3 only | The 80 places where Slack Part 1 times run backwards; the 12 `late_to_early` rows are the useful ones |
| `freeze_bracket_check.csv` | Optional, for U6 | Clock and bracketing test per email |
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

### U1. GARRY pages (11 top-level emails; the quoted ones follow the quote rule): Chicago or Eastern?
- **Answer received:** Garry works at Tulane University School of Medicine, New Orleans: Central time. The app
  uses Chicago (Central), so no time changes. These emails are “Supported”.
- **Still open (optional):** no exact copy with an explicit offset proves it, and a trip away from Central
  would not show. The 10 Feb chain (pp.65-67) favours Chicago (16:51 ET under Chicago; 15:51 under Eastern would
  be before the message it answers) but Garry's link to it is only inferred.
- **Send me (optional):** page references of an exact copy on a GARRY page.

### U2. Small sender groups (14 emails): accept the sender rule?
- **Problem:** each email's zone comes from the sender's institution. Each group has too few linked replies to
  test. The Sydney group (Holmes) is the most doubtful. The Esveld email in the London table is also U5.
- **Send me:** “accept” for all or for named groups, or one exact copy with an explicit offset per group.

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

### U5. Marja Esveld, `farrar-fauci-comms.pdf` p.43, “06 March 2020 10:34”, RE: URGENT - GPMB COVID-19 FUNDING NOTE
- **What the data does now:** the parser files Esveld with Alex Harris under “Wellcome Trust / UK” and reads her
  10:34 as London time (05:34 ET). That label is wrong for her: she writes from the Dutch Ministry of Foreign
  Affairs (the `minbuza.nl` addresses on p.43-44), not from Wellcome.
- **Why London may still be right:** this reply is a top-level message, so its stamp is on the clock of the
  mailbox that shows it, not on her clock. The stamp is English-format (“06 March 2020 10:34”), whereas her own
  earlier message, quoted below it, prints in Dutch (`vrijdag 6 maart 2020 09:23`, now read as Amsterdam, U4).
  So the 10:34 comes from an English-language client, not hers, and the Wellcome mailbox is in London.
- **Why I cannot prove it:** London gives 10:34 UTC, Amsterdam 09:34 UTC. Both fit the thread: her 09:23
  Amsterdam message is 08:23 UTC; Alex Harris answers at 11:56 (p.42, German-language client); Farrar replies at
  14:33:45 +0000 (explicit). Reply order cannot choose.
- **My earlier remark** that the 10:34 was probably one hour out assumed it was on her own clock. For a top-level
  message that is not what the freeze rule says, so I withdraw it.
- **Send me:** “keep London” (then I only relabel the reason as “mailbox clock”) or “Amsterdam” (the entry moves
  one hour earlier, to 04:34 ET).

### U6. Three reply pairs that my separate check flags (pipeline itself: none backwards)
- The app's own data has no reply before its parent. My separate check (`freeze_bracket_check.py`), which reads
  each stamp on the home clock of whoever quotes it, flags three pairs where the second message comes out earlier
  than the first:
  1. `po-emails.pdf` pp.22-29: Garry “5 Feb 2020 1:03 pm”, then Holmes “2/5/2020 1:23:41 AM” (explicit link).
  2. `po-emails.pdf` p.28 and pp.28-45: Holmes “5 Feb 2020 9:04 pm”, then Holmes “2/5/2020 4:22:24 AM” (explicit link).
  3. `po-emails.pdf` pp.57-65 and 55-57: Farrar “08 February 2020 09:45”, then Fouchier “2/8/2020 11:36:30 AM”
     (inferred link only).
- **Why it matters:** in each pair one stamp is on a clock I have wrong, or the reply link is wrong. If the
  check's clock is the wrong one, the app is right and nothing changes.
- **Send me:** for each pair, whether the “From/Sent/To” headers show that the second message really answers the
  first, and the stamps as you read them, or “skip”.

### U3 and U4: done
- **U3.** The 152 quoted blocks (143 P.O. emails, 9 Farrar-Fauci) take the clock of the quoting message's author.
  Check with `rule` = “2. Quoted block” in `zone_format_audit.csv`.
- **U4.** The eight undated emails are read from the page images (400 dpi OCR pass plus your reading). Each is a verified
  override with its evidence in `tools/verified_overrides.json`. They show as Settled because the page fixes the
  printed time; the zone of the Dutch, German, Spanish and Andersen ones follows the freeze rule (and, for
  Andersen p.78, equality with the p.80 copy).

| Where | Header as printed | Now (ET) | Clock used |
|---|---|---|---|
| `po-emails.pdf` pp.17-18, Pope | Sent: Tuesday, February 4, 2020 9:11 AM | 4 Feb 09:11 | Eastern (copy on p.19: 9:10:35 AM UTC-05:00) |
| `po-emails.pdf` p.78, Andersen | Sent: 12 February 2020 23:09 | 13 Feb 02:09 | Pacific (same text as the p.80 copy); assumed |
| `farrar-fauci-comms.pdf` pp.43-44, Esveld | Sent: vrijdag 6 maart 2020 09:23 | 6 Mar 03:23 | Amsterdam (Dutch client) |
| `farrar-fauci-comms.pdf` p.44, Harris | Sent: donderdag 5 maart 2020 15:29 | 5 Mar 09:29 | Amsterdam (quoted in Esveld's Dutch client) |
| `farrar-fauci-comms.pdf` p.57, Farrar | Datum: Samstag, 8. Februar 2020 um 21:21 | 8 Feb 15:21 | Berlin (Drosten's German client) |
| `farrar-fauci-comms.pdf` p.59, Farrar | Datum: Samstag, 8. Februar 2020 um 10:45 | 8 Feb 04:45 | Berlin |
| `farrar-fauci-comms.pdf` p.80, Farrar | Sent: Tuesday, February 4, 2020 6:08 AM | 4 Feb 06:08 | Eastern (quoted in Collins's reply) |
| `farrar-fauci-comms.pdf` pp.169-172, GPMB Secretariat | Sent: martes, 28 de enero de 2020 9:09 | 28 Jan 07:09 | Santiago de Chile, UTC-3 (you confirmed Vega Morales is based there; the Spanish client is hers) |

---

# Part 3. Issues in your P.O. piece

These are in `TRAGICOMEDY_ISSUES.md` (items P1 to P4). That file is kept out of the repository
(`.gitignore`), so it is not pushed. Nothing in the article has been changed. **I have not re-checked them since
the times moved** (for example the 31 Jan chain in P2).

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

### A9. Eight old bookmark keys cannot be re-mapped
- 255 old bookmark keys are re-mapped to the current entries. These eight now name a *different* message, so a
  re-map would be wrong: `po-emails|2020-01-31|1500`, `po-emails|2020-02-04|2008`, `po-emails|2020-02-05|1500|1`,
  `po-emails|2020-02-05|1500|2`, `po-emails|2020-02-05|1500|3`, `po-emails|2020-02-16|1750`,
  `po-emails|2020-02-16|1806`, `po-emails|2020-02-17|1641`.
- **Send me:** nothing, unless you or someone you know bookmarked emails on these dates and times; then tell me which.

---

# Part 5. Housekeeping

### H1. Pushed
- `PO_Slack` (branch `po-sources-and-boxes`) and `Edition_Toolkit` (branch `nested-header-split`) are pushed. The
  skill file `foia-datetime-resolution/freeze-rule-and-tricks.md` in `Edition_Toolkit` holds the freeze rule and the tricks.

### H2. Should `analysis/` stay out of the public repository?
- The repository is public. `analysis/` is pushed, **except `TRAGICOMEDY_ISSUES.md`** (your piece's problems),
  which is git-ignored. The rest is visible on GitHub.
- **Send me:** “ignore the whole folder” (I stop tracking it), or “fine as it is”.

### H3. Check my edits to your own files
- `README.md`: six paths changed to the new layout. `STATUS.md`: one path changed (`tools/tests/test_browser.mjs`).
- **Send me:** “fine”, or what to put back.

### H4. `PO_Slack.code-workspace`
- A VS Code workspace file that is not tracked. **Send me:** “commit”, “ignore” (add to `.gitignore`) or “delete”.
