"""The plan of record's Act II figures, held against the run that produced them.

Issue #80. Section 5 of `docs/plan-of-record.md` gave Act II three numbers -- 13
NGS marks, 18 TxDOT control points, 27 ROW sheets 1937-1998 -- and all three
predated the tool running. `docs/presenting/fallbacks.md` and `CONTEXT.md` had
since been written from the real run and disagreed with the plan on every one of
them, which left the session's most quoted page as the one page that was wrong.

Those numbers get read out loud to licensed surveyors who can check them from
the projector while they are being said. So they are not restated here either.
This file reads both sides and compares them:

* the marks, the control records and the ROW sheets in the Act II row are the
  figures `project-sh16/screening.json` holds
* the Act II row carries **no number the run does not have**, which is the check
  that would have caught 18
* the corridor figure and the county figure both stay on the page and neither is
  given as the other -- and the county figure is checked against its own cached
  capture rather than against a sentence somewhere else in the repo

**Why check prose at all.** A number written in prose beside a thing is a number
that rots. `test_fallbacks.py` says the same about the fallback card and
`test_deck.py` about the slide deck, and both hold the document rather than
replacing it, for the same reason: a presenter reads a page, and a second copy
of the facts only gives the first correction somewhere to not be applied.

**The two that are easy to get wrong.** A count of TxDOT control *records* is
not a count of *monuments* -- four records in this corridor name two stations --
and a corridor sheet count is not a county sheet count. Both distinctions are
already in `CONTEXT.md`, and both are the kind that survive a proofread and then
get said out loud. So each is checked as a pair, never as a lone number.
"""

import json
import os
import re
import unittest
from pathlib import Path

from corridor_screen.arcgis import from_epoch_ms
from corridor_screen.cache import long_path

# Borrowed rather than copied, the way `test_fallbacks` borrows from
# `test_offline`. Two copies of a markdown reader would drift the first time
# somebody fixed one of them. The deck under #12 moves these three into
# `tests/markdown_docs.py` and re-exports them from here, so this import keeps
# working either way -- point it at the new home when next in this file.
from tests.test_fallbacks import markdown_section, table_rows, text_of

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "docs" / "plan-of-record.md"
RUN = REPO / "project-sh16" / "screening.json"
ROW_MAP_CACHE = REPO / "project-sh16" / "cache" / "txdot-row-maps"

# The cross-check that answers the county question rather than the corridor one:
# SH16 through the whole of Bexar County, captured on 2026-09-12 with a
# provenance record beside it. Named by its stable prefix, because the rest of
# the file name is a hash of the exact request.
COUNTY_CAPTURE = "sh16-bexar-county-wide-cross-check__"

# The block this file is about, as the plan of record writes it, with the en
# dash that page uses.
ACT_II = "0:57–1:18"

# The route the demo corridor runs along, as TxDOT spells it in `by_route`.
THE_ROUTE = "SH0016"

# What each figure has to look like on the page. Whole phrases rather than bare
# numbers, deliberately: `4` and `2` on their own would match half the cell, and
# what is being checked is that a number sits beside the words saying which
# question it answers.
MARKS = re.compile(r"(\d+) NGS marks, every one `MARK NOT FOUND`")
CONTROL = re.compile(r"(\d+) TxDOT control records naming (\d+) distinct monuments")
SHEETS = re.compile(r"(\d+) ROW sheets reach the corridor, (\d+) of them SH16's own")
ROUTE_DATES = re.compile(
    r"(\d+) of those (\d+) are SH16's own, dating \*\*(\d{4})–(\d{4})\*\*"
)
COUNTY = re.compile(r"Bexar County has \*\*(\d+)\*\* sheets, \*\*(\d{4})–(\d{4})\*\*")

# A number a reader would read as a number, rather than one glued into a name.
# `SH16` holds a 16 that is part of a highway and not a count of anything.
A_STANDALONE_NUMBER = re.compile(r"(?<![A-Za-z0-9])\d+(?![A-Za-z0-9])")


def plan_section():
    """Section 5 of the plan of record, with its line breaks taken out.

    The Act II figures are spread over a table row and a note under the table,
    and markdown wraps both wherever the line happened to run out. Matching on a
    sentence a reader sees as one line means not caring where it was wrapped.
    """
    return " ".join(markdown_section(text_of(PLAN), "## 5. Run of show").split())


def act_two_cell():
    """The Act II block cell of the run of show, exactly as the table holds it."""
    section = markdown_section(text_of(PLAN), "## 5. Run of show")
    cells = [row[2] for row in table_rows(section) if row[0] == ACT_II]
    if len(cells) != 1:
        raise AssertionError(
            f"{ACT_II} has {len(cells)} rows in the run of show, and should have one"
        )
    return cells[0]


def the_run():
    """The committed SH16 screening run, which is the authority on all of this."""
    return json.loads(text_of(RUN))


def the_county_capture():
    """The cached county-wide cross-check, as (sheets, first year, last year).

    Read out of the response rather than out of any sentence about it. 27 is the
    number this repo has quoted since #16, and the only thing that makes it true
    is this file.

    Listed through `long_path` rather than `Path.glob` for the reason the cache
    module gives: a checkout under "OneDrive - Some Long Firm Name\\Documents"
    reaches the 260 characters Windows opens without being asked, and the
    failure is a missing-file error on a directory that plainly exists.
    """
    names = sorted(
        name
        for name in os.listdir(long_path(ROW_MAP_CACHE))
        if name.startswith(COUNTY_CAPTURE) and name.endswith(".json")
    )
    if len(names) != 1:
        raise AssertionError(
            f"expected one {COUNTY_CAPTURE}*.json in {ROW_MAP_CACHE}, found {names}"
        )
    features = json.loads(text_of(ROW_MAP_CACHE / names[0]))["features"]
    dates = sorted(
        from_epoch_ms(feature["attributes"]["MAP_FROM_DT"]) for feature in features
    )
    return len(features), dates[0][:4], dates[-1][:4]


class TestTheActTwoRowStatesWhatTheRunFound(unittest.TestCase):
    """The row a presenter reads Act II off, against the file that produced it."""

    def setUp(self):
        self.cell = act_two_cell()
        self.run = the_run()

    def test_the_mark_count_is_the_run_s(self):
        found = MARKS.search(self.cell)
        self.assertIsNotNone(found, f"no NGS mark count in {self.cell!r}")
        self.assertEqual(
            int(found.group(1)),
            self.run["control"]["recovery_risk"]["marks_in_corridor"],
        )

    def test_it_hedges_exactly_when_the_run_hedges(self):
        """The row said "several", and the run's answer is stronger than that.

        Every mark in this corridor is recorded `MARK NOT FOUND`, with recovery
        attempts running from 1995 to 2002. That is the finding -- it moves an
        estimate from recovering control to setting new control -- and a hedge
        in front of it gives it away. If a later capture ever finds one, this
        fails, and the sentence gets rewritten rather than quietly kept.
        """
        risk = self.run["control"]["recovery_risk"]
        every_one = risk["mark_not_found"] == risk["marks_in_corridor"]
        self.assertEqual(
            bool(MARKS.search(self.cell)),
            every_one,
            "the row and the run disagree about whether every mark is MARK NOT FOUND",
        )

    def test_the_record_count_and_the_monument_count_are_both_the_run_s(self):
        """The pair that 18 was half of.

        `CONTEXT.md`, under **Distinct stations**: TxDOT holds two records for
        274 of its 492 stations, so a count of records is not a count of
        monuments. Four records in this corridor name two. A crew drives to the
        monument, and an estimator pricing the records would price it twice.
        """
        found = CONTROL.search(self.cell)
        self.assertIsNotNone(found, f"no TxDOT control figure in {self.cell!r}")
        control = self.run["control"]["txdot_control"]
        self.assertEqual(int(found.group(1)), control["points_in_corridor"])
        self.assertEqual(int(found.group(2)), control["distinct_stations"])

    def test_the_sheet_counts_are_the_run_s(self):
        found = SHEETS.search(self.cell)
        self.assertIsNotNone(found, f"no ROW sheet figure in {self.cell!r}")
        row_maps = self.run["row_maps"]
        self.assertEqual(int(found.group(1)), row_maps["sheet_count"])
        self.assertEqual(
            int(found.group(2)), row_maps["by_route"][THE_ROUTE]["sheet_count"]
        )

    def test_the_row_carries_no_number_the_run_does_not(self):
        """The same check from the other direction, and the one that matters.

        Every standalone number in the cell has to be a figure the run holds, in
        the order the cell gives them. A number arriving from somewhere else --
        a different query, an older note, somebody's memory of a meeting --
        fails here even when every sentence around it still reads correctly.
        That is exactly what 18 was.
        """
        control = self.run["control"]
        row_maps = self.run["row_maps"]
        expected = [
            control["recovery_risk"]["marks_in_corridor"],
            control["txdot_control"]["points_in_corridor"],
            control["txdot_control"]["distinct_stations"],
            row_maps["sheet_count"],
            row_maps["by_route"][THE_ROUTE]["sheet_count"],
        ]
        self.assertEqual(
            [int(number) for number in A_STANDALONE_NUMBER.findall(self.cell)],
            expected,
            "a number in the Act II row is not one this run produced",
        )


class TestTheCorridorAndTheCountyStayTwoAnswers(unittest.TestCase):
    """15 and 27 are both right, and they answer different questions.

    Issue #16 predicted 27 sheets over 1937-1998, and was correct about SH16
    through the whole of Bexar County, over three control sections. The demo
    corridor is eight and a half miles inside one of those three and reaches 15
    of them, 1944-1998. The plan of record collapsed the two into a corridor
    figure of 27 -- the shape of error nobody can argue with from the floor,
    because the number did come from a real query.
    """

    def setUp(self):
        self.section = plan_section()
        self.run = the_run()

    def test_the_route_s_own_sheets_and_dates_are_the_run_s(self):
        found = ROUTE_DATES.search(self.section)
        self.assertIsNotNone(
            found, "section 5 no longer says which of the sheets are SH16's own"
        )
        route = self.run["row_maps"]["by_route"][THE_ROUTE]
        self.assertEqual(int(found.group(1)), route["sheet_count"])
        self.assertEqual(int(found.group(2)), self.run["row_maps"]["sheet_count"])
        self.assertEqual(found.group(3), route["date_range"]["from"][:4])
        self.assertEqual(found.group(4), route["date_range"]["to"][:4])

    def test_the_county_figure_is_its_own_capture_s(self):
        found = COUNTY.search(self.section)
        self.assertIsNotNone(found, "section 5 no longer carries the county figure")
        sheets, first, last = the_county_capture()
        self.assertEqual(int(found.group(1)), sheets)
        self.assertEqual(found.group(2), first)
        self.assertEqual(found.group(3), last)

    def test_the_two_figures_are_actually_different(self):
        """If they ever stop differing, the careful wording stops earning its keep.

        Said plainly so that a later capture which made them equal shows up as a
        failing test rather than as a page explaining a distinction that is no
        longer there.
        """
        sheets, _first, _last = the_county_capture()
        self.assertNotEqual(sheets, self.run["row_maps"]["sheet_count"])

    def test_the_corridor_s_own_sheets_are_some_of_the_county_s(self):
        """15 of 27, not 15 and 27.

        The corridor's SH16 sheets are drawn from the county's set, so one can
        never exceed the other. If a capture made it so, the arithmetic on the
        page would be something no reader could follow, and the two figures
        would need establishing again rather than rewording.
        """
        sheets, _first, _last = the_county_capture()
        self.assertLessEqual(
            self.run["row_maps"]["by_route"][THE_ROUTE]["sheet_count"], sheets
        )


class TestThePageSaysWhereTheNumbersCameFrom(unittest.TestCase):
    """Directions, the way the fallback card gives directions.

    A figure with no provenance is an anecdote. Section 5 names the run it was
    read out of, and that run has to be in the repo and have finished --
    otherwise the page cites a file nobody can open, which on a page reads
    exactly like a file everybody can.
    """

    def test_the_section_names_the_run_it_was_read_from(self):
        self.assertIn("project-sh16/screening.json", plan_section())

    def test_that_run_is_committed_and_opens(self):
        self.assertTrue(
            Path(long_path(RUN)).is_file(), f"{RUN} is cited and is not in the repo"
        )
        self.assertGreater(len(text_of(RUN).strip()), 0)

    def test_the_run_it_names_is_one_that_finished(self):
        """A run that stopped early would have smaller numbers and say nothing.

        `status` is the tool's own account of whether it got to the end. Reading
        figures off a partial run understates every one of them, which is the
        failure that does not look like one.
        """
        self.assertEqual(the_run()["run"]["status"], "complete")


if __name__ == "__main__":
    unittest.main()
