"""The dry-run runbook, held against the run of show it hands to a timekeeper.

Issue #121. [#36](https://github.com/RickSmith/survey-recon/issues/36) asks for
the full two hours in front of Seneca and CBI staff, timed block by block and
cut against the clock. It did not say how, and nothing in `docs/` did either --
the words "dry run" were on no page. `docs/presenting/dry-run.md` is that page.

What makes it worth testing is what makes it useful: it is the **third** place
the run of show is written down. The plan of record sets the clock, the deck's
speaker notes carry it one line to a slide, and this page prints it as a form
somebody holds a pen against. Three copies of one table, and the third one is
the copy that gets photographed and quoted afterward.

This repo has already published four corrections for a number that was right
once and then was not -- #80, #104, #109, #118. So the sheet is read rather
than trusted:

* every block of the run of show is on the sheet, with the same name, the same
  planned start and the same length, in the same order
* the sheet invents no block the plan does not have, which is the check that
  matters when somebody adds a segment to one document and not the other
* the sheet is **blank** where a timekeeper writes, because a form that arrives
  with answers already in it is not a form
* the cut line is the plan's, in the plan's order, and the four things the plan
  says never to cut are all named

**Why check prose at all.** `test_fallbacks.py` gives the reason for the
fallback card and `test_deck.py` for the deck, and it is the same reason here:
a presenter reads a page, and a second copy of the facts only gives the first
correction somewhere to not be applied.
"""

import re
import unittest
from pathlib import Path

from corridor_screen.cache import long_path
from tests.markdown_docs import (
    headings,
    local_link_targets,
    markdown_section,
    plain,
    table_rows,
    text_of,
)

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "presenting" / "dry-run.md"
PLAN = REPO / "docs" / "plan-of-record.md"
NAV = REPO / "mkdocs.yml"

# `0:57–1:18`, with the en dash the plan of record actually uses. Anchored to
# the whole cell the way `test_fallbacks` anchors its own, because what is being
# matched is a time column rather than a time mentioned in a sentence.
A_SPAN = re.compile(r"^(\d:\d\d)\u2013(\d:\d\d)$")

# `0:00` on the sheet, which is the left-hand half of a span above.
A_START = re.compile(r"^\d:\d\d$")

# The block name is the bolded lead-in of the run of show's third cell --
# "**Act I — The grilling.** `/grill-with-docs` live ..." -- and the trailing
# period belongs to the sentence rather than to the name. One row has no bold
# at all ("Stretch + questions"), so the whole cell is the fallback.
A_BOLD_LEAD = re.compile(r"^\*\*(.+?)\*\*")

# `1. Hermes segment → recorded teaser`, as §7 writes the cut line.
A_CUT = re.compile(r"^\d+\.\s+(.+?)\s+\u2192\s+(.+)$")

# `**Never cut:** the cold open, the grilling, ...`
NEVER_CUT = re.compile(r"Never cut:\s*(.+?)\.")


def block_name(cell):
    """The name of a block, as the run of show's third cell gives it."""
    found = A_BOLD_LEAD.match(cell)
    name = found.group(1) if found else cell
    return name.rstrip(".").strip()


def run_of_show():
    """The session's blocks, in order, as (start, end, minutes, name).

    Read rather than restated. The plan of record is the spec, and a runbook
    holding its own private copy of the clock would go on passing its own tests
    after the clock changed underneath it.
    """
    section = markdown_section(text_of(PLAN), "## 5. Run of show")
    blocks = []
    for row in table_rows(section):
        found = A_SPAN.match(row[0])
        if found:
            blocks.append(
                (found.group(1), found.group(2), int(row[1]), block_name(row[2]))
            )
    if not blocks:
        raise AssertionError("no run-of-show rows found in the plan of record")
    return blocks


def sheet_rows():
    """Every row of the timing sheet, as its cells.

    Filtered on the first cell looking like a start time, so a heading row, a
    divider, or the end marker at the foot of the sheet does not arrive here
    pretending to be a block.
    """
    rows = [row for row in table_rows(text_of(PAGE)) if A_START.match(row[0])]
    if not rows:
        raise AssertionError(f"no timing-sheet rows found in {PAGE}")
    return rows


def block_rows():
    """The timing sheet without its end marker.

    The last row of the sheet carries the finish time and the word End rather
    than a block, so that a timekeeper has somewhere to write the time the
    session actually stopped. It is not a twelfth block.
    """
    return [row for row in sheet_rows() if "end" not in row[2].lower()]


def end_row():
    rows = [row for row in sheet_rows() if "end" in row[2].lower()]
    if len(rows) != 1:
        raise AssertionError(f"the sheet has {len(rows)} end rows, and should have one")
    return rows[0]


def content_words(phrase):
    """The words of a phrase that carry its meaning, lowercased.

    The plan of record writes the cut line telegraphically -- "Token slide →
    footnote to repo" -- because it is a list of decisions. The runbook writes
    the same cut as a sentence a presenter reads under time pressure, "A
    footnote to the repo", because that is a different reader.

    Matching the whole phrase would make the two documents agree on articles,
    which is agreement about nothing, and the first person to make either page
    read better would break a test. Matching the words that mean something
    still fails when a cut's destination changes, which is the thing worth
    catching.
    """
    small = {"a", "an", "the", "to", "as", "of", "it"}
    found = re.findall(r"[\w-]+", phrase.lower())
    return [word for word in found if word not in small]


def cut_line():
    """The three cuts, in order, as (what goes, what it becomes)."""
    section = markdown_section(text_of(PLAN), "### Cut line, in order")
    cuts = []
    for line in section.splitlines():
        found = A_CUT.match(line.strip())
        if found:
            cuts.append((found.group(1).strip(), found.group(2).strip()))
    if not cuts:
        raise AssertionError("the plan of record no longer carries a cut line")
    return cuts


def never_cut():
    """The things the plan says never to cut, as a list of phrases."""
    section = markdown_section(text_of(PLAN), "### Cut line, in order")
    found = NEVER_CUT.search(plain(section))
    if not found:
        raise AssertionError("the plan of record no longer carries a never-cut list")
    return [item.strip() for item in found.group(1).split(",")]


class TestTheSheetIsTheRunOfShow(unittest.TestCase):
    """The eleven blocks a timekeeper writes against, versus the eleven there are.

    Checked as a whole list rather than one row at a time. A block added to the
    plan and not to the sheet, or a block that drifted two places down it, is
    the failure this is for -- and both of those pass every per-row check that
    only looks at the rows it can pair up.
    """

    def setUp(self):
        self.plan = run_of_show()
        self.sheet = block_rows()

    def test_the_sheet_has_every_block_and_no_others(self):
        self.assertEqual(
            [row[2] for row in self.sheet],
            [name for _start, _end, _minutes, name in self.plan],
            "the timing sheet and the run of show disagree about the blocks",
        )

    def test_every_planned_start_is_the_plan_s(self):
        """The left-hand half of the plan's span, which is where a block begins.

        A timekeeper compares one number against one number. Printing the whole
        span would give them two, and the second one is the planned end, which
        is not a thing anybody writes down.
        """
        self.assertEqual(
            [row[0] for row in self.sheet],
            [start for start, _end, _minutes, _name in self.plan],
        )

    def test_every_length_is_the_plan_s(self):
        self.assertEqual(
            [int(row[1]) for row in self.sheet],
            [minutes for _start, _end, minutes, _name in self.plan],
        )

    def test_the_lengths_add_up_to_the_session(self):
        """Two hours, from the sheet's own numbers.

        If the plan ever gains a block without the clock moving, the arithmetic
        is what says so, and it says so on the document somebody is holding.
        """
        self.assertEqual(sum(int(row[1]) for row in self.sheet), 120)

    def test_the_sheet_ends_where_the_session_ends(self):
        self.assertEqual(end_row()[0], self.plan[-1][1])


class TestItIsAFormRatherThanAReport(unittest.TestCase):
    """The two columns the timekeeper fills in have to arrive empty.

    A sheet that came with times already in it would be read instead of
    written, and what it would be read as is a prediction of how the rehearsal
    went. That is the opposite of the job.
    """

    def test_the_actual_start_column_is_blank(self):
        for row in sheet_rows():
            self.assertEqual(row[3], "", f"{row[2]} already has an actual start on it")

    def test_the_notes_column_is_blank(self):
        for row in sheet_rows():
            self.assertEqual(row[4], "", f"{row[2]} already has a note on it")

    def test_the_sheet_asks_for_start_times_rather_than_durations(self):
        """The instruction the whole sheet depends on.

        A timekeeper writing down how long a block took is doing arithmetic in
        a dark room while listening. A timekeeper writing down the time a block
        started is reading a clock. Only the second one survives contact with
        an actual rehearsal, and the sheet has to say which one it wants.
        """
        self.assertIn("not how long it took", plain(text_of(PAGE)))


class TestTheCutLineIsThePlanS(unittest.TestCase):
    """Cutting in the wrong order is how the never-cut list gets cut.

    The three cuts are ordered on purpose -- Hermes first because it is the one
    that survives as a recording. A page that listed them in some other order,
    or dropped one, would send a presenter under time pressure at the block the
    plan spent a paragraph protecting.
    """

    def setUp(self):
        self.page = plain(text_of(PAGE))

    def test_the_three_cuts_are_named_in_the_plan_s_order(self):
        rows = [row for row in table_rows(text_of(PAGE)) if "Cut " in row[0]]
        self.assertEqual(len(rows), len(cut_line()))
        for position, (row, (goes, becomes)) in enumerate(zip(rows, cut_line()), 1):
            self.assertIn(f"Cut {position} of {len(rows)}", row[0])
            for word in content_words(goes):
                self.assertIn(
                    word, row[1].lower(), f"cut {position} goes {row[1]!r}, not {goes!r}"
                )
            for word in content_words(becomes):
                self.assertIn(
                    word,
                    row[2].lower(),
                    f"cut {position} becomes {row[2]!r}, not {becomes!r}",
                )

    def test_all_four_never_cuts_are_named(self):
        for item in never_cut():
            self.assertIn(item.lower(), self.page.lower(), f"{item} is not on the page")

    def test_the_page_says_not_to_skip_down_the_list(self):
        """An order nobody is told to keep is a list, not an order."""
        self.assertIn("do not skip down the list", self.page.lower())


class TestThePageDoesTheJobTheIssueAskedFor(unittest.TestCase):
    """#121's acceptance criteria, as checks rather than as ticks.

    Each of these is a sentence somebody could quietly drop in an edit, and
    each one is the reason a rehearsal produces a record instead of a feeling.
    """

    def setUp(self):
        self.text = text_of(PAGE)
        self.page = plain(self.text)

    def test_the_timekeeper_is_a_named_job(self):
        self.assertIn("timekeeper", self.page.lower())

    def test_the_timekeeper_is_not_the_presenter(self):
        """The one that makes the rehearsal measurable.

        A presenter watching a clock has stopped presenting, and a rehearsal
        timed by the person talking is timed by the person least able to.
        """
        self.assertIn("not one of the above", self.page.lower())

    def test_what_goes_wrong_becomes_a_work_order(self):
        self.assertIn("open one issue per problem", self.page.lower())

    def test_it_says_to_do_that_the_same_day(self):
        """Impressions fade in hours. A rehearsal written up on Monday is a mood."""
        self.assertIn("same day", self.page.lower())

    def test_it_points_at_the_work_order_it_serves(self):
        self.assertIn("issues/36", self.page)

    def test_it_has_a_section_for_each_part_of_the_job(self):
        """A page that mentions all of this in prose is not a runbook.

        `test_principals_brief.py` draws the same line for the same reason: a
        sentence somewhere in a document is not something a reader under
        pressure can find, and a heading is.
        """
        found = headings(self.text)
        for expected in ("who is in the room", "the timing sheet", "when it runs long"):
            self.assertTrue(
                any(expected in heading for heading in found),
                f"no section about {expected}; the page has {found}",
            )

    def test_it_tells_the_reader_to_print_it(self):
        """Same argument the fallback card makes about itself.

        A page you have to load is a page you cannot load at the moment you
        need it -- and here there is a second reason, which is that the person
        holding it is writing on it.
        """
        self.assertIn("print", self.page.lower())


class TestThePageIsReachableAndItsLinksAre(unittest.TestCase):
    """A runbook nobody can find is a runbook nobody reads.

    `mkdocs build --strict` catches a broken link and a page missing from the
    menu, but only once somebody builds the site, and by then the rehearsal may
    already have happened without it. The suite runs on every pull request.
    """

    def setUp(self):
        self.page = plain(text_of(PAGE))

    def test_it_is_in_the_menu(self):
        self.assertIn(
            "presenting/dry-run.md",
            text_of(NAV),
            "the dry-run page is not in the mkdocs.yml menu",
        )

    def test_every_local_link_resolves(self):
        for target in local_link_targets(text_of(PAGE)):
            resolved = (PAGE.parent / target).resolve()
            self.assertTrue(
                Path(long_path(resolved)).exists(),
                f"{PAGE.name} links to {target}, which is not in the repo",
            )

    def test_it_names_the_test_that_keeps_it_honest(self):
        """This file, named on the page it checks.

        Every other checked page in `docs/` carries a "how this page is kept
        honest" section saying which test holds it. A reader deciding whether
        to trust a number needs to be able to find the thing that would have
        caught it being wrong.
        """
        self.assertIn("test_dry_run.py", self.page)


if __name__ == "__main__":
    unittest.main()
