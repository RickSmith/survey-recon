"""Where the nearest help is, for the crew that has to stand on the road.

This is the one block in the output that nobody prices. Everything else here
answers a bid question; this answers a party chief's question, asked before the
truck leaves the yard: **if somebody gets hurt out here, where do we go.**

Issue #18 is blunt that it is a different output from the flagged parcel list,
and it is kept apart in the file for that reason. A hospital does not belong in
a column of things that cost days of notice.

Four rules shape this file, and three of them are about not getting somebody
hurt.

**A distance here is a straight line, and the file says so every time.** The
line does not know about the river with no crossing, the freeway with no
turnaround, or the ranch gate that is locked. Two miles on this sheet can be a
twenty-minute drive. This is the single most dangerous number in the tool to
report without its caveat, so the caveat is a note in the block rather than a
sentence in a documentation page nobody opens in the field.

**Nothing found is never reported as nothing there.** A corridor with no
hospital within the search radius gets ``nearest: null`` beside the radius that
was searched -- not an empty list that reads as "there is no hospital." Same
rule as ``unknown`` against ``no`` everywhere else in this repo, and here the
consequence is a crew that believes it has no cover when it has cover nobody
looked for.

**Nearest to the line is not nearest to the crew.** A corridor is miles long.
The hospital two miles off the centerline can be nine miles from the end
somebody is actually standing on, so every place carries its distance from both
ends of the corridor as well as from the line. One number would have been
tidier and would have been wrong at one end.

**A record is as old as the day it was loaded.** USGS publishes ``LOADDATE``,
and on the SH16 corridor the records run from 2016 to 2025. A fire station that
closed in 2017 is still in a record loaded in 2016, so the date is carried and
the reader decides.

----

This is a screening aid. It is not a safety plan
================================================

It is worth saying plainly, because the shape of this output invites more trust
than it has earned. What it does is find published points and measure straight
lines to them. It does not know opening hours, whether a hospital has an
emergency department, whether an ambulance service runs at night, or what
mutual-aid agreement covers the county line. It has never been near this
corridor.

The party chief still makes the call and still confirms the numbers. The tool
says so in its own output, not only here.
"""

from .arcgis import attribute, from_epoch_ms
from .geometry import haversine_miles, point_of, point_to_paths_miles
from .output import not_screened
from .sources import SAFETY_FIELDS, SAFETY_TYPES

# How many places of each kind are kept. The ticket asks for the nearest; the
# two behind it are what stop "nearest to the corridor" being read as "nearest
# to where I am standing" at the far end of eight and a half miles.
PLACES_PER_TYPE = 3

# How far out to look, in miles around the corridor, unless told otherwise.
# Stated, never derived -- the same rule as every other distance in this tool.
#
# 25 is chosen to be wrong in the safe direction. On the SH16 corridor the
# answers are identical at 5 miles and at 15, so it is far more than urban Bexar
# needs; in West Texas a smaller number would report a corridor as having no
# hospital when what happened is that nobody looked far enough. Read live on
# 2026-09-13: at 25 miles this corridor returns 33 hospitals, 33 ambulance
# services, 140 fire or EMS stations and 57 police stations, all well under the
# service's 2,000 cap.
DEFAULT_SEARCH_RADIUS_MI = 25.0

# The things a reader has to know before trusting this sheet. Kept as constants
# so the tests name them rather than quoting prose back.
NOTE_STRAIGHT_LINE = "these distances are straight lines"
NOTE_NOT_A_PLAN = "this is a screening aid, not a safety plan"
NOTE_HOW_OLD = "how old these records are"

STRAIGHT_LINE_DETAIL = (
    "Every distance on this sheet is measured as a straight line -- to the "
    "nearest point of the centerline, and to each end of the corridor. It is "
    "not a drive time and it is not a road distance. The line does not know "
    "about the river with no crossing, the freeway with no turnaround, or the "
    "locked gate on the ranch road, and an ambulance does. Two miles here can "
    "be a twenty-minute drive. Check the route before the crew goes out."
)

NOT_A_PLAN_DETAIL = (
    "This block finds published points and measures straight lines to them. It "
    "does not know opening hours, whether a hospital has an emergency "
    "department, whether an ambulance service runs at night, or what mutual-aid "
    "agreement covers the county line. It has never been near this corridor. "
    "The party chief makes the call and confirms the numbers."
)

HOW_OLD_DETAIL = (
    "source_load_date is the day USGS loaded that record, not the day anybody "
    "checked the place is still there. On this corridor those dates run from "
    "2016 to 2025. A station that closed in 2017 is still in a record loaded "
    "in 2016."
)


def to_place(feature, point, to_centerline_mi, to_start_mi, to_end_mi, source_name=None):
    """One place a crew might have to get to, in the shape the output file uses.

    Built complete, the same way ``control.to_mark`` and ``row_maps.to_sheet``
    are: every measured distance is passed in rather than filled in afterwards,
    so no half-made record crosses a function boundary waiting for somebody to
    finish it.
    """
    attributes = feature.get("attributes") or {}

    def read(key):
        """One output field, from whichever service field ``sources.py`` names."""
        return attribute(attributes, SAFETY_FIELDS[key])

    return {
        "name": read("name"),
        # What a party chief actually needs. A name with no address is a name
        # somebody has to look up on a phone with no signal.
        "address": read("address"),
        "city": read("city"),
        "state": read("state"),
        "zipcode": read("zipcode"),
        # Straight line to the nearest point of the centerline. The number the
        # places are ranked by, and never a drive time -- see the note above.
        "distance_from_centerline_mi": to_centerline_mi,
        # The same measure from each end, because the crew is standing at one
        # end and not on the whole corridor at once.
        "distance_from_start_mi": to_start_mi,
        "distance_from_end_mi": to_end_mi,
        "longitude": point[0],
        "latitude": point[1],
        # The day USGS loaded the record, not the day anybody confirmed the
        # place is still open.
        "source_load_date": from_epoch_ms(read("load_date")),
        "usgs_id": read("id"),
        "source_service": source_name,
    }


def nearest(features, alignment_paths, start, end, plane, source_name=None, limit=PLACES_PER_TYPE):
    """The closest few places of one kind, nearest the centerline first.

    Returns ``(places, without_position)``. The second number is records the
    service sent with no point on them. They cannot be measured at all, so they
    are counted and reported rather than dropped -- the caller turns a non-zero
    count into a recorded warning, the same way every other step here does.

    **Ranked by distance to the centerline, then by name.** The name breaks the
    tie because the output file is committed to git, and two places the same
    distance away would otherwise swap places between runs and show a diff.
    """
    measured = []
    without_position = 0
    for feature in features:
        point = point_of(feature)
        if point is None:
            without_position += 1
            continue
        miles = point_to_paths_miles(point, alignment_paths, plane)
        if miles is None:
            without_position += 1
            continue
        measured.append(
            to_place(
                feature,
                point,
                round(miles, 2),
                round(haversine_miles(point, start), 2),
                round(haversine_miles(point, end), 2),
                source_name,
            )
        )
    measured.sort(key=lambda p: (p["distance_from_centerline_mi"], p["name"] or ""))
    return measured[:limit], without_position


def _for_type(places, without_position):
    """What this sheet says about one kind of help.

    ``nearest`` is ``None`` when the service answered and nothing of this kind
    was inside the radius. That is deliberately not an empty list, and the
    kind is named in ``not_found_within_the_radius`` beside the block's own
    ``search_radius_mi``, so the answer reads as "none within 25 miles"
    rather than "none".
    """
    return {
        "nearest": places[0] if places else None,
        # The two behind it. A crew at the far end of the corridor may be
        # closer to one of these than to the nearest.
        "others": places[1:],
        "without_position": without_position,
    }


def block(by_type, search_radius_mi=DEFAULT_SEARCH_RADIUS_MI, detail=None):
    """The ``crew_safety`` block of the output file.

    ``by_type`` maps a safety type to its ``(places, without_position)`` pair,
    and holds a key only for a type whose service actually answered. ``None``
    means no service was asked at all.

    **Three answers per type, never two.** A type with places found reports
    them. A type whose service answered with nothing inside the radius reports
    ``nearest: null`` and is named in ``not_found_within_the_radius``. A type
    nobody could ask -- a blocked host -- is named in ``not_checked`` and is
    never reported as absent, because a blocked host is not a fact about the
    world. The distinction is the one ``CONTEXT.md`` is bluntest about, and on
    this sheet the cost of getting it wrong is a crew that believes it has no
    cover.
    """
    if by_type is None:
        return not_screened(detail or "the crew safety services were not called")
    found = {kind: _for_type(*by_type[kind]) for kind in SAFETY_TYPES if kind in by_type}
    return {
        "search_radius_mi": search_radius_mi,
        "by_type": found,
        # Asked, and there was nothing of this kind inside the radius. Not the
        # same claim as "there is none".
        "not_found_within_the_radius": [k for k, v in found.items() if v["nearest"] is None],
        # Never asked. Not reported as absent, ever.
        "not_checked": [k for k in SAFETY_TYPES if k not in by_type],
        "notes": [
            {"topic": NOTE_STRAIGHT_LINE, "detail": STRAIGHT_LINE_DETAIL},
            {"topic": NOTE_NOT_A_PLAN, "detail": NOT_A_PLAN_DETAIL},
            {"topic": NOTE_HOW_OLD, "detail": HOW_OLD_DETAIL},
        ],
    }
