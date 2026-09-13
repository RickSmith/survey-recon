"""The money slide, held to the build-up its figures come out of.

Issue #32. Six minutes at 0:46, moved up the run of show on purpose: the room is
firm owners, and owners want the money frame before they will spend another
forty-five minutes watching a demo.

It is the block most likely to be argued with out loud, from the floor, by
people who price this work for a living. So every figure on it is read back out
of `project-sh16/crew-day.md` and compared:

* the two day counts, as the build-up writes them and refuses to add them
* **every number anywhere on the block** is one the build-up publishes, unless
  it sits on a line that carries its own source
* every rate handle named is a handle the build-up has
* cost is in hours, never in what software costs by the seat
* rework is said before speed is
* `cannot be invoiced` is on this block and not only somewhere in the deck
* nothing here still says it is waiting to be written

**Why check prose at all.** `test_plan_of_record.py`'s answer, which this repo
keeps coming back to:

> A number written in prose beside a thing is a number that rots.

The build-up regenerates whenever the tool runs. A slide does not. And unlike
every other document that quotes it, this one is read out loud to three hundred
people who can check it from their seats while it is being said.

**What this file deliberately does not do.** It does not re-check the frame.
`test_deck.py` owns the clock in the notes, the break at the head of the block,
the cut marks, the canvas, and the rule that a claim with legal weight carries
its citation on the slide — `cannot be invoiced` included. A second copy of any
of those would drift the first time somebody fixed one of them.
"""

import re
import unittest

from tests.build_up_figures import (
    A_NUMBER,
    HANDLE,
    PRICED_BY_THE_SEAT,
    figures,
    numbers_it_publishes,
    rate_handles,
    rate_values,
)
from tests.deck_reader import block_headed, content_slides, visible, with_markup

# What the block's break slide is headed, which is how this file finds it.
THE_BLOCK = "money slide"

# The unit a speaker note counts slides in. Notes in this deck are written for a
# person, so they say "two slides" rather than "2".
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
}
# Anchored to the number words rather than to any word, so a note that happens
# to say "these slides" before it says how many is read past instead of failing
# with "'these' is not a number".
SLIDE_COUNT = re.compile(
    r"\b(" + "|".join(NUMBER_WORDS) + r") slides\b", re.IGNORECASE
)

# A line that carries its own source may carry its own numbers -- a manual
# revision year and a chapter number are the manual's, not the build-up's.
A_SOURCE = "txdot.gov"

# A rate handle is `A4`, and the 4 in it is not a quantity. Taken out before any
# line is searched for numbers.
A_HANDLE_ON_A_LINE = re.compile(r"`A\d+`")


def the_block():
    """Every slide of the money slide block, break slide first."""
    return block_headed(THE_BLOCK)


def the_content():
    """The block's slides that carry content, which is all but the break."""
    return content_slides(the_block())


class TheFiguresAreTheBuildUpsFigures(unittest.TestCase):
    def test_the_day_counts_are_the_build_ups_own(self):
        """The two numbers the build-up refuses to add together."""
        build_up = figures()
        seen = visible(the_content())
        self.assertIn(f"{build_up.field_days} crew-days", seen)
        self.assertIn(f"{build_up.office_days} days", seen)

    def test_it_says_how_big_a_crew_day_is(self):
        """A day count read out to a room of surveyors without the crew it
        counts is a number they cannot check against anything.

        The crew size is `2`, and the first draft of this looked for that digit
        anywhere on the block -- which the placeholder's own `#32` satisfied.
        So the digit is wanted beside the noun it counts.
        """
        self.assertIn(f"{figures().crew_size} people", visible(the_content()))

    def test_every_number_on_the_block_is_one_the_build_up_publishes(self):
        """The blunt check, and the one the issue actually asks for.

        A figure invented on a slide is a figure said out loud to a room that
        prices this work. A line carrying its own source is allowed its own
        numbers -- a manual's revision year and chapter belong to the manual.
        """
        published = numbers_it_publishes()
        for slide in the_content():
            for line in slide.content_lines():
                if A_SOURCE in line:
                    continue
                for number in A_NUMBER.findall(A_HANDLE_ON_A_LINE.sub("", line)):
                    with self.subTest(slide=slide.number, number=number):
                        self.assertIn(
                            number,
                            published,
                            f"slide {slide.number} shows {number!r}, which is "
                            f"in no line of the crew-day build-up and carries "
                            f"no source of its own",
                        )

    def test_every_rate_handle_it_names_is_a_real_handle(self):
        real = rate_handles()
        self.assertTrue(real, "no rate handles found in the build-up at all")
        for handle in set(HANDLE.findall(with_markup(the_block()))):
            self.assertIn(handle, real, f"{handle} is not a rate in the build-up")

    def test_a_handle_is_shown_beside_the_rate_it_stands_for(self):
        """The hole the two checks above leave between them.

        `A4` is a real handle and `0.75` is a real number, so a slide reading
        *rate `A4` — 0.75 hours per tract* passes both and is wrong: 0.75 is
        `A1`'s rate. A handle on a slide is an invitation to argue with one
        rate by name, and the room can only take it up if the name and the
        number it is shown beside are the same rate.

        Some line naming the handle has to carry its value. Not every line --
        *argue with `A4`, not with the total* names it and is not quoting it.
        """
        values = rate_values()
        self.assertTrue(values, "the build-up's rate table no longer reads")
        for slide in the_content():
            for handle in set(HANDLE.findall(with_markup([slide]))):
                wanted = values.get(handle, set())
                quoted = any(
                    handle in line
                    and wanted & set(A_NUMBER.findall(A_HANDLE_ON_A_LINE.sub("", line)))
                    for line in slide.content_lines()
                )
                with self.subTest(slide=slide.number, handle=handle):
                    self.assertTrue(
                        quoted,
                        f"slide {slide.number} names {handle} and never shows "
                        f"the rate it stands for, which the build-up gives as "
                        f"{sorted(wanted)}",
                    )

    def test_it_names_at_least_one_rate_to_argue_with(self):
        """The block's whole argument is that the arithmetic is open. A slide
        of totals with no handle on it is a slide you can only disagree with by
        disagreeing with the total, which is the thing the build-up exists to
        stop."""
        self.assertTrue(
            HANDLE.search(with_markup(the_content())),
            "no rate handle anywhere on the block, so nobody in the room can "
            "argue with one rate by name",
        )


class TheCostIsInHours(unittest.TestCase):
    def test_nothing_is_priced_by_the_seat(self):
        seen = visible(the_block()).lower()
        for word in PRICED_BY_THE_SEAT:
            self.assertNotIn(
                word,
                seen,
                f"{word!r} is subscription pricing. Nobody in that room buys "
                f"software by the seat.",
            )

    def test_the_block_talks_in_hours_and_days(self):
        seen = visible(the_content()).lower()
        for unit in ("hours", "days"):
            self.assertIn(unit, seen, f"the block never says {unit!r}")


class ReworkLeadsAndSpeedFollows(unittest.TestCase):
    def test_a_slide_of_the_block_is_headed_about_rework(self):
        """The issue: *Rework leads; speed is secondary.*

        Rework gets a slide of its own, headed as such. A word somewhere in a
        bullet is the block mentioning rework, which is not the same as leading
        with it.
        """
        headings = [slide.heading.lower() for slide in the_content()]
        self.assertTrue(
            any("rework" in heading for heading in headings),
            f"no slide of the block is headed about rework. Its headings are "
            f"{headings}",
        )

    def test_rework_is_said_before_speed_is(self):
        """The same criterion, as a question about order.

        **Read across the content slides only, and the break slide is left
        out on purpose.** The break slide is headed *Rework is the argument.
        Speed is not*, which puts rework in front of speed no matter what the
        rest of the block does -- so a first draft of this check that read the
        whole block could not fail, and would have passed with the rework slide
        deleted outright.
        """
        seen = visible(the_content()).lower()
        rework = seen.find("rework")
        speed = seen.find("speed")
        self.assertNotEqual(rework, -1, "the content slides never say 'rework'")
        self.assertNotEqual(speed, -1, "the content slides never say 'speed'")
        self.assertLess(
            rework,
            speed,
            "speed is argued before rework on the money slide, which is the "
            "way round the issue says not to do it",
        )

    def test_the_unbillable_survey_is_on_this_block(self):
        """`test_deck.py` checks the deck says it somewhere, with its source.
        This checks it is said *here*, which is what the issue asks for."""
        self.assertIn("cannot be invoiced", visible(the_content()).lower())


class TheBlockIsFinishedAndFitsSixMinutes(unittest.TestCase):
    def test_nothing_on_the_block_is_still_a_placeholder(self):
        for slide in the_block():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_the_block_has_the_slides_its_own_note_says_it_has(self):
        """Six minutes is the plan's, and `test_deck.py` holds the note to it.
        What can rot here is the block quietly growing a fourth slide while its
        note still says two, and six minutes still buying two.

        The count is read off the note rather than written down here, for the
        same reason the fallback card's gap count is: a number in this file
        would be the next thing to go stale.
        """
        note = the_block()[0].note
        stated = SLIDE_COUNT.search(note)
        self.assertIsNotNone(
            stated, "the block's break slide no longer says how many slides it is"
        )
        word = stated.group(1).lower()
        self.assertIn(word, NUMBER_WORDS, f"{word!r} is not a number this reads")
        self.assertEqual(NUMBER_WORDS[word], len(the_content()))


if __name__ == "__main__":
    unittest.main()
