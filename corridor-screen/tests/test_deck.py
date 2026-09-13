"""The slide deck, held against the run of show it is supposed to cover.

Issue #12 asks for a skeleton rather than a talk: **a slide for every block of
the two hours, with the clock in the speaker notes, section breaks on the act
boundaries, and type a back row can read.** The content lands later, under #31
through #34. What this file checks is the frame.

A deck is the one document in this repo nobody reads carefully. It gets skimmed
in a hotel room the night before, and a block that quietly has no slide is
discovered on stage. So the deck is checked the same way the fallback card is,
one folder over, and for the same reason:

* every block of the run of show in `docs/plan-of-record.md` §5 has at least one
  slide, and the deck invents no block the plan does not have
* the slides arrive in the order the session runs them, in one run each
* every slide carries a speaker note, and that note opens with the block's
  clock and its length **taken from the plan** rather than typed again here
* every block opens with a break slide, so a cut is made by deleting whole
  slides between two breaks rather than by picking through a deck
* every item on the cut line in §7 is marked on the slide it would take out,
  and nothing §7 says never to cut is marked
* every file a speaker note sends a presenter to is committed
* nothing in the theme drops below 28pt, and no slide carries more than the
  1920 x 1080 canvas holds

**Why read the plan instead of restating it.** `docs/plan-of-record.md` is the
spec. A deck that kept its own private copy of the run of show would go on
passing its own tests for weeks after the run of show changed, which is the
exact failure this file exists to prevent.

**Where the rest lives.** Opening a committed markdown document and reading a
table out of it is `tests/markdown_docs.py`, shared with `test_fallbacks.py`.
Working out how much room a slide asks the projector for is
`tests/slide_canvas.py`, which changes when the theme changes rather than when
the session does.
"""

import itertools
import re
import unittest
from collections import namedtuple
from pathlib import Path

from corridor_screen.cache import long_path

from tests.markdown_docs import markdown_section, table_rows, text_of
from tests.slide_canvas import Canvas, points, style_rules

REPO = Path(__file__).resolve().parents[2]
DECK = REPO / "docs" / "slides" / "beyond-the-prompt.md"
SLIDES_PAGE = REPO / "docs" / "slides" / "index.md"
THEME = REPO / "docs" / "slides" / "themes" / "tsps.css"
PLAN = REPO / "docs" / "plan-of-record.md"
SLIDES_WORKFLOW = REPO / ".github" / "workflows" / "slides.yml"

# `0:57–1:18`, with the en dash the plan of record actually uses. Searched for
# rather than anchored, because this one has to be found inside a line of prose
# as well as alone in a table cell -- which is why it is not the same pattern
# `test_fallbacks.py` uses, and not shared with it.
A_TIME = re.compile(r"\d:\d\d\u2013\d:\d\d")

# The first line of a speaker note, which is the line this whole file keys on:
#
#     0:30–0:46 · 16 min · Act I — The grilling
#
# A note is told apart from a Marp directive by that leading digit. Directives
# are `_class: title` and the like, so they start with a letter or an
# underscore and can never match this.
A_NOTE = re.compile(
    r"^(?P<time>\d:\d\d\u2013\d:\d\d) \u00b7 (?P<min>\d+) min \u00b7 (?P<block>.+)$"
)

# `1. Hermes segment → recorded teaser`, in §7.
A_CUT = re.compile(r"^(\d+)\.\s+(.+)$")

# What a slide has to say to claim it is the one a cut takes out.
CUT_MARK = "Cut {rank} of {total}"

# What a slide says on its face while it is still waiting for its content. It
# is on the slide rather than in the note on purpose: the note is only on the
# presenter's screen, and the thing being guarded against is a half-finished
# deck going on a projector looking finished.
PLACEHOLDER = "To be written"

# What a placeholder says when no work order would fill it. Building the frame
# is what found these: #31, #32, #33 and #34 write some of the slides and
# nothing writes the rest. Same rule as everywhere else in this repo -- "not
# found", never "does not exist" -- so the gap is a sentence on a page rather
# than a discovery in October.
NO_WORK_ORDER = "no work order yet"

# Marp starts a new slide on a line that is exactly three dashes. The front
# matter is fenced with the same three, which is why it is stripped first.
A_SLIDE_BREAK = "---"

# The class that makes a slide a section break. The opening slide is a break
# too -- it is what is on screen for the whole cold open -- and it carries
# `title` instead.
BREAK_CLASSES = ("divider", "title")

# Words too common to identify anything, dropped before the phrases §7 uses for
# the blocks it protects are matched against the names §5 gives them.
COMMON_WORDS = ("the", "a", "an", "and", "of", "our", "own")

# One row of the run of show. The three travel together through every check
# here, so they travel as one thing.
Block = namedtuple("Block", "time minutes label")


# ---------------------------------------------------------------------------
# Reading the plan of record
# ---------------------------------------------------------------------------


def block_label(cell):
    """The short name of a block, out of the long cell the plan writes.

    The plan gives each block a name and then a sentence about it, in one cell:

        **Act I — The grilling.** `/grill-with-docs` live → `/to-spec` → ...

    A slide heading wants the name and not the sentence, so this takes what is
    in front of the first full stop. One row -- "Stretch + questions" -- has no
    full stop at all and is its own name, which is why the fallback is the
    whole cell rather than an error.
    """
    plain = cell.replace("**", "").replace("*", "").replace("`", "").strip()
    name, _, _rest = plain.partition(". ")
    return name.rstrip(".").strip()


def run_of_show():
    """The blocks of the session, in order, read from the plan of record.

    Read rather than restated, for the reason in this file's docstring.
    """
    section = markdown_section(text_of(PLAN), "## 5. Run of show")
    return [
        Block(row[0], int(row[1]), block_label(row[2]))
        for row in table_rows(section)
        if A_TIME.fullmatch(row[0])
    ]


def cut_line():
    """What gets dropped if the session runs long, in the order it is dropped.

    §7 of the plan of record. The deck marks each of these on the slide it
    would take out, so the count is read from the plan rather than written
    down twice.
    """
    section = markdown_section(text_of(PLAN), "### Cut line, in order")
    items = []
    for line in section.splitlines():
        found = A_CUT.match(line.strip())
        if found:
            items.append((int(found.group(1)), found.group(2)))
    if not items:
        raise AssertionError("the plan of record no longer has a cut line")
    return items


def never_cut():
    """The blocks §7 says never to cut, as the labels §5 gives them.

    The two sections do not use the same words for the same block. §7 writes
    "the failure beat" and "the accountability close"; §5 heads the same two
    "Review, seal — and the three failures" and "Accountability · Monday
    morning · the live issue". So a phrase is matched to a block on any word it
    carries that is not a common one, allowing a word in §7 to be the start of
    a longer word in §5 -- which is what joins "failure" to "failures".

    A straight substring match was tried first and quietly matched two of the
    four. That is the failure this returns a resolved list to make visible:
    the caller checks it found every block before it trusts any of them.
    """
    section = markdown_section(text_of(PLAN), "### Cut line, in order")
    stated = re.search(r"\*\*Never cut:\*\*(.+)", section)
    if not stated:
        raise AssertionError("the plan of record no longer says what never to cut")
    resolved = {}
    for phrase in stated.group(1).split(","):
        phrase = phrase.strip(" .*")
        if not phrase:
            continue
        wanted = [
            word for word in re.findall(r"\w+", phrase.lower())
            if word not in COMMON_WORDS
        ]
        resolved[phrase] = [
            block for block in run_of_show()
            if any(
                found.startswith(word)
                for word in wanted
                for found in re.findall(r"\w+", block.label.lower())
            )
        ]
    return resolved


# ---------------------------------------------------------------------------
# Reading the deck
# ---------------------------------------------------------------------------


class Slide:
    """One slide of the deck: its markdown, its Marp directives, its note."""

    def __init__(self, number, body):
        self.number = number
        self.body = body
        # A directive is one line and its name starts with a letter, optionally
        # behind an underscore -- `<!-- _class: title -->`. Both halves of that
        # matter: without them a speaker note beginning "0:30–0:46 · ..." parses
        # as a directive named `0`, and a note that happened to open with the
        # word "class" would set one.
        self.directives = dict(
            re.findall(r"<!--\s*(_?[a-zA-Z][\w-]*)\s*:\s*([^\n>]*?)\s*-->", body)
        )
        self.notes = [
            comment.strip()
            for comment in re.findall(r"<!--(.*?)-->", body, flags=re.S)
            if comment.strip()[:1].isdigit()
        ]

    @property
    def classes(self):
        """The Marp classes on this slide. A slide may carry more than one."""
        return self.directives.get("_class", "").split()

    @property
    def note(self):
        """The one speaker note on this slide, or "" if it has none."""
        return self.notes[0] if len(self.notes) == 1 else ""

    @property
    def heading(self):
        for line in self.body.splitlines():
            if line.startswith("#"):
                return line.lstrip("#").strip()
        return ""

    @property
    def is_a_break(self):
        return any(klass in BREAK_CLASSES for klass in self.classes)

    def content_lines(self):
        """The lines a viewer actually sees, with the markdown stripped off.

        Comments, directives and blank lines are dropped: a note is for the
        presenter's screen and a blank line renders as nothing.
        """
        without_comments = re.sub(r"<!--.*?-->", "", self.body, flags=re.S)
        return [line.rstrip() for line in without_comments.splitlines() if line.strip()]


def front_matter_and_body(markdown):
    """Split the deck's YAML front matter off the slides.

    Marp fences front matter with the same three dashes it separates slides
    with, so the front matter has to come off before anything counts slides.
    """
    lines = markdown.splitlines()
    if lines[0].strip() != A_SLIDE_BREAK:
        raise AssertionError("the deck has no front matter, so Marp will not render it")
    for end in range(1, len(lines)):
        if lines[end].strip() == A_SLIDE_BREAK:
            return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])
    raise AssertionError("the deck's front matter is never closed")


def slides():
    """Every slide of the deck, in order, numbered from 1."""
    _front, body = front_matter_and_body(text_of(DECK))
    parts, current, fenced = [], [], False
    for line in body.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if line.strip() == A_SLIDE_BREAK and not fenced:
            parts.append("\n".join(current))
            current = []
            continue
        current.append(line)
    parts.append("\n".join(current))
    return [Slide(n, part) for n, part in enumerate(parts, start=1) if part.strip()]


def noted(slide):
    """The Block a slide's speaker note claims to belong to, or None."""
    if not slide.note:
        return None
    found = A_NOTE.match(slide.note.splitlines()[0].strip())
    if not found:
        return None
    return Block(found.group("time"), int(found.group("min")), found.group("block").strip())


def blocks_in_deck_order():
    """The clock of every slide that claims one, in the order they appear."""
    return [noted(slide).time for slide in slides() if noted(slide)]


def slides_by_block():
    """The deck grouped into blocks, keyed by the clock in the speaker notes."""
    grouped = {}
    for slide in slides():
        claim = noted(slide)
        if claim:
            grouped.setdefault(claim.time, []).append(slide)
    return grouped


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------


class TestTheDeckCoversTheWholeSession(unittest.TestCase):
    """The first acceptance criterion, and the one that matters most.

    A block with no slide is not noticed until somebody is standing in front of
    it, because the deck is skimmed and the run of show is read.
    """

    def test_every_block_in_the_run_of_show_has_at_least_one_slide(self):
        covered = slides_by_block()
        missing = [
            f"{block.time} {block.label}"
            for block in run_of_show()
            if block.time not in covered
        ]
        self.assertEqual(missing, [], "these blocks of the session have no slide")

    def test_the_deck_invents_no_block_the_plan_of_record_does_not_have(self):
        """A section for something that was cut is time spent on stage on it."""
        planned = {block.time for block in run_of_show()}
        extra = sorted(set(slides_by_block()) - planned)
        self.assertEqual(extra, [], "these are in the deck and not in the run of show")

    def test_the_slides_are_in_the_order_the_session_runs_them(self):
        """A deck out of order is found by paging through it, which nobody does."""
        order = [block.time for block in run_of_show()]
        seen = blocks_in_deck_order()
        self.assertEqual(seen, sorted(seen, key=order.index))

    def test_a_block_is_one_unbroken_run_of_slides(self):
        """Half a block at the front of the deck and half at the back is a cut
        that takes out the wrong slides, made by somebody in a hurry.

        `groupby` collapses each run of the same clock to one entry, so a block
        that appears in two places appears twice in `runs` and nowhere else.
        The first draft of this compared `dict.fromkeys` against `set`, which
        are equal in length by definition -- an assertion that could not fail.
        """
        runs = [time for time, _slides in itertools.groupby(blocks_in_deck_order())]
        self.assertEqual(
            runs, list(dict.fromkeys(runs)),
            "this block is split across two places in the deck",
        )

    def test_that_contiguity_check_can_actually_fail(self):
        """The guard on the guard, since the first version of it could not."""
        runs = [time for time, _s in itertools.groupby(["a", "b", "a"])]
        self.assertNotEqual(runs, list(dict.fromkeys(runs)))


class TestEverySlideCarriesTheClock(unittest.TestCase):
    """The second acceptance criterion. The timings live in the speaker notes.

    Not on the slide. A clock on the slide is a promise to the room that the
    session is on time, and the first thing that slips is the clock.
    """

    def test_every_slide_has_exactly_one_speaker_note(self):
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertEqual(
                    len(slide.notes), 1,
                    f"slide {slide.number} has {len(slide.notes)} speaker notes, not 1",
                )

    def test_every_note_opens_with_the_clock_the_length_and_the_block(self):
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                opening = slide.note.splitlines()[0] if slide.note else ""
                self.assertIsNotNone(
                    noted(slide),
                    f"slide {slide.number} opens its note with {opening!r}, which is "
                    "not `0:00–0:08 · 8 min · Cold open`",
                )

    def test_the_clock_is_nowhere_the_room_can_see_it(self):
        """The other half of "in the speaker notes", and the half worth saying.

        A clock printed on a slide is a promise to three hundred people that
        the session is where it says it is. The first thing a live demo does is
        break that promise, and then every slide is an accusation.
        """
        for slide in slides():
            for line in slide.content_lines():
                with self.subTest(slide=slide.number, line=line):
                    self.assertIsNone(
                        A_TIME.search(line),
                        f"slide {slide.number} puts the clock on the projector",
                    )

    def test_the_length_on_every_slide_is_the_length_in_the_plan_of_record(self):
        """A note saying 12 minutes for a block the plan gives 6 is a deck that
        was right once."""
        planned = {block.time: block for block in run_of_show()}
        for slide in slides():
            claim = noted(slide)
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertIsNotNone(claim, f"slide {slide.number} has no readable note")
                self.assertIn(
                    claim.time, planned, f"{claim.time} is not a block of this session"
                )
                self.assertEqual(claim, planned[claim.time])

    def test_a_note_says_more_than_the_clock(self):
        """A note with nothing under the header line is a header, not a note,
        and the presenter's screen shows it either way."""
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                under = "\n".join(slide.note.splitlines()[1:]).strip()
                self.assertGreater(
                    len(under), 0, f"slide {slide.number} has a clock and nothing else",
                )


class TestTheSectionBreaksMatchTheActs(unittest.TestCase):
    """The fifth acceptance criterion, which is really about October 5th.

    The dry run cuts against the clock. A cut is cheap when it is "delete from
    this break to the next one" and expensive when it is a judgment call about
    every slide, so every block opens with a break and none has one in the
    middle.
    """

    def test_every_block_opens_with_a_break_slide(self):
        for time, slides_in_block in slides_by_block().items():
            with self.subTest(block=time):
                self.assertTrue(
                    slides_in_block[0].is_a_break,
                    f"{time} opens on an ordinary slide, so a cut has no edge to start at",
                )

    def test_no_block_has_a_break_slide_in_the_middle_of_it(self):
        for time, slides_in_block in slides_by_block().items():
            with self.subTest(block=time):
                inside = [s.number for s in slides_in_block[1:] if s.is_a_break]
                self.assertEqual(inside, [], f"{time} has a second break inside it")

    def test_the_deck_opens_on_the_title_slide(self):
        self.assertIn("title", slides()[0].classes)

    def test_each_act_is_marked_as_one(self):
        """The three acts carry a class of their own, on top of `divider`.

        Eleven identical breaks make every block look the same size to the
        room, and the acts are not the same size as the stretch break. This is
        what lets the theme set them apart.
        """
        acts = [block for block in run_of_show() if block.label.startswith("Act ")]
        self.assertEqual(len(acts), 3, "the run of show no longer has three acts")
        for act in acts:
            opener = slides_by_block()[act.time][0]
            with self.subTest(act=act.label):
                self.assertEqual(opener.heading, act.label)
                self.assertIn("act", opener.classes)

    def test_nothing_but_an_act_is_marked_as_one(self):
        act_times = {b.time for b in run_of_show() if b.label.startswith("Act ")}
        for slide in slides():
            if "act" not in slide.classes:
                continue
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertIn(noted(slide).time, act_times)

    def test_every_break_slide_is_headed_with_the_block_it_opens(self):
        for slide in slides():
            if not slide.is_a_break or slide.number == 1:
                continue
            with self.subTest(slide=slide.number):
                self.assertEqual(slide.heading, noted(slide).label)


class TestTheCutLineIsMarkedOnTheSlides(unittest.TestCase):
    """§7 names three things to drop and the order to drop them in. Knowing
    that at the podium is worth nothing unless the slides say which they are."""

    def test_every_item_on_the_cut_line_is_marked_on_a_slide(self):
        items = cut_line()
        notes = "\n".join(slide.note for slide in slides())
        for rank, what in items:
            mark = CUT_MARK.format(rank=rank, total=len(items))
            with self.subTest(cut=rank, what=what):
                self.assertIn(mark, notes, f"nothing in the deck is marked {mark!r}")

    def test_a_cut_mark_names_one_slide_and_not_several(self):
        """Two slides both claiming to be cut 2 is a presenter deleting one of
        them and believing the cut is made."""
        items = cut_line()
        for rank, what in items:
            mark = CUT_MARK.format(rank=rank, total=len(items))
            marked = [slide.number for slide in slides() if mark in slide.note]
            with self.subTest(cut=rank, what=what):
                self.assertEqual(len(marked), 1, f"{mark} is on slides {marked}")

    def test_every_phrase_the_plan_protects_resolves_to_exactly_one_block(self):
        """The guard on the guard below, and it was needed.

        §7 and §5 name the same blocks differently, so the check that nothing
        protected is marked can only work if every protected phrase is first
        matched to a block. A substring match looked like it worked and
        silently resolved two of the four, which left half the guard dead while
        the test went on passing.
        """
        resolved = never_cut()
        self.assertEqual(len(resolved), 4, "the plan protects a different number of blocks")
        for phrase, blocks in resolved.items():
            with self.subTest(protected=phrase):
                self.assertEqual(
                    [block.label for block in blocks].__len__(), 1,
                    f"{phrase!r} matches {[b.label for b in blocks]} in the run of show",
                )

    def test_nothing_the_plan_says_never_to_cut_is_marked(self):
        """§7 is blunt about four of them. A deck that marked one for cutting
        would be read at the one moment nobody re-reads the plan.

        Only the formal `Cut N of M` marker counts, and that is not a
        loophole. §7 protects the failure beat as a **block** while the timing
        warning above it says, in the same document, to cut **beat 2** inside
        that block if the run is behind at 1:36. Both are true: the block
        survives and one of its three beats goes. A first draft matched the
        bare word "Cut" and read the note carrying that instruction as a
        cut-line mark, which would have made the plan contradict itself.
        """
        protected = {
            block.time: phrase for phrase, blocks in never_cut().items() for block in blocks
        }
        a_cut_mark = re.compile(r"Cut \d+ of \d+")
        for slide in slides():
            if not a_cut_mark.search(slide.note):
                continue
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn(
                    noted(slide).time, protected,
                    f"slide {slide.number} is marked for cutting and the plan of record "
                    f"says never to cut {protected.get(noted(slide).time)!r}",
                )


class TestTheSpeakerNotesSendYouSomewhereReal(unittest.TestCase):
    """Most of the notes carry a fallback: open this file if that will not run.

    They are directions, and directions to a file that is not there are worse
    than no directions, because they are followed - at four minutes past the
    hour, on a laptop with no network. Same rule the fallback card is held to
    one folder over.

    This is also what catches a **half** path. A note that wrapped across two
    lines left `the-claim-we-got-wrong.md` with no folder in front of it, which
    reads as a complete instruction and is not one.
    """

    # A path is anything with a file extension this repo actually commits.
    # The leading dot matters: `.github/ISSUE_TEMPLATE/` is named in a note and
    # a pattern anchored on a word boundary silently drops it.
    A_PATH = re.compile(r"\.?\w[\w./-]*\.(?:md|svg|json|txt|yml|yaml|css|py)\b")

    def named_files(self):
        for slide in slides():
            for found in self.A_PATH.finditer(slide.note):
                yield slide, found.group(0)

    def test_the_notes_name_some_files_at_all(self):
        """If this ever finds nothing, every check below is passing vacuously."""
        self.assertGreater(len(list(self.named_files())), 5)

    def test_every_file_a_note_names_is_committed(self):
        for slide, named in self.named_files():
            with self.subTest(slide=slide.number, file=named):
                self.assertTrue(
                    Path(long_path(REPO / named)).is_file(),
                    f"slide {slide.number} sends a presenter to {named}, which is not here",
                )


class TestTheClaimsWithConsequencesCarryTheirSource(unittest.TestCase):
    """`CLAUDE.md`: *"Numbers with legal consequence -- accuracy tolerances,
    notice periods, fees -- get a source link next to them"*, and *"Never
    invent a TxDOT requirement. Cite the manual section and its URL."*

    The deck publishes on every push to `main`, so a claim about Texas law or
    a TxDOT rule is on the web the moment it is written, whether or not the
    slide around it is finished. Saying the source in the speaker notes is not
    enough: nobody in the room can see the presenter's screen.

    So a slide that states one carries its citation, and the citation is the
    repo's own -- checked here against `CONTEXT.md`, `docs/txdot-research.md`
    and `docs/governance/`, not against this file's memory of them.
    """

    # Each is (a phrase that appears on a slide, something its citation must
    # carry). Kept short on purpose: this is a list of the claims that would
    # cost somebody money or a license if they were wrong, not of every fact.
    CONSEQUENCES = (
        ("no acceptable failure rate", "txdot.gov/manuals/row/ess"),
        ("cannot be invoiced", "txdot.gov/manuals/row/ess"),
        ("PAO 71", "pels.texas.gov"),
        ("responsible charge", "131.2"),
        ("Right of entry", "1071.358"),
    )

    def slide_saying(self, phrase):
        for slide in slides():
            if any(phrase.lower() in line.lower() for line in slide.content_lines()):
                return slide
        return None

    def test_every_claim_with_consequences_carries_its_citation_on_the_slide(self):
        for phrase, citation in self.CONSEQUENCES:
            slide = self.slide_saying(phrase)
            with self.subTest(claim=phrase):
                self.assertIsNotNone(slide, f"no slide says {phrase!r} any more")
                visible = "\n".join(slide.content_lines())
                self.assertIn(
                    citation, visible,
                    f"slide {slide.number} states {phrase!r} with no source the room can see",
                )

    def test_no_slide_cites_the_superseded_manual_host(self):
        """`CLAUDE.md`: never `onlinemanuals.txdot.gov`. It is a scripted demo
        in this very session, which would be an unfortunate place to do it."""
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn("onlinemanuals.txdot.gov", "\n".join(slide.content_lines()))


class TestThePlaceholdersSayTheyArePlaceholders(unittest.TestCase):
    """#12 asks for a frame and says plainly there is no real content yet.

    That is fine on the 13th of September and dangerous on the 7th of October,
    because this deck renders and publishes on every push. A slide with a
    heading and three bullets looks finished from the back of a room. So every
    slide still waiting on its content says so on its face, and names the work
    order that would fill it.
    """

    def test_every_placeholder_either_names_a_work_order_or_says_there_is_none(self):
        """A placeholder with nothing after it is a slide nobody owns.

        Naming the work order is the answer where one exists. Where none does,
        saying so is the answer -- and it is the more useful of the two,
        because it is the sentence that gets an issue written.
        """
        for slide in slides():
            for line in slide.content_lines():
                if PLACEHOLDER not in line:
                    continue
                with self.subTest(slide=slide.number, heading=slide.heading):
                    self.assertTrue(
                        re.search(r"#\d+", line) or NO_WORK_ORDER in line,
                        f"slide {slide.number} says it is unfinished and not who finishes it",
                    )

    def test_a_placeholder_never_both_names_a_work_order_and_denies_one(self):
        """Half an answer reads as a whole one, the same as on the fallback card."""
        for slide in slides():
            for line in slide.content_lines():
                if PLACEHOLDER not in line or NO_WORK_ORDER not in line:
                    continue
                with self.subTest(slide=slide.number, heading=slide.heading):
                    self.assertIsNone(re.search(r"#\d+", line))

    def test_a_break_slide_is_never_a_placeholder(self):
        """A break carries a name and a clock. There is nothing to fill in."""
        for slide in slides():
            if not slide.is_a_break:
                continue
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertNotIn(PLACEHOLDER, slide.body)

    def test_the_slides_page_states_the_size_the_deck_actually_is(self):
        """A number written in prose beside a thing is a number that rots.

        `docs/slides/index.md` is the page a reader lands on, and it is where
        the deck admits what state it is in. Every number on it is checkable,
        so every number is checked -- same reasoning as the gap count on the
        fallback card, which was wrong on its first draft for exactly this
        reason.
        """
        stated = re.search(r"\*\*(\d+) slides\*\*", text_of(SLIDES_PAGE))
        self.assertIsNotNone(stated, "the Slides page no longer says how big the deck is")
        self.assertEqual(int(stated.group(1)), len(slides()))

    def test_the_slides_page_states_how_much_of_it_is_still_a_placeholder(self):
        stated = re.search(
            r"\*\*(\d+) of them are still placeholders\*\*", text_of(SLIDES_PAGE)
        )
        self.assertIsNotNone(stated, "the Slides page no longer says what is unfinished")
        waiting = [slide for slide in slides() if PLACEHOLDER in slide.body]
        self.assertEqual(int(stated.group(1)), len(waiting))

    def test_the_slides_page_states_how_much_of_the_deck_nobody_is_writing(self):
        """The number the skeleton turned up, on the page a reader lands on.

        It was 22 slides across six blocks when #12 landed, and #81 through #86
        took it to nothing the same day. It is still counted rather than
        declared closed, because the next block added to the run of show
        arrives with no work order and this is the sentence that should say so.

        Written to read at any value -- the first draft phrased it as "N of
        those have no work order yet", which is fine at 22 and clumsy at 0, and
        a sentence nobody wants to write is a sentence that gets deleted along
        with its check.
        """
        page = text_of(SLIDES_PAGE)
        stated = re.search(
            r"Slides still waiting on a work order: \*\*(\d+)\*\*, across\s+\*\*(\d+)\*\*",
            page,
        )
        self.assertIsNotNone(stated, "the Slides page no longer says what nobody is writing")
        unowned = [slide for slide in slides() if NO_WORK_ORDER in slide.body]
        self.assertEqual(int(stated.group(1)), len(unowned))
        self.assertEqual(
            int(stated.group(2)), len({noted(slide).time for slide in unowned})
        )


class TestNothingIsTooSmallOrTooBigForTheRoom(unittest.TestCase):
    """The fourth acceptance criterion, in its two halves.

    Too small is a number in a stylesheet. Too big is a slide that asks the
    canvas for more room than it has, and the back row gets neither.
    """

    def setUp(self):
        self.canvas = Canvas(THEME)

    def test_the_canvas_is_the_size_the_projector_runs_at(self):
        rules = style_rules(THEME)["section"]
        self.assertEqual(rules["width"], "1920px")
        self.assertEqual(rules["height"], "1080px")

    def test_nothing_in_the_theme_is_smaller_than_28pt(self):
        """28pt exactly is what the page number is, and that is the floor, not
        a rounding error. `section::after` sits at it deliberately."""
        self.assertGreaterEqual(self.canvas.smallest_type(), 28)

    def test_no_relative_size_drops_a_run_of_text_below_28pt(self):
        """`font-size: 0.85em` on a code span is how 28pt quietly becomes 24."""
        for selector, declarations in style_rules(THEME).items():
            size = declarations.get("font-size", "")
            found = re.fullmatch(r"([\d.]+)em", size.strip())
            if not found:
                continue
            with self.subTest(selector=selector):
                self.assertGreaterEqual(
                    float(found.group(1)) * self.canvas.body_pt, 28,
                    f"{selector} sets {size}, which is under 28pt of the "
                    f"{self.canvas.body_pt}pt body",
                )

    def test_no_slide_asks_for_more_room_than_the_canvas_has(self):
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                asked = self.canvas.height_of_lines(slide.content_lines(), slide.classes)
                self.assertLessEqual(
                    asked, self.canvas.height,
                    f"slide {slide.number} ({slide.heading!r}) asks for about "
                    f"{asked:.0f}px of a {self.canvas.height:.0f}px canvas",
                )

    def test_the_budget_would_notice_a_slide_that_overflowed(self):
        """A budget that can never fail is not a check, it is a comment.

        Twenty-four bullets on one slide is well past anything a projector
        renders, and if this passes then the arithmetic has broken and every
        other slide is being waved through.
        """
        too_much = ["# Heading"] + ["- a line of text"] * 24
        self.assertGreater(self.canvas.height_of_lines(too_much), self.canvas.height)


class TestTheDeckIsWiredIntoTheBuild(unittest.TestCase):
    """The third acceptance criterion. CI renders the HTML and the PDF, so what
    can be checked from here is that it is pointed at the right files.

    This is the cheap half of it and it is worth having: a deck renamed without
    the workflow being renamed builds a stale deck, successfully, and says so
    in green.
    """

    def setUp(self):
        self.workflow = text_of(SLIDES_WORKFLOW)

    def test_the_workflow_renders_the_deck_this_file_checks(self):
        named = re.search(r"DECK:\s*(\S+)", self.workflow)
        self.assertIsNotNone(named, "slides.yml no longer says which deck it renders")
        self.assertEqual(REPO / named.group(1), DECK)

    def test_the_workflow_renders_both_a_web_page_and_a_pdf(self):
        self.assertIn("deck.html", self.workflow)
        self.assertIn(".pdf", self.workflow)

    def test_the_theme_the_deck_asks_for_is_in_the_folder_the_workflow_hands_marp(self):
        """`theme: tsps` in the deck has to be a theme Marp was given. It is
        not an error if it is not -- Marp falls back to its default and renders
        a deck in the wrong type, at the wrong size, without complaining."""
        front, _body = front_matter_and_body(text_of(DECK))
        asked = re.search(r"^theme:\s*(\S+)", front, flags=re.M)
        self.assertIsNotNone(asked, "the deck names no theme")
        folder = re.search(r"--theme-set (\S+)", self.workflow)
        self.assertIsNotNone(folder, "slides.yml hands Marp no theme folder")
        declared = re.search(r"/\*\s*@theme\s+(\S+)\s*\*/", text_of(THEME))
        self.assertIsNotNone(declared, "tsps.css does not declare a theme name")
        self.assertEqual(asked.group(1), declared.group(1))
        self.assertEqual((REPO / folder.group(1)).resolve(), THEME.parent.resolve())

    def test_the_deck_is_kept_out_of_the_site_builder(self):
        """MkDocs and Marp both build markdown, and both would build this.

        `mkdocs.yml` excludes it. Without that the site publishes the deck's
        source as an ordinary page -- every slide run together, the directives
        showing -- at a URL nobody would think to check.
        """
        mkdocs = text_of(REPO / "mkdocs.yml")
        self.assertIn("slides/beyond-the-prompt.md", mkdocs)
        self.assertIn("slides/themes/", mkdocs)


if __name__ == "__main__":
    unittest.main()
