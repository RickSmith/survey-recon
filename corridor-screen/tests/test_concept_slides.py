"""The concept slides, held to the audience rule and to what they ported.

Issue #31. Eight slides across two blocks — *What is an agent* at `0:08–0:20`
and *Vocabulary of managing one* at `0:20–0:30`. They are the only part of the
session that teaches software rather than surveying, to a room of licensed
professionals who mostly have never opened a terminal and have no patience for
being condescended to about it.

So three things are checked, and the third is the one that matters:

* **Each named concept carries its substance**, not just its heading. Every
  check below names a fact the slide has to state — the four steps of the loop,
  the size of a token, that every new token re-reads the whole window. **Every
  one of them fails against the outline these slides replaced**, which is the
  test this file had to pass before it was worth having
* **Every software term is introduced by its survey equivalent**, read out of
  `CONTEXT.md`'s translation table rather than listed here. `CLAUDE.md` makes
  that a rule: *"Introduce every software term by its survey equivalent first"*
* **Nothing condescends about the programming gap.** A word list, which is a
  blunt instrument, and blunt is what is available. `CLAUDE.md`: *"These are
  licensed professionals who know things you do not"*

**Where the ported material came from, and why it is not committed.** The
source is Rick's own brain-dump deck, `Beyond the Prompt Getting Started with
Agentic AI for Geomatics Tools and Workflows.pptx`, which sits in the working
folder and is not in this repo. It is his unpublished draft, so this file
carries the handful of facts the port had to keep rather than a copy of the
deck. If it is ever committed, the checks below should read it instead of
holding these strings.

**What this file does not do.** The frame — the clock, the break slides, the
cut marks, the canvas — is `test_deck.py`'s.
"""

import re
import unittest

from tests.deck_reader import block_headed, slide_headed, visible
from tests.markdown_docs import flat, markdown_section, table_rows, text_of
from tests.test_deck import PLAN, REPO

CONTEXT = REPO / "CONTEXT.md"

# The two blocks these eight slides live in, by the heading of their break
# slide. Found through the deck for `deck_reader.block_headed`'s reason.
THE_BLOCKS = ("what is an agent", "vocabulary of managing one")

# Each concept the issue names, the slide that carries it, and a fact the
# source states that the port had to keep.
#
# **Every phrase here fails against the outline that stood in these slides.**
# That was the bar: an earlier draft of this file matched the concepts against
# the slide headings, and the headings were already right in the outline, so it
# passed on eight placeholders. A check a placeholder satisfies tests nothing —
# `test_principals_brief.py` learned the same lesson on the same day.
CONCEPTS = (
    ("LLM basics", "predicts the next word", "at scale"),
    ("chatbot to copilot to agent", "chatbot", "doing the work"),
    ("the agentic loop", "the loop", ("goal", "reason", "act", "observe")),
    # Not "#": every slide's own heading is a hash, so that check passed on
    # the placeholder. The syntax table is what the source slide carried, and
    # naming two of its rows is the smallest honest sign the port kept it.
    ("markdown", "markdown", ("heading", "bold")),
    ("tokens", "tokens", "4 characters"),
    ("context", "context", ("re-reads", "window")),
)

# Words and phrases that talk down to the room. `CLAUDE.md` is blunt about this
# and gives the reason: they are licensed professionals who know things we do
# not. A machine cannot hear condescension; it can refuse the phrasings that
# carry it.
CONDESCENDING = (
    "don't worry",
    "do not worry",
    "it's easy",
    "it is easy",
    "quite simple",
    "very simple",
    "obviously",
    "of course you",
    "anyone can",
    "even you",
    "no need to understand",
    "you don't need to know",
    "trust me",
    "just a",
    "nothing to be afraid",
    "not as scary",
    "non-technical",
)

# What the token slide has to carry, because §7 of the plan of record drops it
# third and the deck's own rule is that a cut is a whole-slide deletion.
TOKENS = "tokens"


def the_slides():
    """Every slide of the two concept blocks, break slides included."""
    found = []
    for heading in THE_BLOCKS:
        found.extend(block_headed(heading))
    return found


def content_of(slides_):
    return [slide for slide in slides_ if not slide.is_a_break]


def bullets(slide):
    """One string per bullet, with its wrapped continuation lines joined on.

    The deck is hard-wrapped, so a bullet that says a term and then gives its
    survey equivalent may well have a line break between the two. What is
    wanted is the unit a reader sees as one point, which is the bullet.

    The heading is not one of them. "Issues, and pull requests" is a title, and
    a title cannot introduce anything -- the bullets under it do that. Leaving
    headings in failed every slide that names its own subject, which is all of
    them.
    """
    found, current = [], []
    for line in visible([slide]).splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith(("-", "#")) or re.match(r"^\s*\d+\.", line):
            if current:
                found.append(flat(" ".join(current)))
            current = [line]
        else:
            current.append(line)
    if current:
        found.append(flat(" ".join(current)))
    return [one for one in found if not one.lstrip().startswith("#")]


def a_stem(term):
    """A word-boundary pattern for a software term and its ordinary endings.

    `merge` has to match "merging" and `issue` has to match "issues", while
    `spec` must not match "specific" -- which a bare prefix search does, and
    which would demand a scope of work on a slide that said "specifically".
    """
    if " " in term:
        return re.compile(re.escape(term), re.IGNORECASE)
    stem = term[:-1] if term.endswith("e") else term
    return re.compile(rf"\b{re.escape(stem)}(e|es|s|ed|d|ing)?\b", re.IGNORECASE)


def survey_words(phrase):
    """The first two words of a survey term worth matching on.

    The translation table answers in sentences -- "A working copy nobody else
    is affected by" -- and a slide will not repeat one verbatim. The opening
    words carry the sense: working copy, field book, check print, work order.
    """
    common = {"the", "a", "an", "and", "of", "you", "it", "is", "that", "your"}
    words = [
        word
        for word in re.findall(r"[\w']+", phrase.lower())
        if len(word) > 2 and word not in common
    ]
    return words[:2]


def translation_table():
    """`CONTEXT.md`'s software-to-survey table, as {software: survey}."""
    section = markdown_section(text_of(CONTEXT), "## Translation table")
    pairs = {}
    for row in table_rows(section):
        if len(row) == 2 and row[0] not in ("Software term", "") and "---" not in row[0]:
            pairs[row[0].strip("* ")] = row[1]
    if not pairs:
        raise AssertionError("CONTEXT.md no longer has a translation table")
    return pairs


class EachConceptCarriesItsSubstance(unittest.TestCase):
    def test_every_named_concept_has_a_slide_that_says_something(self):
        for concept, heading, wanted in CONCEPTS:
            slide = slide_headed(heading)
            seen = flat(visible([slide])).lower()
            for phrase in (wanted,) if isinstance(wanted, str) else wanted:
                with self.subTest(concept=concept, phrase=phrase):
                    self.assertIn(
                        phrase.lower(),
                        seen,
                        f"the slide for {concept!r} never says {phrase!r}, which "
                        f"is the part of it worth porting",
                    )

    def test_none_of_these_slides_is_still_a_placeholder(self):
        for slide in the_slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn("To be written", slide.body)


class EverySoftwareTermArrivesWithItsSurveyEquivalent(unittest.TestCase):
    def test_a_software_term_is_never_alone_in_the_bullet_it_appears_in(self):
        """`CLAUDE.md`: introduce every software term by its survey equivalent
        first. Read from `CONTEXT.md`'s table, so a row added there is enforced
        here without anybody remembering to.

        **Checked bullet by bullet, not slide by slide.** The first draft
        searched the whole slide, and the repo-and-git slide passed with the
        survey words stripped off its commit bullet -- because a *different*
        bullet on the same slide still said "field book". A term is introduced
        by its equivalent or it is not; being on a slide where some other line
        got it right is not being introduced.
        """
        for software, survey in translation_table().items():
            pattern, wanted = a_stem(software), survey_words(survey)
            for slide in content_of(the_slides()):
                for bullet in bullets(slide):
                    if not pattern.search(bullet):
                        continue
                    for word in wanted:
                        with self.subTest(term=software, slide=slide.number):
                            self.assertIn(
                                word,
                                bullet.lower(),
                                f"slide {slide.number} says {software!r} with "
                                f"no sign of {survey!r} in the same bullet: "
                                f"{bullet!r}",
                            )


class NothingCondescends(unittest.TestCase):
    def test_no_slide_and_no_note_talks_down_to_the_room(self):
        for slide in the_slides():
            where = f"slide {slide.number} ({slide.heading})"
            for text in (flat(visible([slide])), slide.note):
                for phrase in CONDESCENDING:
                    with self.subTest(slide=slide.number, phrase=phrase):
                        self.assertNotIn(
                            phrase,
                            text.lower(),
                            f"{where} says {phrase!r} to a room of licensed "
                            f"professionals who know things we do not",
                        )


class TheTokenSlideStaysOneDeletion(unittest.TestCase):
    def test_tokens_is_a_single_slide(self):
        """§7 drops the token slide third, and the deck's rule is that a cut is
        a whole-slide deletion. Two token slides make it two."""
        carrying = [
            slide
            for slide in content_of(the_slides())
            if TOKENS in slide.heading.lower()
        ]
        self.assertEqual(
            len(carrying), 1, f"{len(carrying)} slides are headed about tokens"
        )

    def test_that_slide_is_the_one_marked_for_the_cut(self):
        """The mark and the content on the same slide, so a presenter deleting
        `Cut 3 of 3` deletes the thing §7 named."""
        rank = [
            line
            for line in markdown_section(
                text_of(PLAN), "### Cut line, in order"
            ).splitlines()
            if "oken" in line
        ]
        self.assertTrue(rank, "§7 no longer drops the token slide")
        slide = slide_headed(TOKENS)
        self.assertIn("Cut 3 of 3", slide.note)


if __name__ == "__main__":
    unittest.main()
