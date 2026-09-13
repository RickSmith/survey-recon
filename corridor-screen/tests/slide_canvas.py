"""How much room a slide asks the projector for, read out of the theme.

This lives apart from `test_deck.py` because it changes for a different reason.
That file changes when the session changes — a block added, a slide moved, a
cut line rewritten. This one changes when `tsps.css` changes shape, which is a
question about a browser's box model and has nothing to do with the run of
show.

**It is a budget, not a renderer.** Marp and a browser are the authority on
whether a slide fits, and neither is available to a test that has to run with
no Docker and no Node — the prerequisites for this repo are git, a GitHub
account and the Claude desktop app, and a test that needed more than that would
be a test nobody runs.

**It is calibrated against the real thing rather than argued from the box
model.** All 45 slides were rendered with the pinned Marp container on
13 September 2026 and the page was asked how tall each one had come out. The
first draft of this arithmetic ran up to 7% *under* those numbers, which would
have made it an estimate wearing a guard's uniform. With `ELEMENT_GAP` it sits
above the measured height on all 45, by between 2% and 29%.

So it errs one way: it may refuse a dense slide that would have fitted, and it
will not wave through one that would not. For a ballroom that is the right
direction to be wrong in.

**Re-measure it if the theme changes shape.** The method is in the pull request
for #12, and the authority is still `.github/workflows/slides.yml`, which
renders the deck for real on every push.
"""

import math
import re

from tests.markdown_docs import text_of

# 96 CSS pixels to the inch, 72 points to the inch. The canvas in `tsps.css` is
# given in pixels and the type in points, so one of them has to be converted.
PX_PER_PT = 96 / 72

# Roughly how wide an average character is, as a fraction of the type size, in
# the Helvetica the theme asks for. Used to work out where a long line wraps.
AVERAGE_CHARACTER = 0.50

# What a browser puts between two blocks that the stylesheet does not account
# for. Not derived -- measured, as the docstring above describes.
ELEMENT_GAP = 16


def style_rules(theme):
    """`tsps.css` as {selector: {property: value}}.

    Small enough to read with a regular expression, and a real CSS parser is a
    dependency this repo will not take on for one file.

    Two things get thrown away first. Comments, because the theme explains
    itself at length and half of what it says is a number. And statements that
    end in a semicolon outside any block -- `@import 'default';` is the only
    one today -- because otherwise the import sticks to the front of the first
    selector and `section` is suddenly not in the file.
    """
    css = re.sub(r"/\*.*?\*/", "", text_of(theme), flags=re.S)
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


def tag_of(line):
    """Which element one line of markdown renders as, and its visible text."""
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


class Canvas:
    """The type sizes and the space to put them in, read out of the theme.

    Everything here comes from `tsps.css`. Nothing is typed in twice, so
    changing a size in the theme changes what this will accept.

    **Classes are read too.** `section.title h1` is 84pt where `section h1` is
    66, and a budget blind to that would wave through the two slides carrying
    the biggest type in the deck -- which are the only two where the type alone
    can fill the canvas.
    """

    def __init__(self, theme):
        self.rules = style_rules(theme)
        body = self.rules["section"]
        self.width = pixels(body["width"]) - 2 * self._padding(body, side=1)
        self.height = pixels(body["height"]) - 2 * self._padding(body, side=0)
        self.body_pt = points(body["font-size"])
        self.body_leading = float(body["line-height"])

    @staticmethod
    def _padding(declarations, side):
        """`padding: 90px 120px` -- side 0 is top and bottom, 1 is left and right."""
        return pixels(declarations["padding"].split()[side])

    def style_for(self, tag, classes=()):
        """(size in points, line height, bottom margin in em) for one tag.

        A rule set on a class wins over the same rule set on every slide, which
        is what the browser does. A slide may carry more than one class --
        `divider act` is two -- and they are applied in the order written.
        Anything no rule sets falls back to the body.
        """
        declarations = dict(self.rules.get(f"section {tag}", {}))
        for klass in classes:
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

    def height_of(self, tag, text, classes=()):
        """How tall one line of markdown renders, wrapping included."""
        size, leading, margin = self.style_for(tag, classes)
        per_character = size * PX_PER_PT * AVERAGE_CHARACTER
        wrapped = max(1, math.ceil(len(text) * per_character / self.width))
        return wrapped * size * PX_PER_PT * leading + margin * size * PX_PER_PT

    def height_of_lines(self, lines, classes=()):
        """About how tall a run of markdown renders, in pixels of the canvas.

        `ELEMENT_GAP` is added once per *block*, not once per line: a run of
        bullets is one list to a browser however many bullets are in it, which
        is how the gap was measured.
        """
        total, blocks, previous = 0.0, 0, None
        for line in lines:
            tag, text = tag_of(line.strip())
            if tag != "li" or previous != "li":
                blocks += 1
            total += self.height_of(tag, text, classes)
            previous = tag
        return total + blocks * ELEMENT_GAP
