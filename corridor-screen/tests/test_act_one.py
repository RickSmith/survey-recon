"""The Act I slides, held to the grilling they describe.

Issue #82. Sixteen minutes, five slides, and the hinge of the session. Three of
the five are holding cards for a live run; the two that carry content carry
numbers, and every one of those numbers is counted out of
`corridor-screen/captures/the-grilling/` rather than read out of its prose.

**Counted, not matched.** The capture's README states "nineteen questions" and
"thirteen of the nineteen" in its own sentences, and a check comparing the slide
to those sentences would be comparing two things somebody typed. So these count
the rows of the captured tables. The first draft of this file did match a
substring for the work-order figures, and review proved it: a scratch deck
saying **350 work orders** passed. It counts the rows now.

**Two counts overlap, and that is the trap.** Thirteen answers said "your
recommendation" and five changed the shape of the tool, and Q14 is in both -- it
says "your recommendation" and then adds a condition. Thirteen and five do not
add to eighteen. Somebody in the second row will check.

**Two claims here are about honesty rather than accuracy.** The captured run is
a *transcript, not a recording* -- there is no video and there never was -- and
that run never ran `/to-tickets` at all, so the work orders are captured as a
**result** rather than as a run. The work order for these slides is explicit
that nothing may imply otherwise, and a speaker note is where that would slip.

Nothing here defines its own reader. `deck_reader` already owns the deck and
`markdown_docs` already owns reading a committed page; a third copy of either
would drift the first time somebody fixed one of them.
"""

import re
import unittest

from .deck_reader import REPO, noted, slide_headed, slides, with_markup
from .markdown_docs import flat, text_of

CAPTURES = REPO / "corridor-screen" / "captures" / "the-grilling"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"

BLOCK = "Act I — The grilling"

# One row of the captured question table: the number, and what Rick answered.
A_QUESTION = re.compile(r"^\|\s*\*\*(Q\d+)\*\*\s*\|.*?\|.*?\|(.*?)\|\s*$", re.M)

# One row of the captured work-order table: the issue number, and the time
# GitHub stamped it. Those stamps are the part of that file nothing later can
# edit, which is why the figures are counted off them.
A_TICKET = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d\d:\d\d:\d\d)\s*\|", re.M)

# What an answer says when the human took the agent's proposal.
DELEGATED = "your recommendation"

# What an answer says when the human changed the tool. Four verbs, because
# those are the four the capture uses. A fifth appearing is something a reader
# should have to look at rather than something to match loosely.
CHANGED = re.compile(r"\*\*(Widened|Overrode|Added|Cut)")


def answers():
    """Every question in the capture, as (number, what Rick answered)."""
    return A_QUESTION.findall(text_of(CAPTURES / "README.md"))


def tickets():
    """Every work order in the capture, as (issue number, time stamped)."""
    return A_TICKET.findall(text_of(CAPTURES / "the-tickets.md"))


def seconds_they_took():
    """How long the run took, off the first and last stamp rather than prose."""
    stamps = sorted(when for _number, when in tickets())
    first, last = (
        [int(part) for part in stamps[0].split(":")],
        [int(part) for part in stamps[-1].split(":")],
    )
    return (last[0] - first[0]) * 3600 + (last[1] - first[1]) * 60 + last[2] - first[2]


def act_one():
    """The five content slides of the block.

    The section break at its head belongs to the block too and carries the same
    note, so it is dropped here -- what this file checks is the slides that
    carry content, and a break carries a name and a clock.
    """
    return [s for s in slides()
            if noted(s) and noted(s).label == BLOCK and not s.is_a_break]


def on_screen(heading):
    """What the room sees on one slide, markup and all, note taken out."""
    return with_markup([slide_headed(heading)])


def note(heading):
    """That slide's note as one line, so a phrase survives the hard wrapping."""
    return flat(slide_headed(heading).note)


class TestTheNumbersAreTheGrillingS(unittest.TestCase):
    """Counted off the captured tables, never read out of their prose."""

    def test_the_capture_still_holds_nineteen_questions(self):
        """If this fails, the rest of this file is measuring something else."""
        self.assertEqual(len(answers()), 19)

    def test_the_question_count_is_on_the_slide(self):
        self.assertIn(f"**{len(answers())} questions**",
                      on_screen("What the grilling is"))

    def test_the_delegated_count_is_the_one_the_capture_holds(self):
        delegated = [q for q, said in answers() if DELEGATED in said.lower()]
        self.assertEqual(len(delegated), 13)
        self.assertIn(f"**{len(delegated)} of the {len(answers())} answers**",
                      on_screen("Why this is the hinge"))

    def test_the_overridden_count_is_the_one_the_capture_holds(self):
        changed = [q for q, said in answers() if CHANGED.search(said)]
        self.assertEqual(len(changed), 5)
        self.assertIn(f"**{len(changed)} answers changed the shape of the tool.**",
                      on_screen("Why this is the hinge"))

    def test_the_two_counts_really_do_overlap(self):
        """Thirteen and five do not add to eighteen, and the note has to say
        why before somebody in the second row works it out."""
        delegated = {q for q, said in answers() if DELEGATED in said.lower()}
        changed = {q for q, said in answers() if CHANGED.search(said)}
        self.assertEqual(sorted(delegated & changed), ["Q14"])
        self.assertIn("overlap", note("Why this is the hinge").lower())

    def test_the_work_order_count_is_the_rows_the_capture_has(self):
        """Counted, because `assertIn("35", ...)` passes for 350.

        That is not hypothetical -- it is what the first draft of this check
        did, and a review caught it by mutating the slide.
        """
        said = on_screen("Live: from a scope to work orders")
        self.assertEqual(len(tickets()), 35)
        self.assertIn(f"**{len(tickets())} work orders", said)

    def test_the_span_is_the_one_github_stamped(self):
        said = on_screen("Live: from a scope to work orders")
        self.assertEqual(seconds_they_took(), 89)
        self.assertIn(f"in {seconds_they_took()} seconds**", said)

    def test_the_numbers_they_run_between_are_the_captured_ones(self):
        numbered = sorted(int(number) for number, _when in tickets())
        said = on_screen("Live: from a scope to work orders")
        self.assertIn(f"numbered {numbered[0]} to {numbered[-1]}", said)


class TestNothingClaimsMoreThanTheCaptureCan(unittest.TestCase):
    """The two honesty rules the work order names, checked where they break."""

    def test_the_transcript_is_never_called_a_recording(self):
        """There is no video of that session and there never was."""
        self.assertIn("transcript, not a recording", note("Live: the interview"))

    def test_the_tickets_note_says_they_are_a_result_not_a_run(self):
        """That run never ran /to-tickets at all."""
        said = note("Live: from a scope to work orders").lower()
        self.assertIn("not a recording of one", said)

    def test_the_captured_figures_are_marked_as_past_rather_than_promised(self):
        """A live run asks what it asks and writes what it writes. A slide
        that promises 35 has promised a number nobody controls."""
        self.assertIn("Last time", on_screen("Live: from a scope to work orders"))
        self.assertIn("past fact, not a promise",
                      note("Live: from a scope to work orders"))

    def test_the_question_count_is_not_promised_live_either(self):
        self.assertIn("Do not promise", note("What the grilling is"))


class TestTheHoldingCardsStayOutOfTheWay(unittest.TestCase):
    """The room learns more from watching the questions arrive than from any
    description of them, so a holding card that invites reading is a holding
    card competing with the demo."""

    HOLDING = ("Live: the interview",
               "Live: from answers to a scope of work",
               "Live: from a scope to work orders")

    # The heading, and what the room may read under it. Counted across every
    # visible line rather than only the bullets: the first draft counted lines
    # beginning with a hyphen, which let a slide grow a paragraph and a source
    # line without tripping anything.
    MOST_LINES_UNDER_A_HEADING = 4

    def test_no_holding_card_gives_the_room_more_than_four_lines(self):
        for heading in self.HOLDING:
            with self.subTest(slide=heading):
                seen = [line for line in on_screen(heading).splitlines()
                        if line.strip() and not line.startswith("#")]
                self.assertLessEqual(
                    len(seen), self.MOST_LINES_UNDER_A_HEADING,
                    f"{heading!r} gives the room {len(seen)} lines to read. It "
                    f"is a holding card for a live run, and the demo is the "
                    f"content.",
                )

    def test_every_holding_card_says_it_is_one_in_its_note(self):
        for heading in self.HOLDING:
            with self.subTest(slide=heading):
                self.assertIn("Live block", note(heading))


class TestTheHingeStandsOnItsOwn(unittest.TestCase):
    """If Act I is ever reduced, this is the slide that survives. So it has to
    make the argument without the four slides before it."""

    def test_it_says_the_work_before_the_agent_starts_is_what_decides(self):
        self.assertIn("before the agent starts", on_screen("Why this is the hinge"))

    def test_it_reaches_for_something_the_room_already_does(self):
        """Not condescending about the programming gap means arguing from what
        they already know. A party chief is the parallel."""
        self.assertIn("party chief", on_screen("Why this is the hinge"))

    def test_it_carries_its_source_on_its_face(self):
        """Two counted figures, and nobody in the room sees the note."""
        self.assertIn("corridor-screen/captures/the-grilling",
                      on_screen("Why this is the hinge"))


class TestEveryOnSlideSourceIsAPathThatOpens(unittest.TestCase):
    """`test_deck.py` holds the speaker notes to this and reads only the notes.

    The citation the room photographs off the projector is the one nothing was
    guarding, and three of these slides shipped a half path -- `captures/...`,
    which is not where that folder is.
    """

    A_PATH = re.compile(r"(?<![\w/.-])((?:corridor-screen|docs|project-sh16)/[\w./-]+)")

    def test_every_path_on_an_act_one_slide_is_committed(self):
        for slide in act_one():
            for named in self.A_PATH.findall(with_markup([slide])):
                with self.subTest(slide=slide.heading, path=named):
                    self.assertTrue(
                        (REPO / named).exists(),
                        f"{slide.heading!r} shows the room {named}, which is "
                        f"not there. A half path reads as a whole one.",
                    )


class TestTheBlockIsStillTheShapeTheRunOfShowGivesIt(unittest.TestCase):

    def test_there_are_five_slides_in_it(self):
        self.assertEqual(len(act_one()), 5)

    def test_none_of_them_is_still_a_placeholder(self):
        for slide in act_one():
            with self.subTest(slide=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_the_block_has_a_row_on_the_fallback_card(self):
        """A block with a fallback has to say so where a presenter looks."""
        self.assertIn("Act I — the grilling", text_of(CARD))

    def test_a_note_in_the_block_sends_a_presenter_to_what_the_card_names(self):
        """The card's row for this block names the captured grilling. At least
        one note has to send a presenter to the same place, because the note is
        what is on the presenter's screen when the demo dies."""
        said = " ".join(flat(slide.note) for slide in act_one())
        self.assertIn("corridor-screen/captures/the-grilling/README.md", said)


if __name__ == "__main__":
    unittest.main()
