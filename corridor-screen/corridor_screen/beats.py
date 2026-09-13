"""What the failure beats have in common, and the one rule worth enforcing.

Issue #67. `manual_links` and `elevation_trap` grew the same shape. This is the
part of that shape worth having in one place -- and, more to the point, the
rule it carries.

----

The rule
========

**A beat prints plain ASCII.** An em dash is a ``UnicodeEncodeError`` and a
traceback on a Windows console that has not been told otherwise, which is every
borrowed podium laptop. Beat one shipped with one and was caught by review on
`PR #65 <https://github.com/RickSmith/survey-recon/pull/65>`_ -- not by anything
running. Beat two avoided it because whoever wrote it had just read about it.

That is a lesson being remembered, and the person who writes the next beat in
six weeks gets no such warning. So `render` refuses a non-ASCII character
outright, and it refuses at the moment somebody runs the beat, on their own
machine, naming the character and the line. Not in CI, and not at 1:36 in front
of three hundred people.

----

`render` has a third caller, and it is not a beat
=================================================

`crew_day.summary` -- the console rendering printed at 1:18 -- goes through
`render` too. It has no captures, no `CHECKED_ON` and no ``beat()``, and it
should not be given any of them to look like a beat: it renders an estimate.
What it shares is the console it prints to.

**That module's other output is the opposite case**, which is worth saying
here because it is the thing somebody will get backwards. `crew_day` also
writes the Markdown build-up, as UTF-8, full of multiplication signs and em
dashes, correctly -- it is read in an editor or on the site. Only the printed
one is held to ASCII.

----

The shape a beat module has
===========================

`tests/test_beats.py` finds beat modules rather than listing them, and checks
each against this. A module is a beat when it exports a callable ``beat``, and
a beat is expected to export three more things:

``beat()``
    Returns the rendered beat, built through `render` and from committed
    captures only -- it is checked with the network taken away at the socket.
``CAPTURE_DIR``
    Where its committed evidence lives. Built with `capture_dir`.
``CAPTURES``
    Its committed evidence. A tuple of records or a dict of them, whichever
    suits the beat; each record carries at least ``file`` and the ``url`` it
    came from, because **a capture nobody can repeat is not evidence**.
``CHECKED_ON``
    The date that evidence was checked, as ``YYYY-MM-DD``. Per beat, not
    shared: it dates *that* beat's captures, and two beats checked on the same
    day is a coincidence rather than a fact about beats.

Written down because the checks read it. A third beat that exports ``beat`` and
nothing else should be told which piece is missing, not die on an
``AttributeError`` that reads like a broken test.

----

What is deliberately **not** here
=================================

**The argument parsers.** They are close but not the same: `manual_links` has a
``--check`` that walks the repo, and `elevation_trap` has nothing like it. What
is shared is the two options every beat has, so `beat_arguments` adds those and
hands back the group for a beat to add its own to. A helper that owned the
whole parser would have to grow a hook for `--check`, which is more machinery
than two modules are worth.

**`capture_text`.** The issue lists it as byte-identical between the two. It is
not, and **it was not at `747a7db` either** -- the commit the issue measured
on. Read both there and they are different functions: `elevation_trap` reads
JSON as UTF-8; `manual_links` reads bytes and decodes them as the page declares
itself, because the legacy manual says ``charset=ISO-8859-1`` in its own head
and reading it as UTF-8 corrupts every byte above 127.

They share a name and a one-line summary, which is what makes a table of
identical things easy to get wrong. Two different jobs wearing one name, and
merging them would mean one function with a flag -- the shape this repo keeps
arguing against.

**`CHECKED_ON`.** Also listed, also left alone, for a reason worth stating:
both beats say ``2026-09-13`` because both were checked that day, not because
beats share a date. Sharing it would turn a coincidence into a fact and make a
stale beat quietly inherit a fresh beat's date.

**Anything for a third beat.** The issue is explicit that one may never exist,
and that beat three's evidence is a different kind of thing -- issues, a
comment, a commit -- rather than captured HTTP responses. Every function here
has two callers today. None is built for a caller that has been promised.
"""

import unicodedata
from pathlib import Path

from .cache import long_path

# The beat as `--show` renders it, committed beside the captures so a podium
# where Python will not start still has it. A test pins it to what `beat()`
# produces, for every beat, found rather than listed.
BEAT_NAME = "the-beat.txt"


def capture_dir(leaf):
    """The committed evidence folder for one beat.

    `Path(__file__)` is this module, which sits beside every beat module, so
    the expression is the same one each of them used to write out by hand.
    """
    return Path(__file__).resolve().parent.parent / "captures" / leaf


def render(lines):
    """The lines of a beat as one string, refusing anything a podium cannot print.

    **This is the whole reason this module exists.** The check is here rather
    than in a test because a test runs where somebody remembers to run it, and
    this runs every time anybody prints the beat -- including the presenter,
    the morning of, on the machine that will be plugged into the projector.

    The message names the character, its Unicode name and the line it is on. A
    beat is thirty lines long, and "there is an em dash in it somewhere" is a
    worse thing to read at a podium than the line number.
    """
    for number, line in enumerate(lines, start=1):
        for character in line:
            if ord(character) < 128:
                continue
            name = unicodedata.name(character, "an unnamed character")
            raise ValueError(
                f"line {number} of this beat contains {character!r} ({name}), "
                f"which a Windows console that has not been told to speak "
                f"UTF-8 cannot print. Every borrowed podium laptop is one of "
                f"those. Use plain ASCII: a hyphen for a dash, straight quotes."
                f"\n  line {number}: {line}"
            )
    return "\n".join(lines)


def write_fallback(folder, text):
    """Write the rendered beat beside its captures, and say where it went.

    UTF-8 and ``\\n`` line endings, so the committed file is byte-for-byte the
    same whoever regenerates it and on whichever platform. Opened through
    `cache.long_path`, like every other file this package touches: a firm's
    checkout under "OneDrive - Some Long Firm Name" runs past the 260
    characters Windows opens without being asked in the extended form.
    """
    path = folder / BEAT_NAME
    with open(long_path(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return path


def beat_arguments(parser):
    """Add the two options every beat has, and hand back the group.

    Returned rather than swallowed so a beat can put its own option in the same
    mutually exclusive group -- `manual_links` adds ``--check`` to it. A helper
    that kept the group to itself would force that beat to build its own parser
    and copy these two back out.
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show", action="store_true",
                       help="print the failure beat (the default)")
    group.add_argument("--write-fallback", action="store_true",
                       help=f"re-render the committed {BEAT_NAME} beside the captures")
    return group
