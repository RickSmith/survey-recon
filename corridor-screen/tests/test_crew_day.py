"""Tests for the crew-day build-up.

This is the output a room of firm owners will argue with, and issue #24 says
that is the point: "showing the math is what makes it credible." So the tests
here are about the four ways a build-up stops being arguable.

**A rate with no name on it.** Every hours-per-thing figure in this build-up is
somebody's assumption, not a published standard. An assumption that does not
say it is one reads as a fact, and a room cannot argue with a fact it has been
handed. The table refuses to load a rate that will not say where it came from.

**An invented TxDOT requirement.** CLAUDE.md: "Never invent a TxDOT
requirement. Cite the manual section and its URL, or say you could not confirm
it." A rate table is exactly where a plausible-sounding "TxDOT requires" would
slip in, so a row whose source names TxDOT has to carry the URL and the date
somebody read it, and may not be marked as an assumption.

**A count nobody measured, printed as a number.** The run does not count
manholes or culverts. Issue #24 asks for them anyway, because "popping manholes
and closing lanes is where time goes." So the arithmetic is wired up and the
quantity is absent -- that line reports no hours at all, rather than reporting
zero.

**Field hours and office hours added together.** A crew-day is a crew standing
on a road. Hand retracement of 69 scanned ROW sheets is real time and real
money and it is not a crew-day, and one total covering both would be quoted as
though it were.
"""

import json
import tempfile
import unittest
from pathlib import Path

from corridor_screen import crew_day

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "project-sh16"


def a_document(**overrides):
    """A screening document, in the shape ``output.build`` produces.

    The numbers are SH16's, so a test that reads wrong reads wrong against the
    corridor the whole repo is about.
    """
    document = {
        "schema_version": "0.1.0",
        "run": {
            "run_id": "texas-bexar-sh0016-kg-20260913T070646",
            "finished_at": "2026-09-13T07:07:31-05:00",
            "status": "complete",
            "mode": "live",
            "tool_version": "0.1.0",
            "half_width_ft": 300,
            "screened_for": ["cemetery", "pipeline", "railroad", "school"],
        },
        "alignment": {
            "source_path": "SH0016-KG DFO 347.7 to 356.367",
            "length_mi": 8.691,
        },
        "roadway": {
            "status": "not-screened",
            "detail": "existing right-of-way width, lane count and traffic were not read",
        },
        "control": {
            "recovery_risk": {
                "marks_in_corridor": 11,
                "mark_not_found": 11,
                "condition_unknown": 0,
            },
            "txdot_control": {"points_in_corridor": 4, "distinct_stations": 2},
        },
        "row_maps": {"sheet_count": 69},
        "parcels": [
            {"id": "1", "flags": []},
            {"id": "2", "flags": [{"type": "cemetery", "relation": "on"}]},
        ],
    }
    document.update(overrides)
    return document


def a_rate(**overrides):
    """One well-formed row of the rate table."""
    row = {
        "label": "Hours per tract",
        "value": 0.5,
        "unit": "hours per tract",
        "kind": "field",
        "assumption": True,
        "source": "Assumption. No published figure was used.",
        "why": "Corner recovery on one tract, from a setup already made.",
        "disagree_with": "Urban lots share corners; halve this and the total moves most.",
    }
    row.update(overrides)
    return row


class TestTheRateTableRefusesWhatCannotBeArguedWith(unittest.TestCase):
    """A rate nobody can attribute is a number with no owner.

    The same shape as ``lead_times._check``: a configuration mistake costs
    nothing to catch before a run and a great deal after, and this table is
    read by people who will quote it.
    """

    def test_a_row_without_a_source_is_refused(self):
        with self.assertRaises(crew_day.CrewRateTableError):
            crew_day.load_rates(rows={"x": a_rate(source="")})

    def test_a_row_without_a_why_is_refused(self):
        with self.assertRaises(crew_day.CrewRateTableError):
            crew_day.load_rates(rows={"x": a_rate(why="")})

    def test_an_assumption_must_say_what_to_argue_with(self):
        with self.assertRaises(crew_day.CrewRateTableError) as caught:
            crew_day.load_rates(rows={"x": a_rate(disagree_with="")})
        self.assertIn("disagree_with", str(caught.exception))

    def test_a_rate_of_an_unknown_kind_is_refused(self):
        with self.assertRaises(crew_day.CrewRateTableError):
            crew_day.load_rates(rows={"x": a_rate(kind="whenever")})

    def test_a_rate_that_is_not_a_positive_number_is_refused(self):
        for bad in (0, -1, None, "half an hour"):
            with self.subTest(value=bad):
                with self.assertRaises(crew_day.CrewRateTableError):
                    crew_day.load_rates(rows={"x": a_rate(value=bad)})

    def test_a_table_with_no_rows_is_refused(self):
        with self.assertRaises(crew_day.CrewRateTableError):
            crew_day.load_rates(rows={})


class TestItCannotInventATxdotRequirement(unittest.TestCase):
    """CLAUDE.md's accuracy rule, made structural rather than remembered.

    A rate table is where "TxDOT requires two hours per setup" would arrive
    wearing a tie. The loader will not accept one without the section and the
    URL somebody actually opened.
    """

    def test_a_source_naming_txdot_may_not_be_an_assumption(self):
        with self.assertRaises(crew_day.CrewRateTableError) as caught:
            crew_day.load_rates(rows={"x": a_rate(
                source="TxDOT standard sheet TCP(S-1)-08A",
                url="https://www.txdot.gov/manuals/row/ess/index.htm",
                verified_on="2026-09-13",
            )})
        self.assertIn("assumption", str(caught.exception))

    def test_a_source_naming_txdot_must_carry_a_url_and_a_date(self):
        with self.assertRaises(crew_day.CrewRateTableError) as caught:
            crew_day.load_rates(rows={"x": a_rate(
                source="TxDOT standard sheet TCP(S-1)-08A",
                assumption=False,
            )})
        self.assertIn("url", str(caught.exception))

    def test_a_confirmed_txdot_row_with_its_citation_loads(self):
        table = crew_day.load_rates(rows={"x": a_rate(
            source="TxDOT standard sheet TCP(S-1)-08A, Note 2",
            assumption=False,
            disagree_with=None,
            url="https://www.txdot.gov/manuals/row/ess/index.htm",
            verified_on="2026-09-13",
        )})
        self.assertFalse(table["x"].assumption)

    def test_the_committed_table_never_cites_the_superseded_host(self):
        """`onlinemanuals.txdot.gov` is the trap this session demonstrates."""
        for rate in crew_day.load_rates().values():
            self.assertNotIn("onlinemanuals", (rate.url or "").lower())


class TestTheCommittedRateTable(unittest.TestCase):
    """The table shipped in this repo, held to its own rules."""

    def setUp(self):
        self.rates = crew_day.load_rates()

    def test_it_loads(self):
        self.assertTrue(self.rates)

    def test_every_rate_the_build_up_asks_for_is_in_it(self):
        for key in crew_day.RATES_USED:
            self.assertIn(key, self.rates)

    def test_every_assumption_says_what_to_argue_with(self):
        for key, rate in self.rates.items():
            if rate.assumption:
                with self.subTest(rate=key):
                    self.assertTrue(rate.disagree_with)


class TestEveryInputIsVisibleAndLabelled(unittest.TestCase):
    """Issue #24's first acceptance criterion, taken literally.

    Every quantity the arithmetic uses is listed with a label, a unit and the
    place in ``screening.json`` it was read from -- so a reader can check one
    without reading the code.
    """

    def setUp(self):
        self.counts = crew_day.counts(a_document())

    def test_each_count_says_where_it_came_from(self):
        for count in self.counts:
            with self.subTest(count=count["key"]):
                self.assertTrue(count["label"])
                self.assertTrue(count["unit"])
                self.assertTrue(count["source"])

    def test_the_corridor_length_is_read_from_the_run(self):
        length = next(c for c in self.counts if c["key"] == "corridor_miles")
        self.assertEqual(length["value"], 8.691)
        self.assertTrue(length["measured"])

    def test_the_tract_count_is_read_from_the_run(self):
        tracts = next(c for c in self.counts if c["key"] == "tracts")
        self.assertEqual(tracts["value"], 2)


class TestACountNobodyMeasuredNeverBecomesANumber(unittest.TestCase):
    """The rule this repo repeats everywhere: unknown is not no.

    Issue #24 asks for manhole and culvert counts, "since popping manholes and
    closing lanes is where time goes." No service in this run publishes either.
    A zero there would price the single most expensive thing on the job at
    nothing, on the page a principal reads first.
    """

    def setUp(self):
        self.counts = {c["key"]: c for c in crew_day.counts(a_document())}

    def test_manholes_are_reported_unmeasured_rather_than_zero(self):
        self.assertIsNone(self.counts["manholes"]["value"])
        self.assertFalse(self.counts["manholes"]["measured"])

    def test_culverts_are_reported_unmeasured_rather_than_zero(self):
        self.assertIsNone(self.counts["culverts"]["value"])
        self.assertFalse(self.counts["culverts"]["measured"])

    def test_an_unmeasured_count_says_why_nobody_measured_it(self):
        for key in ("manholes", "culverts"):
            with self.subTest(count=key):
                self.assertTrue(self.counts[key]["why_not"])

    def test_the_road_occupation_line_reports_no_hours_at_all(self):
        line = next(line for line in crew_day.lines(a_document())
                    if line["key"] == "road_occupations")
        self.assertIsNone(line["hours"])
        self.assertTrue(line["blocked_by"])

    def test_a_blocked_line_is_not_counted_into_the_total(self):
        lines = crew_day.lines(a_document())
        hours, blocked = crew_day.hours_for("field", lines)
        self.assertTrue(blocked)
        self.assertEqual(
            round(hours, 2),
            round(sum(line["hours"] for line in lines
                      if line["kind"] == "field" and line["hours"] is not None), 2),
        )


class TestTheMathIsShownStepByStep(unittest.TestCase):
    """Issue #24: "The math is shown step by step, not just the total."

    A line is a chain of factors and their product. That is what lets the
    Markdown print `8.691 miles x 0.5 pairs per mile x 3.0 hours per pair`
    instead of a number somebody has to take on trust.
    """

    def setUp(self):
        self.lines = crew_day.lines(a_document())

    def test_every_line_carries_its_factors(self):
        for line in self.lines:
            with self.subTest(line=line["key"]):
                self.assertGreaterEqual(len(line["factors"]), 2)

    def test_every_factor_says_where_it_came_from(self):
        for line in self.lines:
            for factor in line["factors"]:
                with self.subTest(line=line["key"], factor=factor["label"]):
                    self.assertTrue(factor["label"])
                    self.assertTrue(factor["unit"])
                    self.assertTrue(factor["source"])

    def test_the_hours_on_a_line_are_the_product_of_its_factors(self):
        for line in self.lines:
            if line["hours"] is None:
                continue
            product = 1.0
            for factor in line["factors"]:
                product *= factor["value"]
            with self.subTest(line=line["key"]):
                self.assertAlmostEqual(line["hours"], round(product, 2), places=2)

    def test_the_markdown_prints_the_arithmetic_and_not_only_the_answer(self):
        said = crew_day.build(a_document())
        self.assertIn("8.691", said)
        self.assertIn("x", said)


class TestFieldDaysAndOfficeDaysAreNeverAddedTogether(unittest.TestCase):
    """A crew-day is a crew standing on a road.

    Hand retracement of scanned ROW sheets is real time and real money, and it
    is not a crew-day. One total covering both would be quoted as though it
    were, by the person least able to tell the difference.
    """

    def setUp(self):
        self.lines = crew_day.lines(a_document())

    def test_every_line_is_field_or_office(self):
        for line in self.lines:
            with self.subTest(line=line["key"]):
                self.assertIn(line["kind"], ("field", "office"))

    def test_the_two_totals_are_separate(self):
        field, _ = crew_day.hours_for("field", self.lines)
        office, _ = crew_day.hours_for("office", self.lines)
        self.assertGreater(field, 0)
        self.assertGreater(office, 0)
        self.assertNotEqual(field, office)

    def test_the_markdown_never_prints_one_combined_day_count(self):
        said = crew_day.build(a_document()).lower()
        self.assertNotIn("total days", said)
        self.assertIn("field", said)
        self.assertIn("office", said)


class TestDaysRoundUp(unittest.TestCase):
    """Half a day in the field is a day. Nobody sends a crew home at noon.

    Rounding down is the quiet way an estimate becomes optimistic, and it does
    it once per line rather than once per estimate.
    """

    def test_a_part_day_becomes_a_whole_day(self):
        self.assertEqual(crew_day.days(8.25, 8.0), 2)

    def test_an_exact_day_stays_one_day(self):
        self.assertEqual(crew_day.days(8.0, 8.0), 1)

    def test_no_hours_is_no_days_rather_than_one(self):
        self.assertEqual(crew_day.days(0, 8.0), 0)


class TestTrafficControlComesFromTheSheetAndNotFromMemory(unittest.TestCase):
    """Issue #24: "Traffic control from TCP(S-1)-08A is factored in."

    Every claim below is checked against `project-sh16/manual-pulls/
    tcp-s-1-08a.md`, which was read with the sheet open. The wrong version of
    this paragraph lived in this repo for a day and is the reason these are
    tests rather than prose.
    """

    def setUp(self):
        self.said = crew_day.build(a_document())

    def test_the_one_hour_duration_line_is_stated(self):
        self.assertIn("one hour", self.said.lower())

    def test_the_sheet_is_named(self):
        self.assertIn("TCP(S-1)-08A", self.said)

    def test_note_3_is_stated_because_sighting_a_line_is_the_job(self):
        self.assertIn("Note 3", self.said)

    def test_it_never_claims_a_posted_speed_triggers_a_shadow_truck(self):
        """The soundbite this repo carried for a day, and had to withdraw.

        "A 20-minute shot on a 55-mph highway converts a two-person crew into a
        crew plus shadow truck" was read across from the mobile-operations
        standard TCP(3-1) because TCP(S-1) could not be fetched. Not found on
        any of the six sheets: 55 mph is an ordinary row in every spacing table.

        The document is allowed to *deny* it -- that denial is worth printing.
        It may not assert it.
        """
        lowered = self.said.lower()
        self.assertIn("no posted speed", lowered)
        self.assertNotIn("converts a two-person crew", lowered)
        self.assertNotIn("20-minute", lowered)

    def test_it_says_a_lane_closure_is_a_different_sheet(self):
        """S-1 draws only the two shoulder cases. A manhole in a travel lane is
        S-2 or S-3 work, and those are the sheets that draw a shadow vehicle."""
        self.assertIn("TCP(S-3)", self.said)

    def test_it_says_the_family_does_not_cover_freeways(self):
        self.assertIn("Conventional Roads Only", self.said)


class TestAssumptionsCanBeDisagreedWithOneAtATime(unittest.TestCase):
    """Issue #24: "Assumptions are stated so a surveyor can disagree with a
    specific one."

    A block of prose saying "rates are estimates" cannot be argued with. A
    numbered row saying `A3  0.5 hours per tract` can, and the number is what
    somebody says out loud in a room.
    """

    def setUp(self):
        self.said = crew_day.build(a_document())

    def test_each_assumption_carries_a_handle_somebody_can_say_out_loud(self):
        for index in range(1, len(crew_day.RATES_USED) + 1):
            with self.subTest(handle=f"A{index}"):
                self.assertIn(f"A{index}", self.said)

    def test_each_assumption_prints_what_to_argue_with(self):
        for rate in crew_day.load_rates().values():
            if rate.assumption and rate.key in crew_day.RATES_USED:
                with self.subTest(rate=rate.key):
                    self.assertIn(rate.disagree_with, self.said)

    def test_the_build_up_says_the_rates_are_nobodys_published_standard(self):
        self.assertIn("not a published", self.said.lower())


class TestItSaysWhatItIsNot(unittest.TestCase):
    """The same closing discipline as the bid memo and the parcel table.

    This is the output most likely to be forwarded with the caveats trimmed
    off, so the caveats are on the face of it.
    """

    def setUp(self):
        self.said = crew_day.build(a_document())

    def test_it_says_nobody_has_walked_the_corridor(self):
        self.assertIn("walked", self.said.lower())

    def test_it_says_the_rpls_decides(self):
        self.assertIn("RPLS", self.said)

    def test_an_incomplete_run_is_said_at_the_top(self):
        """On the face of it, not in an appendix somebody scrolls past."""
        document = a_document()
        document["run"]["status"] = "stopped"
        head = "\n".join(crew_day.build(document).splitlines()[:6])
        self.assertIn("stopped", head)


class TestItSurvivesTheLaptopItWillActuallyRunOn(unittest.TestCase):
    """The console summary at 1:18, on a machine somebody else set up.

    Beat one shipped with an em dash and a `UnicodeEncodeError` on a default
    Windows console. That was caught by review rather than by anything running,
    which is issue #67's whole complaint. Until that seam exists, this is the
    check for this module.
    """

    def test_the_summary_prints_on_a_console_that_only_speaks_ascii(self):
        for console in ("cp437", "cp1252", "ascii"):
            with self.subTest(console=console):
                crew_day.summary(a_document()).encode(console)


class TestTheFallbackARunCanBeReadFrom(unittest.TestCase):
    """Issue #24's last criterion: "A fallback capture is recorded as the work
    happens."

    Not a separate recording session -- issue #27 is blunt that it audits
    captures rather than making them. So the console rendering is written to
    disk on every run, beside the Markdown, and pinned to the code by this
    test. A presenter whose Python will not start opens a text file.
    """

    def test_the_summary_carries_both_totals_and_the_missing_one(self):
        said = crew_day.summary(a_document())
        self.assertIn("field", said.lower())
        self.assertIn("office", said.lower())
        self.assertIn("not measured", said.lower())

    def test_writing_produces_the_document_and_the_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            written = crew_day.write(a_document(), folder)
            names = sorted(Path(p).name for p in written)
            self.assertEqual(names, [crew_day.BUILD_UP_NAME, crew_day.FALLBACK_NAME])


class TestAgainstTheRealRun(unittest.TestCase):
    """The committed SH16 capture, which is the one that goes on the screen.

    The headline numbers are pinned here on purpose. A rate edited in the TOML
    changes them, and it should: the point of this test is that nobody changes
    what a room is told the job costs without the change showing up in a diff
    somebody reviews.
    """

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
        cls.rates = crew_day.load_rates()
        cls.lines = crew_day.lines(cls.document, cls.rates)

    def test_the_field_total_is_thirty_eight_crew_days(self):
        hours, _ = crew_day.hours_for("field", self.lines)
        self.assertEqual(hours, 299.29)
        self.assertEqual(
            crew_day.days(hours, self.rates["field_hours_per_crew_day"].value), 38)

    def test_the_office_total_is_eighteen_days(self):
        hours, _ = crew_day.hours_for("office", self.lines)
        self.assertEqual(hours, 138.26)
        self.assertEqual(
            crew_day.days(hours, self.rates["office_hours_per_day"].value), 18)

    def test_the_biggest_line_is_the_524_tracts(self):
        """Named in the build-up as the first thing to argue with."""
        line = next(x for x in self.lines if x["key"] == "tract_corners")
        self.assertEqual(line["factors"][0]["value"], 524)
        self.assertEqual(line["hours"], 262.0)

    def test_the_traffic_control_line_still_has_no_total_on_the_real_run(self):
        line = next(x for x in self.lines if x["key"] == "road_occupations")
        self.assertIsNone(line["hours"])

    def test_the_field_total_is_reported_as_a_floor(self):
        said = crew_day.build(self.document, self.rates)
        self.assertIn("floor", said)

    def test_the_committed_build_up_is_what_the_code_produces_today(self):
        """Otherwise it is a file that silently stops matching the code that
        made it -- the same check the failure beats and `screening.json` get."""
        written = (DEMO / crew_day.BUILD_UP_NAME).read_text(encoding="utf-8")
        self.assertEqual(written.replace("\r\n", "\n"),
                         crew_day.build(self.document, self.rates))

    def test_the_committed_fallback_is_what_the_code_produces_today(self):
        written = (DEMO / crew_day.FALLBACK_NAME).read_text(encoding="utf-8")
        self.assertEqual(written.replace("\r\n", "\n"),
                         crew_day.summary(self.document, self.rates))


if __name__ == "__main__":
    unittest.main()
