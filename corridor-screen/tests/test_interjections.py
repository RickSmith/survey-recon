"""Seneca's audience-proxy interjections, held to what they are for.

Issue #35. Six questions a firm owner in the room is already thinking and will
not ask out loud, scripted into the speaker notes at the moment each one lands.

**Why they are checked at all.** Everything else in this deck is checked
against a source — a figure against the run that produced it, a citation
against the manual it came out of. An interjection has no source. It is
writing, and writing cannot be read back out of a JSON file.

What *can* be checked is the shape of the thing, and the shape is where this
kind of writing goes wrong:

* **Six lines drifting into two.** Interjections are cheap to write and easy to
  delete, and a session that keeps one of them has an audience proxy with
  nothing to do for two hours
* **All of them in one place.** Placed at a specific time is the whole point —
  clustered in Act I, they are a warm-up act rather than the room's own voice
* **The skeptical one quietly becoming a setup.** This is the failure worth
  the most attention. A question the presenter is glad to be asked is not
  skepticism, it is a cue, and a room of principals knows the difference
  immediately
* **Condescension.** `CLAUDE.md`: *"Never condescend about the programming
  gap. These are licensed professionals who know things you do not."* Seneca
  speaking for the room is exactly where that slips

So this file checks the count, the spread, the form, and four things about the
words themselves. It does not, and cannot, check that a line is funny.

**What is deliberately not checked here.** The clock, the break slides and
whether a file a note names is committed all belong to `test_deck.py`, which
reads every note in the deck. An interjection is in a note, so it already gets
all three for free.
"""

import re
import unittest
from collections import namedtuple

from tests.deck_reader import REPO, noted, slides
from tests.markdown_docs import (
    flat, markdown_section, plain, table_rows, text_of, unemphasized,
)

CONTEXT = REPO / "CONTEXT.md"
SLIDES_PAGE = REPO / "docs" / "slides" / "index.md"

# What an interjection looks like in a speaker note:
#
#     **Seneca (audience proxy), after the last bullet:** "Nineteen questions
#     before it does any work. Who is paying for that hour?"
#
#     **Answer:** You are, the same way you pay for a scoping call. ...
#
# Three things are load-bearing. *(audience proxy)* is spelled out every time
# because a presenter reads these cold, at speed, off a confidence monitor, and
# the second presenter's name on its own does not say what the line is for. The
# **cue** is where on the slide it goes -- "after the last bullet", "once the
# floor has gone quiet" -- which is what makes "placed at a specific time" true
# of the line rather than only of the slide. And the question is in quotes
# because it is said, word for word, by somebody who is not the presenter.
A_MARKER = re.compile(
    r'^\*\*Seneca \(audience proxy\), (?P<cue>[^:*]+):\*\* "(?P<question>[^"]+)"$'
)

# The paragraph under it. The answer is scripted too: an interjection whose
# answer is improvised is a question the presenter walks into.
AN_ANSWER = "**Answer:**"

# The sentence that marks the skeptical one, in the note beside it. There is
# exactly one, and the check below reads its answer rather than trusting this
# label on its own.
THE_SKEPTICAL_ONE = "**This is the skeptical one.**"

Interjection = namedtuple("Interjection", "slide block cue question answer")


def paragraphs_of(note):
    """A speaker note split into paragraphs, each one flattened to a line.

    Notes are hard-wrapped prose, so every phrase worth checking has a line
    break somewhere in the middle of it. `markdown_docs.flat` is the same job
    on a whole page; this keeps the blank lines, because the paragraph after a
    question is the answer to it and that relationship is the wrapping.
    """
    return [flat(chunk) for chunk in re.split(r"\n\s*\n", note) if chunk.strip()]


def marked_paragraphs():
    """Every paragraph in the deck that opens by naming Seneca, with its slide.

    Found by the name rather than by the full marker on purpose. A line that
    was meant to be an interjection and is written wrongly should fail the form
    check below, loudly, rather than disappear from every count in this file.
    """
    for slide in slides():
        for paragraph in paragraphs_of(slide.note):
            if paragraph.startswith("**Seneca"):
                yield slide, paragraph


def interjections():
    """Every interjection in the deck, in the order the session runs them."""
    found = []
    for slide in slides():
        paragraphs = paragraphs_of(slide.note)
        for position, paragraph in enumerate(paragraphs):
            marker = A_MARKER.match(paragraph)
            if not marker:
                continue
            after = paragraphs[position + 1] if position + 1 < len(paragraphs) else ""
            found.append(Interjection(
                slide=slide,
                block=noted(slide),
                cue=marker.group("cue"),
                question=marker.group("question"),
                answer=after[len(AN_ANSWER):].strip() if after.startswith(AN_ANSWER) else "",
            ))
    return found


def minutes_into_the_session(block):
    """Where a block starts, as minutes past the top of the session.

    The clock reads `0:57–1:18`, so the hour and the minute of the first half
    are what a spread check compares.
    """
    hour, minute = block.time.split("–")[0].split(":")
    return int(hour) * 60 + int(minute)


def said_in(interjection):
    """The question and the answer as one lowercased line, emphasis off.

    Both halves, because condescension is at least as likely in the answer as
    in the question, and an answer is the half the presenter says.

    **The emphasis comes off with `markdown_docs.unemphasized`**, which is what
    stops a phrase evading the list below by being italicised. *Don't worry
    about that part* is the same sentence to the room and a different string to
    a test, and a note is exactly where somebody would italicise it.
    """
    return unemphasized(f"{interjection.question} {interjection.answer}").lower()


def slides_whose_note_says(phrase):
    """Every slide whose speaker note carries a phrase, wrapping and all.

    Three checks here look for a sentence in a note that somebody else wrote --
    the money slide's pricing rule, the stretch block's offer of a prompt, the
    line marking the skeptical one. All three are hard-wrapped prose, so all
    three look at the flattened note: `markdown_docs.flat` exists because a
    check that fails when a paragraph is re-wrapped punishes editing, and the
    failure it produces here would be a misleading one -- *the money slide no
    longer carries its pricing rule*, about a rule that never moved.
    """
    return [slide for slide in slides() if phrase in flat(slide.note)]


class TestThereAreRoughlySixOfThem(unittest.TestCase):
    """The work order says roughly six, so this is a range rather than a count.

    Five is a session that dropped one for time. Seven is one more than
    anybody planned. Four or eight is a decision somebody should write down.
    """

    def test_there_are_between_five_and_seven(self):
        found = interjections()
        self.assertGreaterEqual(len(found), 5, "the audience proxy has run out of things to say")
        self.assertLessEqual(len(found), 7, "that is a double act, not an interjection")

    def test_every_paragraph_naming_seneca_is_a_whole_interjection(self):
        """A half-written one is worse than none: it is a line a presenter
        expects to be answered for, and no answer under it."""
        self.assertEqual(
            len(list(marked_paragraphs())), len(interjections()),
            "a note names Seneca in a form nothing here can read",
        )

    def test_every_one_carries_its_scripted_answer(self):
        for one in interjections():
            with self.subTest(slide=one.slide.number, question=one.question[:40]):
                self.assertNotEqual(
                    one.answer, "",
                    f"slide {one.slide.number} asks a question with no answer under it",
                )


class TestEachOneIsPlacedAtATime(unittest.TestCase):
    """*"Roughly six, each placed at a specific time in the run of show."*

    A time comes from two things. The slide's own speaker note carries the
    block, which `test_deck.py` holds to the run of show; the cue in the marker
    says where on that slide the line goes. Neither is any use without the
    other -- a block is up to twenty-one minutes long.
    """

    def test_every_one_sits_on_a_slide_that_claims_a_block(self):
        for one in interjections():
            with self.subTest(slide=one.slide.number):
                self.assertIsNotNone(
                    one.block,
                    f"slide {one.slide.number} carries an interjection and no clock",
                )

    def test_no_two_land_in_the_same_block(self):
        blocks = [one.block.time for one in interjections()]
        self.assertEqual(
            sorted(blocks), sorted(set(blocks)),
            "two interjections in one block leaves another block with none",
        )

    def test_they_are_spread_across_the_two_hours(self):
        """Both ends of the session, not a cluster in the middle of it.

        A room asks its first silent question long before the money slide, and
        the questions that matter most arrive when accountability does.
        """
        placed = sorted(minutes_into_the_session(one.block) for one in interjections())
        self.assertLess(placed[0], 30, "nothing speaks for the room in the first half hour")
        self.assertGreater(placed[-1], 90, "the room goes quiet for the last half hour")

    def test_every_one_says_where_on_the_slide_it_goes(self):
        """The cue is parsed out of the marker, so an empty one cannot happen.
        What this catches is a cue that says nothing -- a presenter reading
        *after the bullet* on a slide with five of them is guessing."""
        for one in interjections():
            with self.subTest(slide=one.slide.number, cue=one.cue):
                self.assertGreater(len(one.cue.split()), 2, f"{one.cue!r} is not a cue")


class TestTheyAskWhatAPrincipalWouldAsk(unittest.TestCase):
    """*"Each one asks what an actual principal would ask."*

    Unfalsifiable as written, so this checks the two things that would make it
    plainly untrue: a question that is not a question, and a question asked in
    software words by somebody who has never used them.
    """

    # Software terms `CONTEXT.md` has to translate for this audience. Seneca is
    # the audience, so they do not appear in a question -- an answer may use
    # them, because teaching them is what the session is for.
    #
    # This is a subset of the translation table rather than all of it, and
    # deliberately so: *issue*, *spec*, *merge* and *seam* are ordinary English
    # as well as software words, and a check that banned them would fail on a
    # sentence about a survey. The subset is held to the table below, so a term
    # the repo stops translating stops being banned here.
    SOFTWARE_WORDS = ("branch", "commit", "pull request", "markdown", "context window", "token")

    def translated_terms(self):
        """The software column of **the translation table** in `CONTEXT.md`.

        That table, not every table. `CONTEXT.md` carries six two-column
        vocabulary tables, and the first draft of this read all of them --
        which would have gone on passing happily while the translation table
        itself lost the row this file leans on.

        The reading is `markdown_docs`'s, not a second copy of it. That module
        exists to delete the copy.
        """
        table = markdown_section(text_of(CONTEXT), "## Translation table")
        return [row[0].lower() for row in table_rows(table)]

    def test_the_banned_words_are_the_repos_own_list(self):
        """If a term left the translation table, this file should not be the
        last place in the repo still calling it jargon."""
        translated = " ".join(self.translated_terms())
        for word in self.SOFTWARE_WORDS:
            with self.subTest(word=word):
                self.assertIn(word, translated)

    def test_every_one_of_them_is_a_question(self):
        for one in interjections():
            with self.subTest(slide=one.slide.number, question=one.question[:40]):
                self.assertTrue(
                    one.question.rstrip().endswith("?"),
                    "an audience proxy asks; it does not make a speech",
                )

    def test_no_question_is_asked_in_software_words(self):
        for one in interjections():
            for word in self.SOFTWARE_WORDS:
                with self.subTest(slide=one.slide.number, word=word):
                    self.assertNotIn(word, one.question.lower())


class TestNoneOfThemCondescend(unittest.TestCase):
    """*"None of them condescend about the programming gap."*

    `CLAUDE.md` makes this a rule for the whole repo, and these six lines are
    where it is hardest to keep. The proxy is written by the people on stage,
    so every one of these is a licensed professional being spoken *for*.

    The list is phrases rather than words, because the condescension is never
    in a single word. It is in *don't worry about that part*.
    """

    PATRONIZING = (
        "don't worry", "do not worry",
        "non-technical", "not technical", "too technical",
        "over your head", "leave that to",
        "you don't need to understand", "you do not need to understand",
        "learn to code", "trust me",
        "simple enough", "easy enough",
    )

    def test_no_interjection_talks_down_to_the_room(self):
        for one in interjections():
            for phrase in self.PATRONIZING:
                with self.subTest(slide=one.slide.number, phrase=phrase):
                    self.assertNotIn(phrase, said_in(one))


class TestOneOfThemIsGenuinelySkeptical(unittest.TestCase):
    """*"At least one is genuinely skeptical, not a setup."*

    The test of a real skeptical question is what the answer is allowed to be.
    A setup is answered with the thing the presenter wanted to say next. This
    one is answered with *we do not know*, which is the deck's own standing
    rule about the agent's savings -- read out of the money slide's note here
    rather than restated, so the day that rule changes, this check says so.
    """

    def skeptical(self):
        marked = [slide.number for slide in slides_whose_note_says(THE_SKEPTICAL_ONE)]
        found = [one for one in interjections() if one.slide.number in marked]
        self.assertEqual(len(found), 1, "exactly one interjection is the skeptical one")
        return found[0]

    def money_slide_note(self):
        found = slides_whose_note_says("Do not price the agent here")
        self.assertEqual(len(found), 1, "the money slide no longer carries its pricing rule")
        return flat(found[0].note)

    def test_the_money_slide_still_refuses_to_price_the_agent(self):
        """The rule the skeptical answer obeys, in the place it was written."""
        self.assertIn("Nothing in this repo has measured what it saves", self.money_slide_note())

    def test_the_skeptical_answer_refuses_the_number_it_was_asked_for(self):
        """Asked what it saved, in hours. Answered *nobody measured that*.

        Both halves are checked, because either one alone passes a sentence
        that should not pass. *We measured it: nine hours* carries the word;
        an answer with no figure in it might still be dodging the question
        rather than conceding it.
        """
        answer = self.skeptical().answer
        self.assertIn("measured", answer.lower())
        self.assertIsNone(
            re.search(r"\d", answer),
            "the answer to what it saved is a figure, which is the thing "
            "the money slide's note forbids",
        )

    def test_the_skeptical_question_asks_for_the_number(self):
        """It is skepticism about the claim, not a general worry about
        computers. If it stops asking for the saving, it stops being the
        question this room actually has."""
        self.assertIn("save", self.skeptical().question.lower())

    def test_no_interjection_prices_the_agent(self):
        """Hours, never a price per seat or per month.

        That is the money block's own rule, read out of its note here rather
        than restated, and the skeptical interjection is the likeliest place in
        the deck to break it: asked what it saves, in hours, by somebody who
        buys things for a living. A price said on a stage in October is stale
        by the spring, and it is the sentence that gets quoted back.
        """
        self.assertIn("never a price per seat or per month", self.money_slide_note())
        for one in interjections():
            for priced in ("$", "per seat", "per month", "monthly", "subscription"):
                with self.subTest(slide=one.slide.number, priced=priced):
                    self.assertNotIn(priced, said_in(one))


class TestTheDeckNoLongerPromisesThemLater(unittest.TestCase):
    """The stretch block's note pointed at this work order while it was open.

    That pointer is the kind of thing that survives the work landing and sends
    a presenter to a closed issue on a phone at 0:52. The block that was
    promised material is the block that has to have it.
    """

    def test_the_stretch_block_carries_one_of_them(self):
        """The note that offers the room a prompt is the note that has to hold
        one. A presenter reading *Seneca has something for this moment* at 0:52
        with nothing written under it is worse off than one reading nothing."""
        offered = slides_whose_note_says("If the room is quiet")
        self.assertEqual(len(offered), 1, "no note offers the room a prompt any more")
        written = [one for one in interjections() if one.slide.number == offered[0].number]
        self.assertEqual(
            len(written), 1,
            "the stretch note promises the room a question and none is written there",
        )

    def test_no_note_still_says_the_interjections_are_coming(self):
        for slide in slides():
            with self.subTest(slide=slide.number):
                self.assertNotIn("see #35", flat(slide.note))


class TestTheSlidesPageSaysHowManyThereAre(unittest.TestCase):
    """A number written in prose beside a thing is a number that rots.

    `docs/slides/index.md` counts them for a reader who will never open the
    deck's notes. The count is read off the deck here, the same way that page's
    slide count and placeholder count already are.
    """

    def test_the_page_states_the_number_the_deck_actually_carries(self):
        page = plain(text_of(SLIDES_PAGE))
        stated = re.search(r"(\d+) audience-proxy interjections", page)
        self.assertIsNotNone(stated, "the slides page does not say how many there are")
        self.assertEqual(int(stated.group(1)), len(interjections()))

    def test_the_page_names_the_file_that_checks_them(self):
        self.assertIn("test_interjections.py", text_of(SLIDES_PAGE))


if __name__ == "__main__":
    unittest.main()
