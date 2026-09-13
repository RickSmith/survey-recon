"""Tests for hanging flags on parcels, and lead times on flags.

This is the money feature, so the tests are about the two mistakes that would
cost somebody money. Reporting a parcel as clear of something that was never
checked. And reporting a lead time that nobody can trace to a source.
"""

import unittest

from corridor_screen import flags, lead_times
from corridor_screen.geometry import LocalPlane
from corridor_screen.sources import CEMETERIES, PIPELINES, RAILROADS, SCHOOLS

PLANE = LocalPlane(29.545)
TABLE = lead_times.load()

# One square parcel on Bandera Road, about half a mile on a side.
PARCEL_RINGS = [[[-98.66, 29.54], [-98.66, 29.55], [-98.65, 29.55], [-98.65, 29.54]]]
# The centerline runs straight through it.
ALIGNMENT = [[[-98.68, 29.545], [-98.63, 29.545]]]


def row(identifier="05678-000-0010"):
    return {
        "id": identifier,
        "screened_for": [],
        "flags": [],
        "max_lead_time_days": None,
        "lead_time_driver": None,
        "warnings": [],
    }


def point_feature(lon, lat, **attributes):
    return {"attributes": attributes, "geometry": {"x": lon, "y": lat}}


def line_feature(path, **attributes):
    return {"attributes": attributes, "geometry": {"paths": [path]}}


def attach(found, rows=None, adjacent_ft=100):
    rows = rows if rows is not None else [row()]
    corridor_flags, counts = flags.attach(
        rows,
        {r["id"]: PARCEL_RINGS for r in rows},
        found,
        adjacent_distance_ft=adjacent_ft,
        alignment_paths=ALIGNMENT,
        corridor_half_width_ft=300,
        plane=PLANE,
        table=TABLE,
    )
    return rows, corridor_flags, counts


class TestReadingAnAttribute(unittest.TestCase):
    """The casing trap, recorded at the bottom of ``sources.py``.

    The USGS structures layers publish ``NAME`` and answer with ``name``. A
    plain dictionary lookup finds nothing and every school comes out unnamed.
    """

    def test_a_field_is_found_whatever_case_the_service_answered_in(self):
        self.assertEqual(flags.attribute({"name": "Helotes Elementary"}, "NAME"), "Helotes Elementary")
        self.assertEqual(flags.attribute({"NAME": "Helotes Elementary"}, "name"), "Helotes Elementary")

    def test_a_blank_is_an_absent_value_rather_than_an_empty_answer(self):
        self.assertIsNone(flags.attribute({"name": "   "}, "NAME"))

    def test_a_field_that_is_not_there_is_not_invented(self):
        self.assertIsNone(flags.attribute({"name": "x"}, "railowner"))


class TestOnAgainstAdjacent(unittest.TestCase):
    def test_a_cemetery_inside_the_parcel_is_on_it(self):
        found = [(CEMETERIES, "cemetery", [point_feature(-98.655, 29.545, name="Evers Family Cemetery")])]
        rows, _, _ = attach(found)
        flag = rows[0]["flags"][0]
        self.assertEqual(flag["relation"], "on")
        self.assertEqual(flag["name"], "Evers Family Cemetery")
        self.assertIsNone(flag["distance_ft"], "distance is recorded only when adjacent")

    def test_a_cemetery_just_outside_the_parcel_is_adjacent_with_its_distance(self):
        # About 50 ft west of the parcel's western edge.
        just_west = -98.66 - (50 / 5280) / 60.2
        found = [(CEMETERIES, "cemetery", [point_feature(just_west, 29.545, name="Nanez Cemetery")])]
        rows, _, _ = attach(found)
        flag = rows[0]["flags"][0]
        self.assertEqual(flag["relation"], "adjacent")
        self.assertAlmostEqual(flag["distance_ft"], 50, delta=5)

    def test_a_cemetery_beyond_the_adjacent_distance_is_not_this_parcel_s_problem(self):
        far_west = -98.66 - (400 / 5280) / 60.2
        found = [(CEMETERIES, "cemetery", [point_feature(far_west, 29.545, name="Somewhere Else")])]
        rows, _, _ = attach(found)
        self.assertEqual(rows[0]["flags"], [])

    def test_on_and_adjacent_are_both_recorded_and_never_merged(self):
        """A party chief needs both. An estimator must not count both."""
        just_west = -98.66 - (50 / 5280) / 60.2
        found = [(CEMETERIES, "cemetery", [
            point_feature(-98.655, 29.545, name="Inside"),
            point_feature(just_west, 29.545, name="Next door"),
        ])]
        rows, _, _ = attach(found)
        self.assertEqual(
            sorted((f["name"], f["relation"]) for f in rows[0]["flags"]),
            [("Inside", "on"), ("Next door", "adjacent")],
        )

    def test_a_railroad_crossing_the_parcel_is_on_it(self):
        found = [(RAILROADS, "railroad", [
            line_feature([[-98.68, 29.5455], [-98.63, 29.5455]], name="SAN ANTONIO SUB", railowner="Union Pacific Railroad Company"),
        ])]
        rows, _, _ = attach(found)
        self.assertEqual(rows[0]["flags"][0]["relation"], "on")
        self.assertEqual(rows[0]["flags"][0]["type"], "railroad")


class TestLeadTimesRideOnFlags(unittest.TestCase):
    def test_a_cemetery_carries_fourteen_days_and_its_statute(self):
        found = [(CEMETERIES, "cemetery", [point_feature(-98.655, 29.545, name="Evers Family Cemetery")])]
        rows, _, _ = attach(found)
        flag = rows[0]["flags"][0]
        self.assertEqual(flag["lead_time_days"], 14)
        self.assertTrue(flag["lead_time_statutory"])
        self.assertIn("711.041", flag["lead_time_source"])
        self.assertTrue(flag["lead_time_url"].startswith("https://"))

    def test_a_railroad_carries_the_top_of_its_published_range(self):
        found = [(RAILROADS, "railroad", [line_feature([[-98.68, 29.5455], [-98.63, 29.5455]], name="SUB")])]
        rows, _, _ = attach(found)
        flag = rows[0]["flags"][0]
        self.assertEqual(flag["lead_time_days"], 45)
        self.assertEqual(flag["lead_time_days_low"], 30)
        self.assertFalse(flag["lead_time_statutory"], "a corporate procedure is not a statute")
        self.assertIn("up.com", flag["lead_time_url"])

    def test_every_lead_time_in_the_table_has_a_source_and_a_link(self):
        for key, entry in TABLE.items():
            self.assertTrue(entry.source, f"[{key}] has no source")
            self.assertTrue(entry.url, f"[{key}] has no link")

    def test_a_school_says_not_found_rather_than_no_delay(self):
        found = [(SCHOOLS, "school", [point_feature(-98.655, 29.545, name="Helotes Elementary School")])]
        rows, _, _ = attach(found)
        flag = rows[0]["flags"][0]
        self.assertIsNone(flag["lead_time_days"])
        self.assertFalse(flag["lead_time_confirmed"])
        self.assertIn("not found", flag["lead_time_not_found"].lower())
        self.assertIn("Looked in", flag["lead_time_not_found"])


class TestTheLongestWaitIsVisible(unittest.TestCase):
    """A parcel you cannot enter for 45 days is a schedule problem the day you bid."""

    def test_the_longest_lead_time_is_a_number_on_the_row(self):
        found = [
            (CEMETERIES, "cemetery", [point_feature(-98.655, 29.545, name="Evers")]),
            (RAILROADS, "railroad", [line_feature([[-98.68, 29.5455], [-98.63, 29.5455]], name="SUB")]),
        ]
        rows, _, _ = attach(found)
        self.assertEqual(rows[0]["max_lead_time_days"], 45)
        self.assertEqual(rows[0]["lead_time_driver"], "railroad")

    def test_a_parcel_with_no_flags_has_no_lead_time(self):
        rows, _, _ = attach([(CEMETERIES, "cemetery", [])])
        self.assertIsNone(rows[0]["max_lead_time_days"])
        self.assertIsNone(rows[0]["lead_time_driver"])

    def test_a_parcel_whose_only_flag_has_no_confirmed_number_is_not_reported_as_clear(self):
        found = [(SCHOOLS, "school", [point_feature(-98.655, 29.545, name="Helotes Elementary School")])]
        rows, _, _ = attach(found)
        self.assertIsNone(rows[0]["max_lead_time_days"])
        self.assertEqual(rows[0]["lead_time_not_found"], ["school"])

    def test_a_confirmed_number_and_an_unconfirmed_flag_are_both_visible(self):
        found = [
            (CEMETERIES, "cemetery", [point_feature(-98.655, 29.545, name="Evers")]),
            (SCHOOLS, "school", [point_feature(-98.6555, 29.5455, name="Helotes Elementary")]),
        ]
        rows, _, _ = attach(found)
        self.assertEqual(rows[0]["max_lead_time_days"], 14)
        self.assertEqual(rows[0]["lead_time_driver"], "cemetery")
        self.assertEqual(rows[0]["lead_time_not_found"], ["school"])


class TestScreenedForKeepsUnknownApartFromNo(unittest.TestCase):
    def test_only_the_types_actually_checked_are_listed(self):
        found = [
            (CEMETERIES, "cemetery", []),
            (SCHOOLS, "school", []),
        ]
        rows, _, _ = attach(found)
        self.assertEqual(rows[0]["screened_for"], ["cemetery", "school"])

    def test_a_service_that_was_never_asked_is_never_reported_as_clear(self):
        """The whole point. A railroad not looked for is not a railroad absent."""
        rows, _, _ = attach([(CEMETERIES, "cemetery", [])])
        self.assertNotIn("railroad", rows[0]["screened_for"])


class TestCorridorLevelFlags(unittest.TestCase):
    def test_a_feature_in_the_corridor_on_no_parcel_is_recorded_against_the_run(self):
        """Nothing gets quietly dropped for being hard to attach."""
        no_parcels = []
        _, corridor_flags, _ = attach(
            [(PIPELINES, "pipeline", [line_feature([[-98.67, 29.545], [-98.64, 29.545]], CMDTY_DESC="NATURAL GAS")])],
            rows=no_parcels,
        )
        self.assertEqual(len(corridor_flags), 1)
        self.assertEqual(corridor_flags[0]["type"], "pipeline")
        self.assertEqual(corridor_flags[0]["relation"], "corridor")
        self.assertEqual(corridor_flags[0]["lead_time_days"], 2)

    def test_a_feature_on_a_parcel_is_not_also_a_corridor_flag(self):
        found = [(CEMETERIES, "cemetery", [point_feature(-98.655, 29.545, name="Evers")])]
        _, corridor_flags, _ = attach(found)
        self.assertEqual(corridor_flags, [])

    def test_a_feature_outside_the_corridor_and_off_every_parcel_is_not_promoted(self):
        """The service answers for a box around the parcels, which is wider than
        the ribbon. A school in the box, on no parcel and outside the corridor,
        is not this corridor's problem and must not be reported as one."""
        far = point_feature(-98.60, 29.60, name="Somewhere in the box")
        rows, corridor_flags, counts = attach([(SCHOOLS, "school", [far])])
        self.assertEqual(rows[0]["flags"], [])
        self.assertEqual(corridor_flags, [])
        self.assertEqual(counts["school"]["unused"], 1)


class TestCountsAreVisible(unittest.TestCase):
    def test_the_honesty_block_can_say_how_many_records_were_used(self):
        found = [(CEMETERIES, "cemetery", [
            point_feature(-98.655, 29.545, name="Evers"),
            point_feature(-98.60, 29.60, name="Miles away"),
        ])]
        _, _, counts = attach(found)
        self.assertEqual(counts["cemetery"], {"returned": 2, "on_parcels": 1, "corridor": 0, "unused": 1})


if __name__ == "__main__":
    unittest.main()
