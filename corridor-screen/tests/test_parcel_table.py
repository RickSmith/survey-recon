"""Tests for the flagged parcel table -- the second of the three renderings.

Specification section 2: "It does not produce the bid memo, the parcel table,
or the crew-day build-up. Those are separate jobs that read this file. **One
fetch, many renderings.**"

This one goes on a projector at 1:18, which is the only reason it is not simply
the bid memo with a table in it. Issue #23 asks for something "readable from the
back of a conference room" that "fits on screen without scrolling," and
specification section 9 already answered how this repo does that: SVG, because
it "stays sharp on a projector at any size" and commits to git as text.

**The hard part of this table is not the layout. It is the column that has no
number in it.** Seven of the eight flagged parcels on SH16 carry a school flag,
and `docs/corridor-screen/lead-times.md` is deliberate that no number of days
was found for one: "It is not reported as clear. It is reported as unmeasured,
which is a different thing." A blank cell, a dash or a zero in that column would
undo that on the biggest screen in the room.
"""

import json
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from corridor_screen import parcel_table

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "project-sh16"


def a_parcel(**over):
    """One flagged parcel, shaped the way a run writes it."""
    row = {
        "id": "19142-001-0010",
        "owner": "MEHAT PROPERTIES LLC",
        "situs": "10402 BANDERA RD, SAN ANTONIO, TX 78250",
        "legal_acres": 0.556,
        "property_use": "F1",
        "screened_for": ["cemetery", "pipeline", "railroad", "school"],
        "flags": [],
        "max_lead_time_days": None,
        "max_lead_time_basis": None,
        "lead_time_driver": None,
        "lead_time_not_found": [],
        "warnings": [],
    }
    row.update(over)
    return row


def a_flag(**over):
    flag = {
        "type": "school", "relation": "on", "distance_ft": None,
        "name": "Carl Wanke Elementary School", "screenable": True,
        "lead_time_days": None, "lead_time_days_low": None,
        "lead_time_basis": None, "lead_time_statutory": False,
        "lead_time_source": "Tex. Educ. Code § 22.0834 — background checks, "
                            "which is not a notice period",
        "lead_time_url": "https://statutes.capitol.texas.gov/Docs/ED/htm/ED.22.htm",
    }
    flag.update(over)
    return flag


A_CEMETERY = a_flag(
    type="cemetery", lead_time_days=14, lead_time_basis="calendar days",
    lead_time_statutory=True, name="Episcopal Church of the Holy Spirit Columbarium",
    lead_time_source="Tex. Health & Safety Code § 711.041(c)(2)",
    lead_time_url="https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm",
)


def a_document(parcels, **over):
    document = {
        "run": {
            "status": "complete", "mode": "live", "area": "texas-bexar",
            "finished_at": "2026-09-13T07:07:07-05:00",
            "half_width_ft": 300, "adjacent_distance_ft": 100,
            "screened_for": ["cemetery", "pipeline", "railroad", "school"],
            "lead_times": {
                "cemetery": {
                    "label": "Cemetery", "lead_time_days": 14,
                    "lead_time_basis": "calendar days", "confirmed": True,
                    "statutory": True, "not_found": None,
                    "source": "Tex. Health & Safety Code § 711.041(c)(2)",
                    "url": "https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm",
                },
                "school": {
                    "label": "School", "lead_time_days": None,
                    "lead_time_basis": None, "confirmed": False, "statutory": False,
                    "source": "Tex. Educ. Code § 22.0834 — background checks, "
                              "which is not a notice period",
                    "url": "https://statutes.capitol.texas.gov/Docs/ED/htm/ED.22.htm",
                    "not_found": "Not found: no published number of days.",
                },
            },
            "not_screenable": [
                {"type": "gated access", "reason": "no public source publishes them"},
            ],
        },
        "alignment": {"source_path": "SH0016-KG DFO 347.7 to 356.367", "length_mi": 8.69},
        "parcels": parcels,
        "corridor_flags": [],
        "warnings": [],
    }
    document.update(over)
    return document


class TestWhichParcelsMakeTheTable(unittest.TestCase):
    """A flagged parcel table is not a parcel table."""

    def test_a_parcel_with_no_flag_is_not_a_row(self):
        rows = parcel_table.rows(a_document([a_parcel(), a_parcel(id="x", flags=[a_flag()])]))
        self.assertEqual([r["id"] for r in rows], ["x"])

    def test_every_flagged_parcel_is_a_row(self):
        many = [a_parcel(id=f"p{n}", flags=[a_flag()]) for n in range(8)]
        self.assertEqual(len(parcel_table.rows(a_document(many))), 8)


class TestTheOrderPutsTheWorkThatStartsSoonestOnTop(unittest.TestCase):
    """The table's job is to say which tract to start on today.

    A parcel whose wait nobody has measured needs a phone call before a parcel
    whose wait is a known 14 days, because the call is what turns the unknown
    into a date. So unmeasured sorts above measured, and measured sorts longest
    first. Sorting the unknowns to the bottom would read as "these are the easy
    ones," which is the exact inversion this repo exists to prevent.
    """

    def test_an_unmeasured_wait_sorts_above_a_known_one(self):
        document = a_document([
            a_parcel(id="known", flags=[A_CEMETERY], max_lead_time_days=14,
                     max_lead_time_basis="calendar days", lead_time_driver="cemetery"),
            a_parcel(id="unmeasured", flags=[a_flag()], lead_time_not_found=["school"]),
        ])
        self.assertEqual([r["id"] for r in parcel_table.rows(document)],
                         ["unmeasured", "known"])

    def test_a_longer_known_wait_sorts_above_a_shorter_one(self):
        document = a_document([
            a_parcel(id="short", flags=[A_CEMETERY], max_lead_time_days=14),
            a_parcel(id="long", flags=[A_CEMETERY], max_lead_time_days=45),
        ])
        self.assertEqual([r["id"] for r in parcel_table.rows(document)], ["long", "short"])

    def test_the_order_is_stable_when_two_parcels_tie(self):
        document = a_document([
            a_parcel(id="b", flags=[A_CEMETERY], max_lead_time_days=14),
            a_parcel(id="a", flags=[A_CEMETERY], max_lead_time_days=14),
        ])
        self.assertEqual([r["id"] for r in parcel_table.rows(document)], ["a", "b"])


class TestTheColumnWithNoNumberInIt(unittest.TestCase):
    """Seven of the eight SH16 rows land here. It is the whole table."""

    def test_a_confirmed_wait_prints_its_number_and_its_basis(self):
        cell = parcel_table.wait_cell(
            a_parcel(max_lead_time_days=14, max_lead_time_basis="calendar days",
                     lead_time_driver="cemetery", flags=[A_CEMETERY])
        )
        self.assertIn("14", cell)
        self.assertIn("calendar days", cell)

    def test_a_bare_number_is_never_printed_without_its_basis(self):
        """"2 working days" and "2 calendar days" are different promises."""
        cell = parcel_table.wait_cell(
            a_parcel(max_lead_time_days=2, max_lead_time_basis="working days",
                     lead_time_driver="pipeline",
                     flags=[a_flag(type="pipeline", lead_time_days=2,
                                   lead_time_basis="working days")])
        )
        self.assertIn("working days", cell)

    def test_an_unmeasured_wait_says_not_found_and_never_a_number(self):
        cell = parcel_table.wait_cell(
            a_parcel(flags=[a_flag()], lead_time_not_found=["school"])
        )
        self.assertIn("not found", cell.lower())
        self.assertNotIn("0", cell)

    def test_an_unmeasured_wait_names_the_flag_nobody_could_price(self):
        """So a reader knows who to ring, not just that a call is needed."""
        cell = parcel_table.wait_cell(
            a_parcel(flags=[a_flag()], lead_time_not_found=["school"])
        )
        self.assertIn("school", cell)

    def test_a_tract_with_both_a_number_and_an_unknown_shows_both(self):
        """`docs/corridor-screen/lead-times.md`: a parcel with a cemetery and a
        school shows 14 days **and** `school` in the not-found list, "because 14
        is the longest number anybody can stand behind and it is not the whole
        answer."

        The first draft returned the number and dropped the unknown, which is
        the same `unknown`-reported-as-`no` inversion the rest of this file is
        built to prevent. No SH16 parcel carries both, so the real run could
        never have caught it.
        """
        cell = parcel_table.wait_cell(a_parcel(
            flags=[A_CEMETERY, a_flag()], max_lead_time_days=14,
            max_lead_time_basis="calendar days", lead_time_driver="cemetery",
            lead_time_not_found=["school"],
        ))
        self.assertIn("14", cell)
        self.assertIn("school", cell)

    def test_the_cell_is_never_empty_and_never_a_dash(self):
        for parcel in (a_parcel(flags=[a_flag()]),
                       a_parcel(flags=[a_flag()], lead_time_not_found=["school"]),
                       a_parcel(flags=[A_CEMETERY], max_lead_time_days=14,
                                max_lead_time_basis="calendar days")):
            with self.subTest(parcel=parcel["id"]):
                cell = parcel_table.wait_cell(parcel).strip()
                self.assertTrue(cell)
                self.assertNotIn(cell, ("-", "--", "—", "0", "n/a"))


class TestEveryNumberCarriesItsCitation(unittest.TestCase):
    """CLAUDE.md: "Numbers with legal consequence -- accuracy tolerances, notice
    periods, fees -- get a source link next to them."
    `docs/corridor-screen/lead-times.md` puts it harder: "a lead time is worth
    exactly what its citation is worth."

    The first draft of this table printed "14 calendar days" in both files and
    cited it in neither -- the one confirmed statutory figure in the whole run
    was the one number with no source beside it, and on the projector it was
    bare. The same miss had already been caught once, on #22.
    """

    def _markdown(self):
        return parcel_table.build(a_document([
            a_parcel(id="cem", flags=[A_CEMETERY], max_lead_time_days=14,
                     max_lead_time_basis="calendar days", lead_time_driver="cemetery"),
            a_parcel(id="sch", flags=[a_flag()], lead_time_not_found=["school"]),
        ]))

    def test_the_statutory_number_carries_its_section(self):
        self.assertIn("711.041(c)(2)", self._markdown())

    def test_the_statutory_number_carries_a_link_that_can_be_followed(self):
        self.assertIn("https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm",
                      self._markdown())

    def test_a_not_found_carries_where_it_looked(self):
        """"Not found" without where you looked is not a finding."""
        self.assertIn("22.0834", self._markdown())

    def test_the_projector_shows_the_source_of_every_number_on_it(self):
        """A URL cannot be read from the back of a room, but a section number
        can, and a number with no source beside it is the thing this repo
        exists to stop people quoting."""
        drawn = parcel_table.svg(a_document([
            a_parcel(id="cem", flags=[A_CEMETERY], max_lead_time_days=14,
                     max_lead_time_basis="calendar days", lead_time_driver="cemetery"),
        ]))
        self.assertIn("711.041(c)(2)", drawn)

    def test_only_the_types_actually_on_the_table_are_cited(self):
        """A citation list carrying railroads a corridor does not have is noise."""
        self.assertNotIn("up.com", self._markdown())


class TestTheFlagsColumn(unittest.TestCase):
    def test_it_says_whether_the_feature_is_on_the_tract_or_beside_it(self):
        """"On" and "adjacent" are different jobs. One of them needs a ROE."""
        cell = parcel_table.flag_cell(a_parcel(flags=[a_flag(relation="adjacent",
                                                            distance_ft=71.8)]))
        self.assertIn("adjacent", cell.lower())

    def test_two_flags_on_one_parcel_both_appear(self):
        cell = parcel_table.flag_cell(a_parcel(flags=[a_flag(), A_CEMETERY]))
        self.assertIn("school", cell.lower())
        self.assertIn("cemetery", cell.lower())


class TestNothingFoundIsDropped(unittest.TestCase):
    """The mistake #22 caught, kept caught."""

    def test_a_corridor_wide_flag_is_reported_even_though_it_has_no_parcel(self):
        document = a_document(
            [a_parcel(id="x", flags=[a_flag()])],
            corridor_flags=[{"type": "pipeline", "name": "Valero Crude",
                             "parcels_crossed": 40, "lead_time_days": 2,
                             "lead_time_basis": "working days"}],
        )
        built = parcel_table.build(document)
        self.assertIn("Valero Crude", built)

    def test_a_type_that_was_never_screened_for_is_named(self):
        """A type missing from `screened_for` is unknown, never clear."""
        document = a_document([a_parcel(id="x", flags=[a_flag()])])
        document["run"]["screened_for"] = ["school"]
        built = parcel_table.build(document)
        self.assertIn("cemetery", built.lower())

    def test_an_incomplete_run_says_so_rather_than_looking_finished(self):
        document = a_document([a_parcel(id="x", flags=[a_flag()])])
        document["run"]["status"] = "incomplete"
        self.assertIn("incomplete", parcel_table.build(document).lower())

    def test_the_incomplete_warning_is_not_a_mkdocs_admonition(self):
        """This file is read on GitHub, where `!!! warning` comes out as
        literal text and an indented code block. `bid_memo` refuses it for
        exactly this reason and says so in a comment."""
        document = a_document([a_parcel(id="x", flags=[a_flag()])])
        document["run"]["status"] = "incomplete"
        self.assertNotIn("!!!", parcel_table.build(document))

    def test_the_flag_types_come_from_the_source_list_not_a_copy_of_it(self):
        """A fifth flag type must not be silently reported as screened."""
        from corridor_screen.sources import FLAG_SOURCES
        document = a_document([a_parcel(id="x", flags=[a_flag()])])
        document["run"]["screened_for"] = []
        built = parcel_table.build(document).lower()
        for _source, kind in FLAG_SOURCES:
            self.assertIn(kind, built)


class TestItFitsOnAScreen(unittest.TestCase):
    """Acceptance criterion: no scrolling during the demo."""

    def test_exactly_the_rows_that_fit_are_drawn_and_no_more(self):
        many = [a_parcel(id=f"p{n}", flags=[a_flag()]) for n in range(200)]
        drawn = parcel_table.svg(a_document(many))
        self.assertEqual(sum(1 for n in range(200) if f">p{n}<" in drawn),
                         parcel_table.ROWS_ON_SCREEN)

    def test_a_capped_table_says_how_many_it_did_not_draw(self):
        """Silently showing 10 of 200 is the quiet wrong answer on a projector."""
        many = [a_parcel(id=f"p{n}", flags=[a_flag()]) for n in range(200)]
        drawn = parcel_table.svg(a_document(many))
        self.assertIn(str(200 - parcel_table.ROWS_ON_SCREEN), drawn)

    def test_the_markdown_never_caps_anything(self):
        """The drawing has a screen to fit. The file does not."""
        many = [a_parcel(id=f"p{n}", flags=[a_flag()]) for n in range(40)]
        built = parcel_table.build(a_document(many))
        for n in range(40):
            self.assertIn(f"p{n}", built)

    def test_a_confirmed_deadline_is_never_the_row_the_cap_drops(self):
        """The sort puts unmeasured waits first, because those need a call. On a
        corridor with more flagged tracts than fit, that made the one legally
        binding date the **first** thing cut from the projector -- silently.

        A date somebody is bound by does not come off the screen to make room
        for a date nobody has found yet.
        """
        many = [a_parcel(id=f"u{n}", flags=[a_flag()], lead_time_not_found=["school"])
                for n in range(40)]
        many.append(a_parcel(id="STATUTORY", flags=[A_CEMETERY], max_lead_time_days=14,
                             max_lead_time_basis="calendar days",
                             lead_time_driver="cemetery"))
        self.assertIn("STATUTORY", parcel_table.svg(a_document(many)))

    def test_the_drawing_says_how_many_it_left_off(self):
        many = [a_parcel(id=f"u{n}", flags=[a_flag()]) for n in range(40)]
        drawn = parcel_table.svg(a_document(many))
        self.assertIn(str(40 - parcel_table.ROWS_ON_SCREEN), drawn)

    def test_the_svg_is_well_formed_xml(self):
        drawn = parcel_table.svg(a_document([a_parcel(id="x", flags=[a_flag()])]))
        ElementTree.fromstring(drawn)

    def test_an_owner_name_with_an_ampersand_does_not_break_the_drawing(self):
        """`BOERNE STAGE & OAK` is a real shape of Bexar owner name."""
        document = a_document([a_parcel(id="x", owner="SMITH & SONS <LP>",
                                        flags=[a_flag()])])
        ElementTree.fromstring(parcel_table.svg(document))

    def test_a_full_table_of_every_flag_type_still_has_room_to_cite_them(self):
        """The citation block is stacked up from the warning line, so a full
        table and the longest citation list have to not meet in the middle."""
        from corridor_screen.sources import FLAG_SOURCES
        last_row = parcel_table.ROW_TOP + (parcel_table.ROWS_ON_SCREEN - 1) * parcel_table.ROW_STEP
        top_citation = (parcel_table.NOTE_Y - 38
                        - (len(FLAG_SOURCES) - 1) * parcel_table.CITE_STEP)
        self.assertGreater(top_citation, last_row + parcel_table.CITE_STEP)

    def test_no_column_runs_past_the_right_margin(self):
        """A column that overran would not look wrong. It would silently
        shorten the value inside it, which is worse."""
        label, x, width = parcel_table.COLUMNS[-1]
        self.assertLessEqual(x + width, parcel_table.WIDTH - 60)

    def test_every_row_it_claims_to_draw_is_drawn(self):
        document = a_document([a_parcel(id=f"p{n}", flags=[a_flag()]) for n in range(5)])
        drawn = parcel_table.svg(document)
        for n in range(5):
            self.assertIn(f"p{n}", drawn)


class TestAgainstTheRealRun(unittest.TestCase):
    """The committed SH16 capture, which is what goes on the projector."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))

    def test_it_finds_the_eight_flagged_parcels(self):
        self.assertEqual(len(parcel_table.rows(self.document)), 8)

    def test_the_seven_school_parcels_all_say_not_found(self):
        unmeasured = [r for r in parcel_table.rows(self.document)
                      if "not found" in parcel_table.wait_cell(r).lower()]
        self.assertEqual(len(unmeasured), 7)

    def test_the_one_confirmed_wait_is_the_cemetery_at_fourteen_days(self):
        known = [r for r in parcel_table.rows(self.document)
                 if r["max_lead_time_days"] is not None]
        self.assertEqual(len(known), 1)
        self.assertEqual(known[0]["max_lead_time_days"], 14)
        self.assertEqual(known[0]["lead_time_driver"], "cemetery")

    def test_no_row_prints_a_zero_in_the_wait_column(self):
        for row in parcel_table.rows(self.document):
            self.assertNotIn("0 ", parcel_table.wait_cell(row))

    def test_nothing_on_the_real_drawing_is_cut_short(self):
        """The ellipsis is honest, but a clipped statutory wait is not readable.

        The first version of this drawing cut "14 calendar days (cemetery)" to
        "14 calendar days (cemeter…" -- the one confirmed legal figure in the
        whole run, on the projector, in front of the people most likely to
        quote it.
        """
        self.assertNotIn("…", parcel_table.svg(self.document))

    def test_the_markdown_still_names_which_flag_drove_the_wait(self):
        """Dropped from the drawing to make room, kept where there is room."""
        self.assertIn("(cemetery)", parcel_table.build(self.document))

    def test_both_files_are_written_where_the_demo_looks_for_them(self):
        with tempfile.TemporaryDirectory() as temporary:
            written = parcel_table.write(self.document, temporary)
        self.assertEqual([p.name for p in written],
                         [parcel_table.TABLE_NAME, parcel_table.DRAWING_NAME])


if __name__ == "__main__":
    unittest.main()
