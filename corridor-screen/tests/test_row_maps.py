"""Tests for the ROW map sheets over the corridor.

Old sheets mean hand retracement and illegible scans, and that is time on the
estimate. So the number that matters is how many sheets there are and how far
back they go, and the tests here are about the mistakes that would put the
wrong one of those two numbers in front of a surveyor.

The date trap is the big one and it is not hypothetical. This service publishes
its dates as a real date type, which ArcGIS sends as milliseconds since 1970 --
and every sheet older than 1970 is therefore a **negative** number. Handed to
Python's ``datetime.fromtimestamp`` on Windows, a negative value does not
return a wrong date. It raises ``OSError``, which would take the whole ROW step
down on exactly the oldest sheets, which are exactly the ones that drive the
estimate.
"""

import unittest

from corridor_screen import row_maps
from corridor_screen.geometry import LocalPlane

PLANE = LocalPlane(29.545)
# The centerline runs west to east along Bandera Road.
ALIGNMENT = [[[-98.68, 29.545], [-98.63, 29.545]]]
HALF_WIDTH_FT = 300

# 1937-09-01 and 1998-03-06, as this service sends them. The first is negative
# because it is before 1970, and that is the whole trap.
MS_1937 = -1020384000000
MS_1998 = 889142400000


def sheet_feature(path=None, **attributes):
    """One ROW map sheet record, in the shape the service answers with.

    The geometry is a polyline, not a point. A sheet covers a stretch of route
    centerline, so what comes back is the line it covers.
    """
    if path is None:
        path = [[-98.65, 29.545], [-98.64, 29.545]]
    return {"attributes": attributes, "geometry": {"paths": [path]}}


def select(features, half_width_ft=HALF_WIDTH_FT):
    return row_maps.select(features, ALIGNMENT, half_width_ft, PLANE)


class TestReadingTheDates(unittest.TestCase):
    """The dates arrive as milliseconds since 1970, and half of them are negative."""

    def test_a_date_after_1970_is_read(self):
        self.assertEqual(row_maps.from_epoch_ms(MS_1998), "1998-03-06")

    def test_a_date_before_1970_is_read_rather_than_crashing(self):
        """The trap. ``datetime.fromtimestamp`` raises ``OSError`` here on Windows."""
        self.assertEqual(row_maps.from_epoch_ms(MS_1937), "1937-09-01")

    def test_no_date_stays_no_date(self):
        self.assertIsNone(row_maps.from_epoch_ms(None))

    def test_a_value_this_code_does_not_recognize_is_passed_through_untouched(self):
        """A value it cannot read is not a value it should be rewriting."""
        self.assertEqual(row_maps.from_epoch_ms("19980306"), "19980306")

    def test_the_date_read_matches_the_date_in_the_sheets_own_name(self):
        """The cross-check that says the milliseconds were read in the right zone.

        Every sheet name ends in the sheet's own date, so the service states it
        twice. Read an hour out and the two stop agreeing.
        """
        sheets, _ = select(
            [sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998)]
        )
        self.assertEqual(sheets[0]["map_from_date"], "1998-03-06")
        self.assertTrue(sheets[0]["map_name"].endswith("19980306"))


class TestWhichSheetsCountAsInTheCorridor(unittest.TestCase):
    """A sheet is a line. It is in the corridor if any part of it is."""

    def test_a_sheet_over_the_centerline_is_in(self):
        sheets, _ = select([sheet_feature(MAP_NM="SAT-029110-SH0016-19980306")])
        self.assertEqual(len(sheets), 1)

    def test_a_sheet_that_only_crosses_the_corridor_is_still_in(self):
        """A crossing route's ROW is the record you retrace at the interchange."""
        crossing = [[-98.65, 29.56], [-98.65, 29.53]]
        sheets, _ = select([sheet_feature(path=crossing, MAP_NM="SAT-052104-IH0410-19470101")])
        self.assertEqual(len(sheets), 1)

    def test_a_sheet_well_outside_the_corridor_is_left_out(self):
        far = [[-98.65, 29.60], [-98.64, 29.60]]
        sheets, _ = select([sheet_feature(path=far, MAP_NM="SAT-029109-SH0016-19370901")])
        self.assertEqual(sheets, [])

    def test_a_sheet_with_no_shape_is_counted_rather_than_dropped(self):
        """It cannot be placed in the corridor or out of it, so it is said out loud."""
        sheets, without_shape = select(
            [{"attributes": {"MAP_NM": "SAT-029110-SH0016-19980306"}, "geometry": None}]
        )
        self.assertEqual(sheets, [])
        self.assertEqual(without_shape, 1)

    def test_the_distance_from_the_centerline_is_recorded(self):
        sheets, _ = select([sheet_feature(MAP_NM="SAT-029110-SH0016-19980306")])
        self.assertEqual(sheets[0]["distance_from_centerline_ft"], 0.0)

    def test_the_order_is_the_same_every_run(self):
        """The output file is committed to git. An unstable order is a diff every run."""
        features = [
            sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998),
            sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", MAP_FROM_DT=MS_1937),
        ]
        first, _ = select(features)
        second, _ = select(list(reversed(features)))
        self.assertEqual([s["map_name"] for s in first], [s["map_name"] for s in second])

    def test_the_oldest_sheet_is_first_because_age_is_what_costs_time(self):
        features = [
            sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998),
            sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", MAP_FROM_DT=MS_1937),
        ]
        sheets, _ = select(features)
        self.assertEqual(sheets[0]["map_from_date"], "1937-09-01")


class TestTheFieldsOnASheet(unittest.TestCase):
    """Every field the specification names is carried, as the service sent it."""

    def test_the_named_fields_are_all_present(self):
        sheets, _ = select(
            [
                sheet_feature(
                    MAP_NM="SAT-029110-SH0016-19980306",
                    ROW_MAP_ID=993.0,
                    CTRL_SECT_NBR="029110",
                    CSJ_NBR=None,
                    RTE_NM="SH0016",
                    CNTY_NM="Bexar",
                    MAP_FROM_DT=MS_1998,
                    MAP_TO_DT=None,
                    TOTL_MAP_PAGE_QTY=1.0,
                )
            ]
        )
        sheet = sheets[0]
        self.assertEqual(sheet["map_name"], "SAT-029110-SH0016-19980306")
        self.assertEqual(sheet["row_map_id"], 993.0)
        self.assertEqual(sheet["control_section"], "029110")
        self.assertIsNone(sheet["csj"])
        self.assertEqual(sheet["route"], "SH0016")
        self.assertEqual(sheet["county"], "Bexar")
        self.assertEqual(sheet["map_from_date"], "1998-03-06")
        self.assertIsNone(sheet["map_to_date"])
        self.assertEqual(sheet["total_pages"], 1.0)

    def test_the_service_is_read_whatever_case_it_answers_in(self):
        """The casing trap recorded in ``sources.py``, guarded against here too."""
        sheets, _ = select([sheet_feature(map_nm="SAT-029110-SH0016-19980306", rte_nm="SH0016")])
        self.assertEqual(sheets[0]["map_name"], "SAT-029110-SH0016-19980306")
        self.assertEqual(sheets[0]["route"], "SH0016")


class TestTheDateRange(unittest.TestCase):
    """How far back the records go. Half of the answer this ticket asks for."""

    def test_the_range_runs_from_the_oldest_sheet_to_the_newest(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998),
                sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", MAP_FROM_DT=MS_1937),
            ]
        )
        spread = row_maps.date_range(sheets)
        self.assertEqual(spread["from"], "1937-09-01")
        self.assertEqual(spread["to"], "1998-03-06")

    def test_the_range_names_the_sheets_the_two_dates_came_from(self):
        """So a reader can check the number against the drawing rather than trust it."""
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998),
                sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", MAP_FROM_DT=MS_1937),
            ]
        )
        spread = row_maps.date_range(sheets)
        self.assertEqual(spread["oldest_sheet"], "SAT-029109-SH0016-19370901")
        self.assertEqual(spread["newest_sheet"], "SAT-029110-SH0016-19980306")

    def test_sheets_with_no_date_are_counted_rather_than_ignored(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", MAP_FROM_DT=MS_1998),
                sheet_feature(MAP_NM="SAT-029110-SH0016-00000000", MAP_FROM_DT=None),
            ]
        )
        spread = row_maps.date_range(sheets)
        self.assertEqual(spread["sheets_without_a_date"], 1)
        self.assertEqual(spread["from"], "1998-03-06")

    def test_no_dated_sheet_at_all_gives_no_range_rather_than_a_made_up_one(self):
        sheets, _ = select([sheet_feature(MAP_NM="SAT-029110-SH0016-00000000", MAP_FROM_DT=None)])
        spread = row_maps.date_range(sheets)
        self.assertIsNone(spread["from"])
        self.assertIsNone(spread["to"])
        self.assertEqual(spread["sheets_without_a_date"], 1)


class TestTheRouteBreakdown(unittest.TestCase):
    """Which sheets belong to the corridor's own route, and which to a crossing one.

    This is the split that answers the ticket's own headline number. SH16
    through the whole of Bexar County has 27 sheets; this corridor is eight and
    a half miles inside one of that route's three control sections, and the
    sheets that reach it are a smaller set. Both numbers are right and they
    answer different questions, so the file shows the working.
    """

    def test_each_route_gets_its_own_count_and_range(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", RTE_NM="SH0016", MAP_FROM_DT=MS_1998),
                sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", RTE_NM="SH0016", MAP_FROM_DT=MS_1937),
                sheet_feature(MAP_NM="SAT-052104-IH0410-19980306", RTE_NM="IH0410", MAP_FROM_DT=MS_1998),
            ]
        )
        breakdown = row_maps.by_route(sheets)
        self.assertEqual(breakdown["SH0016"]["sheet_count"], 2)
        self.assertEqual(breakdown["SH0016"]["date_range"]["from"], "1937-09-01")
        self.assertEqual(breakdown["IH0410"]["sheet_count"], 1)

    def test_each_route_carries_the_control_sections_its_sheets_belong_to(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", RTE_NM="SH0016", CTRL_SECT_NBR="029110"),
                sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", RTE_NM="SH0016", CTRL_SECT_NBR="029109"),
            ]
        )
        breakdown = row_maps.by_route(sheets)
        self.assertEqual(breakdown["SH0016"]["control_sections"], ["029109", "029110"])

    def test_a_sheet_with_no_route_is_named_rather_than_dropped(self):
        sheets, _ = select([sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", RTE_NM=None)])
        breakdown = row_maps.by_route(sheets)
        self.assertEqual(breakdown[row_maps.NO_ROUTE]["sheet_count"], 1)


class TestTheControlSections(unittest.TestCase):
    """Which numbered segments of highway the corridor's records belong to."""

    def test_every_control_section_is_listed_once_in_order(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="a", CTRL_SECT_NBR="029110"),
                sheet_feature(MAP_NM="b", CTRL_SECT_NBR="029110"),
                sheet_feature(MAP_NM="c", CTRL_SECT_NBR="029109"),
            ]
        )
        self.assertEqual(row_maps.control_sections(sheets), ["029109", "029110"])


class TestTheBlock(unittest.TestCase):
    """The ``row_maps`` block of the output file."""

    def test_a_run_that_looked_reports_the_count_and_the_range(self):
        sheets, _ = select(
            [
                sheet_feature(MAP_NM="SAT-029110-SH0016-19980306", RTE_NM="SH0016", MAP_FROM_DT=MS_1998),
                sheet_feature(MAP_NM="SAT-029109-SH0016-19370901", RTE_NM="SH0016", MAP_FROM_DT=MS_1937),
            ]
        )
        block = row_maps.block(sheets)
        self.assertEqual(block["sheet_count"], 2)
        self.assertEqual(block["date_range"]["from"], "1937-09-01")
        self.assertEqual(block["date_range"]["to"], "1998-03-06")

    def test_a_run_that_never_asked_says_so_rather_than_reporting_zero(self):
        """Zero sheets and never-looked are different answers.

        A corridor with no ROW record at all would be remarkable. Reported as a
        count of zero it reads as a finding; reported as ``not-screened`` it
        reads as the gap it is.
        """
        block = row_maps.block(None, detail="the host was blocking")
        self.assertEqual(block["status"], "not-screened")
        self.assertIn("blocking", block["detail"])

    def test_a_run_that_looked_and_found_nothing_reports_zero(self):
        block = row_maps.block([])
        self.assertEqual(block["sheet_count"], 0)
        self.assertIsNone(block["date_range"]["from"])

    def test_sheets_the_service_sent_with_no_shape_are_recorded_in_the_block(self):
        block = row_maps.block([], without_shape=2)
        self.assertEqual(block["sheets_without_a_shape"], 2)

    def test_the_block_says_the_service_gives_no_link_to_the_drawing(self):
        """Spec section 10: the output says so rather than leaving a blank."""
        block = row_maps.block([])
        topics = [note["topic"] for note in block["notes"]]
        self.assertIn(row_maps.NOTE_DRAWINGS, topics)

    def test_the_block_says_what_the_count_covers(self):
        """So nobody reads a corridor figure as a whole-route one."""
        block = row_maps.block([])
        topics = [note["topic"] for note in block["notes"]]
        self.assertIn(row_maps.NOTE_WHAT_IS_COUNTED, topics)

    def test_the_block_doubts_the_suspect_date_in_the_file_not_only_in_the_docs(self):
        """The date this service uses often enough to be worth doubting.

        The doubt has to travel with the number it doubts. A caveat that lives
        only in a documentation page is a caveat nobody reads at the moment
        they are about to quote 1900 off a projector.
        """
        block = row_maps.block([])
        note = next(n for n in block["notes"] if n["topic"] == row_maps.NOTE_EARLIEST_DATE)
        self.assertIn(row_maps.SUSPECT_DATE, note["detail"])
        self.assertIn("could not confirm", note["detail"])

    def test_the_drawings_note_cites_txdot_rather_than_asserting_the_procedure(self):
        """A statement about TxDOT's own process carries its source."""
        block = row_maps.block([])
        note = next(n for n in block["notes"] if n["topic"] == row_maps.NOTE_DRAWINGS)
        self.assertIn("txdot.gov", note["detail"])
        self.assertNotIn("onlinemanuals", note["detail"])


if __name__ == "__main__":
    unittest.main()
