"""Tests for the bid memo.

This is the document a principal reads before pricing a job, and it is the only
output of this tool that looks like something a firm would send rather than
something a program produced. That makes it the easiest place to mislead
somebody, because it reads with authority.

So the tests here are about the three ways a memo could do damage.

**Printing a number the run did not measure.** ``acres_in_corridor`` is not
implemented -- every parcel carries ``None``. A memo that summed those into
"0.0 acres in the corridor" would put a figure in front of a principal that no
part of this tool ever calculated.

**Burying what is uncertain inside what is certain.** The ticket asks for
uncertainty "stated plainly rather than buried inside a number," which means it
gets its own section and its own heading, not a footnote under a total.

**Reading as complete when it is not.** A run that skipped a service, or a
corridor where a flag type was never checked, has to say so on the face of the
memo -- not in an appendix somebody scrolls past.
"""

import unittest

from corridor_screen import bid_memo


def a_document(**overrides):
    """A screening document, in the shape ``output.build`` produces."""
    document = {
        "schema_version": "0.1.0",
        "run": {
            "run_id": "texas-bexar-sh0016-kg-20260913T070646",
            "started_at": "2026-09-13T07:06:46-05:00",
            "finished_at": "2026-09-13T07:07:31-05:00",
            "status": "complete",
            "stopped_at_service": None,
            "mode": "live",
            "tool_version": "0.1.0",
            "half_width_ft": 300,
            "adjacent_distance_ft": 100,
            "sanity_margin_ft": 500.0,
            "safety_search_miles": 25.0,
            "area": "texas-bexar",
            "not_screenable": [
                {"type": "gated access", "reason": "no public source publishes gate locations"},
                {"type": "livestock", "reason": "no public source publishes livestock presence"},
            ],
            "screened_for": ["cemetery", "pipeline", "railroad", "school"],
            "map_link": "https://www.openstreetmap.org/?mlat=29.5&mlon=-98.6",
            "lead_times": {},
        },
        "alignment": {
            "source_path": "SH0016-KG DFO 347.7 to 356.367",
            "length_mi": 8.691,
            "run_count": 1,
            "bbox": [-98.68, 29.48, -98.59, 29.57],
        },
        "corridor": {"area_sq_mi": 0.9986},
        "roadway": {"status": "not-screened", "detail": "Roadway_Inventory_2023 is not called"},
        "services": [
            {"name": "BCAD_Parcels", "status": "ok", "record_count": 530,
             "captured_at": "2026-09-13T07:06:55-05:00", "warnings": []},
        ],
        "control": {
            "ngs_marks": [{"pid": "AY0958", "condition": "MARK NOT FOUND"}],
            "recovery_risk": {
                "marks_in_corridor": 11,
                "mark_not_found": 11,
                "condition_unknown": 0,
                "by_condition": {"MARK NOT FOUND": 11},
            },
            "txdot_control": {"points_in_corridor": 4, "distinct_stations": 2, "destroyed": 0},
        },
        "row_maps": {
            "sheet_count": 69,
            "date_range": {"from": "1900-01-01", "to": "2005-04-30",
                           "oldest_sheet": "SAT-052104-IH0410-19000101"},
            "by_route": {"SH0016": {"sheet_count": 15,
                                    "date_range": {"from": "1944-01-01", "to": "1998-03-06"}}},
            "notes": [],
        },
        "crew_safety": {
            "search_radius_mi": 25.0,
            "by_type": {
                "hospital": {"nearest": {"name": "Audie L Murphy VA",
                                         "distance_from_centerline_mi": 2.05}},
            },
            "not_found_within_the_radius": [],
            "not_checked": [],
        },
        "parcels": [a_parcel(), a_parcel(id="17920-009-0180", flags=[{"type": "school"}],
                                        max_lead_time_days=14,
                                        max_lead_time_basis="calendar days",
                                        lead_time_driver="cemetery")],
        "corridor_flags": [],
        "warnings": [],
    }
    document.update(overrides)
    return document


def a_parcel(**overrides):
    parcel = {
        "id": "17919-008-0280",
        "id_source": "Geo_id",
        "owner": "LARAMIE FORDS LANDING LTD",
        "legal_acres": "4.515",
        "acres_in_corridor": None,
        "roe_required": "unknown",
        "txdot_owned": None,
        "screened_for": ["cemetery", "pipeline", "railroad", "school"],
        "flags": [],
        "max_lead_time_days": None,
        "max_lead_time_basis": None,
        "lead_time_driver": None,
        "lead_time_not_found": [],
    }
    parcel.update(overrides)
    return parcel


class TestItIsBuiltFromTheRun(unittest.TestCase):
    """Every number on the page comes off the document, never from this file."""

    def test_the_corridor_is_named_as_the_run_recorded_it(self):
        memo = bid_memo.build(a_document())
        self.assertIn("SH0016-KG", memo)
        self.assertIn("347.7", memo)
        self.assertIn("8.69", memo)

    def test_the_tract_count_is_the_number_of_rows(self):
        memo = bid_memo.build(a_document())
        self.assertIn("2", memo.split("## ")[0] + memo)

    def test_a_different_run_produces_different_numbers(self):
        """The blunt check that nothing is hard-coded."""
        one = bid_memo.build(a_document())
        other = a_document()
        other["parcels"] = [a_parcel(), a_parcel(), a_parcel()]
        other["control"]["recovery_risk"]["marks_in_corridor"] = 40
        self.assertNotEqual(one, bid_memo.build(other))
        self.assertIn("40", bid_memo.build(other))

    def test_the_stated_distances_are_on_the_page(self):
        """A parcel count is only arguable against the width somebody chose."""
        memo = bid_memo.build(a_document())
        self.assertIn("300", memo)


class TestWhatItRefusesToSay(unittest.TestCase):
    """The numbers this tool did not measure do not appear as numbers."""

    def test_acres_in_the_corridor_is_never_summed_into_a_total(self):
        """Every parcel carries None. Summing them would invent 0.0 acres."""
        memo = bid_memo.build(a_document())
        self.assertNotIn("0.0 acres", memo)
        self.assertNotIn("0 acres in", memo)

    def test_it_says_the_take_was_not_measured(self):
        memo = bid_memo.build(a_document())
        self.assertIn("not measured", memo.lower())

    def test_it_never_reports_a_right_of_entry_as_settled(self):
        memo = bid_memo.build(a_document())
        self.assertNotIn("no right of entry required", memo.lower())
        self.assertIn("unknown", memo.lower())


class TestUncertaintyGetsItsOwnSection(unittest.TestCase):
    """Stated plainly, the ticket says. Not buried inside a number."""

    def test_there_is_a_heading_for_it(self):
        memo = bid_memo.build(a_document())
        headings = [line for line in memo.splitlines() if line.startswith("#")]
        self.assertTrue(
            any("not" in h.lower() or "uncertain" in h.lower() for h in headings),
            f"no heading names what is uncertain: {headings}",
        )

    def test_what_no_public_source_publishes_is_named(self):
        """The memo capitalizes them as labels, so the match ignores case."""
        memo = bid_memo.build(a_document()).lower()
        self.assertIn("gated access", memo)
        self.assertIn("livestock", memo)

    def test_a_step_the_tool_does_not_run_is_named(self):
        memo = bid_memo.build(a_document())
        self.assertIn("Roadway_Inventory_2023", memo)

    def test_a_flag_type_with_no_lead_time_is_named_rather_than_counted_as_zero(self):
        document = a_document()
        document["parcels"][1]["lead_time_not_found"] = ["school"]
        memo = bid_memo.build(document)
        self.assertIn("school", memo)
        self.assertNotIn("0 days", memo)

    def test_how_old_the_data_is_appears(self):
        memo = bid_memo.build(a_document())
        self.assertIn("2026-09-13", memo)


class TestTheFindingsThatDriveThePrice(unittest.TestCase):
    """What a principal is reading this for."""

    def test_marks_nobody_could_find_are_the_headline_not_a_footnote(self):
        memo = bid_memo.build(a_document())
        self.assertIn("MARK NOT FOUND", memo)
        self.assertIn("11", memo)

    def test_the_row_sheets_carry_their_age(self):
        memo = bid_memo.build(a_document())
        self.assertIn("1944", memo)

    def test_the_longest_lead_time_is_stated_with_which_days_it_counts(self):
        """Two working days and two calendar days are different promises."""
        memo = bid_memo.build(a_document())
        self.assertIn("14", memo)
        self.assertIn("calendar days", memo)

    def test_a_corridor_with_no_lead_time_at_all_does_not_invent_one(self):
        document = a_document()
        for parcel in document["parcels"]:
            parcel["max_lead_time_days"] = None
        memo = bid_memo.build(document)
        self.assertNotIn("0 days", memo)


class TestARunThatDidNotFinish(unittest.TestCase):
    """A memo that reads complete when the run was not is the worst outcome."""

    def test_an_incomplete_run_says_so_near_the_top(self):
        document = a_document()
        document["run"]["status"] = "incomplete"
        document["run"]["stopped_at_service"] = "BCAD_Parcels"
        memo = bid_memo.build(document)
        top = memo[: len(memo) // 3]
        self.assertIn("incomplete", top.lower())
        self.assertIn("BCAD_Parcels", memo)

    def test_a_flag_type_that_was_never_checked_is_named(self):
        document = a_document()
        document["run"]["screened_for"] = ["cemetery", "railroad"]
        memo = bid_memo.build(document)
        self.assertIn("pipeline", memo)
        self.assertIn("school", memo)

    def test_a_recorded_doubt_reaches_the_memo(self):
        document = a_document()
        document["warnings"] = [
            {"check": "records fall outside the corridor", "service": "BCAD_Parcels",
             "severity": "warning", "detail": "12 of 530 records are far away",
             "what_to_do": "compare against the corridor drawing"}
        ]
        memo = bid_memo.build(document)
        self.assertIn("records fall outside the corridor", memo)


class TestItReadsLikeSomethingAFirmWouldSend(unittest.TestCase):
    """Not a program's output. The ticket is explicit about this."""

    def test_it_says_what_it_is_not(self):
        memo = bid_memo.build(a_document())
        lowered = memo.lower()
        self.assertIn("not a survey", lowered)
        self.assertIn("not a title", lowered)

    def test_it_names_who_has_to_sign(self):
        memo = bid_memo.build(a_document())
        self.assertIn("RPLS", memo)

    def test_it_does_not_dump_field_names_at_the_reader(self):
        """`max_lead_time_days` is a column name, not something a principal reads."""
        memo = bid_memo.build(a_document())
        for identifier in ("max_lead_time_days", "acres_in_corridor", "id_source",
                           "recovery_risk", "by_condition", "screened_for"):
            self.assertNotIn(identifier, memo)

    def test_it_carries_the_map_link_so_the_location_can_be_confirmed(self):
        memo = bid_memo.build(a_document())
        self.assertIn("openstreetmap.org", memo)


if __name__ == "__main__":
    unittest.main()
