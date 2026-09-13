"""Tests for failure beat two -- the answer that is wrong rather than missing.

Issue #26: "USGS 3DEP ignored the coordinate-system parameter ... and returned a
plausible non-answer instead of an error. It did not fail. It answered. That is
worse."

**The shape of the failure is not what the ticket describes, and the difference
is the finding.** `wkid` is honored today: ask in Web Mercator meters with
`wkid=3857` and the right elevation comes back. What is not honored is `units`.

Ask the elevation of SH16 at Bandera Road, twice, one word apart:

- ``units=Feet``    -> ``866.8668528742528``  a JSON number, in feet
- ``units=US_Feet`` -> ``"264.221008301"``    a JSON string, in meters

866.87 / 264.22 is 3.28084, which is feet per meter. It is the same elevation.
And ``US_Feet`` is not a typo a programmer would make -- **it is what a Texas
surveyor calls the unit they work in**: the one EPSG numbers 9003, and the one
TxDOT's Survey Manual requires in deliverables (Ch. 3, Control Points).

No error. HTTP 200. Valid JSON. A number that is a perfectly plausible elevation
for San Antonio, three and a quarter times too small, with nothing anywhere in
the response saying which unit it is.

Everything here reads from committed captures in
``corridor-screen/captures/silent-nodata/``, so it runs with no network.
"""

import json
import unittest
from pathlib import Path

from corridor_screen import elevation_trap

# The socket guard `test_offline` built under #19, so "it works offline" is
# proven rather than asserted.
from tests.test_offline import no_network

REPO = Path(__file__).resolve().parents[2]


class TestTheUnitThatIsNotHonored(unittest.TestCase):
    """The dangerous half: a right-looking number in the wrong unit."""

    def test_asking_in_feet_answers_in_feet(self):
        self.assertAlmostEqual(elevation_trap.value_of("feet"), 866.8668528742528, places=6)

    def test_asking_in_us_feet_answers_in_meters(self):
        """The unit a Texas surveyor actually works in."""
        self.assertAlmostEqual(elevation_trap.value_of("us_feet"), 264.221008301, places=6)

    def test_the_two_numbers_are_the_same_height(self):
        """Which is what makes the wrong one plausible rather than obviously
        broken. A number that looked wrong would be caught."""
        ratio = elevation_trap.value_of("feet") / elevation_trap.value_of("us_feet")
        self.assertAlmostEqual(ratio, elevation_trap.FEET_PER_METER, places=4)

    def test_the_us_feet_answer_equals_the_meters_answer_exactly(self):
        """Not approximately. It is the metric answer, handed back unchanged."""
        self.assertEqual(elevation_trap.raw_value("us_feet"),
                         elevation_trap.raw_value("meters"))

    def test_nothing_in_the_response_says_which_unit_it_used(self):
        """There is no field to check. That is why this cannot be caught by
        reading the answer more carefully -- only by asking a second time."""
        body = json.loads(elevation_trap.capture_text("us_feet"))
        self.assertNotIn("unit", json.dumps(body).lower())

    def test_the_json_type_changes_between_the_two(self):
        """A float for feet, a string for everything else. A caller that does
        arithmetic on it breaks; a caller that prints it does not."""
        self.assertIsInstance(json.loads(elevation_trap.capture_text("feet"))["value"], float)
        self.assertIsInstance(json.loads(elevation_trap.capture_text("us_feet"))["value"], str)


class TestTheCoordinateSystemHasTwoNames(unittest.TestCase):
    """The ticket's own premise, still live -- and an earlier draft of this
    module said it was not, because it tested `wkid` and the research named
    `sr`. `docs/data-sources/not-used.md` had it right the whole time."""

    def test_sr_is_ignored_whatever_it_is_set_to(self):
        self.assertEqual(elevation_trap.raw_value("sr_4326"),
                         elevation_trap.raw_value("sr_3857"))

    def test_sr_makes_no_difference_at_all(self):
        """Same answer as sending no coordinate system, so it is discarded."""
        self.assertEqual(elevation_trap.raw_value("sr_4326"),
                         elevation_trap.raw_value("feet"))

    def test_wkid_by_contrast_is_honored(self):
        """Web Mercator meters, correctly declared, give the right elevation --
        which is what makes the `sr` silence a trap rather than an unsupported
        option quietly declined."""
        self.assertAlmostEqual(elevation_trap.value_of("wkid_mercator"),
                               elevation_trap.value_of("feet"), places=6)


class TestTheOtherHalfThatAtLeastBreaks(unittest.TestCase):
    """A 200 carrying plain text. Ugly, and much safer than the above."""

    def test_a_point_with_no_elevation_data_still_answers_two_hundred(self):
        self.assertEqual(elevation_trap.CAPTURES["no_data"]["http_status"],
                         elevation_trap.ALL_ANSWERED)

    def test_every_single_capture_answered_two_hundred(self):
        """That is the point of the set: not one of these is an error by the
        only test most callers apply. Re-requested and read off the wire on
        2026-09-13; a saved body carries no headers of its own."""
        statuses = {c["http_status"] for c in elevation_trap.CAPTURES.values()}
        self.assertEqual(statuses, {elevation_trap.ALL_ANSWERED})

    def test_that_answer_is_not_json_at_all(self):
        with self.assertRaises(ValueError):
            json.loads(elevation_trap.capture_text("no_data"))

    def test_a_mismatched_coordinate_system_does_the_same(self):
        with self.assertRaises(ValueError):
            json.loads(elevation_trap.capture_text("wkid_mismatch"))

    def test_the_error_text_is_never_matched_on(self):
        """`docs/data-sources/not-used.md` records this endpoint returning two
        different messages for the same condition on the same day: "Call
        failed. [Failed cloud operation...]" and "Invalid or missing input
        parameters." Matching on either is a check that stops working."""
        source = Path(elevation_trap.__file__).read_text(encoding="utf-8")
        for message in ("Call failed", "Invalid or missing input parameters",
                        "empty geometry"):
            with self.subTest(message=message):
                self.assertNotIn(f'"{message}', source)


class TestWhyTheWrongAnswerIsWorse(unittest.TestCase):
    """Acceptance criterion: "makes clear why a wrong answer is more dangerous
    than an error message." The argument is made out of the two halves above
    rather than asserted, so it has to hold for both."""

    def test_the_error_half_is_caught_by_an_ordinary_caller(self):
        """Plain text in a 200 breaks `json.loads`. Somebody finds out."""
        self.assertFalse(elevation_trap.survives_a_generic_check("no_data"))

    def test_general_care_does_not_catch_the_wrong_number(self):
        """It parses, it is the right type, it is a real elevation of real
        ground. Nothing you would write without local knowledge finds it."""
        self.assertTrue(elevation_trap.survives_a_generic_check("us_feet"))

    def test_knowing_the_county_does_catch_it(self):
        """**The correction.** An earlier version claimed nothing at the point
        of the call could catch this, on the strength of a range written as
        `0 < feet < 5000` above a comment saying Bexar runs 400 to 2,000. The
        two disagreed and the wider one was doing the work.

        264.22 is below the county floor. A caller who checks against this
        county catches it, and that check needed somebody who knew the ground."""
        self.assertFalse(elevation_trap.survives_a_local_check("us_feet"))

    def test_the_right_answer_passes_both(self):
        """Otherwise the local check is just a stricter filter, not a test."""
        self.assertTrue(elevation_trap.survives_a_generic_check("feet"))
        self.assertTrue(elevation_trap.survives_a_local_check("feet"))

    def test_the_beat_says_so_in_one_sentence(self):
        self.assertIn(elevation_trap.VERDICT, elevation_trap.beat())
        self.assertEqual(elevation_trap.VERDICT.count("."), 1)


class TestTheBeatOnAProjector(unittest.TestCase):

    def setUp(self):
        self.said = elevation_trap.beat()

    def test_both_numbers_are_on_it_together(self):
        """Criterion: "The plausible-but-wrong answer is visible next to the
        right one." Next to, not on the following slide."""
        self.assertIn("866.8668528742528", self.said)
        self.assertIn("264.221008301", self.said)

    def test_it_names_the_one_word_that_differs(self):
        self.assertIn("US_Feet", self.said)
        self.assertIn("Feet", self.said)

    def test_it_says_when_this_was_checked(self):
        self.assertIn(elevation_trap.CHECKED_ON, self.said)

    # Printing on a borrowed podium laptop -- the console that killed beat one
    # -- is checked in `tests/test_beats.py` under issue #67, over every module
    # that renders a beat rather than over this one. `beats.render` also refuses
    # a non-ASCII character outright, so it now fails when somebody runs the
    # beat rather than only when somebody runs the suite.


class TestItRunsWithTheNetworkActuallyGone(unittest.TestCase):
    """Criterion two, proven at the socket rather than asserted."""

    def test_the_whole_beat_builds_with_every_network_door_refused(self):
        with no_network():
            said = elevation_trap.beat()
        self.assertIn("264.221008301", said)


class TestTheEvidenceIsCommittedAndTraceable(unittest.TestCase):

    def test_every_capture_the_record_names_is_on_disk(self):
        for name, capture in elevation_trap.CAPTURES.items():
            with self.subTest(capture=name):
                self.assertTrue((elevation_trap.CAPTURE_DIR / capture["file"]).is_file())

    def test_every_capture_records_the_exact_request_it_came_from(self):
        """A capture nobody can repeat is not evidence."""
        for name, capture in elevation_trap.CAPTURES.items():
            with self.subTest(capture=name):
                self.assertTrue(capture["url"].startswith("https://epqs.nationalmap.gov/"))

    # The committed rendering, held to what `beat()` produces today, is checked
    # in `tests/test_beats.py` under issue #67 -- over every beat, and through
    # `cache.long_path`, which the copy that stood here was not. That is the
    # same miss issue #76 found in `manual_links.capture_text`: it would have
    # failed on a checkout whose paths run past 260 characters, which this
    # repo's own worktrees already do.


if __name__ == "__main__":
    unittest.main()
