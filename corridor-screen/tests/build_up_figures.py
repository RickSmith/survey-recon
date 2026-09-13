"""The figures the crew-day build-up publishes, for the documents that quote it.

`project-sh16/crew-day.md` is generated. It says so on its last line: *nothing
here was typed by hand*. Two documents in this repo quote it to people who
cannot see it —

* `docs/for-principals/index.md`, the page a firm owner is handed on paper
* `docs/slides/beyond-the-prompt.md`, the money slide, on a projector in front
  of three hundred surveyors who can check it from their seats

— and both are typed by hand. So both are checked against this, and this is one
module rather than two copies of the same regular expressions, for
`tests/markdown_docs.py`'s reason:

> Two copies of any of them would drift the first time somebody fixed one of
> them.

**Why the sentences and not the JSON.** `screening.json` holds the counts, but
the build-up is where the counts became hours and the hours became days, and it
is the days a quoting document says out loud. Reading the run instead would mean
redoing the build-up's arithmetic here, in a second place, which is the thing
this file exists to stop.

**Every pattern here matches a sentence the build-up writes exactly once.**
Finding one twice is as much a finding as not finding it — a second copy is what
drifts — so `one` treats both as failures.
"""

import re
from collections import namedtuple
from pathlib import Path

from tests.markdown_docs import text_of

REPO = Path(__file__).resolve().parents[2]
BUILD_UP = REPO / "project-sh16" / "crew-day.md"

# How the build-up writes the two day counts it refuses to add together.
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

# **The build-up's unit is the hour.** These are the words that mean a document
# quoting it has left that unit and started pricing software instead, which
# both [#30] and [#32] forbid in the same sentence: billable-hour terms, never
# subscription pricing.
#
# They live beside the figures rather than in either document's own test file
# because the rule is about the unit the build-up estimates in, and there are
# two documents obeying it.
PRICED_BY_THE_SEAT = (
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
)

# Any number the build-up prints, however it is punctuated.
A_NUMBER = re.compile(r"\d[\d.]*\d|\d")

Figures = namedtuple(
    "Figures",
    "field_days office_days crew_size field_hours office_hours untotaled_lines",
)


def one(pattern, markdown, what):
    """The single match for a pattern, or a failure that names what was wanted."""
    found = pattern.findall(markdown)
    if len(found) != 1:
        raise AssertionError(
            f"{what} appears {len(found)} times in {BUILD_UP.name}, wanted once"
        )
    return found[0]


def figures():
    """What the build-up totals, as the strings it writes them in.

    Strings rather than numbers, deliberately. What a quoting document has to
    get right is the figure as it is printed -- `299.29`, not 299.29 -- because
    a page that rounded it to 299 would be quoting a number the build-up does
    not have, and comparing floats would wave that through.
    """
    markdown = text_of(BUILD_UP)
    field_days, office_days = one(DAY_COUNTS, markdown, "the two day counts")
    return Figures(
        field_days=field_days,
        office_days=office_days,
        crew_size=one(CREW_SIZE, markdown, "the crew size"),
        field_hours=one(FIELD_HOURS, markdown, "the field hours total"),
        office_hours=one(OFFICE_HOURS, markdown, "the office hours total"),
        untotaled_lines=one(UNTOTALED, markdown, "the lines with no total"),
    )


def rate_handles():
    """`A1` through `A12`, as the build-up's rate table stamps them.

    A handle is an invitation to argue with one rate by name, which only works
    if the handle is one the build-up has. Read from the table rather than
    listed here, so a rate that is added or renamed does not need finding in
    three files.
    """
    return set(HANDLE.findall(text_of(BUILD_UP)))


def numbers_it_publishes():
    """Every number printed anywhere in the build-up.

    The blunt half of the check. A document quoting the build-up may print a
    number this set does not have only by inventing it, which is the one thing
    the issue behind the build-up says these documents must not do.

    It cannot catch a figure quoted in the wrong place -- office hours offered
    as field hours are both in here -- so the named figures above are checked
    one by one as well. This is the net under those.
    """
    return set(A_NUMBER.findall(text_of(BUILD_UP)))
