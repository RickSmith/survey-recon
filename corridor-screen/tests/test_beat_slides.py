"""The review-and-three-failures slides, held to the evidence behind each beat.

Issue #85. Twelve minutes, five slides, and the block the whole session has been
paying for. The three beats were scripted and captured first, under #25, #26 and
#47; these slides are written around them.

**The risk here is not a stale number. It is a stale story.** Each of these
slides tells a room what happened, and the thing that happened is committed in
`corridor-screen/captures/`. A slide can go on reading perfectly from the fourth
row while describing a run nobody captured -- which is not a hypothetical. The
skeleton's beat 2 slide said the service *"ignored the coordinate system, landed
in the ocean, and said `NoData`"*. Every capture in `captures/silent-nodata/`
says otherwise: `wkid` is honored, `units` is the parameter that is ignored, and
the token `NoData` is in no response this repo holds. That draft would have been
a slide about being confidently wrong, being confidently wrong, on a projector,
to three hundred people who could check it.

So every figure and every date on these five slides is read back out of the
committed evidence here, and the one word the evidence does not support is
checked for by name.

**What this file does not do.** Whether the deck covers the block, keeps the
clock off the projector and carries its citations is `test_deck.py`, for every
slide including these. Whether the beats themselves reproduce is
`test_manual_links.py` and `test_elevation_trap.py`. This file sits between
them: it asks whether the slide agrees with the beat.
"""

import re
import unittest

from corridor_screen import elevation_trap, manual_links

from tests.deck_reader import (
    A_PATH,
    REPO,
    note,
    on_screen,
    seen,
    slide_headed,
    slides_in_block,
)
from tests.markdown_docs import flat, markdown_section, plain, table_rows, text_of

BLOCK = "Review, seal — and the three failures"

FORCE_PUSH = REPO / "docs" / "managing-your-agent" / "the-force-push.md"
THE_CLAIM = REPO / "docs" / "managing-your-agent" / "the-claim-we-got-wrong.md"
SEAL = REPO / "docs" / "governance" / "seal-and-responsible-charge.md"
WORK_ORDER = REPO / "corridor-screen" / "captures" / "the-work-order" / "issue-7.txt"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
PLAN = REPO / "docs" / "plan-of-record.md"
GLOSSARY = REPO / "CONTEXT.md"

# `NoData` as a word rather than as part of one, so that the folder name
# `silent-nodata` -- which stays -- does not count as saying it. #104.
A_BARE_NODATA = re.compile(r"(?<![\w-])nodata")

# The five slides this work order owns, in the order the block runs them. The
# beat headings are matched on `Beat N` rather than on their whole titles, so a
# title that gets sharpened does not fail a check about ordering.
OWNED = (
    "Where the work got sent back",
    "Beat 1",
    "Beat 2",
    "Beat 3",
    "You seal it",
)

# `866.87 / 264.22 = 3.28084` on a slide, whichever sign it uses for divide.
# A slide that prints the division invites the room to do it, so the figures it
# prints have to survive being divided at the precision it printed them.
A_DIVISION = re.compile(
    r"([\d.]+)\s*(?:/|÷)\s*([\d.]+)\s*=\s*\*{0,2}([\d.]+)"
)


def block():
    """The content slides of the block, without its section break."""
    return slides_in_block(BLOCK)


def captured_elevations():
    """The two answers the beat turns on, as the committed captures hold them."""
    return elevation_trap.value_of("feet"), elevation_trap.value_of("us_feet")


def quoted(path):
    """A page as one long line, with its blockquote markers taken off first.

    `markdown_docs.flat` joins a hard-wrapped page into one line, which is what
    lets a check survive re-wrapping. It leaves the `>` at the head of each line
    alone, and every rule this block cites is quoted in a blockquote -- so
    *"prior to their implementation"* arrives as *"prior to their > implementation"*
    and a check for the sentence the rule actually turns on cannot find it.

    Kept here rather than in `markdown_docs` because this is the first caller
    that needs it. The second one is where it moves.
    """
    stripped = "\n".join(
        re.sub(r"^\s*>\s?", "", line) for line in text_of(path).splitlines()
    )
    return flat(stripped)


class TestTheBlockIsTheFiveSlidesTheWorkOrderNames(unittest.TestCase):
    """A beat that quietly lost its slide is found on stage, at 1:41."""

    def test_the_block_runs_the_five_slides_in_order(self):
        headings = [slide.heading for slide in block()]
        self.assertEqual(len(headings), len(OWNED), f"the block is {headings}")
        for heading, wanted in zip(headings, OWNED):
            with self.subTest(slide=heading):
                self.assertIn(wanted.lower(), heading.lower())

    def test_nothing_in_the_block_still_says_it_is_unfinished(self):
        for slide in block():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn("To be written", slide.body)

    def test_no_slide_in_the_block_is_marked_for_cutting(self):
        """§7 protects this block outright. The plan's own timing warning drops
        **beat 2** inside it if the run is behind at 1:36, and that instruction
        lives in beat 2's note as prose rather than as a `Cut N of M` mark --
        which `test_deck.py` would read as the block being on the cut line."""
        a_cut_mark = re.compile(r"Cut \d+ of \d+")
        for slide in block():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertIsNone(a_cut_mark.search(slide.note))

    def test_beat_two_is_the_one_its_note_offers_up_if_the_run_is_behind(self):
        said = note("Beat 2").lower()
        self.assertIn("1:36", said)
        self.assertIn("behind", said)

    def test_beat_three_says_on_the_presenter_screen_that_it_is_never_cut(self):
        self.assertIn("never cut", note("Beat 3").lower())

    def test_every_slide_in_the_block_labels_its_fallback(self):
        """#85: *"the speaker notes ... still name a fallback where one
        exists."*

        Every slide in this block has one -- `docs/presenting/fallbacks.md`
        carries a row for each. Naming it in prose is not enough: a presenter
        four minutes past the hour with no network is scanning for the word,
        not reading the note. Two of these five said it in a sentence and were
        caught by review for exactly that.
        """
        for slide in block():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertIn(
                    "Fallback:", slide.note,
                    f"slide {slide.number} has no labeled fallback to scan for",
                )


class TestWhereTheWorkGotSentBack(unittest.TestCase):
    """The slide that claims this repo's own history is worth showing.

    It is the one slide in the block with no capture behind it, because its
    evidence *is* the repo. So what is checked is that the two accounts it sends
    a presenter to are committed and still say what the slide says they say.
    """

    def test_it_sends_the_presenter_at_both_accounts(self):
        said = note("Where the work got sent back")
        for page in (FORCE_PUSH, THE_CLAIM):
            with self.subTest(page=page.name):
                self.assertIn(f"docs/managing-your-agent/{page.name}", said)

    def test_every_path_in_that_note_is_a_whole_path(self):
        """A note that wraps mid-path leaves a bare file name behind, which
        reads as a complete instruction at four minutes past the hour and is
        not one. `test_deck.py` checks the files exist; this checks the folder
        did not get left on the line above."""
        for found in re.finditer(r"[\w./-]+\.md\b", note("Where the work got sent back")):
            with self.subTest(path=found.group(0)):
                self.assertIn("/", found.group(0))

    def test_it_says_the_history_rule_was_broken_once(self):
        """`CLAUDE.md` says it was broken once, deliberately, and that the
        account is a record rather than a precedent. A slide that rounded that
        up to a habit, or down to nothing, would misread the page it points at."""
        self.assertIn("once", seen("Where the work got sent back").lower())

    def test_the_force_push_page_still_says_a_human_made_that_call(self):
        """The slide's point is not that a rule was broken. It is who chose."""
        page = flat(text_of(FORCE_PUSH))
        self.assertIn("A licensed human chose", page)
        self.assertIn("Do not squash commits or rewrite history", page)


class TestBeatOne(unittest.TestCase):
    """The superseded manual. The figures are revisions, read out of the two
    committed captures rather than typed onto the slide from memory."""

    def setUp(self):
        self.seen = on_screen("Beat 1")
        self.current = manual_links.revision_in(manual_links.capture_text("current"))
        self.legacy = manual_links.revision_in(manual_links.capture_text("legacy"))

    def test_the_captures_still_carry_two_different_revisions(self):
        """If these ever match, the beat has no beat in it and every check
        below passes while saying nothing."""
        self.assertNotEqual(self.current["revised"], self.legacy["revised"])

    def test_the_slide_names_the_revision_the_agent_cited(self):
        self.assertIn(self.legacy["revised"], self.seen)

    def test_the_slide_names_the_revision_actually_in_force(self):
        self.assertIn(self.current["revised"], self.seen)

    def test_the_slide_carries_the_address_that_serves_it(self):
        self.assertIn("txdot.gov/manuals/row/ess", self.seen)

    def test_the_slide_does_not_call_the_old_address_a_missing_page(self):
        """The whole defense turns on this. The old host does not answer at
        all, so a caller sees a timeout rather than a 404 -- and a timeout
        looks like weather, which is why the agent followed the link anyway."""
        self.assertIn("nothing accepted a connection", manual_links.HOST_TODAY)
        for missing in ("404", "not found", "page not found"):
            with self.subTest(phrase=missing):
                self.assertNotIn(missing, self.seen.lower())


class TestBeatTwo(unittest.TestCase):
    """The answer that was wrong rather than missing.

    Two numbers and a ratio, all three read out of `captures/silent-nodata/`.
    """

    def setUp(self):
        self.seen = seen("Beat 2")
        self.feet, self.us_feet = captured_elevations()

    def test_both_captured_answers_are_on_the_slide(self):
        for value in (self.feet, self.us_feet):
            with self.subTest(value=value):
                self.assertIn(f"{value:,.2f}", self.seen)

    def test_the_conversion_factor_on_the_slide_is_the_captured_one(self):
        """The point of the beat is that the second answer is the first one in
        another unit. A slide stating the conversion factor states a claim
        about two numbers beside it, so it is divided rather than trusted."""
        ratio = round(self.feet / self.us_feet, 5)
        self.assertEqual(ratio, round(elevation_trap.FEET_PER_METER, 5))
        self.assertIn(f"{ratio}", self.seen)

    def test_any_sum_this_block_prints_is_true_at_the_precision_it_prints(self):
        """**A slide that shows its arithmetic is asking the room to check it.**

        The first draft of this one read `866.87 / 264.22 = 3.28084`, and every
        figure in it was read out of the captures. It is still wrong: divide the
        two numbers a room can see and the answer is 3.28086. The full-precision
        check above passed the whole time, because it divided the captures
        rather than the slide -- a guard testing something other than the thing
        on the projector.

        A surveyor who does that division on a phone in the fourth row gets a
        different last digit from the one this session just told them to trust,
        during the beat about being confidently wrong. So the sum is checked as
        printed, and the fix was to stop printing a sum at all.
        """
        for slide in block():
            for line in slide.content_lines():
                found = A_DIVISION.search(line)
                if not found:
                    continue
                left, right, stated = found.groups()
                places = len(stated.partition(".")[2])
                with self.subTest(slide=slide.number, sum=found.group(0)):
                    self.assertEqual(
                        round(float(left) / float(right), places), float(stated),
                        f"slide {slide.number} prints a sum that does not come out",
                    )

    def test_that_arithmetic_check_can_actually_fail(self):
        """The guard on the guard, since the check above finds nothing today --
        and a check that can only pass is a comment."""
        found = A_DIVISION.search("- 866.87 ÷ 264.22 = **3.28084**, feet per meter")
        left, right, stated = found.groups()
        places = len(stated.partition(".")[2])
        self.assertNotEqual(round(float(left) / float(right), places), float(stated))

    def test_the_slide_names_the_unit_a_surveyor_would_ask_for(self):
        self.assertIn("US_Feet", on_screen("Beat 2"))

    def test_the_slide_never_says_a_word_no_capture_contains(self):
        """`NoData` is the name this beat was given in the plan of record and
        in the ticket that scripted it, and no response in `captures/` contains
        it. The Gulf of Mexico point -- the one a `NoData` would belong to --
        answers with plain text that is not JSON at all.

        This is the check that would have caught the skeleton's draft, and it
        is the same rule the slide beside it is about: say what the evidence
        says, or say you could not confirm it.

        **The folder is still called `silent-nodata`** and that is deliberate:
        renaming committed evidence to match a corrected story is its own kind
        of tidying-up. So the word is looked for as a word, which is why a
        hyphen in front of it does not count."""
        for name in elevation_trap.CAPTURES:
            with self.subTest(capture=name):
                self.assertIsNone(
                    A_BARE_NODATA.search(elevation_trap.capture_text(name).lower())
                )
        self.assertIsNone(A_BARE_NODATA.search(self.seen.lower().replace("`", "")))

    def test_the_slide_does_not_blame_the_coordinate_system(self):
        """`wkid` is honored -- `wkid_mercator` is the capture that proves it,
        and it is why this beat moved to `units`. A slide still blaming the
        coordinate system is describing the ticket rather than the run."""
        self.assertEqual(
            elevation_trap.value_of("wkid_mercator"), self.feet,
            "the Web Mercator capture no longer agrees with the degrees one",
        )
        self.assertNotIn("coordinate system", self.seen.lower())

    def test_the_slide_says_no_error_was_raised(self):
        """A reader who thinks this failed loudly has taken the opposite
        lesson from the one the beat teaches."""
        self.assertRegex(self.seen.lower(), r"no error|without an error|nothing said")


class TestBeatThree(unittest.TestCase):
    """The error in our own work order, held to the captured issue.

    Beat three is the one the plan of record protects outright, and the one a
    room is most likely to check afterward. Every claim on it is in
    `captures/the-work-order/issue-7.txt`, which is a terminal's bytes rather
    than a retelling.
    """

    def setUp(self):
        self.seen = seen("Beat 3")
        self.captured = flat(text_of(WORK_ORDER))

    def test_the_work_order_still_carries_the_instruction_it_was_given(self):
        self.assertIn(
            "It states plainly that TBPELS has not spoken directly to AI",
            self.captured,
        )

    def test_the_same_work_order_still_carries_the_rule_that_refused_it(self):
        """This is the sentence the slide credits, and it is criterion 5 of the
        very issue whose criterion 4 was wrong. The account on
        `the-claim-we-got-wrong.md` credits the handbook rule it came from;
        both are true and the capture is the one on the projector."""
        self.assertIn(
            "No invented requirement anywhere", self.captured,
        )
        self.assertIn("is what caught this one", self.captured)

    def test_the_slide_credits_the_criterion_and_not_the_agent(self):
        self.assertRegex(self.seen.lower(), r"criterion 5|acceptance criteri")

    def test_the_opinion_date_on_the_slide_is_the_date_in_the_capture(self):
        self.assertIn("14 November 2024", self.captured)
        self.assertRegex(self.seen, r"14 Nov(?:ember)? 2024")

    def test_the_slide_carries_the_board_source_beside_the_opinion(self):
        """`test_deck.py` holds every slide saying `PAO 71` to this. Repeated
        here because this is the slide a room photographs."""
        self.assertIn("pels.texas.gov", self.seen)

    def test_the_number_of_pages_that_carried_it_is_the_number_written_up(self):
        """*Four pages* is a count, and a count in prose beside a table is a
        count that rots. It is read off the table on the account page."""
        rows = table_rows(text_of(THE_CLAIM))
        pages = [row for row in rows if row and row[0].startswith("`")]
        self.assertEqual(len(pages), 4, f"the account now lists {len(pages)} pages")
        self.assertIn("four pages", self.seen.lower())


class TestTheSeal(unittest.TestCase):
    """The punchline, and the claim most likely to be quoted afterward.

    It said the opposite on four pages of this repo until 2026-09-12, so every
    sentence on it is checked against the governance page that quotes the rules
    in full rather than against this file's memory of them.
    """

    def setUp(self):
        self.seen = seen("You seal it")
        self.page = quoted(SEAL)

    def test_the_board_did_speak_and_the_page_still_says_so(self):
        self.assertIn("Policy Advisory Opinion 71", self.page)
        self.assertIn("14 November 2024", self.page)

    def test_the_slide_says_the_tool_is_not_banned_as_narrowly_as_the_board_did(self):
        """**The board said *directly* ban, and the qualifier is the claim.**

        PAO 71 says neither the Practice Acts nor the board rules *directly*
        ban AI software. It does not say nothing anywhere bans it, and the
        opinion goes on to set three caveats. This slide's own note calls it the
        claim most likely to be photographed and forwarded, and a first draft
        of it read "Nothing bans it" — broader than the source it cites, on the
        one slide that can least afford to be.
        """
        self.assertIn("directly ban the use of AI software", self.page)
        self.assertRegex(self.seen.lower(), r"is a tool")
        self.assertRegex(self.seen.lower(), r"bans it directly|directly bans")
        self.assertNotIn("nothing bans it", self.seen.lower())

    def test_responsible_charge_is_a_synonym_and_the_slide_does_not_soften_it(self):
        self.assertIn('Synonymous with the term "direct supervision"', self.page)
        self.assertRegex(self.seen.lower(), r"synonym|not a looser|same standard")

    def test_the_slide_keeps_the_word_the_rule_turns_on(self):
        """§ 131.2(11) is *prior to their implementation*. A slide that said
        "review the work afterward" would be describing a different rule."""
        self.assertIn("prior to their implementation", self.page)
        self.assertRegex(self.seen.lower(), r"before they are acted on|prior to")

    def test_the_citations_on_the_slide_are_the_ones_the_page_quotes(self):
        for section in ("131.2(11)", "131.2(38)"):
            with self.subTest(section=section):
                self.assertIn(section, self.page.replace("§ ", "§").replace("§", "§ "))
        seen = on_screen("You seal it")
        self.assertIn("131.2", seen)
        self.assertIn("pels.texas.gov", seen)


class TestTheFallbackCardAgreesWithTheDeck(unittest.TestCase):
    """A presenter holds the card and looks at the slide. Two names for one
    beat is a presenter deciding, at the podium, whether they are the same
    thing.

    This is the check that was missing when beat 2 was renamed: the card, the
    plan of record and the deck all carried `the silent NoData`, and nothing
    held them to each other.
    """

    def rows_for_the_block(self):
        return [row for row in table_rows(text_of(CARD)) if row and "1:36" in row[0]]

    def test_the_card_covers_the_block(self):
        self.assertGreaterEqual(len(self.rows_for_the_block()), 4)

    def test_every_beat_on_the_card_is_named_the_way_the_slide_names_it(self):
        headings = {slide.heading for slide in block()}
        for row in self.rows_for_the_block():
            named = row[1].replace("**", "").replace("`", "").strip()
            if not named.lower().startswith("beat"):
                continue
            with self.subTest(card=named):
                self.assertIn(
                    named,
                    {heading.replace("`", "") for heading in headings},
                    f"the card calls it {named!r} and no slide is headed that",
                )


class TestThePlanAndTheGlossaryAgreeWithTheDeck(unittest.TestCase):
    """The other two documents that carried the old account of beat 2.

    The card was held to the deck above. The plan of record and `CONTEXT.md`
    were not, and both went on describing a run nobody captured. The skeleton
    slide for this beat was written out of the glossary rather than out of the
    captures, and inherited every error in it.

    **That is why these two pages get checked and a third does not.**
    `CONTEXT.md` is the glossary every other page is told to trust, and the
    plan of record is the page that gets read out loud.

    Issue #104. What was wrong and how it survived is the account at
    `docs/managing-your-agent/the-description-that-outlived-its-evidence.md`,
    which is the place to change it rather than here.
    """

    def setUp(self):
        self.section = markdown_section(text_of(PLAN), "### The failure beat")
        self.beat = plain(self.section)

    def short_name(self):
        """`wrong, not missing` -- the deck's own name for beat 2, read off the
        slide rather than written down a second time here.

        Guarded, because an unguarded `partition` that misses returns an empty
        string and every caller degrades to `assertIn("", ...)` -- a check that
        can only pass, which is what this whole file exists to not be."""
        heading = next(slide.heading for slide in block() if "Beat 2" in slide.heading)
        _, dash, after = heading.partition("—")
        self.assertTrue(dash, f"beat 2 is headed {heading!r} and carries no short name")
        self.assertTrue(after.strip(), f"beat 2 is headed {heading!r}")
        return after.strip().lower()

    def glossary_entry(self):
        """The `NoData` row of `CONTEXT.md`, by its term rather than by where
        in the table it sits."""
        return next(
            row[1] for row in table_rows(text_of(GLOSSARY))
            if len(row) > 1 and row[0].replace("*", "").replace("`", "") == "NoData"
        )

    def test_the_plan_names_beat_two_the_way_the_slide_is_headed(self):
        """Scoped to the numbered bullet rather than to the section, so that it
        can fail on its own. The timing-warning check below reads the same name
        out of the same section, and a section-wide check here would have been
        passed by the warning alone."""
        bullet = next(
            line for line in self.section.splitlines() if line.startswith("2. ")
        )
        self.assertIn(self.short_name(), plain(bullet).lower())

    def test_the_timing_warning_names_the_beat_it_offers_to_cut(self):
        """It is the sentence a presenter acts on at 1:36, so it has to name
        the beat by the name that is on the slide in front of them."""
        _, marker, warning = flat(self.section).partition("Timing warning.")
        self.assertTrue(marker, "the failure-beat section carries no timing warning")
        self.assertIn(self.short_name(), plain(warning).lower())

    def test_the_plan_stops_naming_the_beat_after_a_word_no_capture_contains(self):
        """The whole failure-beat section, not just beat 2 -- the old name was
        in the beat and in the timing warning that offers to cut it, and both
        get read out loud.

        Not the whole page, though, because the ban is on the *claim* and not
        on the token. `NoData` stays a term worth defining -- see the glossary
        check below -- and a page-wide ban would forbid defining it."""
        self.assertIsNone(A_BARE_NODATA.search(self.beat.lower()))

    def test_the_glossary_keeps_the_term_and_drops_the_claim(self):
        """`NoData` is a real thing an elevation service returns, so the entry
        stays. What goes is this service having returned one here, and the two
        details that were invented around it."""
        entry = self.glossary_entry()
        self.assertIn("no capture", entry.lower())
        for invented in ("Atlantic", "Web Mercator"):
            with self.subTest(claim=invented):
                self.assertNotIn(invented.lower(), entry.lower())

    def test_the_plan_blames_the_unit_rather_than_the_coordinate_system(self):
        """`wkid` is honored, so a page still saying the coordinate system moved
        the point is describing the ticket rather than the run.

        Section-wide again, for the same reason as the check above: the run of
        show is three beats and a timing warning, and none of the other two is
        about a coordinate system either."""
        self.assertIn("us_feet", self.beat.lower())
        self.assertNotIn("web mercator", self.beat.lower())

    def test_the_glossary_entry_carries_both_captured_answers(self):
        """Every sentence in the entry has to be supported by a capture. The
        two numbers are the part a reader can check, so they are read back out
        of the captures rather than trusted."""
        entry = self.glossary_entry()
        feet, us_feet = captured_elevations()
        self.assertIn(str(feet), entry)
        self.assertIn(str(us_feet), entry)

    def test_the_glossary_points_at_the_account_of_the_correction(self):
        entry = flat(text_of(GLOSSARY))
        self.assertIn("the-description-that-outlived-its-evidence.md", entry)
        named = REPO / "docs" / "managing-your-agent" / (
            "the-description-that-outlived-its-evidence.md"
        )
        self.assertTrue(named.exists(), f"{named} is linked and not committed")


class TestThePathsOnTheseSlidesAreReal(unittest.TestCase):
    """Every one of these slides points somewhere. A slide pointing at a file
    that is not committed is worse than one pointing nowhere, because it is
    read out loud."""

    def test_every_path_on_a_slide_in_this_block_is_committed(self):
        for slide in block():
            for found in A_PATH.finditer("\n".join(slide.content_lines())):
                with self.subTest(slide=slide.number, path=found.group(1)):
                    named = REPO / found.group(1)
                    self.assertTrue(
                        named.exists(),
                        f"slide {slide.number} shows {found.group(1)}, which is not here",
                    )


if __name__ == "__main__":
    unittest.main()
