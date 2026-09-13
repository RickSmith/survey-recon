"""Tests for the NGS marks along the corridor.

The whole reason to pull the marks is recovery against setting new, so the
tests are about the mistakes that would put the wrong number in that column.

Dropping ``condition``, which turns a mark nobody could find into a mark you
have. Letting a blank condition read as a good mark. And counting a mark
sixty feet outside the corridor as one you are going to recover.
"""

import unittest

from corridor_screen import control
from corridor_screen.geometry import LocalPlane

PLANE = LocalPlane(29.545)
# The centerline runs west to east along Bandera Road.
ALIGNMENT = [[[-98.68, 29.545], [-98.63, 29.545]]]
HALF_WIDTH_FT = 300


def mark_feature(lon=-98.65, lat=29.545, **attributes):
    """One NGS datasheet record, in the shape the service answers with."""
    return {"attributes": attributes, "geometry": {"x": lon, "y": lat}}


def select(features, half_width_ft=HALF_WIDTH_FT):
    return control.select(features, ALIGNMENT, half_width_ft, PLANE)


class TestCarryingTheCondition(unittest.TestCase):
    """``condition`` is the field the ticket exists for. It is never dropped."""

    def test_mark_not_found_is_in_the_output_verbatim(self):
        marks, _ = select([mark_feature(PID="AY0713", LAST_COND="MARK NOT FOUND")])
        self.assertEqual(marks[0]["condition"], "MARK NOT FOUND")

    def test_the_pid_is_carried_so_the_mark_can_be_looked_up(self):
        marks, _ = select([mark_feature(PID="AY0713", LAST_COND="GOOD")])
        self.assertEqual(marks[0]["pid"], "AY0713")

    def test_a_not_found_mark_is_called_recovery_risk_not_left_to_be_read(self):
        marks, _ = select([mark_feature(PID="AY0713", LAST_COND="MARK NOT FOUND")])
        self.assertEqual(marks[0]["recovery"], control.RECOVERY_NOT_FOUND)

    def test_any_other_condition_is_reported_rather_than_interpreted(self):
        """``POOR`` is not this tool's judgment to make. It reports and points."""
        marks, _ = select([mark_feature(PID="AY1234", LAST_COND="POOR")])
        self.assertEqual(marks[0]["recovery"], control.RECOVERY_REPORTED)
        self.assertEqual(marks[0]["condition"], "POOR")

    def test_the_service_is_read_whatever_case_it_answers_in(self):
        """The casing trap recorded in ``sources.py``, guarded against here too."""
        marks, _ = select([mark_feature(pid="AY0713", last_cond="MARK NOT FOUND")])
        self.assertEqual(marks[0]["pid"], "AY0713")
        self.assertEqual(marks[0]["condition"], "MARK NOT FOUND")


class TestABlankCondition(unittest.TestCase):
    """A mark with no published condition is unknown. It is never a mark you have.

    The service publishes a single space for six records around Bexar County.
    Read carelessly that is a non-empty string, and a mark nobody has visited
    goes into an estimate as recoverable.
    """

    def test_a_blank_condition_is_absent_not_empty(self):
        marks, _ = select([mark_feature(PID="AY0001", LAST_COND=" ")])
        self.assertIsNone(marks[0]["condition"])

    def test_a_blank_condition_is_unknown_never_reported(self):
        marks, _ = select([mark_feature(PID="AY0001", LAST_COND=" ")])
        self.assertEqual(marks[0]["recovery"], control.RECOVERY_UNKNOWN)

    def test_a_missing_condition_field_is_unknown_too(self):
        marks, _ = select([mark_feature(PID="AY0001")])
        self.assertEqual(marks[0]["recovery"], control.RECOVERY_UNKNOWN)


class TestWhichMarksAreInTheCorridor(unittest.TestCase):
    """The strict inside-the-corridor test, which points can be held to.

    Spec section 8 says so in as many words: the strict form "stays correct for
    services that return points -- NGS marks, TxDOT control."
    """

    def test_a_mark_on_the_centerline_is_in(self):
        marks, _ = select([mark_feature(lat=29.545, PID="ON")])
        self.assertEqual([m["pid"] for m in marks], ["ON"])

    def test_a_mark_beyond_the_half_width_is_out(self):
        # About 1,100 ft north of the centerline, well past a 300 ft half-width.
        marks, skipped = select([mark_feature(lat=29.548, PID="FAR")])
        self.assertEqual(marks, [])
        self.assertEqual(skipped, 0)

    def test_the_distance_from_the_centerline_is_recorded_in_feet(self):
        # A hundredth of a degree of latitude is a little over 3,600 ft.
        marks, _ = select([mark_feature(lat=29.5455, PID="OFF")], half_width_ft=1000)
        self.assertAlmostEqual(marks[0]["distance_from_centerline_ft"], 182.2, delta=2.0)

    def test_a_mark_on_the_centerline_reads_zero_rather_than_blank(self):
        marks, _ = select([mark_feature(lat=29.545, PID="ON")])
        self.assertEqual(marks[0]["distance_from_centerline_ft"], 0.0)


class TestAMarkWithNoPosition(unittest.TestCase):
    """A mark the service sent without a point is counted, never dropped."""

    def test_it_does_not_reach_the_list(self):
        marks, skipped = select([{"attributes": {"PID": "AY0002"}, "geometry": None}])
        self.assertEqual(marks, [])
        self.assertEqual(skipped, 1)


class TestOrdering(unittest.TestCase):
    """The output file is committed to git, so its order has to be stable."""

    def test_nearest_the_centerline_comes_first(self):
        marks, _ = select(
            [
                mark_feature(lat=29.5455, PID="FURTHER"),
                mark_feature(lat=29.545, PID="NEAREST"),
            ],
            half_width_ft=1000,
        )
        self.assertEqual([m["pid"] for m in marks], ["NEAREST", "FURTHER"])

    def test_marks_the_same_distance_out_are_ordered_by_pid(self):
        marks, _ = select(
            [mark_feature(PID="AY0900"), mark_feature(lon=-98.66, PID="AY0100")]
        )
        self.assertEqual([m["pid"] for m in marks], ["AY0100", "AY0900"])


class TestTheRecoveryRiskCount(unittest.TestCase):
    """The number an estimator reads before deciding recovery against setting new."""

    def marks(self):
        found, _ = select(
            [
                mark_feature(PID="A", LAST_COND="MARK NOT FOUND"),
                mark_feature(lon=-98.66, PID="B", LAST_COND="MARK NOT FOUND"),
                mark_feature(lon=-98.67, PID="C", LAST_COND="GOOD"),
                mark_feature(lon=-98.64, PID="D", LAST_COND=" "),
            ]
        )
        return found

    def test_it_counts_the_marks_nobody_could_find(self):
        counted = control.recovery_risk(self.marks())
        self.assertEqual(counted["mark_not_found"], 2)

    def test_unknown_is_counted_apart_from_not_found(self):
        counted = control.recovery_risk(self.marks())
        self.assertEqual(counted["condition_unknown"], 1)

    def test_every_condition_the_service_returned_is_tallied(self):
        counted = control.recovery_risk(self.marks())
        self.assertEqual(
            counted["by_condition"],
            {"MARK NOT FOUND": 2, "GOOD": 1, "(none published)": 1},
        )

    def test_the_total_is_the_marks_in_the_corridor(self):
        counted = control.recovery_risk(self.marks())
        self.assertEqual(counted["marks_in_corridor"], 4)


class TestTheControlBlock(unittest.TestCase):
    """What the output file carries under ``control``."""

    def test_txdot_points_are_named_as_not_screened_rather_than_left_out(self):
        """A block that is absent looks like an oversight. #15 is not done yet."""
        block = control.block([])
        self.assertEqual(block["txdot_points"]["status"], "not-screened")
        self.assertIn("15", block["txdot_points"]["detail"])

    def test_a_run_that_never_asked_says_so_rather_than_reporting_no_marks(self):
        """Zero marks and never-looked are different answers. ``unknown`` vs ``no``."""
        block = control.block(None, detail="the host was not answering")
        self.assertEqual(block["ngs_marks"]["status"], "not-screened")
        self.assertEqual(block["ngs_marks"]["detail"], "the host was not answering")

    def test_a_run_that_asked_and_found_nothing_reports_an_empty_list(self):
        block = control.block([])
        self.assertEqual(block["ngs_marks"], [])
        self.assertEqual(block["recovery_risk"]["marks_in_corridor"], 0)


if __name__ == "__main__":
    unittest.main()
