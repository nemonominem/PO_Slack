# analysis: the datetime record

This folder is the working record for getting the dates and times of the email entries
right. It is not uploaded to GitHub Pages. The repository is public, so see item H2 in
`FOR_HUMAN_REVIEWER.md` before pushing.

## 1. What you need to do

**Open `FOR_HUMAN_REVIEWER.md`.** It is the only file with instructions for you, and it says
which files (if any) you need to open. Everything else here is evidence or test output.

## 2. What is in this folder

| File | What it is | When to open it |
|---|---|---|
| `FOR_HUMAN_REVIEWER.md` | **Every instruction and decision for you** | First |
| `README.md` | This file | To find your way around |
| `ZONE_AND_DATE_ANALYSIS.md` | The datetime analysis: what is settled, the rules, the evidence | For the evidence behind an open item |
| `zone_format_audit.csv` | One row per email entry (386), with the rule behind its time | Optional lookup tool for item U1 in `FOR_HUMAN_REVIEWER.md` |
| `reply_order_check.csv` | Result of the reply-order test, by zone group | Support output; nothing to check |
| `owner_zone_check.csv` | Exact-copy pairs for the page owners | Support output; nothing to check |
| `zone_rule_dedupe.log` | Which copies were removed as duplicates | If an entry looks missing |
| `chapter_links_report.txt` | Citations in your article that could not be linked to an entry | When checking chapter buttons |
| `bookmark_rekey_report.txt` | Old bookmark keys that could not be mapped | Rarely |

## 3. Reading `zone_format_audit.csv`

Open it in a spreadsheet and filter on `zone_status`.

| Column | Meaning |
|---|---|
| `release`, `idx` | The entry: `po-emails` or `farrar-fauci`, and its number |
| `thread_key` | The key the app uses (bookmarks and chapter links) |
| `date`, `time` | The Eastern date and time the app shows |
| `sender`, `stamp`, `stamp_format` | As parsed: the sender, the printed stamp, and its format |
| `rule` | The rule that set the time, in plain words |
| `pdf`, `pdf_pages` | Where to look: the PDF file and the page |
| `zone_status` | **Settled**, **Supported** or **Not settled** (below) |
| `status_reason` | Why |
| `check` | Anything odd about the entry (no time, no sender, ...) |
| `note` | A note from a check against the page image, where one exists |

- **Settled:** fixed by the stamp, an exact copy, the page image, or a decision of yours.
- **Supported:** consistent with every test, but the tests cannot prove it.
- **Not settled:** an assumption with no test, or the data cannot decide. These are the
  rows behind items U1 to U4 in `FOR_HUMAN_REVIEWER.md`.

## 4. Rebuilding

Do not edit the generated files by hand. The scripts and their order are in
`tools/README.md`. Hand-checked corrections go in `tools/verified_overrides.json`, with
the evidence beside each one.
