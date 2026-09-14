"""Failure beat two: the answer that is wrong rather than missing.

Written under [issue #26](https://github.com/RickSmith/survey-recon/issues/26).

**Ask the same question twice, one word apart.** The elevation of SH16 at
Bandera Road, from the USGS Elevation Point Query Service::

    ...&units=Feet      ->  866.8668528742528     a JSON number
    ...&units=US_Feet   ->  "264.221008301"       a JSON string

866.8668528742528 divided by 264.221008301 is 3.28084, which is feet per meter.
It is the same elevation. The second answer is in meters.

There is no error. HTTP 200, valid JSON, and a number that is a perfectly
ordinary elevation for San Antonio -- three and a quarter times too small, with
**nothing anywhere in the response saying which unit it is**.

And ``US_Feet`` is not a typo a programmer would make. It is what a Texas
surveyor calls the unit they work in: the one EPSG numbers 9003, the one
TxDOT's Survey Manual requires in deliverables (Ch. 3, Control Points --
https://www.txdot.gov/manuals/row/ess/index.html), and the one this repo
already has a
trap page about on
`the geometry service <../../docs/data-sources/arcgis-geometry-service.md>`_,
where the same code silently returned a different corridor.

----

Two names for one idea, and only one of them works
==================================================

Issue #26 describes the service ignoring "the coordinate-system parameter."
That is still true, and an earlier draft of this module said it was not --
because it tested the wrong parameter. The correction is worth keeping, because
what is actually there is **worse** than the ticket describes.

There are two spellings of the coordinate system, and the service treats them
differently without saying which one it used. Checked 2026-09-13:

- ``sr=4326``, ``sr=3857``, and no ``sr`` at all -> ``866.8668528742528``,
  identical every time. ``sr`` is the parameter this repo's original research
  named, and it is **silently ignored**, exactly as recorded.
- ``wkid=3857`` with Web Mercator meters -> the correct elevation. ``wkid`` is
  **honored**.

So a caller who writes ``sr`` gets no coordinate system at all and no warning,
and a caller who writes ``wkid`` gets what they asked for. One letter of
difference between a parameter that works and one that is discarded in silence.

``docs/data-sources/not-used.md`` recorded the ``sr`` half before this beat was
written. What is added here is that ``wkid`` works -- which is what makes the
``sr`` silence a trap rather than simply an unsupported option -- and the third
parameter below, which is the one that hands you a number.

----

Why a wrong answer is worse than an error, argued rather than asserted
======================================================================

This endpoint fails in two ways, and the comparison is the beat.

**The loud one.** Ask about a point in the Gulf of Mexico, or with a coordinate
system that does not match the numbers, and it returns HTTP 200 carrying plain
text. That breaks ``json.loads`` in the caller. It is ugly, and it is **safe**:
somebody finds out immediately.

**The quiet one.** Ask in ``US_Feet`` and everything works. It parses. It is the
right kind of value. It is a real elevation of real ground. Nothing about it is
malformed, so no amount of general care at the point of the call finds it.

**One thing does find it, and it is the interesting thing.** 264.22 feet is
below the floor of Bexar County, which runs roughly 400 to 2,000. A caller who
range-checks against *this county* catches it immediately. A caller who
range-checks against the Earth does not.

``survives_a_generic_check`` and ``survives_a_local_check`` are that pair in
code, with a test on each. The second one needed somebody who knew the ground to
write it, which is the argument this whole repo is making, reached from the
wrong end.
"""

import argparse
import json
import sys

from . import beats
from .cache import long_path

CAPTURE_DIR = beats.capture_dir("silent-nodata")

# When every response below was captured. Services change; this endpoint already
# changed shape once between this repo's research and its re-test.
CHECKED_ON = "2026-09-13"

# The conversion that proves the two numbers are one elevation rather than two
# readings. Stated here so the test can check the ratio rather than a constant.
FEET_PER_METER = 3.280839895013123

# The range a careful caller would sanity-check an elevation against in this
# county. Both the right answer and the wrong one fall inside it, which is the
# point of `survives_a_careful_caller`: the check a reasonable person would
# write does not separate them.
BEXAR_FLOOR_FT, BEXAR_CEILING_FT = 400, 2000

# The one sentence. Issue #26: "makes clear why a wrong answer is more dangerous
# than an error message." One sentence, and a test on the full stops.
VERDICT = (
    "The broken answer is caught by anything that reads it, and the plausible "
    "one is caught only by somebody who already knew what this ground is."
)

# The corridor point every capture asks about: SH16 at Bandera Road, which is
# the corridor the rest of this tool screens.
POINT = "SH16 at Bandera Road, San Antonio (-98.644635, 29.528488)"

# The committed evidence. Every entry carries the exact request it came from,
# because a capture nobody can repeat is not evidence. Every one answered 200,
# which `test_elevation_trap` checks rather than this comment asserting it.
#
# No count is written here on purpose. This comment said "all five" while the
# dictionary held twelve, and it was one of four places stating a number that
# had stopped being true -- the failure this whole beat is about, in the module
# that teaches it.
BASE = "https://epqs.nationalmap.gov/v1/json"
CAPTURES = {
    "feet": {
        "file": "units-feet.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=Feet",
        "http_status": 200,
        "note": "The right answer, in the unit that was asked for.",
    },
    "us_feet": {
        "file": "units-us-feet.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=US_Feet",
        "http_status": 200,
        "note": "The unit a Texas surveyor works in. Answered in meters, as a "
                "string, with no error and nothing saying so.",
    },
    "meters": {
        "file": "units-meters.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=Meters",
        "http_status": 200,
        "note": "Kept to prove the US_Feet answer is the metric one unchanged, "
                "rather than a conversion that went wrong somewhere.",
    },
    "no_data": {
        "file": "no-data-gulf.txt",
        "url": f"{BASE}?x=-92.0&y=25.0&wkid=4326&units=Feet",
        "http_status": 200,
        "note": "A point in the Gulf of Mexico. HTTP 200 carrying plain text.",
    },
    "wkid_mismatch": {
        "file": "wkid-mismatch.txt",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=3857&units=Feet",
        "http_status": 200,
        "note": "Degrees declared as Web Mercator meters. Also a 200 carrying "
                "plain text -- so `wkid` is applied, unlike `units`.",
    },
    "wkid_mercator": {
        "file": "wkid-3857-mercator.json",
        "url": f"{BASE}?x=-10981070.536&y=3443084.221&wkid=3857&units=Feet",
        "http_status": 200,
        "note": "The same point in Web Mercator meters, correctly declared. "
                "Answers 866.8668528742528 -- so `wkid` really is honored, "
                "which is the evidence for saying the hazard moved to `units` "
                "rather than saying the ticket was wrong.",
    },
    # The rest of the `units` vocabulary, captured because the table on
    # `not-used.md` states what each one does and a stated number with no
    # response behind it is the thing this whole beat is about.
    "lowercase_feet": {
        "file": "units-lowercase-feet.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=feet",
        "http_status": 200,
        "note": "Answers in feet. This is what rules out case sensitivity as "
                "the explanation, so `match the capitalization` is the wrong "
                "lesson to take away.",
    },
    "ft": {
        "file": "units-ft.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=ft",
        "http_status": 200,
        "note": "The obvious abbreviation. Meters.",
    },
    "furlongs": {
        "file": "units-furlongs.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326&units=Furlongs",
        "http_status": 200,
        "note": "A unit nobody would mean seriously, kept because it shows the "
                "rule: anything off the short accepted list becomes meters.",
    },
    "omitted": {
        "file": "units-omitted.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&wkid=4326",
        "http_status": 200,
        "note": "No `units` at all. Meters, with no default stated anywhere.",
    },
    # The parameter the original research named, and the reason an earlier draft
    # of this module wrongly declared the ticket out of date.
    "sr_4326": {
        "file": "sr-4326-ignored.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&units=Feet&sr=4326",
        "http_status": 200,
        "note": "`sr` is silently ignored: identical to sr=3857 and to sending "
                "no coordinate system at all. This is the ticket's premise, "
                "still live.",
    },
    "sr_3857": {
        "file": "sr-3857-ignored.json",
        "url": f"{BASE}?x=-98.644635&y=29.528488&units=Feet&sr=3857",
        "http_status": 200,
        "note": "The control for the row above. Same answer, so the value of "
                "`sr` changes nothing at all.",
    },
}

# Every capture above was re-requested on 2026-09-13 and the status read off the
# wire; all ten answered 200. `http_status` is stated rather than parsed because
# a saved body carries no headers -- and the whole point of the set is that not
# one of these is an error by the only test most callers apply.
ALL_ANSWERED = 200

# Every value on the `not-used.md` table that should come back in meters. Named
# here so a test can check the claim against the captures rather than against a
# sentence somebody typed.
ANSWERED_IN_METERS = ("meters", "us_feet", "ft", "furlongs", "omitted")
ANSWERED_IN_FEET = ("feet", "lowercase_feet")


def capture_text(name):
    """One committed response, as text. Never a network call."""
    path = CAPTURE_DIR / CAPTURES[name]["file"]
    with open(long_path(path), encoding="utf-8", errors="replace") as handle:
        return handle.read()


def raw_value(name):
    """The ``value`` field exactly as the service sent it, type and all.

    Not coerced. The type is part of the evidence: a float for ``Feet``, a
    string for everything else, from the same endpoint on the same second.
    """
    return json.loads(capture_text(name))["value"]


def value_of(name):
    """That value as a number, for comparing the two answers.

    Coercion happens **here and nowhere else**, deliberately. A caller that did
    this quietly at the point of the call is exactly the caller this beat is
    about -- it would turn `"264.221008301"` into a number and never notice the
    string it arrived as.
    """
    return float(raw_value(name))


def survives_a_generic_check(name):
    """Whether a well-written caller that does not know this county is fooled.

    "Well-written" here means everything you would do without local knowledge:
    check the status, parse the body, confirm the field is there, confirm it is
    a number, confirm it is a sane elevation for somewhere on Earth. That is
    more checking than most code does.

    It returns **True** for the wrong answer, and that is the point. Nothing in
    that list separates 264.221008301 from a real elevation, because it *is* a
    real elevation -- of the same ground, in a unit nobody asked for.
    """
    if CAPTURES[name]["http_status"] != 200:
        return False
    try:
        answer = json.loads(capture_text(name))
    except ValueError:
        return False
    if "value" not in answer:
        return False
    try:
        feet = value_of(name)
    except (TypeError, ValueError):
        return False
    # Dead Sea to Denali, in feet, with room either side. This is the bound a
    # careful programmer with no particular knowledge of Texas would reach for.
    return -1500 < feet < 21000


def survives_a_local_check(name):
    """The same, plus one thing only somebody who knows the ground would add.

    **This is the correction that matters.** An earlier version of this module
    had a single function with the range written as ``0 < feet < 5000``, above a
    comment saying Bexar County runs 400 to 2,000 feet. The two did not agree,
    and the wider bound was doing the work -- it was calibrated, without anyone
    deciding to, so that the answer came out the way the argument wanted.

    Checked honestly, **264.22 is below the county floor**, so a caller who
    range-checks against Bexar County catches this. The claim "nothing at the
    point of the call can catch it" was false.

    What is true is narrower and more useful: the check that catches it is the
    one that needed a person who knows their own ground to write it. Generic
    care is not enough. That is the whole argument of this repo, arrived at from
    the wrong direction.
    """
    if not survives_a_generic_check(name):
        return False
    return BEXAR_FLOOR_FT < value_of(name) < BEXAR_CEILING_FT


def beat():
    """The failure beat, built entirely from committed captures.

    Plain ASCII, and `beats.render` refuses anything else rather than trusting
    this sentence to be read. Beat one found the em dash the hard way; issue
    #67 is about making that structural instead of remembered.
    """
    feet, us_feet = raw_value("feet"), raw_value("us_feet")
    ratio = value_of("feet") / value_of("us_feet")

    return beats.render([
        "  Failure beat 2 - the answer that is wrong rather than missing",
        "",
        f"  One question, asked twice, one word apart. {POINT}:",
        "",
        f"    units=Feet      value = {feet!r}",
        f"                    a JSON number, in feet. Correct.",
        "",
        f"    units=US_Feet   value = {us_feet!r}",
        "                    a JSON string, in meters. No error was raised.",
        "",
        f"  {value_of('feet'):.4f} / {value_of('us_feet'):.4f} = {ratio:.5f},"
        f" which is feet per meter.",
        "  It is the same elevation. Nothing in the response says which unit.",
        "",
        "  US_Feet is not a typo. It is what a Texas surveyor calls the unit",
        "  they work in, and it is what EPSG numbers 9003.",
        "",
        "  The same endpoint has two names for the coordinate system, and only",
        "  one of them does anything:",
        "    sr=4326, sr=3857, and no sr at all  ->  the same answer, every time",
        "    wkid=3857 with Web Mercator meters  ->  correct",
        "",
        "  The same service can also fail loudly. A point in the Gulf of Mexico:",
        f"    HTTP {CAPTURES['no_data']['http_status']}, and a body that is not JSON at all.",
        "",
        "  What separates the two, in code:",
        f"    a check against the whole Earth   -> the wrong number survives",
        f"    a check against Bexar County      -> it is caught, because"
        f" {value_of('us_feet'):.0f} ft is",
        f"                                         below the county floor of"
        f" {BEXAR_FLOOR_FT} ft",
        "",
        f"  {VERDICT}",
        "",
        f"  Checked {CHECKED_ON}. Every line reads from captures in",
        "  captures/silent-nodata/, so it needs no network to run again.",
    ])


def main(argv=None):
    """``python -m corridor_screen.elevation_trap --show``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen elevation-trap",
        description="Failure beat two: a plausible wrong answer, beside the right one.",
    )
    beats.beat_arguments(parser)
    args = parser.parse_args(argv)

    if args.write_fallback:
        print(f"  written  {beats.write_fallback(CAPTURE_DIR, beat())}")
        return 0

    print(beat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
