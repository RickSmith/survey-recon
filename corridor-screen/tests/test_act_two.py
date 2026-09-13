"""The Act II slides, held to the run that produced their numbers.

Issue #83. Twenty-one minutes, and every figure on these five slides is read
back out of `project-sh16/screening.json`. This is the block where getting a
word wrong is expensive, because the words are the content: `MARK NOT FOUND`
against *monument destroyed* against *condition unknown*, and a record count
against a monument count.

**The stale set is checked for by name.** Until 2026-09-13 this repo said 13
NGS marks, 18 TxDOT control points and 27 ROW sheets. All three predated the
tool running: 13 is a radial call two miles off the corridor midpoint, 18 has
no capture behind it anywhere, and 27 is the county figure rather than the
corridor one. The account is issue #80. Any of them reappearing on a slide is
worse than an unchecked number, because each one is plausible and two of them
were on a projector.

**Two of the distinctions on these slides are definitions, not findings.** No
monument in this corridor is published destroyed and none is condition unknown
-- all four TxDOT records read `Good`. A room that hears the definitions will
assume they were found, so the slide says so and this file holds it to that.

**27 is not wrong, it is a different question.** SH16 across the whole of Bexar
County has 27 sheets; 69 reach this corridor and 15 of those are SH16's own.
Both figures are on the slide because a presenter who quotes one will be asked
about the other.
"""

import re
import unittest

from .deck_reader import A_PATH, REPO, note, on_screen, slides_in_block, with_markup
from .markdown_docs import flat, json_of, text_of

SCREENING = REPO / "project-sh16" / "screening.json"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
CAPTURE_NOTE = REPO / "docs" / "scenarios" / "sh16" / "capture-note.md"

BLOCK = "Act II — Find the control"

# What this repo said before the tool ran, and must never say again. Each is
# (the figure, the noun it was attached to, why it was wrong).
STALE = (
    ("13", "NGS marks", "a radial call two miles off the corridor midpoint"),
    ("18", "TxDOT", "no capture behind it anywhere, and it reads like a record count"),
)


def run():
    return json_of(SCREENING)


def act_two():
    """The content slides of the block, without its section break.

    The datum gap is in this block and is **not** this work order -- it landed
    under #33 and `test_datum_gap.py` owns it. It is left in the list on
    purpose, because the block's shape is a thing this file should notice
    changing.
    """
    return slides_in_block(BLOCK)


class TestTheNgsMarksAreTheRunS(unittest.TestCase):
    """Eleven marks, every one last reported as not found."""

    def setUp(self):
        self.risk = run()["control"]["recovery_risk"]
        self.said = on_screen("The NGS marks")

    def test_the_mark_count_is_the_run_s(self):
        self.assertEqual(self.risk["marks_in_corridor"], 11)
        self.assertIn(f"**{self.risk['marks_in_corridor']} marks in the corridor",
                      self.said)

    def test_the_slide_says_every_one_of_them_rather_than_most(self):
        """Several, most and many are all softer than the run, and the softer
        word is the one that lets an estimate assume recoverable control."""
        self.assertEqual(self.risk["mark_not_found"], self.risk["marks_in_corridor"])
        self.assertIn(f"All {self.risk['mark_not_found']} read `MARK NOT FOUND`",
                      self.said)

    def test_it_says_that_is_a_report_rather_than_a_verdict(self):
        self.assertIn("not a verdict", self.said)

    def test_it_refuses_to_let_the_count_read_as_control_in_hand(self):
        """`11 marks` reads as eleven things you have. It is eleven you may
        have to set -- CONTEXT.md says *may*, and so does the slide."""
        self.assertIn("is not 11 pieces of control you have", self.said)

    def test_the_condition_unknown_count_is_the_run_s_and_is_on_the_slide(self):
        """Zero is a finding here. A corridor where it is not zero has a gap
        nobody has measured, and the slide teaches the word either way."""
        self.assertEqual(self.risk["condition_unknown"], 0)
        self.assertIn("Nothing here was *condition unknown*", self.said)


class TestTheTxdotControlIsTheRunS(unittest.TestCase):
    """Four records, two monuments, all four published good."""

    def setUp(self):
        self.control = run()["control"]["txdot_control"]
        self.said = on_screen("The TxDOT control points")

    def test_both_counts_are_on_the_slide(self):
        """A record count is not a monument count, and the tool reports both
        rather than picking one. So does the slide."""
        self.assertEqual(self.control["points_in_corridor"], 4)
        self.assertEqual(self.control["distinct_stations"], 2)
        self.assertIn(
            f"**{self.control['points_in_corridor']} records in the corridor. "
            f"They name {self.control['distinct_stations']} distinct monuments**",
            self.said,
        )

    def test_it_says_which_of_the_two_a_crew_drives_to(self):
        self.assertIn("A crew drives to the monument", self.said)

    def test_the_condition_counts_are_the_run_s(self):
        self.assertEqual(self.control["destroyed"], 0)
        self.assertEqual(self.control["condition_unknown"], 0)
        self.assertEqual(self.control["by_condition"], {"Good": 4})

    def test_the_condition_word_on_the_slide_is_the_one_the_run_published(self):
        """The check this class shipped without, and a review found it.

        Asserting `by_condition == {"Good": 4}` compares the run with itself.
        A slide reading ``All 4 published `Destroyed` `` passed every test in
        this file. The word on the projector is the claim; this reads it.
        """
        published = list(self.control["by_condition"])
        self.assertEqual(len(published), 1, "the run now publishes more than one condition")
        word = published[0]
        self.assertIn(
            f"All {self.control['by_condition'][word]} published `{word}`",
            self.said,
            f"the slide does not say what the run published, which is {word!r}",
        )

    def test_it_says_none_of_those_conditions_carries_a_date(self):
        """An undated `Good` is weaker than a dated `MARK NOT FOUND`, and the
        slide before this one makes a point of the date. TxDOT publishes
        `last_recovered` and it is empty on every record here."""
        dated = [p for p in run()["control"]["txdot_points"] if p.get("last_recovered")]
        self.assertEqual(dated, [], "a TxDOT record now carries a recovery date")
        self.assertIn("**None carries a recovery date**", self.said)

    def test_the_slide_says_the_two_worse_words_were_not_found_here(self):
        """Bullets five and six define words. A room that hears a definition
        assumes it was found, so the slide has to say it was not."""
        self.assertIn("None destroyed and none unknown here", self.said)

    def test_it_still_teaches_both_words(self):
        for word in ("Monument destroyed", "Condition unknown"):
            with self.subTest(word=word):
                self.assertIn(word, self.said)

    def test_it_says_which_of_the_two_is_the_stronger_claim(self):
        self.assertIn("stronger claim than `MARK NOT FOUND`", self.said)


class TestTheRowSheetsAreTheRunS(unittest.TestCase):
    """69 reach the corridor, 15 of them SH16's own, and 27 is the county."""

    def setUp(self):
        self.maps = run()["row_maps"]
        self.said = on_screen("The right-of-way map sheets")

    def test_the_corridor_figure_is_the_run_s(self):
        self.assertEqual(self.maps["sheet_count"], 69)
        self.assertIn(f"**{self.maps['sheet_count']} sheets reach this corridor",
                      self.said)

    def test_the_routes_own_sheets_are_the_run_s(self):
        own = self.maps["by_route"]["SH0016"]
        self.assertEqual(own["sheet_count"], 15)
        self.assertIn(f"{own['sheet_count']} of them are SH16's own", self.said)

    def test_the_rest_add_up_to_what_the_slide_says(self):
        """54 is not in the run as a number; it is 69 less SH16's 15. A slide
        that states it has done arithmetic, so the arithmetic is checked."""
        others = self.maps["sheet_count"] - self.maps["by_route"]["SH0016"]["sheet_count"]
        self.assertEqual(others, 54)
        self.assertIn(f"The other {others} belong to the crossing routes", self.said)

    def test_the_dates_on_the_slide_are_the_routes_own(self):
        span = self.maps["by_route"]["SH0016"]["date_range"]
        self.assertIn(span["from"][:4], self.said)
        self.assertIn(span["to"][:4], self.said)

    def test_the_county_figure_is_on_the_slide_and_marked_as_the_county(self):
        """Both numbers are right and a presenter who quotes one gets asked
        about the other."""
        self.assertIn("Across all of Bexar County SH16 has **27**", self.said)
        self.assertIn("Both are right", self.said)

    def test_the_county_figure_matches_the_page_that_works_it_through(self):
        said = flat(text_of(REPO / "docs" / "data-sources" / "row-map-sheets.md"))
        self.assertIn("27", said)


class TestTheStaleFiguresNeverComeBack(unittest.TestCase):
    """13 marks, 18 control points, 27 sheets-as-the-corridor. Issue #80.

    Each was plausible, each predated the tool running, and two of them were on
    a projector. A wrong number that has already been believed once is the one
    worth a check of its own.
    """

    def test_no_act_two_slide_states_a_figure_from_the_old_set(self):
        said = with_markup(act_two())
        for figure, noun, why in STALE:
            with self.subTest(figure=figure, noun=noun):
                self.assertIsNone(
                    re.search(rf"\b{figure}\b[^.\n]*{re.escape(noun)}", said),
                    f"an Act II slide states {figure} {noun}. That figure is "
                    f"stale -- {why}. See issue #80.",
                )

    def test_the_sheet_count_is_never_the_county_one_called_a_corridor(self):
        said = on_screen("The right-of-way map sheets")
        self.assertIsNone(
            re.search(r"\b27 sheets reach", said),
            "27 is SH16 across the whole county, not what reaches this corridor",
        )


class TestWhatWeAskedItToFindIsWhatItDid(unittest.TestCase):
    """The opening slide states two things about the run itself."""

    def setUp(self):
        self.document = run()
        self.said = on_screen("What we asked it to find")

    def test_the_service_count_is_the_run_s(self):
        self.assertEqual(len(self.document["services"]), 14)
        self.assertIn("Fourteen services", self.said)

    def test_every_one_of_them_really_did_answer(self):
        """`Every one answered` is a claim about fourteen services, and the
        tool is built for the other outcome -- a dead service stops the run."""
        unanswered = [s["name"] for s in self.document["services"]
                      if s.get("status") != "ok"]
        self.assertEqual(unanswered, [])
        self.assertIn("Every one answered", self.said)

    def test_the_run_really_did_finish_complete(self):
        """`incomplete` is a real outcome of this tool and says so in the file.
        A slide claiming complete when the run stopped early is the worst kind
        of wrong, because it is the kind nobody checks."""
        self.assertEqual(self.document["run"]["status"], "complete")
        self.assertIn("the run finished complete", self.said)

    def test_it_says_no_client_data_on_its_own_face(self):
        """A governance point disguised as a technical one, and the one claim
        on this slide a principal will repeat to their insurer."""
        self.assertIn("**No client data, ever**", self.said)


class TestTheLiveCallClaimsOnlyWhatItIs(unittest.TestCase):

    def test_the_slide_marks_its_figure_as_last_time_rather_than_a_promise(self):
        """It is a live call. It finds what it finds."""
        self.assertIn("Last time", on_screen("The one genuinely live call"))

    def test_the_five_is_the_capture_note_s_five(self):
        """**This one figure is not in `screening.json`**, and the work order
        asks for every number to come from the run.

        It cannot: the live cross-check is a separate command from the
        screening run, on purpose, so that a dead network costs only this
        moment. So it is held to the committed account of that run instead --
        `docs/scenarios/sh16/capture-note.md` -- and the exception is written
        down here rather than left for somebody to notice.
        """
        self.assertIn("Five marks appear in both. All five conditions agree",
                      flat(text_of(CAPTURE_NOTE)))
        self.assertIn("**5 marks in both, and all 5 conditions agreed**",
                      on_screen("The one genuinely live call"))

    def test_the_note_says_it_is_a_cross_check_rather_than_a_replay(self):
        """A recording agreeing with itself proves nothing. The live call asks
        NGS today and compares it with what NGS said in September."""
        self.assertIn("not a recording agreeing with itself",
                      note("The one genuinely live call"))

    def test_the_note_says_losing_it_costs_only_the_live_moment(self):
        said = note("The one genuinely live call")
        self.assertIn("screening run is unaffected", said)


class TestTheBlockIsStillTheShapeTheRunOfShowGivesIt(unittest.TestCase):

    def test_none_of_its_slides_is_still_a_placeholder(self):
        for slide in act_two():
            with self.subTest(slide=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_the_five_this_work_order_owns_are_all_there(self):
        """The datum gap is the sixth and belongs to #33."""
        headings = [s.heading for s in act_two()]
        for wanted in ("What we asked it to find", "The NGS marks",
                       "The TxDOT control points", "The right-of-way map sheets",
                       "The one genuinely live call"):
            with self.subTest(slide=wanted):
                self.assertIn(wanted, headings)

    def test_every_path_on_one_of_its_slides_is_committed(self):
        """A half path reads as a whole one, and the room photographs the
        slide rather than the speaker note. #82's review found three."""
        for slide in act_two():
            for named in A_PATH.findall(with_markup([slide])):
                with self.subTest(slide=slide.heading, path=named):
                    self.assertTrue((REPO / named).exists(),
                                    f"{slide.heading!r} shows the room {named}")

    def test_every_slide_that_states_a_figure_shows_where_it_came_from(self):
        """Nobody in the room sees the speaker note.

        Three of these five slides carry counted figures, and each has to say
        on its own face where they came from. Deleting the source line off the
        NGS slide used to fail nothing at all.
        """
        carrying_figures = ("The NGS marks", "The TxDOT control points",
                            "The right-of-way map sheets")
        for heading in carrying_figures:
            with self.subTest(slide=heading):
                self.assertTrue(
                    A_PATH.search(on_screen(heading)),
                    f"{heading!r} states counted figures and shows the room no "
                    f"source for them",
                )

    def test_the_block_still_has_its_row_on_the_fallback_card(self):
        self.assertIn("Act II — find the control", text_of(CARD))


if __name__ == "__main__":
    unittest.main()
