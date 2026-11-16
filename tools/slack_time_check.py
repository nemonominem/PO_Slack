"""List the places in Slack Part 1 where two consecutive timed messages inside one date run
backwards by more than an hour (for example 12:47, then 01:28, then 12:50).

Part 1 has no AM/PM and shows a time only for the first message of a run, so these are
potential OCR slips, date-assignment issues, or redaction-placement estimates.
Part 2 has none. Output: ../analysis/slack_part1_time_check.csv
The 'late_to_early' rows (evening followed by small hours on the same date) are the pattern of a
day divider placed one message too early or too late (compare slack_date_fixes.json); the
others need source-page review. Estimated redaction placements are not printed
timestamps and cannot establish the redacted messages' actual times.
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "page_based")
OUT = os.path.join(HERE, "..", "analysis", "slack_part1_time_check.csv")


def minutes(e):
    return int(e["time"][:2]) * 60 + int(e["time"][3:5])


def words(e, n=60):
    return re.sub(r"\s+", " ", (e.get("content") or ""))[:n]


def main():
    d = json.load(open(os.path.join(DATA, "part1.json"), encoding="utf-8"))
    entries = d["entries"] if isinstance(d, dict) else d
    pages = json.load(open(os.path.join(DATA, "part1_page_map.json"), encoding="utf-8"))
    timed = [e for e in entries if e.get("time") and e.get("date")]
    rows = []
    for a, b in zip(timed, timed[1:]):
        if a["date"] == b["date"] and minutes(b) < minutes(a) - 60:
            pattern = "late_to_early" if minutes(a) >= 18 * 60 and minutes(b) <= 6 * 60 else "other"
            rows.append({
                "pdf": "slack-part1.pdf",
                "page_first": pages[str(a["idx"])]["start"], "page_second": pages[str(b["idx"])]["start"],
                "date": a["date"],
                "first_time": a["time"], "first_sender": a["sender"], "first_words": words(a),
                "second_time": b["time"], "second_sender": b["sender"], "second_words": words(b),
                "pattern": pattern,
            })
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("wrote %d rows (%d late_to_early) to %s" % (len(rows), sum(r["pattern"] == "late_to_early" for r in rows), OUT))


if __name__ == "__main__":
    main()
