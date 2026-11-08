import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parse_part1


class Page71MessageTests(unittest.TestCase):
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
