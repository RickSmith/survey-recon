"""Reading `docs/slides/beyond-the-prompt.md` as slides rather than as markdown.

Marp turns one markdown file into a deck. Everything a test wants to ask about
that deck -- which slide is this, what does the room see on it, which block of
the session does its speaker note claim -- means splitting the file on Marp's
rules first, and those rules are fiddly enough to be worth one implementation:
front matter is fenced with the same three dashes that separate slides, a fenced
code block may contain a line of three dashes that separates nothing, and a
speaker note and a Marp directive are both HTML comments.

Three test files ask:

* `test_deck.py` -- the frame. Every block covered, in order, the clock in every
  note and on no slide, the cut line marked, nothing oversized
* `test_money_slide.py` -- the content of one block, against the crew-day
  build-up its figures come out of
* `test_datum_gap.py` -- the content of one slide, against the research note and
  the SH16 run behind it

It lives here for `tests/markdown_docs.py`'s reason, which is this repo's
standing one:

> Two copies of any of them would drift the first time somebody fixed one of
> them.

**What is deliberately not here.** Reading the run of show, the cut line and the
never-cut list out of `docs/plan-of-record.md` stays in `test_deck.py`. That is
reading the spec, not reading the deck, and this module should not change when
the session does.
"""

import re
from collections import namedtuple
from pathlib import Path

from tests.markdown_docs import text_of, unemphasized

REPO = Path(__file__).resolve().parents[2]
DECK = REPO / "docs" / "slides" / "beyond-the-prompt.md"

# Marp starts a new slide on a line that is exactly three dashes. The front
# matter is fenced with the same three, which is why it is stripped first.
A_SLIDE_BREAK = "---"

# The class that makes a slide a section break. The opening slide is a break
# too -- it is what is on screen for the whole cold open -- and it carries
# `title` instead.
BREAK_CLASSES = ("divider", "title")

# The first line of a speaker note, which is the line every grouping here keys
# on:
#
#     0:30–0:46 · 16 min · Act I — The grilling
#
# A note is told apart from a Marp directive by that leading digit. Directives
# are `_class: title` and the like, so they start with a letter or an
# underscore and can never match this.
A_NOTE = re.compile(
    r"^(?P<time>\d:\d\d\u2013\d:\d\d) \u00b7 (?P<min>\d+) min \u00b7 (?P<block>.+)$"
)

# One block of the session. The three travel together wherever a block is read
# -- out of the run of show, or off the front of a speaker note -- so they
# travel as one thing, and `test_deck.py` compares the two readings row for row.
Block = namedtuple("Block", "time minutes label")


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


def block_headed(phrase):
    """Every slide of the block whose break slide is headed with a phrase.

    A block is found through the deck rather than through the run of show,
    deliberately. `test_deck.py` already holds every block of the deck to the
    plan of record -- same clock, same order, same length -- so the block this
    finds is the plan's block, and reading the plan again here would be a
    second copy of that relationship rather than a check of anything.
    """
    for slide in slides():
        if slide.is_a_break and phrase.lower() in slide.heading.lower():
            claim = noted(slide)
            if claim:
                return slides_by_block()[claim.time]
    raise AssertionError(f"no break slide in the deck is headed {phrase!r}")


def slide_headed(phrase, exactly=False):
    """The one slide whose heading carries a phrase.

    More than one is as much a finding as none: a check meant for one slide
    that silently reads whichever came first is a check nobody can trust.

    **`exactly` matches the whole heading instead of a phrase inside it**, and
    the close is why it exists. That block's section break is headed
    *Accountability · Monday morning · the live issue* and one of its slides is
    headed *Monday morning* -- one heading contains the other, so the substring
    reading finds two slides and, rightly, refuses to guess. Any block whose
    break names its own slides will hit the same wall.
    """
    found = [
        slide for slide in slides()
        if (slide.heading == phrase if exactly
            else phrase.lower() in slide.heading.lower())
    ]
    if len(found) != 1:
        raise AssertionError(
            f"{len(found)} slides are headed {phrase!r} in the deck, wanted one"
        )
    return found[0]


def with_markup(slides_):
    """Everything the room can see across a run of slides, as one string.

    The markdown is left on, for the checks that want a rate handle: `A4` is
    told apart from the letter A followed by a four by those backticks.
    """
    return "\n".join(line for slide in slides_ for line in slide.content_lines())


def visible(slides_):
    """The same, with the bold and the backticks taken off.

    A figure and the noun it counts have to sit beside each other to be checked
    at all, and `**38 crew-days**` re-emphasized as `**38** crew-days` is the
    same slide to the room and a different string to a test. `markdown_docs.flat`
    does this job for line wrapping on the pages in `docs/`; this is the same
    class of false failure, wearing emphasis instead of a line break.

    The replacements themselves are `markdown_docs.unemphasized`, because the
    pages in `docs/` need the same three and a fourth copy was being written in
    `test_act_three.py`. **One slide per line is kept**, which is why this is
    not `markdown_docs.plain`: a phrase that ran across two bullets would start
    matching, and the checks here tell one bullet from two on purpose.
    """
    return unemphasized(with_markup(slides_))


# A repo path as it appears on a slide or in a speaker note. Anchored to the
# three folders a slide ever points at, because a bare word with a slash in it
# is not a path and `MARK NOT FOUND`/`A4` should not be read as one.
#
# It lives here because the checks that use it are per-block and there are now
# three of them. #82's review found three slides shipping `captures/...`, which
# is not where that folder is: a **half path reads as a whole one**, and the
# room photographs the slide rather than the presenter's screen.
A_PATH = re.compile(r"(?<![\w/.-])((?:corridor-screen|docs|project-sh16)/[\w./-]+)")


def slides_in_block(label, breaks=False):
    """The slides of one block, found by what their speaker notes claim.

    `breaks` keeps the section break at the head of the block. It is off by
    default because a break carries a name and a clock and nothing a
    content check wants to read.

    Written once for Act I, copied for Act II, and extracted on Act II's own
    review before a third copy existed.
    """
    return [slide for slide in slides()
            if noted(slide) and noted(slide).label == label
            and (breaks or not slide.is_a_break)]


def on_screen(heading, exactly=False):
    """What the room sees on one slide, markup and all, note taken out.

    The note is deliberately excluded. A note is allowed to say "do not put
    524 on this slide"; a check reading the whole body would find the 524 in
    that warning and fail the slide for obeying it.

    `exactly` is `slide_headed`'s, and means the same thing here.
    """
    return with_markup([slide_headed(heading, exactly=exactly)])


def seen(heading):
    """The same, with the bold and the backticks taken off. `visible` of one.

    `on_screen` above is for a check that wants a rate handle or a parameter
    name -- `A4` and `units=Feet` are told apart from ordinary prose by their
    backticks. Most checks want the opposite, because a phrase re-emphasized is
    the same slide to the room and a different string to a test.

    Written out as `visible([slide_headed(heading)])` four times in
    `test_beat_slides.py` before that file's own review found it, which is the
    second copy this module exists to stop.
    """
    return visible([slide_headed(heading)])


def note(heading):
    """That slide's speaker note as one line.

    Notes are hard-wrapped prose, so a phrase worth checking usually has a
    line break in the middle of it. `markdown_docs.flat` is the same job on a
    page instead of on a note.
    """
    return " ".join(slide_headed(heading).note.split())
