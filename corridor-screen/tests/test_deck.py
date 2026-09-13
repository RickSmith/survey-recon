"""The slide deck, held against the run of show it is supposed to cover.

Issue #12 asks for a skeleton rather than a talk: **a slide for every block of
the two hours, with the clock in the speaker notes, section breaks on the act
boundaries, and type a back row can read.** The content lands later, under #31
and #32. What this file checks is the frame.

A deck is the one document in this repo nobody reads carefully. It gets skimmed
in a hotel room the night before, and a block that quietly has no slide is
discovered on stage. So the deck is checked the same way the fallback card is,
one folder over, and for the same reason:

* every block of the run of show in `docs/plan-of-record.md` §5 has at least one
  slide, and the deck invents no block the plan does not have
* the slides arrive in the order the session runs them
* every slide carries a speaker note, and that note opens with the block's
  clock and its length **taken from the plan** rather than typed again here
* every block opens with a break slide, so a cut is made by deleting whole
  slides between two breaks rather than by picking through a deck
* every item on the cut line in §7 is marked on the slide it would take out
* nothing in the theme drops below 28pt, and no slide carries more than the
  1920 x 1080 canvas holds

**Why read the plan instead of restating it.** `docs/plan-of-record.md` is the
spec. A deck that kept its own private copy of the run of show would go on
passing its own tests for weeks after the run of show changed, which is the
exact failure this file exists to prevent.

**On the last check.** Marp and a browser are the authority on whether a slide
fits, and neither is available to a test that has to run with no Docker and no
Node. So the fitting check here is a **budget**, not a renderer: it reads the
type sizes out of `tsps.css` and adds up what a slide asks the canvas for.

That budget is calibrated against the real thing rather than argued from the
box model. All 45 slides were rendered with the pinned Marp container on
13 September 2026 and the page was asked how tall each one had come out. The
first draft of the arithmetic here ran up to 7% **under** those numbers, which
would have made it an estimate wearing a guard's uniform. With `ELEMENT_GAP`
it is above the measured height on all 45, by between 2% and 29%.

So it errs one way: it may refuse a dense slide that would have fitted, and it
will not wave through one that would not. Re-measure it if the theme changes
shape. The authority is still `.github/workflows/slides.yml`, which renders the
deck for real on every push.
"""

import math
import re
import unittest
from pathlib import Path

from corridor_screen.cache import long_path

REPO = Path(__file__).resolve().parents[2]
DECK = REPO / "docs" / "slides" / "beyond-the-prompt.md"
SLIDES_PAGE = REPO / "docs" / "slides" / "index.md"
THEME = REPO / "docs" / "slides" / "themes" / "tsps.css"
PLAN = REPO / "docs" / "plan-of-record.md"
SLIDES_WORKFLOW = REPO / ".github" / "workflows" / "slides.yml"

# `0:57–1:18`, with the en dash the plan of record actually uses. Same pattern
# as `test_fallbacks.A_TIME`, and deliberately not imported from there: these
# two files check different documents and should be able to disagree about what
# a time looks like without one of them being edited to suit the other.
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

# The class on a break slide. The opening slide is a break too -- it is what is
# on screen for the whole cold open -- and it carries `title` instead.
BREAK_CLASSES = ("divider", "title")

# 96 CSS pixels to the inch, 72 points to the inch. The canvas in `tsps.css` is
# given in pixels and the type in points, so one of them has to be converted.
PX_PER_PT = 96 / 72

# Roughly how wide an average character is, as a fraction of the type size, in
# the Helvetica the theme asks for. Used to work out where a long line wraps.
AVERAGE_CHARACTER = 0.50

# What a browser puts between two blocks that the stylesheet does not account
# for. Not derived -- **measured**, on 13 September 2026, by rendering all 45
# slides with the pinned Marp container and asking the page how tall each one
# had come out.
#
# Without it the estimate below ran up to 7% under the real height, which made
# it an estimate pretending to be a guard. With it the estimate is above the
# real height on every one of the 45, by between 2% and 29%. That is the
# direction to be wrong in: it refuses a dense slide that might have fitted,
# and it never waves through one that did not.
#
# Re-measure if the theme changes shape. The method is in the pull request for
# #12, and the real render is `.github/workflows/slides.yml`.
ELEMENT_GAP = 16


def text_of(path):
    """Read a committed file, through the door that survives a long path.

    A surveyor's checkout sits under something like "OneDrive - Some Long Firm
    Name\\Documents\\Projects", and this repo's own worktrees already push a
    path past the 260 characters Windows opens without being asked in the
    extended form. `cache.long_path` is how every other read here gets in.
    """
    with open(long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


# ---------------------------------------------------------------------------
# Reading the plan of record
# ---------------------------------------------------------------------------


def markdown_section(markdown, heading):
    """Everything under one heading, up to the next heading of any depth.

    Matched on how the heading starts rather than on the whole of it, because
    the plan of record writes its running time into one of them -- "## 5. Run
    of show (2:00)" -- and a heading that gains or loses a parenthesis should
    not fail a check about slides.
    """
    lines = markdown.splitlines()
    for start, line in enumerate(lines):
        if line.strip().startswith(heading):
            break
    else:
        raise AssertionError(f"{heading!r} is not in that file")
    for end in range(start + 1, len(lines)):
        if lines[end].startswith("#"):
            return "\n".join(lines[start + 1:end])
    return "\n".join(lines[start + 1:])


def table_rows(markdown):
    """Every table row in a markdown file, as a list of stripped cells."""
    rows = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


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
    """The blocks of the session as (time, minutes, label), in order.

    Read rather than restated, for the reason in this file's docstring.
    """
    section = markdown_section(text_of(PLAN), "## 5. Run of show")
    return [
        (row[0], int(row[1]), block_label(row[2]))
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
        return self.directives.get("_class") in BREAK_CLASSES

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
    """The (time, minutes, label) a slide's speaker note claims, or None."""
    if not slide.note:
        return None
    found = A_NOTE.match(slide.note.splitlines()[0].strip())
    if not found:
        return None
    return found.group("time"), int(found.group("min")), found.group("block").strip()


def slides_by_block():
    """The deck grouped into blocks, keyed by the clock in the speaker notes."""
    grouped = {}
    for slide in slides():
        claim = noted(slide)
        if claim:
            grouped.setdefault(claim[0], []).append(slide)
    return grouped


# ---------------------------------------------------------------------------
# Reading the theme
# ---------------------------------------------------------------------------


def style_rules():
    """`tsps.css` as {selector: {property: value}}.

    Small enough to read with a regular expression, and a real CSS parser is a
    dependency this repo will not take on for one file.

    Two things get thrown away first. Comments, because the theme explains
    itself at length and half of what it says is a number. And statements that
    end in a semicolon outside any block -- `@import 'default';` is the only
    one today -- because otherwise the import sticks to the front of the first
    selector and `section` is suddenly not in the file.
    """
    css = re.sub(r"/\*.*?\*/", "", text_of(THEME), flags=re.S)
    rules = {}
    for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selector = selector.rpartition(";")[2]
        declarations = {}
        for declaration in block.split(";"):
            name, _, value = declaration.partition(":")
            if value:
                declarations[name.strip()] = value.strip()
        for one in selector.split(","):
            rules.setdefault(one.strip(), {}).update(declarations)
    return rules


def points(value):
    """`34pt` as the number 34, or None for anything not written in points."""
    found = re.fullmatch(r"([\d.]+)pt", value.strip())
    return float(found.group(1)) if found else None


def pixels(value):
    found = re.fullmatch(r"([\d.]+)px", value.strip())
    return float(found.group(1)) if found else None


def margin_bottom(declarations):
    """The bottom margin of a rule, in em, however it was written.

    `margin: 0 0 0.55em 0` and `margin-bottom: 0.5em` mean the same thing and
    the theme uses both.
    """
    if "margin-bottom" in declarations:
        found = re.fullmatch(r"([\d.]+)em", declarations["margin-bottom"].strip())
        return float(found.group(1)) if found else 0.0
    shorthand = declarations.get("margin", "").split()
    if len(shorthand) == 4:
        found = re.fullmatch(r"([\d.]+)em", shorthand[2])
        return float(found.group(1)) if found else 0.0
    return 0.0


class Canvas:
    """The type sizes and the space to put them in, read out of the theme.

    Everything here comes from `tsps.css`. Nothing is typed in twice, so
    changing a size in the theme changes what this will accept.

    **Classes are read too.** `section.title h1` is 84pt where `section h1` is
    66, and a budget blind to that would wave through the two slides carrying
    the biggest type in the deck -- which are the only two where the type alone
    can fill the canvas.
    """

    def __init__(self):
        self.rules = style_rules()
        body = self.rules["section"]
        self.width = pixels(body["width"]) - 2 * self._padding(body, side=1)
        self.height = pixels(body["height"]) - 2 * self._padding(body, side=0)
        self.body_pt = points(body["font-size"])
        self.body_leading = float(body["line-height"])

    @staticmethod
    def _padding(declarations, side):
        """`padding: 90px 120px` -- side 0 is top and bottom, 1 is left and right."""
        return pixels(declarations["padding"].split()[side])

    def style_for(self, tag, klass=None):
        """(size in points, line height, bottom margin in em) for one tag.

        A rule set on the class wins over the same rule set on every slide,
        which is what the browser does. Anything neither of them sets falls
        back to the body.
        """
        declarations = dict(self.rules.get(f"section {tag}", {}))
        if klass:
            declarations.update(self.rules.get(f"section.{klass} {tag}", {}))
        size = points(declarations.get("font-size", "")) or self.body_pt
        leading = float(declarations.get("line-height", self.body_leading))
        # A paragraph gets no rule of its own in the theme, so it is given a
        # bullet's bottom margin. That is a guess, and it is the pessimistic
        # one: guessing zero would let a slide of paragraphs through that a
        # real render would overflow.
        margin = margin_bottom(declarations or self.rules.get("section li", {}))
        return size, leading, margin

    def smallest_type(self):
        """The smallest size anywhere in the theme, including the page number."""
        sizes = [self.body_pt]
        for declarations in self.rules.values():
            size = points(declarations.get("font-size", ""))
            if size:
                sizes.append(size)
        return min(sizes)

    def height_of(self, tag, text, klass=None):
        """How tall one line of markdown renders, wrapping included."""
        size, leading, margin = self.style_for(tag, klass)
        per_character = size * PX_PER_PT * AVERAGE_CHARACTER
        wrapped = max(1, math.ceil(len(text) * per_character / self.width))
        return wrapped * size * PX_PER_PT * leading + margin * size * PX_PER_PT

    @staticmethod
    def tag_of(line):
        """Which element one line of markdown renders as."""
        if line.startswith("###"):
            return "h3", line.lstrip("#").strip()
        if line.startswith("##"):
            return "h2", line.lstrip("#").strip()
        if line.startswith("#"):
            return "h1", line.lstrip("#").strip()
        if line.startswith("> "):
            return "blockquote", line[2:]
        if line.startswith(("- ", "* ", "1. ")):
            return "li", line
        return "p", line

    def height_of_slide(self, slide):
        """About how tall a slide renders, in pixels of the 1080 canvas.

        `ELEMENT_GAP` is added once per *block*, not once per line: a run of
        bullets is one list to a browser however many bullets are in it, which
        is how the gap was measured.
        """
        klass = slide.directives.get("_class")
        total, blocks, previous = 0.0, 0, None
        for line in slide.content_lines():
            tag, text = self.tag_of(line.strip())
            if tag != "li" or previous != "li":
                blocks += 1
            total += self.height_of(tag, text, klass)
            previous = tag
        return total + blocks * ELEMENT_GAP


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
            f"{time} {label}" for time, _min, label in run_of_show() if time not in covered
        ]
        self.assertEqual(missing, [], "these blocks of the session have no slide")

    def test_the_deck_invents_no_block_the_plan_of_record_does_not_have(self):
        """A section for something that was cut is time spent on stage on it."""
        planned = {time for time, _min, _label in run_of_show()}
        extra = sorted(set(slides_by_block()) - planned)
        self.assertEqual(extra, [], "these are in the deck and not in the run of show")

    def test_the_slides_are_in_the_order_the_session_runs_them(self):
        """A deck out of order is found by paging through it, which nobody does."""
        order = [time for time, _min, _label in run_of_show()]
        seen = [noted(slide)[0] for slide in slides() if noted(slide)]
        self.assertEqual(seen, sorted(seen, key=order.index))

    def test_a_block_is_one_unbroken_run_of_slides(self):
        """Half a block at the front of the deck and half at the back is a cut
        that takes out the wrong slides, made by somebody in a hurry."""
        seen = [noted(slide)[0] for slide in slides() if noted(slide)]
        self.assertEqual(len(list(dict.fromkeys(seen))), len(set(seen)))


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
                self.assertIsNotNone(
                    noted(slide),
                    f"slide {slide.number} opens its note with "
                    f"{slide.note.splitlines()[0] if slide.note else '' !r}, which is not "
                    "`0:00–0:08 · 8 min · Cold open`",
                )

    def test_the_length_on_every_slide_is_the_length_in_the_plan_of_record(self):
        """A note saying 12 minutes for a block the plan gives 6 is a deck that
        was right once."""
        planned = {time: (minutes, label) for time, minutes, label in run_of_show()}
        for slide in slides():
            claim = noted(slide)
            with self.subTest(slide=slide.number, heading=slide.heading):
                self.assertIsNotNone(claim, f"slide {slide.number} has no readable note")
                time, minutes, label = claim
                self.assertIn(time, planned, f"{time} is not a block of this session")
                self.assertEqual((minutes, label), planned[time])

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
        first = slides()[0]
        self.assertEqual(first.directives.get("_class"), "title")

    def test_each_act_has_a_break_slide_that_names_it(self):
        """The three acts by name, because they are how the session is described
        to the room and how it is talked about afterwards."""
        acts = [label for _time, _min, label in run_of_show() if label.startswith("Act ")]
        self.assertEqual(len(acts), 3, "the run of show no longer has three acts")
        headings = [slide.heading for slide in slides() if slide.is_a_break]
        for act in acts:
            with self.subTest(act=act):
                self.assertIn(act, headings)

    def test_every_break_slide_is_headed_with_the_block_it_opens(self):
        for slide in slides():
            if not slide.is_a_break or slide.number == 1:
                continue
            _time, _min, label = noted(slide)
            with self.subTest(slide=slide.number):
                self.assertEqual(slide.heading, label)


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

    def test_nothing_the_plan_says_never_to_cut_is_marked(self):
        """§7 is blunt about four of them. A deck that marked one for cutting
        would be read at the one moment nobody re-reads the plan."""
        never = markdown_section(text_of(PLAN), "### Cut line, in order")
        stated = re.search(r"\*\*Never cut:\*\*(.+)", never)
        self.assertIsNotNone(stated, "the plan of record no longer says what never to cut")
        protected = [part.strip(" .*") for part in stated.group(1).split(",")]
        self.assertTrue(protected)
        marked = {
            noted(slide)[2] for slide in slides() if "Cut " in slide.note and noted(slide)
        }
        for label in marked:
            for phrase in protected:
                with self.subTest(marked=label, protected=phrase):
                    # The plan writes "the grilling" and the deck heads that
                    # block "Act I — The grilling", so the leading article has
                    # to come off before the two can be compared.
                    without_article = phrase.lower().removeprefix("the ").strip()
                    self.assertNotIn(without_article, label.lower())


class TestNothingIsTooSmallOrTooBigForTheRoom(unittest.TestCase):
    """The fourth acceptance criterion, in its two halves.

    Too small is a number in a stylesheet. Too big is a slide that asks the
    canvas for more room than it has, and the back row gets neither.
    """

    def setUp(self):
        self.canvas = Canvas()

    def test_the_canvas_is_the_size_the_projector_runs_at(self):
        rules = style_rules()["section"]
        self.assertEqual(pixels(rules["width"]), 1920)
        self.assertEqual(pixels(rules["height"]), 1080)

    def test_nothing_in_the_theme_is_smaller_than_28pt(self):
        self.assertGreaterEqual(self.canvas.smallest_type(), 28)

    def test_no_relative_size_drops_a_run_of_text_below_28pt(self):
        """`font-size: 0.85em` on a code span is how 28pt quietly becomes 24."""
        for selector, declarations in style_rules().items():
            size = declarations.get("font-size", "")
            found = re.fullmatch(r"([\d.]+)em", size.strip())
            if not found:
                continue
            with self.subTest(selector=selector):
                self.assertGreaterEqual(
                    float(found.group(1)) * self.canvas.body_pt, 28,
                    f"{selector} sets {size}, which is under 28pt of the {self.canvas.body_pt}pt body",
                )

    def test_no_slide_asks_for_more_room_than_the_canvas_has(self):
        for slide in slides():
            with self.subTest(slide=slide.number, heading=slide.heading):
                asked = self.canvas.height_of_slide(slide)
                self.assertLessEqual(
                    asked, self.canvas.height,
                    f"slide {slide.number} ({slide.heading!r}) asks for about "
                    f"{asked:.0f}px of a {self.canvas.height:.0f}px canvas",
                )

    def test_the_budget_would_notice_a_slide_that_overflowed(self):
        """A budget that can never fail is not a check, it is a comment.

        Twenty-four bullets on one slide is well past anything a projector
        renders, and if this passes then the arithmetic above has broken and
        every other slide is being waved through.
        """
        too_much = Slide(0, "# Heading\n\n" + "\n".join(["- a line of text"] * 24))
        self.assertGreater(self.canvas.height_of_slide(too_much), self.canvas.height)


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


class TestThePlaceholdersSayTheyArePlaceholders(unittest.TestCase):
    """#12 asks for a frame and says plainly there is no real content yet.

    That is fine on the 13th of September and dangerous on the 7th of October,
    because this deck renders and publishes on every push to `main`. A slide
    with a heading and three bullets looks finished from the back of a room. So
    every slide still waiting on its content says so on its face, and names the
    work order that would fill it.
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
        the deck admits what state it is in. Both numbers on it are checkable,
        so both are checked -- same reasoning as the gap count on the fallback
        card, which was wrong on its first draft for exactly this reason.
        """
        page = text_of(SLIDES_PAGE)
        stated = re.search(r"\*\*(\d+) slides\*\*", page)
        self.assertIsNotNone(stated, "the Slides page no longer says how big the deck is")
        self.assertEqual(int(stated.group(1)), len(slides()))

    def test_the_slides_page_states_how_much_of_it_is_still_a_placeholder(self):
        page = text_of(SLIDES_PAGE)
        stated = re.search(r"\*\*(\d+) of them are still placeholders\*\*", page)
        self.assertIsNotNone(stated, "the Slides page no longer says what is unfinished")
        waiting = [slide for slide in slides() if PLACEHOLDER in slide.body]
        self.assertEqual(int(stated.group(1)), len(waiting))

    def test_the_slides_page_states_how_many_slides_nobody_is_writing(self):
        """The number this whole exercise turned up, on the page a reader lands
        on. It is the one number here that should make somebody uncomfortable,
        which is the argument for checking it rather than trusting it."""
        page = text_of(SLIDES_PAGE)
        stated = re.search(r"\*\*(\d+) of those have no work order yet\*\*", page)
        self.assertIsNotNone(stated, "the Slides page no longer says what nobody is writing")
        unowned = [slide for slide in slides() if NO_WORK_ORDER in slide.body]
        self.assertEqual(int(stated.group(1)), len(unowned))


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
