"""Tests for the lead-time table and the rules it is held to.

The table is checked-in data, and these tests are the guard rail on it. A lead
time with no citation is a rumor with a number on it, and one of those in front
of a licensed surveyor is worse than no tool at all.
"""

import tempfile
import unittest
from pathlib import Path

from corridor_screen import lead_times


def write(text):
    handle = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


GOOD = """
[cemetery]
label = "Cemetery"
confirmed = true
statutory = true
lead_time_days = 14
basis = "calendar days"
driver = "written notice"
source = "Tex. Health & Safety Code S 711.041(c)(2)"
url = "https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm"
verified_on = 2026-09-12
"""


class TestTheShippedTable(unittest.TestCase):
    """The real file, with the real manual_links. These are the numbers that ship."""

    def setUp(self):
        self.table = lead_times.load()

    def test_every_row_carries_a_source_and_a_link(self):
        for key, entry in self.table.items():
            self.assertTrue(entry.source.strip(), f"[{key}] has no source")
            self.assertTrue(entry.url.startswith("http"), f"[{key}] has no usable link")

    def test_the_four_screened_types_are_all_there(self):
        for key in ("school", "cemetery", "railroad", "pipeline"):
            self.assertIn(key, self.table)

    def test_the_cemetery_number_is_fourteen_days_and_statutory(self):
        entry = self.table["cemetery"]
        self.assertEqual(entry.days, 14)
        self.assertTrue(entry.statutory)
        self.assertIn("711.041", entry.source)

    def test_the_pipeline_floor_is_two_working_days_and_statutory(self):
        entry = self.table["pipeline"]
        self.assertEqual(entry.days, 2)
        self.assertTrue(entry.statutory)
        self.assertIn("251.151", entry.source)

    def test_the_railroad_number_is_the_top_of_a_published_range(self):
        entry = self.table["railroad"]
        self.assertEqual((entry.days, entry.days_low), (45, 30))
        self.assertFalse(entry.statutory, "a corporate procedure is not a statute")

    def test_the_school_row_is_unconfirmed_and_says_where_it_looked(self):
        entry = self.table["school"]
        self.assertFalse(entry.confirmed)
        self.assertIsNone(entry.days)
        self.assertTrue(entry.not_found.lower().startswith("not found"))
        self.assertIn("Looked in", entry.not_found)

    def test_no_confirmed_row_is_missing_the_date_it_was_read(self):
        for key, entry in self.table.items():
            if entry.confirmed:
                self.assertIsNotNone(entry.verified_on, f"[{key}] does not say when it was read")


class TestTheTableRefusesWhatCannotBeQuoted(unittest.TestCase):
    def test_a_row_with_no_source_is_a_hard_error(self):
        path = write(GOOD.replace('source = "Tex. Health & Safety Code S 711.041(c)(2)"', ""))
        with self.assertRaises(lead_times.LeadTimeTableError) as caught:
            lead_times.load(path)
        self.assertIn("source", str(caught.exception))

    def test_a_row_with_no_link_is_a_hard_error(self):
        path = write(GOOD.replace('url = "https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm"', ""))
        with self.assertRaises(lead_times.LeadTimeTableError):
            lead_times.load(path)

    def test_a_confirmed_row_with_no_number_is_a_hard_error(self):
        path = write(GOOD.replace("lead_time_days = 14", ""))
        with self.assertRaises(lead_times.LeadTimeTableError):
            lead_times.load(path)

    def test_an_unconfirmed_row_that_does_not_say_not_found_is_a_hard_error(self):
        """Anything softer than "not found" reads as no delay."""
        path = write(
            GOOD.replace("confirmed = true", "confirmed = false")
            .replace("lead_time_days = 14", '')
            .replace('statutory = true', 'not_found = "We could not track this down. Looked in: nowhere useful."')
        )
        with self.assertRaises(lead_times.LeadTimeTableError) as caught:
            lead_times.load(path)
        self.assertIn("Not found", str(caught.exception))

    def test_an_unconfirmed_row_that_does_not_say_where_it_looked_is_a_hard_error(self):
        path = write(
            GOOD.replace("confirmed = true", "confirmed = false")
            .replace("lead_time_days = 14", '')
            .replace('statutory = true', 'not_found = "Not found."')
        )
        with self.assertRaises(lead_times.LeadTimeTableError) as caught:
            lead_times.load(path)
        self.assertIn("where it", str(caught.exception))

    def test_a_row_cannot_be_confirmed_and_not_found_at_once(self):
        path = write(GOOD + '\nnot_found = "Not found. Looked in: everywhere."\n')
        with self.assertRaises(lead_times.LeadTimeTableError):
            lead_times.load(path)

    def test_an_empty_table_is_a_hard_error_rather_than_a_quiet_nothing(self):
        path = write('schema_version = "1.0.0"\n')
        with self.assertRaises(lead_times.LeadTimeTableError):
            lead_times.load(path)

    def test_a_missing_table_says_so_by_name(self):
        with self.assertRaises(lead_times.LeadTimeTableError) as caught:
            lead_times.load("no-such-file.toml")
        self.assertIn("no-such-file.toml", str(caught.exception))


class TestWhichDaysTheNumberCounts(unittest.TestCase):
    """Two working days and two calendar days are different promises."""

    def setUp(self):
        self.table = lead_times.load()

    def test_the_pipeline_floor_is_working_days_because_the_statute_says_so(self):
        self.assertEqual(self.table["pipeline"].basis, "working days")

    def test_the_cemetery_notice_is_calendar_days(self):
        self.assertEqual(self.table["cemetery"].basis, "calendar days")

    def test_a_confirmed_row_that_does_not_say_which_days_is_a_hard_error(self):
        path = write(GOOD.replace('basis = "calendar days"', ""))
        with self.assertRaises(lead_times.LeadTimeTableError) as caught:
            lead_times.load(path)
        self.assertIn("which", str(caught.exception).lower())

    def test_a_basis_nobody_recognizes_is_a_hard_error(self):
        path = write(GOOD.replace('basis = "calendar days"', 'basis = "days"'))
        with self.assertRaises(lead_times.LeadTimeTableError):
            lead_times.load(path)


class TestTheLongestWait(unittest.TestCase):
    def test_the_biggest_number_wins_and_names_itself(self):
        flags = [
            {"type": "cemetery", "lead_time_days": 14, "lead_time_basis": "calendar days"},
            {"type": "railroad", "lead_time_days": 45, "lead_time_basis": "calendar days"},
            {"type": "pipeline", "lead_time_days": 2, "lead_time_basis": "working days"},
        ]
        self.assertEqual(lead_times.longest(flags), (45, "railroad", "calendar days"))

    def test_the_number_never_comes_back_without_saying_which_days(self):
        """A bare "2" is the sort of thing a reader turns into a date and gets wrong."""
        flags = [{"type": "pipeline", "lead_time_days": 2, "lead_time_basis": "working days"}]
        days, driver, basis = lead_times.longest(flags)
        self.assertEqual((days, driver), (2, "pipeline"))
        self.assertEqual(basis, "working days")

    def test_nothing_with_a_number_gives_no_number(self):
        self.assertEqual(
            lead_times.longest([{"type": "school", "lead_time_days": None}]), (None, None, None)
        )

    def test_no_flags_at_all_gives_no_number(self):
        self.assertEqual(lead_times.longest([]), (None, None, None))

    def test_the_types_with_no_number_are_listed_separately(self):
        flags = [
            {"type": "cemetery", "lead_time_days": 14},
            {"type": "school", "lead_time_days": None},
            {"type": "school", "lead_time_days": None},
        ]
        self.assertEqual(lead_times.unconfirmed_types(flags), ["school"])


if __name__ == "__main__":
    unittest.main()
