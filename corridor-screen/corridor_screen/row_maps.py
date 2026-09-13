"""The right-of-way map sheets over the corridor, and how far back they go.

A ROW map sheet is the historical record drawing of a right of way. Old sheets
mean hand retracement off a scan that may barely be legible, and that is time
on the estimate. So the two numbers this file exists to produce are **how many
sheets** and **how old the oldest one is**.

Three rules shape this file.

**A sheet is a line, not a point.** Each record is the stretch of route
centerline that one drawing covers, so the corridor test is whether any part of
the line reaches the ribbon -- the same test ``checks.check_shapes_near_corridor``
applies to a parcel, and not the strict point test ``control.select`` uses for
a survey mark.

**A crossing route's sheet is still a record you need.** SH16 from Loop 410 to
Gibeaut Rd meets two major interchanges, and the right of way at those
interchanges is defined on Loop 410 and Loop 1604 sheets, not on SH16 ones. So
every sheet that reaches the corridor is reported, whatever route it belongs
to, and ``by_route`` is what keeps that readable rather than confusing.

**A run that never asked is not a run that found no sheets.** A corridor with
no ROW record at all would be a remarkable finding. Reported as a count of zero
it reads like one, so ``block`` writes a ``not-screened`` block instead.

----

The date trap, which does not return a wrong answer -- it stops the run
========================================================================

Every other service this tool calls publishes its dates as strings. NGS sends
``19950413`` and ``control._recovered_on`` tidies it up. **This service
publishes real date fields**, and ArcGIS sends a date field as milliseconds
since 1 January 1970.

Every sheet older than 1970 is therefore a negative number, and on SH16 that is
two thirds of them. Handed to ``datetime.fromtimestamp`` or
``datetime.utcfromtimestamp`` on Windows, a negative value raises ``OSError:
[Errno 22] Invalid argument``. Not a wrong date -- an exception, on exactly the
oldest sheets, which are exactly the ones that put time on an estimate.

Confirmed on Windows 11 with Python 3.11 on 2026-09-12, on the real value the
service returns for the 1937 sheet. ``EPOCH + timedelta(milliseconds=...)``
has no such limit and is what this file uses.

The service states each date twice, which is what makes the reading checkable:
``SAT-029110-SH0016-19980306`` carries ``19980306`` in its own name, and
``MAP_FROM_DT`` carries the same day. They agree, so the milliseconds are being
read in the zone ArcGIS sends them in. There is a test that says so.

----

``ROW_MAP_ID`` is not one sheet
===============================

It looks like a unique key and it is not. Of the 27 SH16 sheets in Bexar
County, five different drawings share ``ROW_MAP_ID`` 993, and counting distinct
identifiers gives 22 rather than 27. ``MAP_NM`` is the name that is one per
drawing -- including the ``-1`` suffix TxDOT adds when two sheets carry the
same date. Sheets are counted as records, and ``row_map_id`` is carried through
as what it is.

Counted on 2026-09-12, on the cross-check response cached at
``txdot-row-maps/sh16-bexar-county-wide-cross-check``.
"""

from datetime import datetime, timedelta, timezone

from .arcgis import attribute
from .geometry import FEET_PER_MILE, shape_of, shape_to_paths_miles
from .output import not_screened
from .sources import ROW_MAP_FIELDS

# Milliseconds since here is what an ArcGIS date field carries. See the trap
# above for why the arithmetic is done this way rather than with fromtimestamp.
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# How a sheet with no route on it appears in the breakdown. A missing key reads
# as nothing; a named row reads as the gap it is. Same rule as
# ``control.NO_CONDITION``.
NO_ROUTE = "(none published)"

# The two things a reader has to know before using these numbers. Kept as
# constants so the tests name them rather than quoting prose back.
NOTE_DRAWINGS = "getting the drawings"
NOTE_WHAT_IS_COUNTED = "what this count covers"

DRAWINGS_DETAIL = (
    "No field in this service gives a direct link to a PDF. What you get here is "
    "the sheet count, the dates and the sheet names. The drawings themselves "
    "still come through the TxDOT ROW Division or the RPAM viewer, quoting the "
    "MAP_NM values below."
)

WHAT_IS_COUNTED_DETAIL = (
    "Every sheet whose own centerline reaches this corridor, whatever route it "
    "belongs to -- because the right of way at an interchange is drawn on the "
    "crossing route's sheets, not on this one's. Use by_route to read the "
    "corridor's own route on its own. This is a corridor figure and not a "
    "whole-route one: SH16 across the whole of Bexar County has 27 sheets over "
    "three control sections, and this corridor is about eight and a half miles "
    "inside one of them."
)


def from_epoch_ms(value):
    """One ArcGIS date field, as a date a person can read.

    The service sends milliseconds since 1970, so anything older than 1970 is
    negative -- and a negative value is what raises ``OSError`` on Windows in
    the obvious implementation. See the trap in this file's own docstring.

    Anything that is not a number is passed through exactly as it arrived. A
    value this code does not recognize is not a value it should be rewriting,
    which is the same trade ``control._recovered_on`` already makes.
    """
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    return (EPOCH + timedelta(milliseconds=value)).date().isoformat()


def to_sheet(feature, distance_ft, source_name=None):
    """One ROW map sheet, in the shape the output file uses.

    Built complete, the same way ``control.to_mark`` is: the measured distance
    is passed in rather than filled in afterwards, so no half-made record
    crosses a function boundary waiting for somebody to finish it.
    """
    attributes = feature.get("attributes") or {}

    def read(key):
        """One output field, from whichever service field ``sources.py`` names."""
        return attribute(attributes, ROW_MAP_FIELDS[key])

    return {
        # One per drawing, and the only field here that is. See the
        # ``ROW_MAP_ID`` note in this file's docstring.
        "map_name": read("map_name"),
        "row_map_id": read("row_map_id"),
        "control_section": read("control_section"),
        "csj": read("csj"),
        "route": read("route"),
        "county": read("county"),
        # The half of the answer this ticket is about. A 1937 sheet is hand
        # retracement off a scan, and that is time somebody has to price.
        "map_from_date": from_epoch_ms(read("map_from_date")),
        "map_to_date": from_epoch_ms(read("map_to_date")),
        "total_pages": read("total_pages"),
        "limit_from": read("limit_from"),
        "limit_to": read("limit_to"),
        # How far off the centerline this sheet's own line runs. Zero means it
        # lies on the corridor, which is what the corridor's own route does and
        # what a crossing route does at the interchange.
        "distance_from_centerline_ft": distance_ft,
        "source_service": source_name,
        "warnings": [],
    }


def select(features, alignment_paths, half_width_ft, plane, source_name=None):
    """Every returned sheet that actually reaches the corridor, oldest first.

    Returns ``(sheets, without_shape)``. The second number is sheets the
    service sent with no line on them. They cannot be placed in the corridor or
    out of it, so they are counted and reported rather than dropped -- the
    caller turns a non-zero count into a recorded warning, the same way the
    control step does.

    Sheets the service returned that do not reach the corridor are a different
    thing and are not counted here. The query asks about a box around the
    corridor, which is wider than the ribbon, so a sheet at the corner of that
    box is a correct answer to the question that was asked. The honesty block
    counts those, the same way it does for the flags and the marks.

    **Oldest first, because age is what costs time.** Then by name, so the
    order is the same every run -- the output file is committed to git and an
    unstable order would show a diff on every run.
    """
    limit_miles = float(half_width_ft) / FEET_PER_MILE
    sheets = []
    without_shape = 0
    for feature in features:
        shape = shape_of(feature.get("geometry"))
        # ``shape_of`` answers with a (kind, value) pair, and a record it could
        # not read is ``(None, None)`` -- which is a two-item tuple and so is
        # perfectly truthy. The kind is what has to be tested.
        kind, _ = shape
        if kind is None:
            without_shape += 1
            continue
        miles = shape_to_paths_miles(shape, alignment_paths, plane)
        if miles is None or miles > limit_miles:
            continue
        sheets.append(to_sheet(feature, round(miles * FEET_PER_MILE, 1), source_name))
    # A sheet with no date sorts last rather than first. An absent date is not
    # evidence of an old drawing, and putting it at the head of the list would
    # read as exactly that.
    sheets.sort(key=lambda s: (s["map_from_date"] is None, s["map_from_date"] or "", s["map_name"] or ""))
    return sheets, without_shape


def date_range(sheets):
    """How far back the records go, and which sheets say so.

    Both ends name the drawing the date came from. A reader who wants to check
    the number can pull that one sheet rather than take the range on trust, and
    the sheet name carries its own date, so the two can be read against each
    other.

    Sheets with no date are counted in their own field rather than left out
    quietly. A range built from nine of ten sheets is a different claim from a
    range built from all ten, and only one of those two is what the reader
    assumes.
    """
    dated = [s for s in sheets if s["map_from_date"]]
    without = len(sheets) - len(dated)
    if not dated:
        return {
            "from": None,
            "to": None,
            "oldest_sheet": None,
            "newest_sheet": None,
            "sheets_without_a_date": without,
        }
    oldest = min(dated, key=lambda s: s["map_from_date"])
    newest = max(dated, key=lambda s: s["map_from_date"])
    return {
        "from": oldest["map_from_date"],
        "to": newest["map_from_date"],
        "oldest_sheet": oldest["map_name"],
        "newest_sheet": newest["map_name"],
        "sheets_without_a_date": without,
    }


def control_sections(sheets):
    """Every numbered highway segment these sheets belong to, once each."""
    return sorted({s["control_section"] for s in sheets if s["control_section"]})


def by_route(sheets):
    """The same two numbers again, split by which route each sheet draws.

    This is what lets a reader separate the corridor's own route from the
    crossing routes whose sheets reach it at an interchange. Both sets are
    real records somebody may have to pull, and mixing them into one count
    would hide which is which.
    """
    grouped = {}
    for sheet in sheets:
        grouped.setdefault(sheet["route"] or NO_ROUTE, []).append(sheet)
    return {
        route: {
            "sheet_count": len(group),
            "date_range": date_range(group),
            "control_sections": control_sections(group),
        }
        for route, group in sorted(grouped.items())
    }


def block(sheets, detail=None, without_shape=0):
    """The ``row_maps`` block of the output file.

    ``sheets`` is the list of sheets over the corridor, or ``None`` when the
    service was never asked. Those two are different answers and the file says
    which it is -- a run that found no sheets writes a count of zero, and a run
    that never looked writes a ``not-screened`` block naming why.

    That distinction earns its keep on this service more than any other. Spec
    section 5 calls ``maps.dot.state.tx.us`` "the least reliable host,
    deliberately last," and this repo's own research recorded it failing and
    then succeeding minutes later. A blocked host reported as a count of zero
    would say a corridor has no ROW record at all, which would be the most
    interesting finding in the file and also false.
    """
    if sheets is None:
        return not_screened(detail or "the TxDOT ROW map service was not called")
    return {
        "sheet_count": len(sheets),
        "date_range": date_range(sheets),
        "control_sections": control_sections(sheets),
        "by_route": by_route(sheets),
        # Sheets the service sent with no line on them. Recorded next to the
        # count they are missing from, so the total is readable as what it is.
        "sheets_without_a_shape": without_shape,
        "notes": [
            {"topic": NOTE_DRAWINGS, "detail": DRAWINGS_DETAIL},
            {"topic": NOTE_WHAT_IS_COUNTED, "detail": WHAT_IS_COUNTED_DETAIL},
        ],
        "sheets": sheets,
    }
