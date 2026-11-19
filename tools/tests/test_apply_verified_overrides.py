import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import apply_verified_overrides
import build_po_guide


class ReplyRelationshipTests(unittest.TestCase):
    def test_reapplying_same_parent_preserves_existing_relationship_labels(self):
        child = {
            "thread_key": "emails|child",
            "reply_to": "emails|parent",
            "reply_to_label": "existing parent label",
            "date": "2020-02-01",
            "time": "1234",
            "sender": "Child",
        }
        parent = {
            "thread_key": "emails|parent",
            "replied_by": [{"key": child["thread_key"], "label": "existing child label"}],
        }

        apply_verified_overrides.set_reply_relationship(
            {child["thread_key"]: child, parent["thread_key"]: parent}, child, parent
        )

        self.assertEqual(child["reply_to_label"], "existing parent label")
        self.assertEqual(parent["replied_by"], [
            {"key": child["thread_key"], "label": "existing child label"}
        ])

    def test_body_replacement_is_guarded_and_idempotent(self):
        fix = [{"old": "[ agree with Eddie,", "new": "I agree with Eddie,"}]
        content = "Subject: Test\n\n----------\n\n[ agree with Eddie, yes."
        corrected = apply_verified_overrides.apply_body_replacements(content, fix)
        self.assertEqual(corrected, "Subject: Test\n\n----------\n\nI agree with Eddie, yes.")
        self.assertEqual(apply_verified_overrides.apply_body_replacements(corrected, fix), corrected)
        with self.assertRaises(ValueError):
            apply_verified_overrides.apply_body_replacements("Subject: Test\n\n----------\n\nUnexpected", fix)

    def test_header_fields_restore_missing_to_without_changing_body(self):
        content = "From: Ron\n\nCc: bad OCR\n\nSubject: Test\n\n----------\n\nKeep body."
        fields = {"To": "Andrew; Jeremy", "Cc": "Eddie; kga1978[redacted]"}
        corrected = apply_verified_overrides.apply_header_fields(content, fields)
        self.assertEqual(corrected, "From: Ron\n\nTo: Andrew; Jeremy\n\n"
                         "Cc: Eddie; kga1978[redacted]\n\nSubject: Test\n\n----------\n\nKeep body.")
        self.assertEqual(apply_verified_overrides.apply_header_fields(corrected, fields), corrected)
        with self.assertRaises(ValueError):
            apply_verified_overrides.apply_header_fields("From: Ron\n\n----------\n\nBody.", fields)

    def test_rambaut_inferred_clock_and_fouchier_link_survive_rebuild(self):
        root = Path(__file__).resolve().parents[2]
        overrides = json.loads((root / "tools/verified_overrides.json").read_text())
        override = next(item for item in overrides if item.get("new_thread_key") == "po-emails|2020-02-08|1016")
        fouchier_override = next(item for item in overrides if item.get("new_thread_key") == "po-emails|2020-02-08|1750")
        data = json.loads((root / "page_based/po-emails.json").read_text())
        entry = next(e for e in data["entries"] if e["thread_key"] == override["new_thread_key"])
        fouchier = next(e for e in data["entries"] if e["thread_key"] == fouchier_override["new_thread_key"])
        entry["thread_key"] = "po-emails|2020-02-08|time-unresolved-1916"
        entry["time"] = None
        fouchier.pop("reply_to", None)
        fouchier.pop("reply_to_label", None)
        entry["content"] = entry["content"].replace("I agree with Eddie,", "[ agree with Eddie,", 1)
        entry["content"] = apply_verified_overrides.apply_header_fields(entry["content"], {
            "To": "Jeremy Farrar", "Cc": "bad OCR"
        })
        entry["zone_assumed"] = "UNRESOLVED: " + override["evidence"][:140]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "po-emails.json").write_text(json.dumps({"entries": [fouchier, entry]}))
            (path / "overrides.json").write_text(json.dumps([fouchier_override, override]))
            with patch.object(apply_verified_overrides, "HERE", str(path)), \
                 patch.object(apply_verified_overrides, "OVERRIDES", str(path / "overrides.json")), \
                 contextlib.redirect_stdout(io.StringIO()):
                apply_verified_overrides.main()
                apply_verified_overrides.main()
            result_fouchier, result = json.loads((path / "po-emails.json").read_text())["entries"]
        self.assertIn("\n\nI agree with Eddie,", result["content"])
        self.assertIn("Cc: " + override["header_fields"]["Cc"], result["content"])
        self.assertEqual(result["zone_assumed"], "inferred from the quoting client's presumed time zone: " + override["evidence"])
        self.assertEqual(result["time"], "1016")
        self.assertEqual(result["thread_key"], override["new_thread_key"])
        self.assertEqual(result_fouchier["reply_to"], result["thread_key"])
        self.assertIn("10:16", result_fouchier["reply_to_label"])

    def test_guide_rebuild_preserves_inferred_clock_citation(self):
        config = json.loads(Path(build_po_guide.LIVE_HEADINGS_PATH).read_text())
        sections = []
        for i, item in enumerate(config["sections"], 1):
            sections.append({
                "part": "p1", "number": f"13.{i}", "title": item["source_title_contains"],
                "id": f"p1-13.{i}", "evidence": [],
            })
        section = next(s for s in sections if s["title"] == "Holmes, Farrar and Rambaut")
        section["evidence"].append({
            "doc": "Proximal_Origin_Emails.pdf", "pages": ["51"],
            "raw": "Rambaut p.51; nested 4:16 pm clock, zone unresolved",
        })
        build_po_guide.apply_live_chapter_headings(sections)
        citation = next(e for e in next(s for s in sections if s["id"] == "p1-13.8")["evidence"]
                        if "nested 4:16 pm clock" in e["raw"])
        self.assertIn("inferred CET (10:16 ET / 15:16 UK)", citation["raw"])
        self.assertIn("not Andersen", citation["chapter_link_exclusion"])


if __name__ == "__main__":
    unittest.main()
