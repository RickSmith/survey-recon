"""The Act III slides, held to the three documents they frame.

Issue #84. Eighteen minutes, three slides, and none of them reproduces its
document — the document is on the screen beside the slide. So what these slides
carry is the handful of sentences a room has to hear *while* looking at it, and
every one of those sentences is a claim about a file committed under
`project-sh16/`.

**That is a different risk from Act II's.** Act II's figures come out of one run
and the danger there is a stale number. Here the danger is a slide that
describes a document the document no longer agrees with: a memo said to lead
with its gaps that stopped doing so, a table said to sort the unknowns first
that got re-sorted, a rate handle shown beside a rate that is not its own. Each
of those reads perfectly well from the fourth row and is wrong.

**The three things this block is really teaching:**

* *not found* is a finding, and it is never a zero, a blank or a `no`. Seven of
  the eight flagged tracts on SH16 carry no number at all, which is why that
  count is tallied off the run here rather than read out of the table's prose
* a notice period has legal weight, so its citation is on the projector rather
  than on the presenter's screen. `test_deck.py` holds the deck to that for the
  cemetery figure; this file holds the figure and the citation to the table
* a rate is somebody's assumption with a name on it. A handle quoted beside the
  wrong rate is the one error on this block a surveyor in the room would catch
  before the presenter did

**The crew-day slide is `Cut 2 of 3`**, so it is held to saying so, and to
sending the presenter at a committed file. Dropping that slide has to leave the
block making the same point out of `project-sh16/crew-day.md`.
"""

import re
import unittest

from tests.build_up_figures import (
    HANDLE,
    figures,
    numbers_it_publishes,
    quantities_on,
    rate_handles,
    rate_values,
)
from tests.deck_reader import (
    A_PATH,
    REPO,
    note,
    on_screen,
    slides_in_block,
    visible,
    with_markup,
)
from tests.markdown_docs import json_of, plain, table_rows, text_of

SCREENING = REPO / "project-sh16" / "screening.json"
MEMO = REPO / "project-sh16" / "bid-memo.md"
TABLE = REPO / "project-sh16" / "flagged-parcels.md"
BUILD_UP = REPO / "project-sh16" / "crew-day.md"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"

BLOCK = "Act III — The estimate package"

# The three slides this work order owns, in the order the block runs them.
OWNED = ("The bid memo", "The flagged parcel table", "The crew-day build-up")

# A line carrying its own source may carry its own digits: a statute section and
# a file name belong to the source, not to the build-up. `test_money_slide.py`
# asks the same question of its own block and answers it with the one host that
# block cites; this block cites files as well, so it looks for either.
#
# Taking a rate handle off a line before counting its numbers is
# `build_up_figures.quantities_on`, imported above. It was a second copy of
# `test_money_slide.py`'s pattern until this file's review found it.
A_SOURCE_ON_A_LINE = re.compile(r"\b[\w-]+\.(?:gov|com|org|md|txt|svg|json)\b")


def run():
    return json_of(SCREENING)


def act_three():
    """The content slides of the block, without its section break."""
    return slides_in_block(BLOCK)


def flagged():
    """The flagged tracts of the SH16 run, as the tool selects them."""
    return [parcel for parcel in run()["parcels"] if parcel.get("flags")]


def parcel_rows():
    """The rows of the table's own parcel list, top to bottom.

    Found by the first cell being a parcel id in backticks, so the second table
    on the page -- the citations -- is not read as parcels, and so a column
    added in front of the id would fail loudly rather than quietly.
    """
    return [
        row for row in table_rows(text_of(TABLE))
        if row and re.fullmatch(r"`[\d-]+`", row[0].strip())
    ]


def source_row(flag):
    """One row of the table's *Where these numbers come from* table.

    Read out of `flagged-parcels.md` rather than written here, because the
    whole argument of that table is that a lead time is worth exactly what its
    citation is worth. A citation this file kept a private copy of would be a
    citation nobody checked.
    """
    for row in table_rows(text_of(TABLE)):
        if row and row[0].strip().lower() == flag:
            return row
    raise AssertionError(f"the flagged parcel table has no source row for {flag!r}")


class TestTheBidMemoSlideIsTheMemoS(unittest.TestCase):
    """One page, and the slide's loudest claim is about the order it is in."""

    def setUp(self):
        self.memo = text_of(MEMO)
        self.said = on_screen("The bid memo")

    def test_the_memo_really_does_put_its_gaps_above_its_findings(self):
        """The slide's second bullet is a claim about layout, and layout is the
        easiest thing in a generated document to change without noticing.

        `## What is not known, and why` sits above `## What was found` in the
        file. Swap them and the slide is telling three hundred people something
        that is no longer true of the page beside it.
        """
        gaps = self.memo.index("## What is not known, and why")
        findings = self.memo.index("## What was found")
        self.assertLess(gaps, findings, "the memo now leads with what it found")

    def test_the_slide_says_that_is_what_it_does(self):
        self.assertIn("**What it could not check comes first**", self.said)

    def test_the_two_it_cannot_screen_at_all_are_the_memos_two(self):
        """Gated access and livestock are the two the memo files under *no
        public source publishes these at all*, and they are the two a party
        chief finds out about at a gate. That is why they reach a slide."""
        for gap in ("Gated access", "Livestock"):
            with self.subTest(gap=gap):
                self.assertIn(
                    f"{gap} — no public source publishes", plain(self.memo)
                )
        self.assertIn("Gated access and livestock", self.said)

    def test_the_right_of_entry_verb_on_the_slide_is_the_rpls_one(self):
        """*May seek* and *is entitled to* are two different licenses.

        An RPLS refused permission may seek a court order; an LSLS acting
        officially is entitled to one. This room is mostly RPLSs, and the
        stronger verb on a projector is a promise the statute does not make to
        the people reading it.
        """
        self.assertIn("may seek a court order", plain(self.memo))
        self.assertIn("may seek a court order", plain(self.said))
        self.assertNotIn("entitled to", plain(self.said))

    def test_the_statute_on_the_slide_is_the_rpls_section_and_not_the_lsls_one(self):
        """`test_deck.py` checks that a source is beside the claim at all. This
        checks it is the right one: § 1071.358 is the LSLS section and it is one
        character away from the RPLS's, which is the worst possible distance."""
        self.assertIn("§ 1071.3585", plain(self.memo))
        self.assertIn("§ 1071.3585", plain(self.said))

    def test_it_repeats_what_the_memo_says_it_is_not(self):
        for disclaimed in ("not a survey", "not a title search"):
            with self.subTest(claim=disclaimed):
                self.assertIn(f"It is {disclaimed}", plain(self.memo))
        self.assertIn("Not a survey. Not a title search.", self.said)

    def test_it_says_who_decides(self):
        """The last line of the memo and the last bullet of the slide, and the
        session's whole thesis in five words. The tool decides nothing."""
        self.assertIn("An RPLS reads it and decides", plain(self.memo))
        self.assertIn("**An RPLS reads it and decides**", self.said)


class TestTheFlaggedParcelSlideIsTheTableS(unittest.TestCase):
    """Eight of 524, seven of them with no number at all."""

    def setUp(self):
        self.flagged = flagged()
        self.said = on_screen("The flagged parcel table")

    def test_the_counts_on_the_slide_are_the_runs(self):
        self.assertEqual(len(run()["parcels"]), 524)
        self.assertEqual(len(self.flagged), 8)
        self.assertIn(
            f"**{len(self.flagged)} of {len(run()['parcels'])} tracts** cost time",
            self.said,
        )

    def test_the_count_with_no_number_is_tallied_rather_than_quoted(self):
        """Seven is a count of rows, so it is counted off the run.

        Reading it out of the table's own prose would compare a sentence with
        itself and pass on a day when the tracts changed and the sentence did
        not.
        """
        unmeasured = [p for p in self.flagged if p.get("max_lead_time_days") is None]
        self.assertEqual(len(unmeasured), 7)
        self.assertIn(
            f"{len(unmeasured)} of the {len(self.flagged)}", self.said
        )

    def test_the_unmeasured_rows_really_do_sort_above_the_measured_one(self):
        """The slide says *so it sorts first*, which is a claim about the table
        on the screen next to it.

        A tract whose wait nobody has measured needs the phone call before a
        tract whose wait is a known fourteen days, because the call is what
        turns the unknown into a date. Re-sort the table the obvious way --
        longest known wait at the top -- and the slide is wrong while both the
        table and the slide still look right.
        """
        waits = [row[3].strip().lower() for row in parcel_rows()]
        self.assertEqual(len(waits), len(self.flagged))
        measured = [n for n, wait in enumerate(waits) if "not found" not in wait]
        unmeasured = [n for n, wait in enumerate(waits) if "not found" in wait]
        self.assertTrue(measured and unmeasured, "the table no longer has both kinds")
        self.assertLess(max(unmeasured), min(measured))
        self.assertIn("Unmeasured, so it sorts first", self.said)

    def test_the_cemetery_wait_and_its_statute_are_the_tables(self):
        """A notice period is the plainest number with legal consequence there
        is. A crew that rolls on day 13 is a crew that trespassed, so the days
        and the section both come off the table rather than out of memory."""
        _flag, wait, source = source_row("cemetery")
        self.assertEqual(wait, "14 calendar days")
        self.assertIn("Tex. Health & Safety Code § 711.041(c)(2)", source)
        self.assertIn(f"Cemetery, **{wait}**", self.said)
        self.assertIn("Tex. Health & Safety Code § 711.041(c)(2)", self.said)

    def test_the_school_wait_is_still_not_found_rather_than_a_number(self):
        """If somebody ever finds a published school notice period, this fails
        and the slide gets rewritten. That is the point of checking it."""
        _flag, wait, _source = source_row("school")
        self.assertEqual(wait, "not found")
        self.assertIn(f"School, **{wait}**", self.said)

    def test_the_slide_never_turns_not_found_into_a_zero_a_blank_or_a_no(self):
        """The distinction the whole slide exists for.

        `unknown` written as `no` sends a crew to a locked gate. The table
        refuses to print a blank, a dash or a zero in its wait column, and a
        slide describing that table must not do it either.
        """
        said = visible(
            [s for s in act_three() if s.heading == "The flagged parcel table"]
        )
        for softer in ("0 days", "no wait", "no notice", "none", "n/a"):
            with self.subTest(wording=softer):
                self.assertNotIn(softer, said.lower())

    def test_it_puts_the_two_words_the_room_has_to_keep_apart_on_the_slide(self):
        self.assertIn("`unknown` is never written as `no`", self.said)

    def test_it_names_the_two_that_cannot_be_screened_at_all(self):
        """Not a caveat. A blank where a gate should be reads as clear."""
        self.assertIn("Gated access and livestock **cannot be screened**", self.said)

    def test_the_run_really_does_say_so_and_the_slide_credits_the_run(self):
        """The hole #84's own review found, and the reason this check exists.

        The first draft said *and it says so* under a source line naming only
        `flagged-parcels.md`. The table says nothing of the kind and never
        could: it lists tracts that were flagged, and the whole point of these
        two is that nothing can flag them. The sentence lives in the run, under
        `not_screenable`, with a reason beside each one.

        The old check read the slide's own wording and nothing else, so it was
        circular -- it would have passed a slide crediting any document at all.
        This reads the run.
        """
        recorded = {entry["type"]: entry["reason"]
                    for entry in run()["run"]["not_screenable"]}
        self.assertEqual(set(recorded), {"gated access", "livestock"})
        for kind, reason in recorded.items():
            with self.subTest(kind=kind):
                self.assertIn("no public source publishes", reason)
        self.assertIn("The run says so", self.said)
        self.assertIn("project-sh16/screening.json", self.said)


class TestTheCrewDaySlideIsTheBuildUpS(unittest.TestCase):
    """Arguable math, and the handle is what makes it arguable."""

    def setUp(self):
        self.said = on_screen("The crew-day build-up")
        self.slide = [s for s in act_three()
                      if s.heading == "The crew-day build-up"][0]

    def test_every_handle_it_names_is_a_real_handle(self):
        real = rate_handles()
        self.assertTrue(real, "no rate handles found in the build-up at all")
        named = set(HANDLE.findall(self.said))
        self.assertTrue(named, "the slide names no handle, which is its whole point")
        for handle in named:
            with self.subTest(handle=handle):
                self.assertIn(handle, real, f"{handle} is not a rate in the build-up")

    def test_the_range_it_offers_the_room_is_the_range_that_exists(self):
        """`A1` to `A12` is an invitation to go and find any of the twelve. A
        thirteenth rate added without this slide changing makes the invitation
        quietly short."""
        real = rate_handles()
        self.assertEqual(len(real), 12)
        self.assertIn("`A1` to `A12`", self.said)

    def test_a_handle_quoted_beside_a_rate_is_quoted_beside_its_own_rate(self):
        """The one error on this block a surveyor would catch first.

        `A4` is a real handle and `0.75` is a real number, so *start with `A4` —
        0.75 hours per tract* reads perfectly and is wrong: 0.75 is `A1`'s. This
        ties a handle to the value its own row gives it.

        **This is a guard rather than a requirement**, and today it guards
        nothing: the slide names its handles as a range and quotes no rate
        beside one, because the money slide already gave this room `A4` and its
        half hour. That is deliberate -- see the class below. A handle named
        with no number beside it is not a quote, so it is not checked. The guard
        stays because the first draft of this slide did quote one, and the next
        edit may again.
        """
        values = rate_values()
        self.assertTrue(values, "the build-up's rate table no longer reads")
        for line in self.slide.content_lines():
            for handle in set(HANDLE.findall(line)):
                on_the_line = quantities_on(line)
                if not on_the_line:
                    continue
                with self.subTest(handle=handle, line=line):
                    self.assertTrue(
                        values.get(handle, set()) & on_the_line,
                        f"the slide shows {handle} beside {sorted(on_the_line)}, "
                        f"and the build-up gives it {sorted(values.get(handle, ()))}",
                    )

    def test_that_guard_can_actually_fail(self):
        """A guard that guards nothing today should still be shown to work.

        Without this, the check above is a comment: it would go on passing if
        the arithmetic under it broke, and nobody would find out until a slide
        quoted the wrong rate on a projector.
        """
        values = rate_values()
        wrong = sorted(values["A1"] - values["A4"])
        self.assertTrue(wrong, "A1 and A4 now carry the same value, so pick another pair")
        line = f"- Start with `A4` — {wrong[0]} hours on every one of 524 tracts"
        self.assertFalse(values["A4"] & quantities_on(line))

    def test_it_promises_the_rates_are_a_firms_to_replace(self):
        """Act III is the block about documents a principal can use, so the
        take-home is that these twelve are editable without any Python. The
        file is plain text and the build-up says which file."""
        self.assertIn("plain text a firm edits without touching any Python",
                      plain(text_of(BUILD_UP)))
        self.assertIn("Twelve rates, all plain text", self.said)

    def test_the_unmeasured_input_count_is_the_build_ups_own(self):
        """Five of twelve, and they are the point of the slide rather than a
        caveat on it. Those lines carry no total, and the hours are missing
        from the figures rather than being zero in them."""
        self.assertIn("**5 of these 12 inputs were never measured**", text_of(BUILD_UP))
        self.assertIn("**5 of the 12 inputs were never measured.**", self.said)
        self.assertIn("not a zero", self.said)

    def test_every_number_on_the_slide_is_one_the_build_up_publishes(self):
        """The blunt net under the named checks above.

        A figure invented here is a figure said out loud to a room that prices
        this work for a living. A line carrying its own source is allowed its
        own digits, and a handle is not a quantity.
        """
        published = numbers_it_publishes()
        for line in self.slide.content_lines():
            if A_SOURCE_ON_A_LINE.search(line):
                continue
            for number in quantities_on(line):
                with self.subTest(number=number, line=line):
                    self.assertIn(
                        number, published,
                        f"the slide shows {number!r}, which is in no line of the "
                        f"crew-day build-up and carries no source of its own",
                    )

    def test_it_says_the_rates_are_published_by_nobody(self):
        """TxDOT publishes no production rates. The standard sheets say what
        goes on the road, not how long it takes to put it there, and a room
        that hears twelve rates read out will assume somebody stands behind
        them."""
        self.assertIn("none of them is published by TxDOT or by anybody else",
                      plain(text_of(BUILD_UP)))
        self.assertIn("published by nobody", self.said)

    def test_it_says_nothing_the_money_slide_already_said(self):
        """The block runs eighteen minutes and this slide is on the cut line.

        At 0:46 this room was given the day counts, `A4` by name, and the
        half-hour-per-tract figure behind it -- `test_money_slide.py` holds that
        slide to all three. Saying them twice is how a block that fits becomes a
        block that does not.

        **The first draft said two of the three**, and #84's review caught it:
        *Start with `A4` — 0.5 hours on every one of 524 tracts* is the money
        slide's own sentence in different words. So this reads the money slide
        rather than listing what not to repeat, and a phrase moved onto that
        slide tomorrow is a phrase this one may not carry.
        """
        totals = figures()
        for count, what in ((totals.field_days, "crew-days in the field"),
                            (totals.office_days, "days in the office")):
            with self.subTest(figure=count):
                self.assertIsNone(
                    re.search(rf"\b{count}\b", self.said),
                    f"the crew-day slide reads the money slide's {what} out again",
                )

    def test_it_does_not_re_argue_the_rate_the_money_slide_argued(self):
        """`A4` and its half hour belong to 0:46. Read out of that slide rather
        than written down here, so the two cannot drift apart."""
        money = on_screen("The billable-hour math")
        argued = set(HANDLE.findall(money))
        self.assertTrue(argued, "the money slide no longer names a rate to argue with")
        for handle in argued:
            with self.subTest(handle=handle):
                self.assertNotIn(
                    f"`{handle}` —", self.said,
                    f"the money slide already put {handle} and its rate in front "
                    f"of this room, thirty minutes before this slide",
                )

    def test_the_note_tells_the_presenter_the_same_thing(self):
        said = note("The crew-day build-up")
        self.assertIn("says nothing the money slide already said", said)
        self.assertIn("Do not read any of that out again", said)


class TestTheBlockIsStillTheShapeTheRunOfShowGivesIt(unittest.TestCase):

    def test_none_of_its_slides_is_still_a_placeholder(self):
        for slide in act_three():
            with self.subTest(slide=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_the_three_this_work_order_owns_are_all_there_and_in_order(self):
        self.assertEqual([slide.heading for slide in act_three()], list(OWNED))

    def test_every_path_on_one_of_its_slides_is_committed(self):
        """A half path reads as a whole one, and the room photographs the slide
        rather than the speaker note. #82's review found three."""
        for slide in act_three():
            for named in A_PATH.findall(with_markup([slide])):
                with self.subTest(slide=slide.heading, path=named):
                    self.assertTrue((REPO / named).exists(),
                                    f"{slide.heading!r} shows the room {named}")

    def test_every_slide_shows_the_room_the_document_it_is_framing(self):
        """Nobody in the room sees the speaker note.

        Each of these three slides describes a file, and a description with no
        file name on it is a description nobody can go and check afterwards --
        which is the only reason the repo is the deliverable.
        """
        for heading in OWNED:
            with self.subTest(slide=heading):
                self.assertTrue(
                    A_PATH.search(on_screen(heading)),
                    f"{heading!r} frames a document and never names it",
                )

    def test_the_cut_is_marked_on_the_crew_day_slide(self):
        """`test_deck.py` checks the cut line is marked somewhere in the deck.
        This checks it is marked on the slide the plan means, and that the
        fallback it names is a file rather than a plan to improvise."""
        said = note("The crew-day build-up")
        self.assertIn("Cut 2 of 3", said)
        self.assertIn("project-sh16/crew-day.md", said)

    def test_dropping_that_slide_still_leaves_the_block_its_point(self):
        """The cut has to be cheap. The build-up is committed, so the fallback
        is opening a file rather than rebuilding an argument on stage."""
        self.assertTrue((REPO / "project-sh16" / "crew-day.md").is_file())
        self.assertTrue((REPO / "project-sh16" / "crew-day.txt").is_file())

    def test_every_slide_of_the_block_names_a_fallback(self):
        for slide in act_three():
            with self.subTest(slide=slide.heading):
                self.assertIn("Fallback:", " ".join(slide.note.split()))

    def test_the_block_still_has_a_row_on_the_fallback_card_for_each_document(self):
        card = text_of(CARD)
        for row in ("Act III — the bid memo",
                    "Act III — the flagged parcels",
                    "Act III — the crew-day build-up"):
            with self.subTest(row=row):
                self.assertIn(row, card)


if __name__ == "__main__":
    unittest.main()
