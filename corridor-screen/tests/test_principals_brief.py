"""The principals' brief, held to the five things it promises and to its source.

Issue #30. `docs/for-principals/index.md` is the one page a firm owner is handed
on the way out of the room. It is the only page in this repo written for
somebody who will install nothing that week, open no terminal, and decide
instead whether to point one person in the firm at the rest of it.

That makes it the page with the most ways to go quietly wrong, so it is checked
rather than trusted:

* **It is one page.** The issue asks for one page, not two, and for a principal
  to read it in four minutes and act on it. Those are two different limits, the
  paper is the tighter one, and it is the one enforced
* **There is no command line on it.** No commands, and no fenced code block for
  one to hide in
* **The cost is in hours**, never in a price per seat or per month
* **The hours are the build-up's own hours.** Every crew-day figure on the page
  is read back out of `project-sh16/crew-day.md` and compared, and every rate
  handle it names is a handle that build-up actually has
* **Rework is the argument**, with its citation, at the manual's live address
* **It says who signs**, and links to the rule that says so

**Why check prose at all.** `test_plan_of_record.py` already answers that for
this repo, and the answer holds harder here:

> A number written in prose beside a thing is a number that rots.

The build-up regenerates whenever the tool runs. This page does not. Left
unchecked, the first re-run would put a different number in the repo than the
one on the handout in three hundred pockets, and the handout is the copy nobody
can correct afterwards.

**What this file deliberately does not do.** It does not check that the page is
*good*. Nothing here can. It checks the claims the issue makes that a machine
can actually settle, and leaves the rest to the review that every change in this
repo goes through anyway.
"""

import re
import unittest
from pathlib import Path

from tests.markdown_docs import table_rows, text_of

REPO = Path(__file__).resolve().parents[2]
BRIEF = REPO / "docs" / "for-principals" / "index.md"
BUILD_UP = REPO / "project-sh16" / "crew-day.md"

# The issue sets two limits, and they are not the same limit.
#
# **Four minutes**, at two hundred words a minute -- the ordinary rate for
# reading something you have to think about, slower than a novel and faster than
# a contract. That allows 800 words.
#
# **One page, not two.** A US Letter page at a readable size, with headings and
# the white space that makes a handout look like a handout rather than a
# contract, holds about 600 words. The deck holds this page up as a printed
# handout, so the paper is real and so is its edge.
#
# The tighter of the two is the one that binds, and it is the paper. A page that
# reads in three minutes and fits on one sheet satisfies both criteria; one that
# uses all four minutes satisfies only one of them.
READING_WORDS_PER_MINUTE = 200
READING_MINUTES = 4
WORDS_ON_A_PRINTED_PAGE = 600
WORD_BUDGET = min(READING_WORDS_PER_MINUTE * READING_MINUTES, WORDS_ON_A_PRINTED_PAGE)

# The five questions the issue asks the page to answer. Matched on a distinctive
# few words rather than on a whole heading, so the page may word its own
# headings without this file getting a vote on the wording.
THE_FIVE_QUESTIONS = [
    "Monday",
    "cost",
    "policy",
    "liable",
    "one person",
]

# What a command looks like on a page that is not supposed to have any. These
# are the tools this repo asks a reader to run somewhere else. A file path
# inside a link is not a command and is not here.
#
# Whole words, because a plain substring search finds `gh ` inside "through
# Bexar" and `cd ` inside half the prose in the language. It found both on the
# first run of this file, which is the entire argument for the word boundaries.
COMMAND_WORDS = [
    "git",
    "gh",
    "python",
    "pip",
    "npx",
    "mkdocs",
    "cd",
    "unittest",
    "corridor-screen",
]

# A shell prompt with something typed at it. Only the dollar sign, deliberately:
# a `>` at the start of a line is a markdown quotation, and this repo quotes the
# board and the manual on nearly every page it has.
PROMPT = re.compile(r"(?:^|\s)\$\s+\w", re.MULTILINE)

# Buying software by the seat, in the words it gets sold in. The issue is blunt
# about this: cost is in billable-hour terms, never subscription pricing.
SUBSCRIPTION_WORDS = [
    "subscription",
    "per seat",
    "a seat",
    "per user",
    "per month",
    "/month",
    "monthly fee",
    "license fee",
    "free tier",
    "pricing plan",
]

# The address the manual lives at, and the address search engines still hand
# out. CLAUDE.md names both. The second is a scripted failure in the session,
# which is exactly why it must not reach the handout.
LIVE_MANUAL = "txdot.gov/manuals/row/ess"
SUPERSEDED_MANUAL = "onlinemanuals.txdot.gov"

# How the build-up writes the two day counts it will not add together.
DAY_COUNTS = re.compile(
    r"\*\*(\d+) crew-days in the field\. (\d+) days in the office\.\*\*"
)
# How it writes the size of a crew, which is the unit those day counts are in.
CREW_SIZE = re.compile(r"A crew-day here is \*\*(\d+) people\*\*")
# Its two totals, and the count of lines it could not total at all.
FIELD_HOURS = re.compile(r"\*\*Field hours total: ([\d.]+) hours\.\*\*")
OFFICE_HOURS = re.compile(r"\*\*Office hours total: ([\d.]+) hours\.\*\*")
UNTOTALED = re.compile(r"\*\*That total is a floor\.\*\* (\d+) lines")

# A rate handle, as the build-up stamps them: A1 through A12, in a table whose
# first cell is the handle in backticks.
HANDLE = re.compile(r"`(A\d+)`")


def one(pattern, markdown, what):
    """The single match for a pattern, or a failure that names what was wanted.

    Every pattern above describes a sentence the build-up writes exactly once.
    Finding it twice is as much a finding as not finding it at all -- a second
    copy is the thing that drifts -- so both are failures here.
    """
    found = pattern.findall(markdown)
    if len(found) != 1:
        raise AssertionError(
            f"{what} appears {len(found)} times in {BUILD_UP.name}, wanted once"
        )
    return found[0]


def flat(markdown):
    """The document as one long line, for checking that a phrase is in it.

    Every page in `docs/` is hard-wrapped at about eighty characters, so half
    the phrases worth checking have a line break somewhere in the middle of
    them. A break is where the wrapping fell, not something the page says, and a
    check that fails when a sentence is re-wrapped is a check that punishes
    editing.
    """
    return " ".join(markdown.split())


def readable_words(markdown):
    """What a reader actually reads, as a list of words.

    Link addresses, HTML and the pipes and dashes that draw a table are all
    things a reader's eye does not spend time on, so none of them are counted
    against a budget that is about reading time. The words inside a table cell
    are counted, because those do get read.
    """
    text = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    # The address half of a link, but not its words. "[the build-up](https://…)"
    # costs a reader three words, not thirty characters of URL.
    text = re.sub(r"\]\([^)]*\)", "] ", text)
    text = re.sub(r"^\s*\|[-: |]+\|\s*$", " ", text, flags=re.MULTILINE)
    text = text.replace("|", " ")
    return [word for word in text.split() if re.search(r"[A-Za-z]", word)]


class TheBriefIsOnePage(unittest.TestCase):
    def test_it_fits_on_one_printed_page(self):
        words = readable_words(text_of(BRIEF))
        self.assertLessEqual(
            len(words),
            WORD_BUDGET,
            f"{len(words)} words does not fit on one sheet of paper, and "
            f"{WORD_BUDGET} is the budget. The issue says one page, not two, "
            f"and read in {READING_MINUTES} minutes at "
            f"{READING_WORDS_PER_MINUTE} words a minute.",
        )

    def test_the_chapter_is_one_file(self):
        """One page means one page. A second file in the folder is two."""
        pages = sorted(page.name for page in BRIEF.parent.glob("*.md"))
        self.assertEqual(["index.md"], pages)

    def test_it_answers_all_five_questions(self):
        markdown = text_of(BRIEF).lower()
        for question in THE_FIVE_QUESTIONS:
            self.assertIn(
                question.lower(),
                markdown,
                f"nothing on the page answers the question about {question!r}",
            )

    def test_it_is_no_longer_a_stub(self):
        markdown = text_of(BRIEF)
        for leftover in ("Placeholder", "To be written", "to be written"):
            self.assertNotIn(leftover, markdown)


class TheBriefHasNoTerminalOnIt(unittest.TestCase):
    def test_no_fenced_code_block(self):
        self.assertNotIn(
            "```",
            text_of(BRIEF),
            "a code fence, on the one page whose whole promise is that there is "
            "no command line on it",
        )

    def test_no_command_anywhere(self):
        markdown = text_of(BRIEF)
        for command in COMMAND_WORDS:
            found = re.search(rf"(?<![\w-]){re.escape(command)}(?![\w-])", markdown)
            self.assertIsNone(
                found,
                f"{command!r} is a command, and the issue says no command line "
                f"anywhere on this page",
            )

    def test_no_shell_prompt(self):
        self.assertIsNone(PROMPT.search(text_of(BRIEF)))


class TheCostIsInHours(unittest.TestCase):
    def test_nothing_is_priced_by_the_seat(self):
        markdown = text_of(BRIEF).lower()
        for word in SUBSCRIPTION_WORDS:
            self.assertNotIn(
                word,
                markdown,
                f"{word!r} is subscription pricing. Nobody in that room buys "
                f"software by the seat.",
            )

    def test_the_day_counts_are_the_build_ups_own(self):
        """The two numbers the build-up refuses to add, on the page as it writes
        them, and neither one given as the other."""
        field, office = one(DAY_COUNTS, text_of(BUILD_UP), "the two day counts")
        markdown = flat(text_of(BRIEF))
        self.assertIn(f"{field} crew-days", markdown)
        self.assertIn(f"{office} days in the office", markdown)

    def test_it_says_how_big_a_crew_day_is(self):
        """A day count means nothing without the crew it counts."""
        people = one(CREW_SIZE, text_of(BUILD_UP), "the crew size")
        self.assertIn(f"{people} people", flat(text_of(BRIEF)))

    def test_the_hours_it_quotes_are_the_build_ups_hours(self):
        build_up = text_of(BUILD_UP)
        markdown = flat(text_of(BRIEF))
        for pattern, what in ((FIELD_HOURS, "field"), (OFFICE_HOURS, "office")):
            hours = one(pattern, build_up, f"the {what} hours total")
            self.assertIn(
                hours,
                markdown,
                f"the page quotes no {what} hours figure, or quotes one the "
                f"build-up does not have",
            )

    def test_it_says_the_estimate_is_a_floor(self):
        """The two lines with no total are the most honest thing in the
        build-up, and the easiest thing to leave off a summary of it."""
        lines = one(UNTOTALED, text_of(BUILD_UP), "the lines with no total")
        markdown = flat(text_of(BRIEF))
        self.assertIn(f"{lines} lines", markdown)
        self.assertIn("floor", markdown)

    def test_every_rate_handle_it_names_is_a_real_handle(self):
        """A handle is an invitation to argue with one rate by name. A handle
        the build-up does not have sends that argument nowhere."""
        real = {
            row[0].strip("`")
            for row in table_rows(text_of(BUILD_UP))
            if row and HANDLE.fullmatch(row[0])
        }
        self.assertTrue(real, "no rate handles found in the build-up at all")
        for handle in set(HANDLE.findall(text_of(BRIEF))):
            self.assertIn(handle, real, f"{handle} is not a rate in {BUILD_UP.name}")


class TheArgumentIsRework(unittest.TestCase):
    def test_the_unbillable_survey_is_on_the_page(self):
        self.assertIn("cannot be invoiced", flat(text_of(BRIEF)).lower())

    def test_that_claim_carries_its_source(self):
        """A number with legal consequence gets a source beside it, and this is
        the sentence in the session most likely to be repeated to somebody's
        accountant."""
        self.assertIn(LIVE_MANUAL, text_of(BRIEF))

    def test_it_does_not_cite_the_superseded_address(self):
        self.assertNotIn(SUPERSEDED_MANUAL, text_of(BRIEF))


class TheBriefSaysWhoSigns(unittest.TestCase):
    def test_it_says_who_signs_plainly(self):
        markdown = text_of(BRIEF).lower()
        self.assertIn("seal", markdown)
        self.assertIn("rpls", markdown)

    def test_it_points_at_the_rule_rather_than_paraphrasing_it(self):
        self.assertIn("seal-and-responsible-charge.md", text_of(BRIEF))


class TheBriefsLinksGoSomewhere(unittest.TestCase):
    def test_every_page_it_links_to_is_committed(self):
        """`mkdocs build --strict` catches this on the site build, and by then
        the page is already on a projector. Catch it in the suite instead."""
        for target in re.findall(r"\]\(([^)]+)\)", text_of(BRIEF)):
            if target.startswith("http") or target.startswith("#"):
                continue
            page = (BRIEF.parent / target.split("#")[0]).resolve()
            self.assertTrue(page.exists(), f"{target} is not a file in docs/")


if __name__ == "__main__":
    unittest.main()
