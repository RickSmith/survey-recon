"""THROWAWAY. Does the map still say anything on a black-and-white printer?

Issue #195 asked what a reader on paper loses. A principal is at least as
likely to print the job page as to click it, and an office printer is as
likely to be monochrome as not. On a monochrome printer a color is only its
lightness, so two colors of the same lightness become the same gray.

Run it with::

    python corridor-screen/prototypes/audit_print_contrast.py

It writes nothing and it changes nothing.

----

The rule it checks
==================

**Two things a reader has to tell apart must not differ only by fill color.**

That rule came out of #195. It is written here rather than only on the ticket
because a rule nobody can run is a rule that stops being true quietly.

Note what the rule is not. It does not say a fill may never be used -- a solid
dark triangle is perfectly legible in gray, and four marker kinds drawn as an
x, a triangle, a square and a cross are told apart by their shape whatever the
ink. The rule is about **pairs**: the flagged tract against the ordinary one,
and the inside of the corridor against the outside. Those are the two places
on this map where a reader's whole question turns on which of two colors a
patch is.

----

What it found, on 2026-09-22
============================

Both pairs pass, and both pass **by their outline rather than their fill**:

=================================  ==========  ===========
Pair                               By fill     By outline
=================================  ==========  ===========
Flagged tract vs ordinary tract    1.13:1      3.41:1
Inside the corridor vs outside     1.02:1      3.71:1
=================================  ==========  ===========

Each figure compares like with like -- the two fills against each other, then
the two outlines against each other -- because that is the comparison a reader
makes. Measuring an outline against the paper instead gives a friendlier
number and answers a question nobody asked.

So the fills are decoration on paper and the strokes do the work. Nothing
needed changing. But it holds by luck rather than by intent -- nobody chose
those strokes for a monochrome printer -- and the rule is what keeps somebody
later from drawing a flag as a fill alone and never finding out.

One thing that is faint and meant to be: the 524 ordinary tracts sit at
1.10:1 by fill and 1.47:1 by outline. They are nearly invisible in gray, and
they are nearly invisible on screen too. That is texture, not meaning, and it
is not a print problem.

----

About the numbers
=================

Contrast ratio is the WCAG measure: the two relative luminances, lighter over
darker, each shifted by 0.05. 1.0 means identical, 21.0 is black on white.
Below roughly 1.5 a reader cannot see an edge at all. It is used here only as
an honest way to say "these two go the same gray," not as an accessibility
claim about text.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from corridor_screen import drawings  # noqa: E402

# Below this, two colors are the same gray to a reader.
VISIBLE = 1.5

# The pairs a reader's question actually turns on. Each is the thing, what it
# has to be told apart from, and the two colors each is drawn with.
PAIRS = (
    ("a flagged tract vs an ordinary one",
     (drawings.AMBER_FILL, drawings.AMBER),
     (drawings.PARCEL_FILL, drawings.PARCEL_LINE)),
    ("inside the corridor vs outside it",
     (drawings.TEAL_FILL, drawings.TEAL),
     (drawings.PARCEL_FILL, drawings.PARCEL_LINE)),
)

# Told apart by their shape, so no color comparison applies. Named so the
# reader of this audit knows they were considered rather than forgotten.
BY_SHAPE = ("the four crew-safety and control markers -- an x, a triangle, "
            "a square and a cross")

# Faint on purpose, on screen as much as on paper.
TEXTURE = ("the 524 ordinary tracts", drawings.PARCEL_FILL, drawings.PARCEL_LINE)


def luminance(color):
    color = color.lstrip("#")
    channels = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    adjusted = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                for c in channels]
    return 0.2126 * adjusted[0] + 0.7152 * adjusted[1] + 0.0722 * adjusted[2]


def contrast(one, two):
    a, b = luminance(one), luminance(two)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def main():
    broken = []
    for words, (fill, stroke), (other_fill, other_stroke) in PAIRS:
        by_fill = contrast(fill, other_fill)
        by_outline = contrast(stroke, other_stroke)
        if by_outline >= VISIBLE:
            verdict = "told apart by its outline"
        elif by_fill >= VISIBLE:
            verdict = "TOLD APART BY FILL ALONE -- breaks the rule"
            broken.append(words)
        else:
            verdict = "THE SAME GRAY -- cannot be told apart at all"
            broken.append(words)
        print(f"  {words:<36} fill {by_fill:>5.2f}:1   "
              f"outline {by_outline:>5.2f}:1   {verdict}")

    words, fill, stroke = TEXTURE
    print(f"\n  {words}: fill {contrast(fill, drawings.PAPER):.2f}:1, "
          f"outline {contrast(stroke, drawings.PAPER):.2f}:1 against paper -- "
          f"faint in gray, and faint on screen too. Texture, not meaning.")
    print(f"  Not compared by color: {BY_SHAPE}.")

    print()
    if broken:
        print(f"the rule is broken by: {'; '.join(broken)}")
        return 1
    print("both pairs are told apart by something other than their fill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
