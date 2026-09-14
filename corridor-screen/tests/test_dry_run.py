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
DOCS_WORKFLOW = REPO / ".github" / "workflows" / "docs.yml"
README = REPO / "corridor-screen" / "README.md"
DECK = REPO / "docs" / "slides" / "beyond-the-prompt.md"

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


def slugify(heading):
    """A heading, as the anchor MkDocs will put on it.

    This is python-markdown's own default `slugify`, which the `toc` extension
    uses and `mkdocs.yml` switches on with `permalink: true`. Reproduced rather
    than imported because the tests import nothing outside the standard library
    and this repo's own package -- the same rule `corridor_screen` runs under.

    Worth knowing what it does to a heading like "0:00 · Cold open": the colon
    and the middle dot are dropped rather than replaced, the two spaces they
    leave collapse to one dash, and the answer is `000-cold-open` with one dash
    and not two.
    """
    value = re.sub(r"[^\w\s-]", "", heading.lower()).strip()
    return re.sub(r"[-\s]+", "-", value)


def block_sections(markdown):
    """The per-block instructions, as {heading: body}, in the order written.

    A block section is a third-level heading that opens with a start time --
    "### 0:30 · Act I — The grilling". The time is what separates it from the
    other third-level headings on the page, which are ordinary prose sections
    and have no business being counted as blocks of the session.

    Ordinary `dict` here rather than anything fancier: insertion order is the
    document's order, which is what the clock-order check reads.
    """
    sections, heading, body = {}, None, []
    for line in markdown.splitlines():
        if line.startswith("### "):
            if heading is not None:
                sections[heading] = "\n".join(body)
            title = line[4:].strip()
            heading, body = (title, []) if A_START.match(title.split()[0]) else (None, [])
        elif line.startswith("#"):
            if heading is not None:
                sections[heading] = "\n".join(body)
            heading, body = None, []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        sections[heading] = "\n".join(body)
    return sections


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


class TestEveryBlockHasItsOwnInstructions(unittest.TestCase):
    """#124. The sheet measured the two hours and said nothing about running them.

    A timing sheet tells you a block ran long. It does not tell you what the
    block was supposed to do, what to type, or what should have come back --
    and a demo that prints nothing for four seconds looks exactly like a demo
    that has hung. The person holding the stopwatch is the one who most needs
    to be able to tell those apart, and they are the one who wrote none of it.

    So every block of the run of show has a section of its own above, and the
    sections arrive in clock order. A block added to the session cannot quietly
    turn up without instructions, which is the failure this is really for: the
    plan of record is edited far more often than this page will be.
    """

    def setUp(self):
        self.plan = run_of_show()
        self.sections = block_sections(text_of(PAGE))

    def test_every_block_has_a_section(self):
        for start, _end, _minutes, name in self.plan:
            with self.subTest(block=name):
                self.assertTrue(
                    any(start in heading and name in heading for heading in self.sections),
                    f"no section for {start} {name}; the page has {self.sections}",
                )

    def test_the_sections_are_in_clock_order(self):
        """A presenter reads this while something is on a projector.

        Out of order it is a reference document, and a reference document is
        not what somebody four minutes behind can use.
        """
        found = [heading.split()[0] for heading in self.sections]
        self.assertEqual(found, [start for start, _end, _m, _n in self.plan])

    def test_no_section_invents_a_block(self):
        self.assertEqual(len(self.sections), len(self.plan))

    def test_every_section_says_what_is_on_screen_and_what_to_do(self):
        """The two questions somebody driving this asks in that order."""
        for heading, body in block_sections(text_of(PAGE)).items():
            with self.subTest(block=heading):
                self.assertIn("**On screen.**", body)
                self.assertIn("**You do.**", body)


class TestTheCommandsAreTheOnesThisRepoDocuments(unittest.TestCase):
    """The two screening lines, character for character, against the README.

    `corridor-screen/README.md` is where [the fallback
    card](../../docs/presenting/fallbacks.md) tells a presenter to copy the
    cold-open line from rather than retype it -- it is 119 characters and five
    flags, and the day you need it is the day you will mistype it. A runbook
    holding a *nearly* identical copy is worse than one holding none, because
    it is the copy that will be to hand.
    """

    def readme_lines(self):
        found = re.findall(
            r"^python -m corridor_screen --route.*$",
            text_of(README),
            flags=re.MULTILINE,
        )
        self.assertTrue(found, "the README no longer gives a screening line")
        return found

    def test_the_page_carries_every_screening_line_the_readme_does(self):
        page = text_of(PAGE)
        for line in self.readme_lines():
            with self.subTest(line=line):
                self.assertIn(line, page)

    def test_the_live_line_and_the_cache_only_line_are_both_there(self):
        """One proves the demo is real; the other proves it survives the venue.

        A page with only the live line leaves a presenter with no offline path.
        A page with only the cache-only line is quietly rehearsing the fallback
        as though it were the plan, which the plan of record is blunt about.
        """
        lines = self.readme_lines()
        self.assertTrue(any("--mode cache-only" in line for line in lines))
        self.assertTrue(any("--mode cache-only" not in line for line in lines))


class TestThePageWarnsWhatARehearsalWritesOver(unittest.TestCase):
    """The trap nothing else in this repo says out loud.

    `--out ../project-sh16` is the documented line and it writes into the
    committed demo artifacts. `run_id` carries a timestamp, so **every** run
    leaves the working tree dirty, including one that found identical numbers.
    A rehearsal that found different ones leaves it dirty and failing
    `test_plan_of_record.py`, which reads that file.

    A presenter who does the honest thing -- rehearse live -- has then modified
    the repo they are about to put on a projector, and nothing told them.
    """

    def setUp(self):
        self.page = plain(text_of(PAGE))

    def test_it_has_a_section_about_it(self):
        found = headings(text_of(PAGE))
        self.assertTrue(
            any("rehearsal changes" in heading for heading in found),
            f"no section about what a rehearsal writes over; the page has {found}",
        )

    def test_it_names_the_committed_file_that_gets_written_over(self):
        self.assertIn("screening.json", self.page)

    def test_it_says_to_send_the_rehearsal_output_somewhere_else(self):
        self.assertIn("send the output somewhere else", self.page.lower())

    def test_it_says_to_check_git_status_before_the_laptop_closes(self):
        """The check is worth nothing on Monday. It has to be that evening."""
        self.assertIn("git status", self.page)
        self.assertIn("before you close the laptop", self.page.lower())


class TestTheRoomHasAVoiceInTheRehearsalToo(unittest.TestCase):
    """Six interjections, counted from the deck rather than from this page.

    `docs/slides/index.md` says they are one to a block, spread across the two
    hours, and that they have to be rehearsed **against the clock** rather than
    read off a page on the day. That makes them part of the run-through rather
    than a detail of the deck, so the runbook has to place them -- and the
    number it places has to be the number there are.
    """

    def test_the_page_places_as_many_as_the_deck_carries(self):
        in_deck = len(re.findall(r"Seneca \(audience proxy\)", text_of(DECK)))
        self.assertGreater(in_deck, 0, "the deck no longer carries any interjections")
        placed = [
            heading
            for heading, body in block_sections(text_of(PAGE)).items()
            if "Seneca" in body
        ]
        self.assertEqual(
            len(placed),
            in_deck,
            f"the deck carries {in_deck} interjections and the runbook places "
            f"{len(placed)}: {placed}",
        )


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


class TestTheDeckGetsOntoTheLaptop(unittest.TestCase):
    """The one step on this page that closes a hole rather than measuring one.

    Issue #123. Two blocks of the session -- 0:08 and 0:20 -- are slides and
    nothing else, and the rendered deck lives only on the published site. That
    is twenty-two minutes with nothing to open, and the fallback card said so
    for weeks while pointing at work orders that had already closed.

    Committing the PDF would have closed it in one line and was decided
    against: nothing rendered is committed here, and a stale binary nobody
    re-renders is a worse trap than a missing one, because it opens. So the
    fallback is a step, and a step is worth what the page telling you to take
    it is worth.

    The address is not typed in here either. It is built from `site_url` and
    the path `.github/workflows/docs.yml` refuses to publish without, so a site
    that moves fails this rather than quietly handing a presenter a dead link.
    """

    def setUp(self):
        self.page = plain(text_of(PAGE))

    def published_pdf(self):
        site = re.search(r"^site_url:\s*(\S+)", text_of(NAV), flags=re.MULTILINE)
        self.assertIsNotNone(site, "mkdocs.yml no longer says where the site lives")
        published = re.search(r"test -s site/(\S+\.pdf)", text_of(DOCS_WORKFLOW))
        self.assertIsNotNone(
            published, "docs.yml no longer checks a rendered PDF before publishing"
        )
        return site.group(1).rstrip("/") + "/" + published.group(1)

    def test_the_page_has_a_section_for_it(self):
        found = headings(text_of(PAGE))
        self.assertTrue(
            any("deck on the laptop" in heading for heading in found),
            f"no section about putting the deck on the laptop; the page has {found}",
        )

    def test_it_gives_the_address_the_site_actually_publishes(self):
        self.assertIn(self.published_pdf(), self.page)

    def test_it_says_to_open_the_copy_with_the_network_off(self):
        """A download is not a fallback until somebody has opened it once.

        A file that landed in the wrong folder, or landed at zero bytes, looks
        exactly like one that worked right up to the moment it is needed.
        """
        self.assertIn("turn the wi-fi off and open the file", self.page.lower())

    def test_it_says_to_do_it_again_before_the_day(self):
        """The deck re-renders on every push. The laptop's copy does not.

        A PDF pulled down for the rehearsal is the rehearsal's deck, three
        weeks stale on the day, and nothing on its face says so.
        """
        self.assertIn("do it again before 8 october", self.page.lower())

    def test_it_says_why_the_file_is_not_in_the_repo(self):
        """A reader who does not know why will helpfully commit the PDF."""
        self.assertIn("nothing rendered is committed", self.page.lower())

    def test_the_fallback_card_agrees_this_is_where_the_step_lives(self):
        """Both directions, because a one-way pointer is how the first one rotted.

        The card sends a presenter here for those two blocks. If this page ever
        stops carrying the step, the card is sending them to a page that does
        not have it, and `test_fallbacks.py` cannot see that from its side.
        """
        card = plain(text_of(PAGE.parent / "fallbacks.md"))
        self.assertIn("dry-run.md", card)
        self.assertIn("Put the deck on the laptop", card)


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

    def test_every_link_into_this_page_lands_on_a_heading(self):
        """The jump links, against the anchors MkDocs will actually generate.

        `mkdocs build --strict` does **not** catch this one. A link to a
        heading that does not exist builds clean and silently does nothing when
        clicked, which on a page somebody is following step by step is the
        worst kind of broken: it looks like the page has no more to say.

        Written after `#000--cold-open` shipped with one dash too many, which
        is what python-markdown's slugifier does to "0:00 · Cold open" and not
        what typing it by hand does.
        """
        anchors = {slugify(heading) for heading in headings(text_of(PAGE))}
        wanted = re.findall(r"\]\(#([^)]+)\)", text_of(PAGE))
        self.assertTrue(wanted, "the page has no jump links; this check is idle")
        for anchor in wanted:
            with self.subTest(anchor=anchor):
                self.assertIn(
                    anchor, anchors, f"#{anchor} is linked and is not a heading here"
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
