import sys
import unittest
import contextlib
import io
from pathlib import Path
from unittest.mock import patch, mock_open

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parse_part1


class Page71MessageTests(unittest.TestCase):
    def test_time_fix_rejects_text_drift_or_ambiguous_occurrences(self):
        fix = {"part": "part1", "idx": 0, "sender": "Eddie Holmes",
               "wrong_time": None, "time": "16:08", "text": ["bad text", "good text"]}
        for content, expected in [("bad text", "good text"), ("good text", "good text"),
                                  ("different text", None), ("bad text / bad text", None),
                                  ("good text / good text", None)]:
            entry = {"sender": "Eddie Holmes", "time": None, "content": content}
            with self.subTest(content=content), \
                 patch.object(parse_part1.os.path, "exists", return_value=True), \
                 patch.object(parse_part1, "legacy_parser_index", return_value=0), \
                 patch("builtins.open", mock_open(read_data="[]")), \
                 patch.object(parse_part1.json, "load", return_value=[fix]), \
                 contextlib.redirect_stdout(io.StringIO()):
                if expected is None:
                    with self.assertRaisesRegex(ValueError, "does not uniquely match"):
                        parse_part1.apply_time_fixes([entry])
                    self.assertIsNone(entry["time"])
                else:
                    parse_part1.apply_time_fixes([entry])
                    self.assertEqual((entry["content"], entry["time"]), (expected, "16:08"))

    def test_page47_and_page49_source_times_and_redaction_placement(self):
        entries = parse_part1.correct_page71_messages(parse_part1.parse())
        with contextlib.redirect_stdout(io.StringIO()):
            parse_part1.apply_date_fixes(entries)
            parse_part1.apply_time_fixes(entries)
        entries = parse_part1.apply_redaction_annotations(entries)
        redaction = next(i for i, e in enumerate(entries)
                         if e.get("sender") == "Redacted" and
                         any(s["page"] == 47 for s in e.get("redaction_sources", [])))
        self.assertEqual([e["time"] for e in entries[redaction-2:redaction+6]],
                         ["16:02", "16:08", "16:14", "16:20", "16:21", "16:22", "16:39", "16:46"])
        self.assertTrue(entries[redaction]["time_estimated"])
        self.assertIn("sent to bioRxiv a week ago", entries[redaction-1]["content"])
        page49 = [e for e in entries if e.get("page") == 49]
        self.assertEqual([(e["date"], e["time"]) for e in page49[:8]],
                         [("2020-02-18", t) for t in
                          ["15:37", "15:54", "15:57", "17:14", "17:45", "18:09", "18:11", "18:52"]])

    def test_page42_redaction_uses_inferred_date_between_visible_neighbors(self):
        entries = parse_part1.correct_page71_messages(parse_part1.parse())
        with contextlib.redirect_stdout(io.StringIO()):
            parse_part1.apply_date_fixes(entries)
            parse_part1.apply_time_fixes(entries)
        entries = parse_part1.apply_redaction_annotations(entries)
        redaction = next(i for i, e in enumerate(entries)
                         if e.get("sender") == "Redacted" and
                         any(s["page"] == 42 for s in e.get("redaction_sources", [])))
        before, item, after = entries[redaction - 1:redaction + 2]
        self.assertEqual((before["sender"], before["date"], before["time"]),
                         ("Robert Garry", "2020-02-14", "15:44"))
        self.assertEqual((item["date"], item["time"], item["date_estimated"], item["time_estimated"]),
                         ("2020-02-14", "19:14", True, True))
        self.assertEqual((after["sender"], after["date"], after["time"]),
                         ("Eddie Holmes", "2020-02-14", "22:44"))
        next_message = entries[redaction + 2]
        self.assertEqual((next_message["sender"], next_message["date"], next_message["time"]),
                         ("Robert Garry", "2020-02-15", "08:11"))

    def test_page71_messages_are_split_corrected_and_redacted_by_source_position(self):
        entries = parse_part1.correct_page71_messages(parse_part1.parse())
        entries = parse_part1.apply_redaction_annotations(entries)
        for idx, entry in enumerate(entries):
            entry["idx"] = idx
        parse_part1.preserve_page71_entry_ids(entries)

        page71 = [entry for entry in entries if entry.get("page") == 71]
        andrew = next(e for e in page71 if e["sender"] == "Andrew Rambaut")
        garry = next(e for e in page71 if e["sender"] == "Robert Garry")
        holmes = next(e for e in page71 if e["sender"] == "Eddie Holmes")

        self.assertEqual((andrew["time"], andrew["idx"]), ("13:05", 816))
        self.assertIn("On a visit to Shaoguan, Guangdong province", andrew["content"])
        self.assertIn("the Guardian and staff from CECGDF", andrew["content"])
        self.assertNotIn("sampling those animals", andrew["content"])

        self.assertEqual((garry["time"], garry["idx"]), ("13:37", 1332))
        self.assertEqual(
            garry["content"],
            "[Redacted]\nI hope some one is sampling those animals - would be a good place "
            "to generate diversity in covs.\n[Redacted]",
        )
        self.assertEqual(garry["redaction_count"], 2)
        self.assertNotIn("time_estimated", garry)

        self.assertEqual((holmes["time"], holmes["idx"]), ("15:43", 817))
        self.assertEqual(
            holmes["content"],
            "[Redacted]\nI agree that we should use nCoV-19. Will do so from now on.\n[Redacted]",
        )
        self.assertEqual(holmes["redaction_count"], 2)
        self.assertNotIn("time_estimated", holmes)

    def test_timed_standalone_redactions_have_estimated_time_metadata(self):
        entries = parse_part1.apply_redaction_annotations(
            parse_part1.correct_page71_messages(parse_part1.parse())
        )
        timed = [e for e in entries if e.get("sender") == "Redacted" and e.get("time")]
        self.assertEqual(len(timed), 14)
        self.assertTrue(all(e.get("time_estimated") is True for e in timed))
        example = next(e for e in timed if e["time"] == "13:36")
        self.assertIn("estimated", example["zone_assumed"])
        self.assertNotIn("shown as printed", example["zone_assumed"])

    def test_legacy_correction_and_redaction_anchors_survive_split(self):
        entries = parse_part1.correct_page71_messages(parse_part1.parse())
        split_index = next(i for i, e in enumerate(entries)
                           if e.get("page") == 71 and e.get("sender") == "Robert Garry")
        self.assertEqual(parse_part1.legacy_parser_index(entries, split_index - 1), split_index - 1)
        self.assertEqual(parse_part1.legacy_parser_index(entries, split_index), split_index + 1)
        parse_part1.apply_time_fixes(entries)
        result = parse_part1.apply_redaction_annotations(entries)
        for i, entry in enumerate(result):
            for source in entry.get("redaction_sources", []):
                if source["page"] > 71 and entry["sender"] == "Redacted":
                    self.assertLessEqual(result[i - 1]["page"], source["page"])
        page73 = next(i for i, e in enumerate(result)
                      if e.get("sender") == "Redacted"
                      and any(s["page"] == 73 for s in e.get("redaction_sources", [])))
        self.assertIs(result[page73 - 1], entries[816])


if __name__ == "__main__":
    unittest.main()
