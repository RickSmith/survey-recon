"""Tests for the crew safety sheet.

This is the one output in the tool that nobody prices. A party chief reads it
before the crew goes out, and the question it answers is where the nearest help
is -- not what the job costs.

That changes what a mistake costs, so the tests here are about the three ways
this sheet could hurt somebody.

Reporting a straight-line distance in a way that reads as drive time. The line
does not know about the river, the freeway with no crossing, or the locked gate
on the ranch road, and an ambulance does.

Reporting "no hospital" when what happened is "nobody looked that far." Same
rule as ``unknown`` against ``no`` everywhere else in this repo, and here the
consequence is a crew that believes it has no cover.

And answering for the corridor as a whole when a crew is standing at one end of
it. Eight and a half miles is a long way to be wrong about.
"""

import unittest

from corridor_screen import safety
from corridor_screen.geometry import LocalPlane

PLANE = LocalPlane(29.545)
# The centerline runs west to east along Bandera Road, about three miles of it.
ALIGNMENT = [[[-98.68, 29.545], [-98.63, 29.545]]]
START = [-98.68, 29.545]
END = [-98.63, 29.545]

# 2016-08-11, as this service sends it. USGS publishes LOADDATE as a real date
# field, so it arrives as milliseconds -- the same trap the ROW map sheets
# carry, and the reason both read it through one function.
MS_2016 = 1470873600000


def place_feature(lon=-98.655, lat=29.55, **attributes):
    """One structures record, in the shape the service answers with."""
    return {"attributes": attributes, "geometry": {"x": lon, "y": lat}}


def nearest(features, limit=safety.PLACES_PER_TYPE):
    return safety.nearest(features, ALIGNMENT, START, END, PLANE, limit=limit)


class TestFindingTheNearest(unittest.TestCase):
    """Nearest to the centerline, because that is where the crew is working."""

    def test_the_closest_place_comes_first(self):
        places, _ = nearest(
            [
                place_feature(lat=29.60, NAME="Far Hospital"),
                place_feature(lat=29.55, NAME="Near Hospital"),
            ]
        )
        self.assertEqual(places[0]["name"], "Near Hospital")

    def test_the_distance_is_given_not_just_the_name(self):
        """The ticket asks for this in as many words."""
        places, _ = nearest([place_feature(NAME="Some Hospital")])
        self.assertIsInstance(places[0]["distance_from_centerline_mi"], float)
        self.assertGreater(places[0]["distance_from_centerline_mi"], 0)

    def test_only_so_many_are_kept(self):
        features = [place_feature(lat=29.55 + i / 100, NAME=f"H{i}") for i in range(10)]
        places, _ = nearest(features)
        self.assertEqual(len(places), safety.PLACES_PER_TYPE)

    def test_a_record_with_no_position_is_counted_rather_than_dropped(self):
        places, without_position = nearest(
            [{"attributes": {"NAME": "Nowhere Hospital"}, "geometry": None}]
        )
        self.assertEqual(places, [])
        self.assertEqual(without_position, 1)

    def test_the_order_is_the_same_every_run(self):
        """The output file is committed to git. An unstable order is a diff every run."""
        features = [
            place_feature(lat=29.55, NAME="B Hospital"),
            place_feature(lat=29.55, NAME="A Hospital"),
        ]
        first, _ = nearest(features)
        second, _ = nearest(list(reversed(features)))
        self.assertEqual([p["name"] for p in first], [p["name"] for p in second])


class TestTheEndsOfTheCorridor(unittest.TestCase):
    """Nearest to the line is not nearest to the crew.

    A corridor is miles long. A hospital two miles off the centerline can still
    be nine miles from the end a crew is standing on, so every place carries
    its distance from both ends as well.
    """

    def test_every_place_carries_its_distance_from_both_ends(self):
        places, _ = nearest([place_feature(lon=-98.68, lat=29.55, NAME="West End Hospital")])
        place = places[0]
        self.assertIn("distance_from_start_mi", place)
        self.assertIn("distance_from_end_mi", place)

    def test_a_place_by_one_end_is_far_from_the_other(self):
        places, _ = nearest([place_feature(lon=-98.68, lat=29.545, NAME="West End Hospital")])
        place = places[0]
        self.assertLess(place["distance_from_start_mi"], 0.5)
        self.assertGreater(place["distance_from_end_mi"], 2.0)


class TestTheFields(unittest.TestCase):
    """What a party chief needs is an address, not only a name."""

    def test_the_address_is_carried(self):
        places, _ = nearest(
            [
                place_feature(
                    NAME="University Hospital",
                    ADDRESS="4502 Medical Drive",
                    CITY="San Antonio",
                    STATE="TX",
                    ZIPCODE="78229",
                )
            ]
        )
        place = places[0]
        self.assertEqual(place["address"], "4502 Medical Drive")
        self.assertEqual(place["city"], "San Antonio")
        self.assertEqual(place["state"], "TX")
        self.assertEqual(place["zipcode"], "78229")

    def test_the_service_is_read_whatever_case_it_answers_in(self):
        """USGS publishes these fields in capitals and answers in lower case."""
        places, _ = nearest([place_feature(name="University Hospital", address="4502 Medical Drive")])
        self.assertEqual(places[0]["name"], "University Hospital")
        self.assertEqual(places[0]["address"], "4502 Medical Drive")

    def test_how_old_the_record_is_is_carried_and_readable(self):
        """A fire station that closed in 2017 is still in a record loaded in 2016."""
        places, _ = nearest([place_feature(NAME="Old Station", LOADDATE=MS_2016)])
        self.assertEqual(places[0]["source_load_date"], "2016-08-11")


class TestTheBlock(unittest.TestCase):
    """The ``crew_safety`` block, and the three answers it can give per type."""

    def found(self, **by_type):
        return safety.block(by_type, search_radius_mi=25.0)

    def test_a_type_that_was_found_reports_its_nearest(self):
        places, _ = nearest([place_feature(NAME="University Hospital")])
        block = self.found(hospital=(places, 0))
        self.assertEqual(block["by_type"]["hospital"]["nearest"]["name"], "University Hospital")

    def test_a_type_that_was_looked_for_and_not_found_says_how_far_we_looked(self):
        """Not "there is no hospital". Nobody can say that from this data."""
        block = self.found(hospital=([], 0))
        found = block["by_type"]["hospital"]
        self.assertIsNone(found["nearest"])
        self.assertIn("hospital", block["not_found_within_the_radius"])
        # The radius the answer has to be read against sits on the block,
        # once, rather than being repeated on every kind of help.
        self.assertEqual(block["search_radius_mi"], 25.0)

    def test_a_type_nobody_asked_about_is_not_reported_as_absent(self):
        """A blocked host is not an answer about the world."""
        block = self.found(hospital=([], 0))
        self.assertNotIn("police", block["by_type"])
        self.assertIn("police", block["not_checked"])

    def test_a_run_that_never_asked_at_all_says_so_rather_than_reporting_none(self):
        block = safety.block(None, search_radius_mi=25.0, detail="the host was blocking")
        self.assertEqual(block["status"], "not-screened")
        self.assertIn("blocking", block["detail"])

    def test_the_block_says_the_distance_is_a_straight_line_not_a_drive(self):
        """The one thing on this sheet that could get somebody hurt."""
        block = self.found(hospital=([], 0))
        topics = [note["topic"] for note in block["notes"]]
        self.assertIn(safety.NOTE_STRAIGHT_LINE, topics)
        note = next(n for n in block["notes"] if n["topic"] == safety.NOTE_STRAIGHT_LINE)
        self.assertIn("drive", note["detail"])

    def test_the_block_says_it_is_a_screening_aid_and_not_a_safety_plan(self):
        block = self.found(hospital=([], 0))
        topics = [note["topic"] for note in block["notes"]]
        self.assertIn(safety.NOTE_NOT_A_PLAN, topics)

    def test_records_with_no_position_are_recorded_per_type(self):
        block = self.found(hospital=([], 2))
        self.assertEqual(block["by_type"]["hospital"]["without_position"], 2)

    def test_the_search_radius_is_stated_on_the_block(self):
        """Stated, never derived -- the same rule as every other distance here."""
        block = self.found(hospital=([], 0))
        self.assertEqual(block["search_radius_mi"], 25.0)


class TestWhatIsPrintedWhileSomebodyIsWatching(unittest.TestCase):
    """The sheet as it reaches a screen, not only as it reaches the file.

    This class exists because of a bug the unit tests did not catch. Renaming
    ``distance_mi`` to ``distance_from_centerline_mi`` updated the module, the
    output file and every test here -- and missed the line ``cli._report_safety``
    prints. Every test passed and the tool crashed on the next real run.

    The printer reads keys off the same place dictionaries, so it is a second
    caller of that shape and needs a test of its own. This is the cheapest
    version of one: run it, and require the numbers to actually appear.
    """

    def _printed(self, by_type, search_miles=25.0):
        from corridor_screen import cli

        lines = []
        original = cli._say
        cli._say = lambda message="": lines.append(message)
        try:
            cli._report_safety(by_type, search_miles)
        finally:
            cli._say = original
        return "\n".join(lines)

    def test_the_nearest_place_and_its_distance_both_reach_the_screen(self):
        places, _ = nearest([place_feature(NAME="University Hospital", CITY="San Antonio")])
        printed = self._printed({"hospital": (places, 0)})
        self.assertIn("University Hospital", printed)
        self.assertIn("San Antonio", printed)
        self.assertIn(f"{places[0]['distance_from_centerline_mi']:.2f}", printed)

    def test_the_straight_line_warning_is_printed_every_time(self):
        """Not only when something looks odd. It is the caveat that matters most."""
        places, _ = nearest([place_feature(NAME="University Hospital")])
        self.assertIn("straight lines", self._printed({"hospital": (places, 0)}))

    def test_nothing_found_is_printed_as_the_radius_rather_than_as_none(self):
        printed = self._printed({"hospital": ([], 0)}, search_miles=25.0)
        self.assertIn("none within 25 miles", printed)

    def test_a_kind_nobody_asked_about_is_printed_as_neither(self):
        printed = self._printed({"hospital": ([], 0)})
        self.assertIn("not checked", printed)

    def test_a_run_that_never_asked_prints_nothing_as_absent(self):
        printed = self._printed(None)
        self.assertIn("not checked", printed)
        self.assertNotIn("0.00", printed)


class TestTheTypesAreNamedOnce(unittest.TestCase):
    """A type this tool does not know about cannot be reported on."""

    def test_the_ticket_s_three_are_all_covered(self):
        for wanted in ("hospital", "police"):
            self.assertIn(wanted, safety.SAFETY_TYPES)

    def test_ems_is_covered_by_both_the_services_that_publish_it(self):
        """USGS splits it: ambulance services and fire/EMS stations are two layers."""
        self.assertIn("ambulance", safety.SAFETY_TYPES)
        self.assertIn("fire_ems", safety.SAFETY_TYPES)


if __name__ == "__main__":
    unittest.main()
