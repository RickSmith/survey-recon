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


class TestTheDatasheetLink(unittest.TestCase):
    """``MARK NOT FOUND`` starts a decision. The datasheet is what it is made from."""

    def test_a_mark_carries_a_link_to_its_own_datasheet(self):
        marks, _ = select([mark_feature(PID="AY0713", LAST_COND="MARK NOT FOUND")])
        self.assertEqual(
            marks[0]["datasheet_url"],
            "https://geodesy.noaa.gov/cgi-bin/ds_mark.prl?PidBox=AY0713",
        )

    def test_no_pid_means_no_link_rather_than_a_broken_one(self):
        marks, _ = select([mark_feature(LAST_COND="GOOD")])
        self.assertIsNone(marks[0]["datasheet_url"])


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


# -- TxDOT primary control points -------------------------------------------
#
# Issue #15. The same strict corridor test and the same recovery vocabulary as
# the NGS marks above, against a service that spells almost everything
# differently -- and that writes the string ``N/A`` where NGS writes a blank.


def control_feature(lon=-98.65, lat=29.545, **attributes):
    """One TxDOT control point, in the shape layer 67 answers with."""
    return {"attributes": attributes, "geometry": {"x": lon, "y": lat}}


def select_txdot(features, half_width_ft=HALF_WIDTH_FT, pdf_urls=None):
    return control.select_txdot(
        features, ALIGNMENT, half_width_ft, PLANE, pdf_urls=pdf_urls
    )


class TestTheNotApplicablePlaceholder(unittest.TestCase):
    """``N/A`` is this service's blank, and it is a non-empty string.

    The NGS service writes a single space where it has nothing, and
    ``arcgis.attribute`` strips that away. This service writes the three
    characters ``N/A`` instead -- on 649 of its 766 ``NGS_PERM_ID`` values and
    on 24 of its conditions. Stripped, that is still a non-empty string. So a
    tool that only trims whitespace reports a condition of ``N/A`` as a
    condition that somebody reported, and a monument nobody has assessed goes
    into an estimate as control you have.
    """

    def test_a_not_applicable_condition_is_absent_not_a_value(self):
        points, _ = select_txdot([control_feature(STATN_NM="A", MONUMENT_COND_DSCR="N/A")])
        self.assertIsNone(points[0]["condition"])

    def test_a_not_applicable_condition_is_unknown_never_reported(self):
        points, _ = select_txdot([control_feature(STATN_NM="A", MONUMENT_COND_DSCR="N/A")])
        self.assertEqual(points[0]["recovery"], control.RECOVERY_UNKNOWN)

    def test_a_not_applicable_ngs_id_is_not_carried_as_a_pid(self):
        """649 of 766 records say ``N/A`` here. None of them is an NGS mark."""
        points, _ = select_txdot([control_feature(STATN_NM="A", NGS_PERM_ID="N/A")])
        self.assertIsNone(points[0]["ngs_pid"])

    def test_a_real_ngs_id_is_carried_so_the_two_services_can_be_joined(self):
        points, _ = select_txdot([control_feature(STATN_NM="A", NGS_PERM_ID="AY2100")])
        self.assertEqual(points[0]["ngs_pid"], "AY2100")


class TestWhatTheConditionMeansForRecovery(unittest.TestCase):
    """TxDOT's condition vocabulary, mapped onto the same recovery answers.

    ``Destroyed`` gets its own answer rather than being folded in with the NGS
    ``MARK NOT FOUND``. They are different claims: one says somebody looked and
    could not find it, the other says it is gone. Both cost a crew the same
    trip, and merging them would lose which of the two was actually said.
    """

    def test_destroyed_is_named_rather_than_reported_as_a_condition(self):
        points, _ = select_txdot(
            [control_feature(STATN_NM="A", MONUMENT_COND_DSCR="Destroyed")]
        )
        self.assertEqual(points[0]["recovery"], control.RECOVERY_DESTROYED)

    def test_the_service_answers_in_mixed_case_and_is_read_anyway(self):
        """NGS writes ``GOOD``. This service writes ``Good``. Both are read."""
        points, _ = select_txdot([control_feature(STATN_NM="A", MONUMENT_COND_DSCR="Good")])
        self.assertEqual(points[0]["recovery"], control.RECOVERY_REPORTED)
        self.assertEqual(points[0]["condition"], "Good")

    def test_a_condition_of_unknown_is_unknown_not_a_reported_condition(self):
        """Nine records say this. "Condition reported: Unknown" would be a lie."""
        points, _ = select_txdot(
            [control_feature(STATN_NM="A", MONUMENT_COND_DSCR="Unknown")]
        )
        self.assertEqual(points[0]["recovery"], control.RECOVERY_UNKNOWN)

    def test_poor_is_reported_and_left_to_the_surveyor_who_signs(self):
        points, _ = select_txdot([control_feature(STATN_NM="A", MONUMENT_COND_DSCR="Poor")])
        self.assertEqual(points[0]["recovery"], control.RECOVERY_REPORTED)
        self.assertEqual(points[0]["condition"], "Poor")


class TestTheRecoveryDate(unittest.TestCase):
    """This service publishes a date as milliseconds since 1970. NGS does not."""

    def test_an_epoch_date_is_written_as_a_date_a_person_can_read(self):
        points, _ = select_txdot(
            [control_feature(STATN_NM="A", LAST_RCOV_DT=1159660800000)]
        )
        self.assertEqual(points[0]["last_recovered"], "2006-10-01")

    def test_no_recovery_date_stays_absent_rather_than_becoming_1970(self):
        """752 of 766 records publish none. A zero here would read as New Year 1970."""
        points, _ = select_txdot([control_feature(STATN_NM="A")])
        self.assertIsNone(points[0]["last_recovered"])


class TestTheIntervisiblePartner(unittest.TestCase):
    """TxDOT requires primary control in intervisible pairs, so the partner is data."""

    def test_the_partner_station_is_carried_through(self):
        points, _ = select_txdot(
            [control_feature(STATN_NM="Z0151155AZ", INTERVSBL_STATN_NM="Z0151155")]
        )
        self.assertEqual(points[0]["intervisible_station"], "Z0151155")


class TestTheControlSheetPdf(unittest.TestCase):
    """The field the research note calls a PDF link is empty. The PDF is an attachment."""

    def test_a_point_carries_the_link_to_its_own_control_sheet(self):
        points, _ = select_txdot(
            [control_feature(STATN_NM="A", OBJECTID=10, PDF_Filename="SCP_32.pdf")],
            pdf_urls={10: "https://example.test/67/10/attachments/538"},
        )
        self.assertEqual(
            points[0]["control_sheet_url"], "https://example.test/67/10/attachments/538"
        )

    def test_a_point_with_no_attachment_carries_nothing_rather_than_a_broken_link(self):
        points, _ = select_txdot([control_feature(STATN_NM="A", OBJECTID=11)])
        self.assertIsNone(points[0]["control_sheet_url"])


class TestWhichControlPointsAreInTheCorridor(unittest.TestCase):
    """The same strict point test the NGS marks get, for the same reason."""

    def test_a_point_beyond_the_half_width_is_out(self):
        points, skipped = select_txdot([control_feature(lat=29.548, STATN_NM="FAR")])
        self.assertEqual(points, [])
        self.assertEqual(skipped, 0)

    def test_a_point_with_no_position_is_counted_never_dropped(self):
        points, skipped = select_txdot(
            [{"attributes": {"STATN_NM": "A"}, "geometry": None}]
        )
        self.assertEqual(points, [])
        self.assertEqual(skipped, 1)

    def test_nearest_the_centerline_comes_first_then_the_station_name(self):
        points, _ = select_txdot(
            [
                control_feature(lat=29.5455, STATN_NM="FURTHER"),
                control_feature(STATN_NM="B"),
                control_feature(lon=-98.66, STATN_NM="A"),
            ],
            half_width_ft=1000,
        )
        self.assertEqual([p["station"] for p in points], ["A", "B", "FURTHER"])


class TestTheTxdotControlCount(unittest.TestCase):
    """What an estimator reads before pricing TxDOT control."""

    def points(self):
        found, _ = select_txdot(
            [
                control_feature(STATN_NM="A", MONUMENT_COND_DSCR="Good"),
                control_feature(lon=-98.66, STATN_NM="B", MONUMENT_COND_DSCR="Destroyed"),
                control_feature(lon=-98.67, STATN_NM="C", MONUMENT_COND_DSCR="N/A"),
                control_feature(lon=-98.64, STATN_NM="D", MONUMENT_COND_DSCR="Unknown"),
            ]
        )
        return found

    def test_it_counts_the_monuments_that_are_gone(self):
        counted = control.txdot_recovery_risk(self.points())
        self.assertEqual(counted["destroyed"], 1)

    def test_unknown_covers_both_the_word_and_the_placeholder(self):
        counted = control.txdot_recovery_risk(self.points())
        self.assertEqual(counted["condition_unknown"], 2)

    def test_every_condition_the_service_returned_is_tallied(self):
        counted = control.txdot_recovery_risk(self.points())
        self.assertEqual(
            counted["by_condition"],
            {"Good": 1, "Destroyed": 1, "Unknown": 1, "(none published)": 1},
        )

    def test_the_total_is_the_points_in_the_corridor(self):
        counted = control.txdot_recovery_risk(self.points())
        self.assertEqual(counted["points_in_corridor"], 4)


class TestTheSameMonumentTwice(unittest.TestCase):
    """This service holds two records for a great many of its monuments.

    Read on 2026-09-12: 766 records carrying only 492 distinct station names.
    274 names appear twice, which is 548 of the 766 records. On the SH16
    corridor it is four records naming two monuments.

    A crew drives to the monument, not to the record. Reporting four where
    there are two doubles the control an estimator thinks is already set, and
    that is a discount on a price nobody chose to give.

    Both numbers are reported and neither record is dropped. The service said
    what it said, and all 274 duplicated pairs agree on condition, so there is
    no call to make about which of the two to believe -- only a count to be
    honest about.
    """

    def points(self):
        found, _ = select_txdot(
            [
                control_feature(STATN_NM="Z0151105", MONUMENT_COND_DSCR="Good"),
                control_feature(lon=-98.6501, STATN_NM="Z0151105", MONUMENT_COND_DSCR="Good"),
                control_feature(lon=-98.66, STATN_NM="Z0151225", MONUMENT_COND_DSCR="Good"),
            ]
        )
        return found

    def test_every_record_the_service_sent_stays_on_the_list(self):
        self.assertEqual(len(self.points()), 3)

    def test_the_monument_count_is_reported_beside_the_record_count(self):
        counted = control.txdot_recovery_risk(self.points())
        self.assertEqual(counted["points_in_corridor"], 3)
        self.assertEqual(counted["distinct_stations"], 2)


class TestTheControlBlock(unittest.TestCase):
    """What the output file carries under ``control``."""

    def test_a_run_that_never_asked_txdot_says_so_rather_than_reporting_none(self):
        """Zero points and never-looked are different answers, same as the marks."""
        block = control.block([], txdot_detail="the host was not answering")
        self.assertEqual(block["txdot_points"]["status"], "not-screened")
        self.assertEqual(block["txdot_points"]["detail"], "the host was not answering")

    def test_a_run_that_asked_txdot_and_found_nothing_reports_an_empty_list(self):
        block = control.block([], txdot_points=[])
        self.assertEqual(block["txdot_points"], [])
        self.assertEqual(block["txdot_control"]["points_in_corridor"], 0)

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
