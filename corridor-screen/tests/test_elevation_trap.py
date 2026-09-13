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
surveyor calls the unit they work in**, the one EPSG numbers 9003 and the one
the TxDOT survey specification is written in.

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


class TestTheOtherHalfThatAtLeastBreaks(unittest.TestCase):
    """A 200 carrying plain text. Ugly, and much safer than the above."""

    def test_a_point_with_no_elevation_data_still_answers_two_hundred(self):
        self.assertEqual(elevation_trap.CAPTURES["no_data"]["http_status"], 200)

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
        self.assertFalse(elevation_trap.survives_a_careful_caller("no_data"))

    def test_the_wrong_number_half_is_not(self):
        """It parses, it is the right type of thing, it is in range. Nothing a
        caller can do at the point of the call will catch it."""
        self.assertTrue(elevation_trap.survives_a_careful_caller("us_feet"))

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

    def test_it_prints_on_a_console_that_only_speaks_ascii(self):
        """A borrowed podium laptop. Beat one died here first."""
        for console in ("cp437", "cp1252", "ascii"):
            with self.subTest(console=console):
                self.said.encode(console)


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

    def test_the_committed_rendering_is_what_the_code_produces_today(self):
        path = elevation_trap.CAPTURE_DIR / elevation_trap.BEAT_NAME
        with open(path, encoding="utf-8", newline="") as handle:
            written = handle.read()
        self.assertEqual(written.replace("\r\n", "\n"), elevation_trap.beat() + "\n")


if __name__ == "__main__":
    unittest.main()
