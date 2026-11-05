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

Pages to read (13): 35,36,43,49,52,55,57,64,65,102,104,115,116

The places that are still suspect (11 left; 85 labels from earlier passes are already applied) (page | date | first message time -> next message time as the current OCR has it; the first is later than the next, which is impossible inside one day unless a digit is wrong or a divider is missed):

```
p.35 | 2020-02-11 | Andrew Ram 18:21 -> Robert Gar 16:20
p.36 | 2020-02-12 | Eddie Holm 09:24 -> Eddie Holm 03:32
p.43 | 2020-02-15 | Robert Gar 19:57 -> Andrew Ram 13:57
p.49 | 2020-02-17 | Robert Gar 18:09 -> Andrew Ram 16:11
p.52 | 2020-02-19 | Robert Gar 05:05 -> Eddie Holm 02:16
p.57 | 2020-02-20 | Robert Gar 15:29 -> Andrew Ram 13:29
p.57 | 2020-02-20 | Eddie Holm 13:58 -> Eddie Holm 01:23
p.64 | 2020-02-24 | Robert Gar 10:59 -> Kristian A 01:44
p.102 | 2020-03-18 | Andrew Ram 06:36 -> Eddie Holm 01:19
p.104 | 2020-03-19 | Eddie Holm 16:09 -> Kristian A 10:41
p.115 | 2020-04-02 | Eddie Holm 19:21 -> Kristian A 13:35
```

Already read by hand (do not change; use them to see what a correct reading looks like): p.19 Holmes `19:49`; p.121 Andersen `15:40` ("Very slow going"); p.134 Holmes `18:36`, Andersen `18:51`, Andersen `22:44` ("It's an eel! Eel!!!"), Holmes `23:42`. Also applied 2026-11-04/05: 85 labels from a first external pass (`grok_slack_part1_times_partial.csv`) and its corrections list (`grok_slack_part1_times_STATUS.md`), among them p.121 "Still trying to work through this..." = `13:37`. Do not re-report those; only the pairs listed above are still open.

---

When the answer comes back, Claude: (1) checks each reading against its neighbours (order, divider, and the Zoom/Slack anchors in `analysis/ZONE_AND_DATE_ANALYSIS.md`), (2) adds confirmed ones to `tools/slack_time_fixes.json` with the model named as the source and the page (matching by page, sender and first words), (3) reruns `slack_time_check.py`. Anything the model marks `low` is checked on the page image by you.
