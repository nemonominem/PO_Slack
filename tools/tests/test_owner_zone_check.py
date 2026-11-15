import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import owner_zone_check


class NumericPrintedStampTests(unittest.TestCase):
    def test_numeric_outlook_stamp_preserves_date_and_seconds(self):
        stamp = owner_zone_check.printed("2/10/2020 1:26:57 AM")
        self.assertEqual(stamp, datetime(2020, 2, 10, 1, 26, 57))

    def test_numeric_pacific_stamp_converts_to_eastern_without_day_shift(self):
        stamp = owner_zone_check.printed("2/10/2020 1:26:57 AM")
        eastern = stamp.replace(tzinfo=ZoneInfo("America/Los_Angeles")).astimezone(
            ZoneInfo("America/New_York")
        )
        self.assertEqual(eastern, datetime(2020, 2, 10, 4, 26, 57, tzinfo=ZoneInfo("America/New_York")))

    def test_noon_and_seconds_are_parsed(self):
        stamp = owner_zone_check.printed("2/9/2020 12:00:46 PM")
        self.assertEqual(stamp, datetime(2020, 2, 9, 12, 0, 46))


if __name__ == "__main__":
    unittest.main()
