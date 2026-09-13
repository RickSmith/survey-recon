"""The cold-open slide, held to the run it is a caption for.

Issue #81. Eight minutes, one slide, and it is on the projector while the tool
runs beside it. Everything on it is a number somebody read off a screening run,
so the danger is the ordinary one: the run gets regenerated, the slide does
not, and a figure that was right in September is wrong in October in front of
three hundred people.

Same reasoning as `test_money_slide.py` and `test_datum_gap.py`. A number
written on a slide beside a thing is a number that rots.

**Two of these checks are about what the slide must not say.** The cold open is
watching the run produce its answer. A slide that states the parcel count
before the terminal does has spoiled the one thing the block is for -- the room
seeing something real happen. And a slide that explains the tool has started
the next block eight minutes early.
"""

import json
import unittest
from pathlib import Path

from corridor_screen.cache import long_path

from .deck_reader import noted
from .markdown_docs import text_of
from .test_deck import slides

REPO = Path(__file__).resolve().parent.parent.parent
SCREENING = REPO / "project-sh16" / "screening.json"

# The block this slide belongs to, as the run of show writes it.
BLOCK = "Cold open"


def run():
    with open(long_path(SCREENING), "r", encoding="utf-8") as handle:
        return json.load(handle)


def the_slide():
    found = [s for s in slides() if s.heading == "The job we just handed it"]
    assert len(found) == 1, f"expected one cold-open content slide, found {len(found)}"
    return found[0]


def on_screen():
    """What the room sees, with the speaker note taken out.

    Every check below about what the slide may not say reads this rather than
    `slide.body`. The note is allowed to say "do not put 524 on the slide";
    a check reading the whole body would find the 524 in that warning and
    fail the slide for obeying it.
    """
    return "\n".join(the_slide().content_lines())


def note():
    """The speaker note as one line, so a phrase match survives the wrapping.

    Notes are hard-wrapped prose. "Undisclosed caching" is two words with a
    newline between them in the file, and a check looking for the phrase
    verbatim fails on a note that says exactly the right thing.
    """
    return " ".join(the_slide().note.split())


class TestEveryFigureOnItIsTheRunS(unittest.TestCase):
    """Read back out of `project-sh16/screening.json`, never typed from memory."""

    def setUp(self):
        self.document = run()
        self.body = on_screen()

    def test_the_corridor_length_is_the_run_s(self):
        miles = self.document["alignment"]["length_mi"]
        self.assertIn(
            f"{miles:.2f}", self.body,
            f"the slide no longer says {miles:.2f} miles, which is what the run "
            f"measured",
        )

    def test_the_half_width_is_the_run_s(self):
        """And it is stated, never derived -- see Half-width in CONTEXT.md."""
        feet = self.document["run"]["half_width_ft"]
        self.assertIn(f"{feet:g} ft", self.body)

    def test_the_service_count_is_the_run_s(self):
        self.assertIn(f"{len(self.document['services'])} public map services", self.body)

    def test_the_slide_says_which_county(self):
        self.assertIn("Bexar", self.body)


class TestItGivesNothingAwayThatTheTerminalHasNotSaidYet(unittest.TestCase):
    """The room is watching a real run. The slide must not get there first.

    This is the only block in the session whose slide can spoil its own demo,
    which is why the check exists rather than being left to whoever edits it
    next.
    """

    def test_it_does_not_state_the_parcel_count(self):
        count = str(len(self.document_parcels()))
        self.assertNotIn(
            count, on_screen(),
            f"the slide states {count}, which is what the run comes back with. "
            f"The terminal says it first, or the cold open has spoiled itself.",
        )

    def document_parcels(self):
        return run()["parcels"]

    def test_it_does_not_state_the_flagged_parcel_count(self):
        flagged = sum(1 for p in run()["parcels"] if p.get("flags"))
        body = on_screen()
        self.assertNotIn(f"{flagged} of", body)
        self.assertNotIn(f"{flagged} flagged", body)


class TestItDoesNotStartTheNextBlockEarly(unittest.TestCase):
    """"Do not explain the tool yet" is the work order's own instruction.

    The words below are the vocabulary of the two blocks that follow. Any of
    them on this slide means the cold open has begun teaching, which is the one
    thing these eight minutes are not for.
    """

    TOO_EARLY = ("agentic", "large language model", "LLM", "prompt",
                 "context window", "token", "pull request", "commit")

    def test_no_slide_word_belongs_to_a_later_block(self):
        body = on_screen().lower()
        for word in self.TOO_EARLY:
            with self.subTest(word=word):
                self.assertNotIn(
                    word.lower(), body,
                    f"the cold-open slide says {word!r}. The room has not been "
                    f"given a single definition yet, and this block is for "
                    f"watching rather than for learning words.",
                )


class TestTheCachingIsDisclosedOnTheSlide(unittest.TestCase):
    """Undisclosed caching, if the room notices it, costs you the room.

    The plan of record is blunt about it, and the speaker note is not enough:
    the deck publishes on every push and nobody in the room sees the
    presenter's screen.

    **The slide promises a live run and names the cache as the fallback**, in
    that order. An earlier draft had it the other way round -- "answers
    captured 12-13 September" -- which conceded the live demo before anybody
    had asked for it. The committed SH16 run really did call all fourteen
    services, so the stronger claim is the true one.
    """

    def test_the_slide_promises_real_code_and_real_data(self):
        said = on_screen().lower()
        self.assertIn("real code", said)
        self.assertIn("real data", said)

    def test_the_slide_still_admits_the_cache_on_its_own_face(self):
        """Live first is a claim about intent. This is the part that has to be
        true whatever happens on the day, and it is on the slide rather than
        only in the note because nobody in the room sees the note."""
        self.assertIn("previously captured", on_screen().lower())

    def test_the_slide_says_where_to_run_it(self):
        self.assertIn("corridor-screen/README.md", on_screen())

    def test_the_note_tells_the_presenter_to_say_it_out_loud(self):
        said = note()
        self.assertIn("Undisclosed caching", said)
        self.assertIn("backup, not the plan", said)


class TestTheNoteStillDoesItsJob(unittest.TestCase):
    """`test_deck.py` checks the shape of every note. This checks this one's
    content, because the cold open has a fallback and the note has to name it."""

    def test_it_opens_with_the_clock_the_length_and_the_block(self):
        claim = noted(the_slide())
        self.assertEqual(claim.label, BLOCK)

    def test_it_names_the_fallback_card(self):
        self.assertIn("fallbacks.md", note())

    def test_it_warns_against_retyping_the_cold_open_line(self):
        """119 characters and five flags. The day you need it is the day you
        will mistype it -- the fallback card says so and the note repeats it,
        because the note is what the presenter is actually looking at."""
        said = note()
        self.assertIn("retype", said.lower())


class TestTheFiguresAreAlsoWhatTheFallbackCardPromises(unittest.TestCase):
    """The slide and the card are read minutes apart by the same person."""

    def test_the_card_still_has_a_row_for_this_block(self):
        card = text_of(REPO / "docs" / "presenting" / "fallbacks.md")
        self.assertIn("Cold open", card)

    def test_the_card_row_still_names_the_run_the_slide_describes(self):
        card = text_of(REPO / "docs" / "presenting" / "fallbacks.md")
        self.assertIn("cache-only", card)


if __name__ == "__main__":
    unittest.main()
