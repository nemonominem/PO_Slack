import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import apply_verified_overrides


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


if __name__ == "__main__":
    unittest.main()
