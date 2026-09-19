"""Tests for the roadway facts over the corridor.

Specification section 5 names step 5 as "Roadway facts -- ROW_MIN, lanes,
traffic," and it had never been built. The ``roadway`` block was a constant
saying it was never screened, naming a service the tool did not call.

It is built now, and it costs no request: the layer the run already asks for
the alignment carries all three, so the only change to the query is a longer
field list. Worked out under
[#183](https://github.com/RickSmith/survey-recon/issues/183).

----

The two mistakes these tests exist to stop
==========================================

**Reporting one segment's answer as the corridor's.** A corridor is many
inventory segments -- forty on SH16 -- and they disagree. Read live on
2026-09-19, SH16 carries one right-of-way width along its whole length and
**three different lane counts**, 4, 5 and 6. A block that reported the first
segment would say "4 lanes" about a road that is six lanes in places, and
nothing on the page would say it had chosen.

**Reporting a number TxDOT did not publish as a zero.** ``ROW_MIN`` is
populated on on-system highways and empty everywhere else -- zero of 302,900
county road records carry one. A corridor on a county road gets nothing, and
"TxDOT publishes no width for this road" is a different claim from "this road
has no right of way." Only one of them is true, and a zero would say the wrong
one.
"""

import unittest

from corridor_screen import roadway


def segment(**attributes):
    """One inventory segment, in the shape the route service answers with.

    No geometry: this block is about the attributes on the records the
    alignment step already fetched, not about where they are.
    """
    return {"attributes": attributes}


def corridor(*segments):
    return roadway.block(list(segments))


class TestWhenEverySegmentAgrees(unittest.TestCase):
    """The ordinary case, and the one SH16's right-of-way width really is."""

    def setUp(self):
        self.block = corridor(
            segment(ROW_MIN=180, NUM_LANES=4, ADT_CUR=24473, ADT_YEAR=2024),
            segment(ROW_MIN=180, NUM_LANES=4, ADT_CUR=24473, ADT_YEAR=2024),
        )

    def test_the_width_is_reported_once_rather_than_as_a_range_of_one(self):
        self.assertEqual(self.block["row_width_ft"]["low"], 180)
        self.assertEqual(self.block["row_width_ft"]["high"], 180)

    def test_the_block_says_how_many_segments_it_read(self):
        self.assertEqual(self.block["segment_count"], 2)

    def test_nothing_is_counted_as_missing(self):
        self.assertEqual(self.block["row_width_ft"]["segments_without_a_value"], 0)


class TestWhenSegmentsDisagree(unittest.TestCase):
    """SH16 is four, five and six lanes over its own length, really.

    Read live on 2026-09-19 across the forty segments of the demo corridor. So
    this is not a defensive test about a case that might happen.
    """

    def setUp(self):
        self.block = corridor(
            segment(ROW_MIN=180, NUM_LANES=4, ADT_CUR=24473),
            segment(ROW_MIN=180, NUM_LANES=6, ADT_CUR=53406),
            segment(ROW_MIN=180, NUM_LANES=5, ADT_CUR=41669),
        )

    def test_both_ends_of_the_lane_count_are_reported(self):
        self.assertEqual(self.block["lanes"]["low"], 4)
        self.assertEqual(self.block["lanes"]["high"], 6)

    def test_both_ends_of_the_traffic_count_are_reported(self):
        self.assertEqual(self.block["traffic_aadt"]["low"], 24473)
        self.assertEqual(self.block["traffic_aadt"]["high"], 53406)

    def test_a_disagreement_is_said_out_loud_rather_than_left_to_be_noticed(self):
        """Two numbers that differ are easy to miss in a file this size."""
        self.assertTrue(self.block["lanes"]["varies"])

    def test_agreement_is_also_said_so_the_reader_never_has_to_compare(self):
        self.assertFalse(self.block["row_width_ft"]["varies"])


class TestAValueTxdotDidNotPublish(unittest.TestCase):
    """Empty is not zero, and a corridor with none of it is not a finding."""

    def test_a_segment_with_no_width_is_counted_rather_than_read_as_zero(self):
        block = corridor(
            segment(ROW_MIN=180, NUM_LANES=4),
            segment(ROW_MIN=None, NUM_LANES=4),
        )
        self.assertEqual(block["row_width_ft"]["low"], 180)
        self.assertEqual(block["row_width_ft"]["segments_without_a_value"], 1)

    def test_a_corridor_with_no_width_at_all_reports_no_width_rather_than_zero(self):
        """The county road case. Zero of 302,900 county road records carry one."""
        block = corridor(segment(ROW_MIN=None), segment(ROW_MIN=None))
        width = block["row_width_ft"]
        self.assertIsNone(width["low"])
        self.assertIsNone(width["high"])
        self.assertEqual(width["segments_without_a_value"], 2)

    def test_a_real_zero_is_still_a_zero(self):
        """``ROW_MIN`` is never 0 statewide, but reading empty as zero is the
        bug this guards, and reading zero as empty would be the same bug."""
        block = corridor(segment(NUM_LANES=0))
        self.assertEqual(block["lanes"]["low"], 0)
        self.assertEqual(block["lanes"]["segments_without_a_value"], 0)

    def test_the_service_is_read_whatever_case_it_answers_in(self):
        """The casing trap recorded in ``sources.py``, guarded against here too."""
        block = corridor(segment(row_min=180))
        self.assertEqual(block["row_width_ft"]["low"], 180)


class TestTheTrafficYear(unittest.TestCase):
    """A traffic count with no year is not a number anybody can quote."""

    def test_the_year_is_carried_beside_the_count(self):
        block = corridor(segment(ADT_CUR=24473, ADT_YEAR=2024))
        self.assertEqual(block["traffic_aadt"]["year"], 2024)

    def test_no_year_is_no_year_rather_than_a_guess(self):
        block = corridor(segment(ADT_CUR=24473))
        self.assertIsNone(block["traffic_aadt"]["year"])

    def test_two_years_are_both_reported_rather_than_one_chosen(self):
        block = corridor(segment(ADT_CUR=1, ADT_YEAR=2023), segment(ADT_CUR=2, ADT_YEAR=2024))
        self.assertEqual(block["traffic_aadt"]["year"], "2023 to 2024")


class TestTheBlock(unittest.TestCase):
    """A run that never looked and a run that found nothing are different."""

    def test_a_run_that_never_asked_says_so_rather_than_reporting_nothing(self):
        block = roadway.block(None, detail="the run stopped before the alignment")
        self.assertEqual(block["status"], "not-screened")
        self.assertIn("stopped", block["detail"])

    def test_a_run_that_looked_reports_what_it_read(self):
        self.assertEqual(corridor(segment(ROW_MIN=180))["segment_count"], 1)

    def test_the_block_carries_the_units_of_the_width(self):
        """A bare 180 next to the words right of way is the thing to avoid."""
        note = next(
            n for n in corridor(segment(ROW_MIN=180))["notes"]
            if n["topic"] == roadway.NOTE_WIDTH_UNITS
        )
        self.assertIn("feet", note["detail"])

    def test_the_units_note_cites_txdot_rather_than_asserting_them(self):
        """The service publishes no units. This number needs its source."""
        note = next(
            n for n in corridor(segment(ROW_MIN=180))["notes"]
            if n["topic"] == roadway.NOTE_WIDTH_UNITS
        )
        self.assertIn("txdot", note["detail"].lower())
        self.assertNotIn("onlinemanuals", note["detail"])
        self.assertIn(roadway.ROW_MIN_ITEM, note["detail"])

    def test_the_block_says_where_the_width_is_published_and_where_it_is_not(self):
        note = next(
            n for n in corridor(segment(ROW_MIN=180))["notes"]
            if n["topic"] == roadway.NOTE_COVERAGE
        )
        self.assertIn("on-system", note["detail"].lower())

    def test_the_block_says_it_did_not_measure_anything(self):
        """The corridor is a stated half-width. Nothing here may imply otherwise."""
        note = next(
            n for n in corridor(segment(ROW_MIN=180))["notes"]
            if n["topic"] == roadway.NOTE_NOT_A_BOUNDARY
        )
        self.assertIn("half-width", note["detail"])


if __name__ == "__main__":
    unittest.main()
