import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Part1SanitizationTests(unittest.TestCase):
    def test_google_doc_text_matches_source_image(self):
        data = json.loads((ROOT / "page_based" / "part1.json").read_text(encoding="utf-8"))
        entry = next(e for e in data["entries"] if e.get("idx") == 507)
        self.assertEqual((entry["sender"], entry["date"]), ("Kristian Andersen", "2020-02-17"))
        self.assertIn("@channel Google Doc is now our master document", entry["content"])
        self.assertNotIn("Googie Dox", entry["content"])

        page_map = json.loads((ROOT / "page_based" / "part1_page_map.json").read_text(encoding="utf-8"))
        self.assertEqual(page_map["507"]["start"], 47)
        self.assertEqual(page_map["507"]["end"], 47)


if __name__ == "__main__":
    unittest.main()
