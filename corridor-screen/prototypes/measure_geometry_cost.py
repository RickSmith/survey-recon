"""THROWAWAY. What it would cost to put the map's geometry in `screening.json`.

Issue #193 asked where the job page reads its data from. One live answer was
that `screening.json` should grow to carry everything the page needs, so the
page reads one file instead of two. That is a claim about a size, and nobody
had the size.

Run it with::

    python corridor-screen/prototypes/measure_geometry_cost.py

It writes nothing and changes nothing.

----

What it measures
================

The geometry the map is drawn from, which `screening.json` does **not** carry
today: every tract's rings, the centerline, and the corridor ribbon. The run
names a cache key for the ribbon rather than holding the ring, and a parcel
record has no geometry field at all.

It reports the geometry twice -- compact, and indented the way `output.py`
actually writes `screening.json` -- because the file on disk is the one that
gets committed, not the smallest one that could be.

----

What it found, on 2026-09-22
============================

===============================================  ===========
                                                 Bytes
===============================================  ===========
``screening.json`` today                             473,838
The geometry, written the way the file is             ~1.0 MB
``screening.json`` if it carried the geometry         ~1.4 MB
===============================================  ===========

Roughly triple. And it would not save the cache: `CLAUDE.md` requires every
API response to be cached, so the 4.3 MB folder stays whatever this decides.
Carrying the geometry means committing a second copy of data already on disk.

That is why #193 settled on the page reading **`screening.json` plus the
cache**, which is the shape `drawings.load()` already uses.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from corridor_screen import drawings  # noqa: E402

PROJECT = HERE.parent.parent / "project-sh16"


def geometry(document, capture):
    """Everything the map is drawn from that the run does not write down."""
    return {
        "parcel_rings": {parcel["id"]: rings for parcel, rings
                         in drawings.parcel_rings(document, capture) if rings},
        "centerline": drawings.centerline(document, capture),
        "ribbon": drawings.ribbon(document, capture),
    }


def main():
    document, capture = drawings.load(PROJECT)
    shapes = geometry(document, capture)

    today = (PROJECT / "screening.json").stat().st_size
    # `output.py` writes the run with indent=1, so that is the honest figure.
    grown = len(json.dumps(shapes, indent=1).encode("utf-8"))
    compact = len(json.dumps(shapes, separators=(",", ":")).encode("utf-8"))
    cache = sum(f.stat().st_size for f in (PROJECT / "cache").rglob("*") if f.is_file())

    print(f"tracts carrying rings                       {len(shapes['parcel_rings']):>12,}")
    print(f"screening.json today                        {today:>12,} bytes")
    print(f"the geometry, compact                       {compact:>12,} bytes")
    print(f"the geometry, indented as the file is       {grown:>12,} bytes")
    print(f"screening.json if it carried the geometry   {today + grown:>12,} bytes "
          f"({(today + grown) / today:.1f}x)")
    print(f"the cache, which stays either way           {cache:>12,} bytes")


if __name__ == "__main__":
    main()
