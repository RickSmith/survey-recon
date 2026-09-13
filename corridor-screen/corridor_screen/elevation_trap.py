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
surveyor calls the unit they work in: the one EPSG numbers 9003, the one the
TxDOT survey specification is written in, and the one this repo already has a
trap page about on
`the geometry service <../../docs/data-sources/arcgis-geometry-service.md>`_,
where the same code silently returned a different corridor.

----

What the ticket expected, and what is actually there
====================================================

Issue #26 describes the service ignoring "the coordinate-system parameter" and
reading longitude and latitude as Web Mercator meters. Checked on 2026-09-13,
**that is not what this endpoint does now.** ``wkid`` is honored: ask in Web
Mercator meters with ``wkid=3857`` and the correct elevation comes back.

The hazard did not go away. It moved from the coordinate system to the units,
which is the same failure wearing different clothes -- a parameter accepted,
quietly not applied, and answered around. ``docs/data-sources/not-used.md``
already records this endpoint changing shape between the original research and
a re-test, and says so rather than pretending the note was always right.

----

Why a wrong answer is worse than an error, argued rather than asserted
======================================================================

This endpoint fails in two ways, and the comparison is the beat.

**The loud one.** Ask about a point in the Gulf of Mexico, or with a coordinate
system that does not match the numbers, and it returns HTTP 200 carrying plain
text. That breaks ``json.loads`` in the caller. It is ugly, and it is **safe**:
somebody finds out immediately.

**The quiet one.** Ask in ``US_Feet`` and everything works. It parses. It is the
right kind of value. It is in a believable range for the county. Nothing at the
point of the call can catch it, because nothing about it is malformed -- and the
number goes into a deliverable somebody seals.

``survives_a_careful_caller`` is that argument in code, and there is a test on
each half.
"""

import argparse
import json
import sys
from pathlib import Path

from .cache import long_path

CAPTURE_DIR = Path(__file__).resolve().parent.parent / "captures" / "silent-nodata"

# When every response below was captured. Services change; this endpoint already
# changed shape once between this repo's research and its re-test.
CHECKED_ON = "2026-09-13"

# The beat as `--show` renders it, committed beside the captures so a podium
# where Python will not start still has it. Pinned to the code by a test.
BEAT_NAME = "the-beat.txt"

# The conversion that proves the two numbers are one elevation rather than two
# readings. Stated here so the test can check the ratio rather than a constant.
FEET_PER_METER = 3.280839895013123

# The one sentence. Issue #26: "makes clear why a wrong answer is more dangerous
# than an error message." One sentence, and a test on the full stops.
VERDICT = (
    "The broken answer is caught by anything that reads it, and the plausible "
    "one is caught by nothing until somebody has sealed it."
)

# The corridor point every capture asks about: SH16 at Bandera Road, which is
# the corridor the rest of this tool screens.
POINT = "SH16 at Bandera Road, San Antonio (-98.644635, 29.528488)"

# The committed evidence. Every entry carries the exact request it came from,
# because a capture nobody can repeat is not evidence. All five answered 200.
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
}


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


def survives_a_careful_caller(name):
    """Whether a caller doing everything right would still be fooled.

    "Everything right" means: check the status, parse the body, confirm the
    field is there, confirm it is a number, confirm it is in a believable range
    for this county. That is more checking than most code does.

    The point of this function is that it returns **True** for the wrong
    answer. Nothing available at the point of the call separates 264.221008301
    from a real elevation, because it *is* a real elevation -- of the same
    ground, in a unit nobody asked for.
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
        feet = float(answer["value"])
    except (TypeError, ValueError):
        return False
    # Bexar County runs roughly 400 to 2,000 feet. A number outside that is
    # worth doubting; a number inside it tells you nothing at all.
    return 0 < feet < 5000


def beat():
    """The failure beat, built entirely from committed captures.

    Plain ASCII: an em dash is a `UnicodeEncodeError` and a traceback on a
    Windows console that has not been told otherwise, which is every borrowed
    podium laptop. Beat one found that the hard way.
    """
    feet, us_feet = raw_value("feet"), raw_value("us_feet")
    ratio = value_of("feet") / value_of("us_feet")

    return "\n".join([
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
        "  The same service can also fail loudly. A point in the Gulf of Mexico:",
        f"    HTTP {CAPTURES['no_data']['http_status']}, and a body that is not JSON at all.",
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show", action="store_true",
                       help="print the failure beat (the default)")
    group.add_argument("--write-fallback", action="store_true",
                       help=f"re-render the committed {BEAT_NAME} beside the captures")
    args = parser.parse_args(argv)

    if args.write_fallback:
        path = CAPTURE_DIR / BEAT_NAME
        with open(long_path(path), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(beat() + "\n")
        print(f"  written  {path}")
        return 0

    print(beat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
