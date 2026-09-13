"""The datum-gap slide, held to the research note and the run behind it.

Issue #33. One slide inside Act II, and the plan of record calls it out for this
room specifically:

> a scope-and-liability question, not a geodesy question — *"what datum do you
> certify to, and what does your survey report say when the manual doesn't tell
> you?"*

**It is the slide most likely to be quoted afterwards**, by somebody who was not
in the room, out of a photograph taken from the fourth row. That is the whole
reason it is checked this hard. A slide that overstates the gap is a slide that
says a state agency got something wrong, in front of three hundred of its
contractors, on the strength of a photograph.

So:

* **the gap is stated precisely, with the manual's date** — read from
  `CONTEXT.md`, which is where this repo settles what the manual is
* **all three 2022 replacements are named**, because naming two of them and not
  the third reads as a list somebody half-remembered
* **the geoid count is the run's own count** — `project-sh16/screening.json`,
  not a number typed on a slide
* **nothing on it blames anybody.** Checked against a word list, which is a
  blunt instrument and still catches the drafts that go wrong
* **it asks rather than answers**, and says what a report can say today
* the quote from the manual carries its source, which `test_deck.py` enforces
  for every claim of that kind

**What this file does not do.** It does not check the frame — the clock, the
break slide, the canvas — which is `test_deck.py`'s. And it takes no view on
whether NATRF2022 is a good idea, which is nobody's business here.
"""

import json
import re
import unittest
from pathlib import Path

from corridor_screen.cache import long_path
from tests.deck_reader import slide_headed, visible
from tests.markdown_docs import flat, text_of

REPO = Path(__file__).resolve().parents[2]
CONTEXT = REPO / "CONTEXT.md"
RESEARCH = REPO / "docs" / "txdot-research.md"
RUN = REPO / "project-sh16" / "screening.json"

# How the slide is headed, which is how this file finds it.
THE_SLIDE = "datum gap"

# The three modernized datums, as `CONTEXT.md` spells them in the row it gives
# them. Read rather than listed, because a repo that renamed one of them in its
# own vocabulary and not on the slide would be the exact drift this catches.
THE_ROW = re.compile(r"\*\*(NATRF2022) / (NAPGD2022) / (SPCS2022)\*\*")

# The manual's revision, as `CONTEXT.md` states it in that same row. The date is
# the load-bearing part of the claim: "the Survey Manual does not mention them"
# is a different sentence from "the April 2026 Survey Manual does not mention
# them", and only the second one stays true.
THE_REVISION = re.compile(r"TxDOT's (\w+ \d{4}) Survey Manual")

# What the manual does say about transformations, out of the research note, so
# the slide quotes the repo's reading rather than a fresh one.
NO_TRANSFORMATIONS = "TxDOT will not accept any datum transformations for control"

# How the slide's citation line is told apart from the claims above it. The
# footer repeats the manual's revision, so a check about whether the claim
# carries its date has to read past it.
A_CITATION = "txdot.gov"

# Words that turn a gap into an accusation. Blunt, and deliberately so: the
# issue's first acceptance criterion is that the slide is framed as an open
# question and not a criticism of anyone, and a machine cannot judge tone. It
# can refuse the words that drafts reach for when the tone slips.
BLAME = (
    "failed",
    "failure to",
    "forgot",
    "should have",
    "neglect",
    "oversight",
    "out of date",
    "behind the times",
    "has not bothered",
    "ignores",
    "refuses to",
)


def the_slide():
    return slide_headed(THE_SLIDE)


def seen():
    return flat(visible([the_slide()]))


def one(pattern, markdown, what, source):
    found = pattern.findall(markdown)
    if len(found) != 1:
        raise AssertionError(
            f"{what} appears {len(found)} times in {source}, wanted once"
        )
    return found[0]


def run():
    with open(long_path(RUN), "r", encoding="utf-8") as handle:
        return json.load(handle)


class TheGapIsStatedPrecisely(unittest.TestCase):
    def test_it_gives_the_manual_the_revision_the_repo_gives_it(self):
        """*The gap is stated precisely, with the manual's date.*

        **Read off the claim, not off the citation.** The footer carries the
        revision too, so a first draft of this passed with the date deleted
        from the sentence making the claim -- which is the sentence that gets
        repeated, in a room where nobody reads the footer of a photograph.
        """
        revision = one(THE_REVISION, text_of(CONTEXT), "the manual's revision", "CONTEXT.md")
        claims = flat(
            "\n".join(
                line
                for line in visible([the_slide()]).splitlines()
                if A_CITATION not in line
            )
        )
        self.assertIn(
            revision,
            claims,
            f"the slide states the gap without saying it is the {revision} "
            f"manual. Without the date, the claim stops being true the day "
            f"TxDOT revises it, and the footer is not where a reader looks",
        )

    def test_it_names_all_three_replacements(self):
        """Naming two of the three reads as a list somebody half-remembered,
        and this room contains people who will notice which one is missing."""
        for datum in one(THE_ROW, text_of(CONTEXT), "the modernized datums", "CONTEXT.md"):
            self.assertIn(datum, seen(), f"the slide never names {datum}")

    def test_the_research_note_still_says_what_the_slide_says(self):
        """The slide's claim, against the repo's own reading of the manual.

        If somebody softens or withdraws the finding in `docs/txdot-research.md`
        -- because TxDOT revised the manual, say -- this fails rather than
        leaving a slide making a withdrawn claim to a live room.
        """
        note = flat(text_of(RESEARCH))
        self.assertIn("no reference to SPCS2022, NATRF2022, or NAPGD2022", note)

    def test_the_quote_from_the_manual_is_the_repos_quote(self):
        """Quoted rather than paraphrased, and quoted the same way everywhere.

        `test_deck.py` makes a claim like this carry its citation on the slide.
        This is the other half: that the words are the manual's.
        """
        self.assertIn(NO_TRANSFORMATIONS, flat(text_of(RESEARCH)))
        self.assertIn(NO_TRANSFORMATIONS, seen())


class TheGeoidCountIsTheRunsCount(unittest.TestCase):
    def test_the_slide_counts_what_the_run_counted(self):
        """TxDOT's own control service publishes no geoid model, and the slide
        says so with a number. The number is the SH16 run's, not a slide's."""
        points = run()["control"]["txdot_points"]
        without = [point for point in points if not point.get("geoid")]
        self.assertTrue(points, "the run has no TxDOT control points at all")
        self.assertEqual(
            len(without),
            len(points),
            "some point in this corridor does publish a geoid model, so the "
            "slide's claim needs rewriting rather than recounting",
        )
        self.assertIn(
            f"{len(without)} ",
            seen(),
            f"the slide does not show {len(without)}, which is how many control "
            f"records in this corridor publish no geoid model",
        )


class TheSlideAsksRatherThanAnswers(unittest.TestCase):
    def test_it_asks_a_question(self):
        """*It does not pretend there is a settled answer.*"""
        self.assertIn(
            "?",
            seen(),
            "the datum-gap slide puts no question on the screen, which is the "
            "one thing the plan of record asks it to do",
        )

    def test_it_says_what_a_report_can_say_today(self):
        """*It says what a surveyor should put in their report today.*"""
        self.assertIn("report", seen().lower())

    def test_it_blames_nobody(self):
        """*It is framed as an open question, not a criticism of anyone.*"""
        lowered = seen().lower()
        for word in BLAME:
            self.assertNotIn(
                word,
                lowered,
                f"{word!r} turns a gap into an accusation, and this slide gets "
                f"photographed and quoted by people who were not in the room",
            )

    def test_it_is_no_longer_a_placeholder(self):
        self.assertNotIn("To be written", the_slide().body)


if __name__ == "__main__":
    unittest.main()
