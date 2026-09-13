"""The three closing slides, held to the form and the pages they hand a room.

Issue #86. Six minutes, three slides, and the plan of record puts this block on
the **never cut** list — it is what the room leaves with.

**The risk here is different again from the three Acts'.** Act II's danger is a
stale figure and Act III's is a slide describing a document that changed under
it. Nothing on these three slides is a figure at all. What they carry is
*instructions*: go to this page, write that policy, open this form. So the way
they go wrong is by sending three hundred people somewhere that is not there —
a page renamed, a form field that stopped being required, a short link nobody
ever made.

**The last one is the reason this file exists.** The QR code and the short link
are #10, then #38, and neither has landed. A slide that says *scan the code*
works perfectly in rehearsal, on a laptop, with the repo already open. It fails
in a ballroom in front of the people this session is for. So the close is held
to offering a way in that can be **typed**, and to promising no code and no
short link until somebody has made one.

**The second reason is the network.** This block cannot collect a single reply
without GitHub, and that is fine — the ask survives being done from a seat that
evening. The slide has to say so on its face, because nobody in the room sees
the speaker note.

**What is deliberately not checked here.** The clock, the break slide, the cut
marks and the canvas budget all belong to `test_deck.py`, which holds every
block to the run of show. This file reads the three slides against the four
documents they point at, and nothing else.
"""

import re
import unittest

from tests.deck_reader import A_PATH, REPO, note, on_screen, slides_in_block, with_markup
from tests.markdown_docs import flat, plain, text_of

FORM = REPO / ".github" / "ISSUE_TEMPLATE" / "introduce-yourself.yml"
PLAN = REPO / "docs" / "plan-of-record.md"
PRINCIPALS = REPO / "docs" / "for-principals" / "index.md"
POLICY = REPO / "docs" / "governance" / "ai-use-policy.md"
NEVER_LEAVES = REPO / "docs" / "governance" / "what-never-leaves.md"
SEAL = REPO / "docs" / "governance" / "seal-and-responsible-charge.md"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
README = "corridor-screen/README.md"

BLOCK = "Accountability · Monday morning · the live issue"

# The three slides this work order owns, in the order the block runs them.
OWNED = ("The pattern, said out loud", "Monday morning", "Introduce yourself")

# The pattern, wherever it is written down: four steps joined by arrows. The
# steps themselves are captured rather than spelled out, so the check below
# compares the slide with the documents instead of with this file.
#
# **The emphasis is what marks where the fourth step stops.** Both documents
# write the pattern as one bold phrase, on purpose -- a reader is meant to see
# four steps as a single thing rather than as four clauses of the sentence
# around them. Without that closing `**` the fourth group swallows the rest of
# the sentence, which is exactly what the first draft of this file did.
AN_ARROW_SENTENCE = re.compile(
    r"\*\*([\w ]+?)\s*→\s*([\w ]+?)\s*→\s*([\w ]+?)\s*→\s*([\w ]+?)\*\*"
)

# The form is read as text rather than parsed as YAML on purpose. `CLAUDE.md`:
# *"Do not add a Node dependency to anything attendees run"*, and the same
# reasoning retires PyYAML here — the standard library has no YAML reader, and
# a test suite an attendee cannot run is a test suite that does not hold
# anything. What is checked is flat enough to read with a regex: one field's
# block, and whether `required: true` is inside it.
def field_block(name):
    """The lines of one form field, from its `id:` to the next field.

    A missing field is the drift this file exists to catch, so it says which
    field went missing. The first draft used `str.index`, which raises a bare
    `ValueError` -- the same failure, reported as a crash in the test rather
    than as a finding about the form.
    """
    text = text_of(FORM)
    start = text.find(f"id: {name}")
    if start < 0:
        raise AssertionError(f"the introduce-yourself form has no field {name!r}")
    rest = text[start:]
    ends = re.search(r"\n  - type:", rest)
    return rest[: ends.start()] if ends else rest


def close_slides():
    """The content slides of the block, without its section break."""
    return slides_in_block(BLOCK)


def said_on(heading):
    """What the room sees on one slide of this block, markup and all.

    **`exactly` is not optional here, and this block is why that argument
    exists.** The section break is headed *Accountability · Monday morning ·
    the live issue* and the second slide is headed *Monday morning*, so
    `on_screen`'s ordinary substring reading finds two slides and refuses to
    guess. The exact reading was written as a private copy in this file until
    the review of #86 pointed out that `deck_reader` already claims that job.
    """
    return on_screen(heading, exactly=True)


def steps_of(document):
    """The four steps of the pattern, as one document writes them."""
    found = AN_ARROW_SENTENCE.search(flat(text_of(document)))
    if not found:
        raise AssertionError(f"{document.name} no longer writes the pattern out")
    return [step.strip().lower() for step in found.groups()]


class TestThePatternIsTheOneTwoOtherDocumentsAlreadyWrote(unittest.TestCase):
    """Four steps, and they are written down in two places already."""

    def setUp(self):
        self.said = said_on("The pattern, said out loud")

    def test_the_form_and_the_plan_write_the_same_four_steps(self):
        """The pattern is the session's one portable claim, so it is worth
        knowing that the two documents making it have not drifted apart.

        The plan of record makes it in the run of show. The form's own closing
        paragraph makes it to whoever fills the form in, weeks later, with no
        presenter in the room.
        """
        self.assertEqual(steps_of(PLAN), steps_of(FORM))

    def test_the_slide_says_those_four_steps_in_that_order(self):
        """Read out of the form rather than listed here.

        Writing the four words in this file would be a third copy, and a third
        copy is the one that drifts. This asks the form what the steps are and
        then asks the slide whether it says them, in order.
        """
        said = plain(self.said).lower()
        at = []
        for step in steps_of(FORM):
            with self.subTest(step=step):
                self.assertIn(step, said, f"the slide drops {step!r} from the pattern")
            at.append(said.index(step))
        self.assertEqual(at, sorted(at), "the slide runs the four steps out of order")

    def test_it_keeps_the_two_examples_the_form_offers(self):
        """*A ranch boundary and an ALTA* is what makes the pattern portable to
        a room that will never price a highway. It is the form's own sentence,
        and the slide is where the room first hears it."""
        form = plain(text_of(FORM))
        for example in ("ranch boundary", "ALTA"):
            with self.subTest(example=example):
                self.assertIn(example.lower(), form.lower())
                self.assertIn(example.lower(), plain(self.said).lower())

    def test_it_says_what_makes_the_pattern_worth_anything(self):
        """Not that it finds things. That it says what it could not check.

        This is the thesis of the whole session on one bullet, and the first
        draft of the slide left it off — four steps and two examples read as a
        sales pitch without it.
        """
        self.assertIn("could not check", plain(self.said))

    def test_it_sends_the_room_at_something_it_can_run_and_something_it_can_read(self):
        """A pattern with no file beside it is a slide nobody can check
        afterwards, which is the only reason the repo is the deliverable."""
        self.assertIn(README, self.said)
        self.assertIn("project-sh16/bid-memo.md", self.said)


class TestMondayMorningSendsThemAtPagesThatSayThat(unittest.TestCase):
    """Four instructions, and every one of them is a page in this repo.

    The block is for buyers and risk-owners rather than operators, so each
    bullet is checked against the page that carries the long version.
    """

    def setUp(self):
        self.said = said_on("Monday morning")

    def test_it_gives_the_same_instruction_the_principals_brief_gives(self):
        """One person, and the slide has to say **what** to point them at.

        The brief can write *point one person at this*, because a reader of the
        brief is already on the page. A room is not, and nobody out there sees
        the speaker note -- so *point one person at it* is a pronoun with
        nothing behind it, which is what #86's review found. The slide names
        the repo.

        The test used to be named for an equality it did not check, which is
        its own small version of the same fault.
        """
        self.assertIn("Point one person at this. Not the office.",
                      plain(text_of(PRINCIPALS)))
        said = plain(self.said)
        self.assertIn("Point one person at the repo", said)
        self.assertIn("Not the office", said)

    def test_the_policy_page_really_is_a_template_and_the_slide_calls_it_one(self):
        """*Write the policy* is only useful advice if there is a draft to
        start from. There is, and it is marked up the way the slide promises."""
        policy = plain(text_of(POLICY))
        self.assertIn("This is a template", policy)
        self.assertIn("AI-use policy", plain(self.said))

    def test_the_three_labels_on_the_slide_are_the_three_the_template_uses(self):
        """The point of the template, and the easiest thing on this slide to
        get subtly wrong: a firm choice presented as a board requirement is how
        a firm ends up bound by somebody else's preference."""
        policy = plain(text_of(POLICY))
        for label in ("Rule", "Board guidance", "Firm choice"):
            with self.subTest(label=label):
                self.assertIn(label, policy)
        said = plain(self.said).lower()
        for label in ("board rule", "board guidance", "firm choice"):
            with self.subTest(label=label):
                self.assertIn(label, said)

    def test_the_one_question_on_the_slide_is_the_one_that_page_prints(self):
        """*Would I email this outside the firm?* is the whole checklist in
        seven words, and it is the only part of that page a room will
        remember. Quoted off the page rather than out of memory."""
        question = "Would I email this outside the firm?"
        self.assertIn(question, plain(text_of(NEVER_LEAVES)))
        said = plain(self.said)
        self.assertIn(question, said)
        self.assertIn("what client data never leaves", said)

    def test_the_rule_on_the_slide_is_the_section_that_governs_sealing(self):
        """A claim about who carries the liability is a claim with legal
        consequence, so its citation is on the projector rather than on the
        presenter's screen — `CLAUDE.md`'s rule, and `test_deck.py` holds the
        deck to it. This checks the section is the right one.

        § 138.33(b) is the sealing rule. It is read off the governance page so
        that a section renumbered there fails here rather than on stage.
        """
        self.assertIn("22 Tex. Admin. Code § 138.33(b)", plain(text_of(SEAL)))
        self.assertIn("§ 138.33(b)", plain(self.said))

    def test_it_hands_them_the_page_the_work_order_names(self):
        """`docs/for-principals/` is the one page to hand somebody who was not
        in the room. The slide names the file, not the folder, because a folder
        photographed off a projector is a folder nobody finds."""
        self.assertIn("docs/for-principals/index.md", self.said)

    def test_the_close_does_not_deliver_the_seal_slide_a_second_time(self):
        """PAO 71 was put in front of this room at 1:36, with its citation.

        Six minutes is what the run of show gives this block, and it has three
        jobs to do in them. Re-arguing the board's opinion here is how a block
        that fits stops fitting, and the room hears it as the same slide twice.
        """
        for slide in close_slides():
            with self.subTest(slide=slide.heading):
                self.assertNotIn("PAO 71", with_markup([slide]))


class TestTheLiveIssueSlideIsTheFormS(unittest.TestCase):
    """One issue, opened live, doing three jobs at once."""

    def setUp(self):
        self.said = said_on("Introduce yourself")

    def test_the_form_is_still_there_and_is_still_this_form(self):
        form = text_of(FORM)
        self.assertIn("name: Introduce yourself", form)
        self.assertIn("- introduction", form)

    def test_the_one_box_the_slide_asks_for_is_the_one_the_form_requires(self):
        """The slide asks two things of the room: who you are, and the one job
        you would hand to an agent. Only the second is required, and the whole
        ask depends on it — the replies are what pick the next worked example.

        Make `who` required and half the room stops filling it in. Make
        `automate` optional and the session gets three hundred hellos and no
        work orders.
        """
        self.assertIn("required: true", field_block("automate"))
        self.assertIn("required: false", field_block("who"))
        said = plain(self.said).lower()
        self.assertIn("who you are", said)
        self.assertIn("hand to an agent", said)

    def test_the_client_data_checkbox_is_required_and_the_slide_says_why(self):
        """The repo is public and stays public. A tract description posted from
        a ballroom is public for as long as GitHub exists, and the person who
        posted it was told to by somebody on a stage."""
        self.assertIn("required: true", field_block("no_client_data"))
        said = plain(self.said).lower()
        self.assertIn("public", said)
        self.assertIn("permanent", said)
        self.assertIn("no client names", said)

    def test_the_form_gives_the_same_two_warnings_the_slide_does(self):
        form = plain(text_of(FORM))
        self.assertIn("Assume it is permanent", form)
        self.assertIn("This is public", form)

    def test_it_says_what_the_replies_are_for(self):
        """The form's closing paragraph promises the same thing, and it is the
        only reason to ask a room to fill anything in at 1:59."""
        self.assertIn("pick the next worked example", plain(text_of(FORM)))
        self.assertIn("pick the next worked example", plain(self.said))

    def test_the_way_in_is_one_a_person_can_type(self):
        """The check this file was written for.

        The short link is #10 and the QR code is #38, and neither exists. A
        slide that leans on either is a slide that works in rehearsal and fails
        in the room. What is on screen has to be typeable off a projector by
        somebody holding a phone.
        """
        self.assertIn("github.com/RickSmith/survey-recon", self.said)

    def test_no_slide_of_the_close_promises_a_code_or_a_link_nobody_has_made(self):
        """Held across the whole block rather than the one slide, because the
        promise is as damaging on the Monday-morning slide as on this one.

        Delete this check when #10 and #38 land — and not before, because the
        sentence it is guarding reads perfectly either way.

        **The wording list is wider than the two features**, because #86's own
        review found the first draft guarding only the words *QR* and *short
        link*: *point your camera at the code* and a `tinyurl` both walked
        straight through a check whose docstring promised to stop them.
        """
        for slide in close_slides():
            said = plain(with_markup([slide])).lower()
            for promise in ("qr", "short link", "shortlink", "scan", "camera",
                            "tinyurl", "bit.ly", "tiny.cc"):
                with self.subTest(slide=slide.heading, promise=promise):
                    self.assertNotIn(promise, said)

    def test_the_slide_survives_the_network_being_gone(self):
        """It cannot collect a single reply without GitHub. That is a fact
        about the ask, not a failure of it, and the room has to be told from
        the screen rather than from the presenter's notes — this is the last
        slide of the session and there is no recovering it afterwards."""
        self.assertIn("tonight", plain(self.said).lower())


class TestTheBlockIsStillTheShapeTheRunOfShowGivesIt(unittest.TestCase):

    def test_none_of_its_slides_is_still_a_placeholder(self):
        for slide in close_slides():
            with self.subTest(slide=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_the_three_this_work_order_owns_are_all_there_and_in_order(self):
        self.assertEqual([slide.heading for slide in close_slides()], list(OWNED))

    def test_every_path_on_one_of_its_slides_is_committed(self):
        """A half path reads as a whole one, and the room photographs the slide
        rather than the speaker note. #82's review found three."""
        for slide in close_slides():
            for named in A_PATH.findall(with_markup([slide])):
                with self.subTest(slide=slide.heading, path=named):
                    self.assertTrue((REPO / named).exists(),
                                    f"{slide.heading!r} shows the room {named}")

    def test_every_slide_of_the_block_names_a_fallback(self):
        for slide in close_slides():
            with self.subTest(slide=slide.heading):
                self.assertIn("Fallback:", " ".join(slide.note.split()))

    def test_the_note_sends_the_presenter_at_the_file_the_card_does(self):
        """The fallback card's row for this block names the form. A note
        naming something else would be two plans for one minute of the
        session, and the card is the one that gets printed."""
        form = ".github/ISSUE_TEMPLATE/introduce-yourself.yml"
        self.assertIn(form, flat(text_of(CARD)))
        self.assertIn(form, note("Introduce yourself"))


if __name__ == "__main__":
    unittest.main()
