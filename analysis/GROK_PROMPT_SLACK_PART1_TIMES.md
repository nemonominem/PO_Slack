# Prompt for an external OCR review of Slack Part 1 time labels

Use with `page_based/main_sources/slack-part1.pdf` (attach the PDF, or the pages listed below as images). Paste the prompt between the lines into the model; paste its answer back to Claude, who compares it with the data and applies only what the page confirms.

---

You are doing careful, literal OCR on screenshots of a Slack channel (the pages of a PDF). Do not summarise and do not correct spelling. I need the **time label and the day divider** read exactly as printed.

How a page is laid out:
- Messages are grouped in runs by one author. The first message of a run shows the author's name followed, in a small grey font, by a time such as `12:47` (24-hour clock, **no AM/PM**). Later messages in the same run show their own time label only when hovered, at the left, often like `13:37`.
- A **day divider** is a full-width thin line with a small rounded tile in the middle holding a date such as `February 9th, 2020`. It sits **between** the last message of one day and the first message of the next. Never put the divider's date on the message above it.
- Times inside a day never go backwards. If you read a time that is earlier than the one before it, look again: the usual errors are a dropped or swapped first digit (`1:49` for `19:49`, `01:36` for `18:36`), `1`/`7`, `3`/`8`/`9`, `5`/`6`, `0`/`8`, a `.` read as `:` or the colon missing (`1957`).

For each page of the list below, output one CSV line per message (and one per divider), in reading order, with these columns:

`page,seq,kind,author,time_hhmm,date_if_divider,first_8_words,confidence`

- `kind` = `msg` or `divider`.
- `time_hhmm` = the label exactly as you read it, normalised to `HH:MM` (24 h); leave blank when the message has no visible label (say so in `first_8_words`).
- `date_if_divider` = the tile text, e.g. `February 9th, 2020`.
- `confidence` = `high`, `medium` or `low`; use `low` whenever a digit is hard to read, and in that case add the alternative reading after a `/` in `time_hhmm`, e.g. `19:49/21:49`.

After the CSV, list every place where the time does **not** increase from one message to the next on the same day, and every place where a divider is between two messages.

Pages to read (42): 1,2,4,5,7,11,13,14,22,23,24,26,34,35,36,37,39,40,43,45,49,50,52,55,57,64,65,66,67,69,77,101,102,103,104,115,116,121,126,132,134,139

The places that are known to be suspect (page | date | first message time -> next message time as the current OCR has it; the first is later than the next, which is impossible inside one day unless a digit is wrong or a divider is missed):

```
p.1 | 2020-02-01 | Andrew Ram 12:47 -> Kristian A 01:28
p.1 | 2020-02-01 | Kristian A 19:17 -> Andrew Ram 15:25
p.2 | 2020-02-01 | Kristian A 19:26 -> Andrew Ram 15:00
p.2 | 2020-02-01 | Andrew Ram 15:00 -> Kristian A 13:00
p.2 | 2020-02-01 | Andrew Ram 19:56 -> Kristian A 13:08
p.2 | 2020-02-01 | Kristian A 19:59 -> Andrew Ram 13:42
p.4 | 2020-02-01 | Kristian A 13:59 -> Andrew Ram 01:55
p.5 | 2020-02-02 | Kristian A 11:14 -> Andrew Ram 01:16
p.7 | 2020-02-02 | Robert Gar 19:51 -> Robert Gar 12:50
p.11 | 2020-02-03 | Robert Gar 10:27 -> Kristian A 01:02
p.13 | 2020-02-03 | Kristian A 17:46 -> Robert Gar 16:11
p.13 | 2020-02-03 | Eddie Holm 19:28 -> Robert Gar 16:22
p.13 | 2020-02-03 | Robert Gar 16:22 -> Robert Gar 12:40
p.14 | 2020-02-04 | Andrew Ram 04:15 -> Eddie Holm 00:28
p.22 | 2020-02-08 | Andrew Ram 08:52 -> Robert Gar 00:57
p.23 | 2020-02-08 | Robert Gar 19:09 -> Robert Gar 13:21
p.23 | 2020-02-08 | Kristian A 17:52 -> Robert Gar 16:15
p.24 | 2020-02-08 | Eddie Holm 19:42 -> Robert Gar 16:57
p.26 | 2020-02-09 | Andrew Ram 16:09 -> Robert Gar 14:14
p.34 | 2020-02-11 | Robert Gar 17:13 -> Robert Gar 16:00
p.34 | 2020-02-11 | Robert Gar 16:00 -> Kristian A 10:04
p.35 | 2020-02-11 | Robert Gar 19:04 -> Andrew Ram 16:16
p.36 | 2020-02-12 | Eddie Holm 09:32 -> Andrew Ram 05:09
p.36 | 2020-02-12 | Eddie Holm 09:36 -> Andrew Ram 05:14
p.39 | 2020-02-12 | Kristian A 19:10 -> Robert Gar 16:20
p.40 | 2020-02-13 | Robert Gar 10:27 -> Kristian A 01:19
p.43 | 2020-02-15 | Robert Gar 13:40 -> Andrew Ram 12:00
p.43 | 2020-02-15 | Andrew Ram 19:57 -> Robert Gar 14:00
p.43 | 2020-02-13 | Robert Gar 14:17 -> Eddie Holm 10:58
p.45 | 2020-02-17 | Robert Gar 08:49 -> Andrew Ram 05:49
p.45 | 2020-02-17 | Andrew Ram 05:49 -> Robert Gar 00:52
p.49 | 2020-02-17 | Andrew Ram 17:45 -> Robert Gar 01:00
p.49 | 2020-02-18 | Robert Gar 19:52 -> Andrew Ram 16:55
p.50 | 2020-02-18 | Kristian A 19:09 -> Andrew Ram 17:10
p.52 | 2020-02-19 | Robert Gar 05:05 -> Eddie Holm 02:16
p.55 | 2020-02-19 | Andrew Ram 05:59 -> Robert Gar 04:27
p.55 | 2020-02-20 | Andrew Ram 09:06 -> Robert Gar 07:29
p.57 | 2020-02-20 | Robert Gar 19:25 -> Andrew Ram 15:27
p.57 | 2020-02-20 | Andrew Ram 15:09 -> Robert Gar 13:29
p.57 | 2020-02-20 | Robert Gar 15:00 -> Robert Gar 12:27
p.57 | 2020-02-20 | Robert Gar 13:40 -> Eddie Holm 01:58
p.64 | 2020-02-24 | Robert Gar 10:59 -> Kristian A 01:44
p.65 | 2020-02-24 | Kristian A 15:19 -> Robert Gar 01:52
p.66 | 2020-02-24 | Robert Gar 15:42 -> Robert Gar 14:02
p.67 | 2020-02-25 | Andrew Ram 09:45 -> Robert Gar 05:56
p.69 | 2020-02-25 | Andrew Ram 06:19 -> Robert Gar 04:21
p.77 | 2020-02-29 | Robert Gar 15:27 -> Robert Gar 01:50
p.101 | 2020-03-18 | Andrew Ram 05:05 -> Andrew Ram 03:07
p.102 | 2020-03-18 | Andrew Ram 06:36 -> Eddie Holm 01:19
p.103 | 2020-03-19 | Andrew Ram 03:29 -> Kristian A 02:20
p.103 | 2020-03-19 | Kristian A 09:31 -> Andrew Ram 02:52
p.104 | 2020-03-19 | Andrew Ram 05:40 -> Kristian A 00:51
p.104 | 2020-03-19 | Robert Gar 12:19 -> Eddie Holm 10:09
p.115 | 2020-04-02 | Kristian A 19:18 -> Kristian A 13:09
p.115 | 2020-04-02 | Eddie Holm 19:21 -> Kristian A 13:35
p.121 | 2020-04-10 | Kristian A 19:57 -> Kristian A 15:40
p.126 | 2020-04-16 | Robert Gar 10:39 -> Andrew Ram 01:20
p.132 | 2020-04-18 | Robert Gar 16:18 -> Eddie Holm 10:59
p.134 | 2020-04-21 | Robert Gar 11:59 -> Eddie Holm 01:49
p.139 | 2020-04-30 | Robert Gar 16:19 -> Kristian A 10:25
```

Already read by hand (do not change; use them to see what a correct reading looks like): p.19 Holmes `19:49`; p.121 Andersen `15:40` ("Very slow going"); p.134 Holmes `18:36`, Andersen `18:51`, Andersen `22:44` ("It's an eel! Eel!!!"), Holmes `23:42`. Still open: p.121 the Andersen message before the `15:40` one ("Still trying to work through this...") is read `19:57` but must be before `13:37` (the hover time of the next message).

---

When the answer comes back, Claude: (1) checks each reading against its neighbours (order, divider, and the Zoom/Slack anchors in `analysis/ZONE_AND_DATE_ANALYSIS.md`), (2) adds confirmed ones to `tools/slack_time_fixes.json` with the model named as the source and the page, (3) reruns `slack_time_check.py`. Anything the model marks `low` is checked on the page image by you.
