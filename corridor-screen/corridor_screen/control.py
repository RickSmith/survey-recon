"""The NGS survey marks along the corridor, and what state they were left in.

Recovery against setting new is what drives an estimate, so ``condition`` is
the whole reason to pull the marks at all. A mark stamped ``MARK NOT FOUND`` is
recovery risk. It is not a mark you have.

Three rules shape this file, and breaking any of them puts a wrong number in
front of a licensed surveyor.

**``condition`` is carried through verbatim, never dropped and never
interpreted away.** ``MARK NOT FOUND`` is named, because the whole ticket is
about that one value. Every other condition NGS publishes is reported as it
came and left to the person who signs. This tool does not decide what ``POOR``
means for your crew.

**A blank condition is unknown, never a mark you have.** The service publishes
a single space for six records around Bexar County. Read carelessly that is a
non-empty string, and a mark nobody has visited since 1952 goes into an
estimate as recoverable. Same distinction as ``unknown`` against ``no`` in
``CONTEXT.md``, and the same consequence: one of those two words sends a crew
somewhere for nothing.

**A run that never asked is not a run that found no marks.** Zero marks and
never-looked are different answers, so ``ngs_marks`` is a list when the service
answered and a ``not-screened`` block when it did not.

----

Which marks count as in the corridor
====================================

The strict test: the mark's own point is within the half-width of the
centerline. No margin, no neighbor distance.

Specification section 8 says so in as many words. When the parcel check was
amended on [PR #52](https://github.com/RickSmith/survey-recon/pull/52) from
testing a center point to testing any part of a shape, the note recorded that
the strict form "stays correct for services that return points -- NGS marks,
TxDOT control -- and belongs with the first of those." This is that. A parcel
is an area and can be clipped by a ribbon; a mark is a point and is either in
or out.

So the corridor test lives here, as the filter that builds the list, rather
than in ``checks.py`` as a warning. A warning that tests the same rule the
selection already applied could never trip, and a check that cannot fail
teaches a reader to skip checks.

What ``checks.py`` still tests for this service is the other failure: whether
the service answered about the extent it was asked about at all. That one is
real, and it is the 3DEP shape of failure recorded in
``docs/txdot-research.md``.
"""

from .arcgis import attribute
from .geometry import FEET_PER_MILE, point_to_paths_miles
from .output import not_screened
from .sources import NGS_MARK_FIELDS

# The one condition value this tool names. Confirmed twice on 2026-09-12: the
# datasheets feature service publishes it in ``LAST_COND``, and the NGS Data
# Explorer API publishes the same string in ``condition`` for the same PID.
# See ``docs/data-sources/ngs-datasheets.md``.
CONDITION_NOT_FOUND = "MARK NOT FOUND"

# What this tool says about recovering a mark. Three answers, never two.
RECOVERY_NOT_FOUND = "mark not found"
RECOVERY_REPORTED = "condition reported"
RECOVERY_UNKNOWN = "condition unknown"

# How a blank condition appears in the tally. A missing key in a count table
# reads as a rounding error; a named row reads as the gap it is.
NO_CONDITION = "(none published)"


def recovery_of(condition):
    """What this tool is willing to say about getting this mark back.

    ``MARK NOT FOUND`` is named because it is the answer the ticket exists for.
    Nothing else is interpreted: ``POOR``, ``MONUMENTED`` and ``SEE
    DESCRIPTION`` are all reported, and what they are worth to a particular
    crew is the sealing surveyor's call, not this tool's.
    """
    if condition is None:
        return RECOVERY_UNKNOWN
    if condition.upper() == CONDITION_NOT_FOUND:
        return RECOVERY_NOT_FOUND
    return RECOVERY_REPORTED


def _recovered_on(value):
    """The recovery date, as a date a person can read.

    The service publishes ``19950413``. That is a date, and on a projector it
    reads as a number. Eight digits are written out as ``1995-04-13``; anything
    else is passed through exactly as the service sent it, because a value this
    code does not recognize is not a value it should be rewriting.

    The date matters as much as the condition beside it. ``GOOD`` recovered in
    1952 and ``GOOD`` recovered in 2019 are not the same promise.
    """
    if isinstance(value, str) and len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    return value


def _point_of(feature):
    """The mark's position, or nothing at all.

    NGS marks come back as a single ``x``/``y`` point per record, so this is a
    simpler read than the shapes the flag services return.
    """
    geometry = feature.get("geometry") or {}
    lon = geometry.get("x")
    lat = geometry.get("y")
    if lon is None or lat is None:
        return None
    return [lon, lat]


def to_mark(feature, distance_ft, fields=None):
    """One NGS mark, in the shape the output file uses."""
    fields = fields or NGS_MARK_FIELDS
    attributes = feature.get("attributes") or {}

    def read(key):
        """One output field, from whichever service field ``sources.py`` names."""
        return attribute(attributes, fields[key])

    condition = read("condition")
    return {
        "pid": read("pid"),
        # The field the ticket exists for. Verbatim, or absent when the service
        # published nothing -- never rewritten into a shorter list of values.
        "condition": condition,
        "recovery": recovery_of(condition),
        "last_recovered": _recovered_on(read("last_recovered")),
        "last_recovered_by": read("last_recovered_by"),
        "designation": read("designation"),
        "stamping": read("stamping"),
        "marker": read("marker"),
        "setting": read("setting"),
        "stability": read("stability"),
        "horizontal_datum": read("horizontal_datum"),
        "vertical_datum": read("vertical_datum"),
        "ortho_height_m": read("ortho_height"),
        "spc_zone": read("spc_zone"),
        "horizontal_order": read("horizontal_order"),
        "vertical_order": read("vertical_order"),
        "cors_id": read("cors_id"),
        "pacs_sacs": read("pacs_sacs"),
        "longitude": None,
        "latitude": None,
        # How far off the centerline the crew will be walking. Zero means the
        # mark is on the line, and is written as a measurement rather than left
        # blank, because a blank in this column would read as unmeasured.
        "distance_from_centerline_ft": distance_ft,
        "source_service": None,
        "warnings": [],
    }


def select(features, alignment_paths, half_width_ft, plane, fields=None, source_name=None):
    """Every returned mark that is actually in the corridor, nearest first.

    Returns ``(marks, without_position)``. The second number is marks the
    service sent with no point on them. They cannot be placed in the corridor
    or out of it, so they are counted and reported rather than dropped -- the
    caller turns a non-zero count into a recorded warning.

    Marks the service returned that sit outside the corridor are a different
    thing and are not counted here. The query asks about a box around the
    corridor, which is wider than the ribbon, so a mark at the corner of that
    box is a correct answer to the question that was asked and simply is not in
    the corridor. The honesty block counts those, the same way it does for the
    flag services: "54 returned, 12 used."

    Nearest the centerline first, then by PID. The output file is committed to
    git, so the order has to be the same every run or every run shows a diff.
    """
    limit_miles = float(half_width_ft) / FEET_PER_MILE
    marks = []
    without_position = 0
    for feature in features:
        point = _point_of(feature)
        if point is None:
            without_position += 1
            continue
        miles = point_to_paths_miles(point, alignment_paths, plane)
        if miles is None or miles > limit_miles:
            continue
        mark = to_mark(feature, round(miles * FEET_PER_MILE, 1), fields)
        mark["longitude"], mark["latitude"] = point
        mark["source_service"] = source_name
        marks.append(mark)
    marks.sort(key=lambda m: (m["distance_from_centerline_ft"], m["pid"] or ""))
    return marks, without_position


def recovery_risk(marks):
    """The counts an estimator reads before pricing recovery against setting new.

    ``mark_not_found`` is the headline. ``condition_unknown`` sits beside it
    rather than inside it, because a mark nobody has reported on is not the
    same as a mark somebody looked for and could not find -- and neither of
    them is a mark you have.

    ``by_condition`` tallies every value the service actually returned,
    including the ones this tool does not name. A condition it has never seen
    is visible in that table rather than quietly folded into "reported".
    """
    tally = {}
    for mark in marks:
        key = mark["condition"] or NO_CONDITION
        tally[key] = tally.get(key, 0) + 1
    return {
        "marks_in_corridor": len(marks),
        "mark_not_found": sum(1 for m in marks if m["recovery"] == RECOVERY_NOT_FOUND),
        "condition_unknown": sum(1 for m in marks if m["recovery"] == RECOVERY_UNKNOWN),
        "by_condition": tally,
    }


# TxDOT primary control points are their own work order. Named here rather than
# left out, because a block that is absent looks like an oversight and a block
# that says `not-screened` says what happened.
TXDOT_POINTS_PENDING = (
    "TxDOT Primary_Control_Points is layer 67 on the TxDOT feature server and is "
    "a separate work order, issue #15. It was not called on this run, so no "
    "TxDOT control point is reported as present or absent."
)


def block(marks, detail=None, without_position=0):
    """The ``control`` block of the output file.

    ``marks`` is the list of marks in the corridor, or ``None`` when the
    service was never asked. Those two are different answers and the file says
    which it is: a run that found no marks writes an empty list, and a run that
    never looked writes a ``not-screened`` block naming why.
    """
    if marks is None:
        return {
            "ngs_marks": not_screened(detail or "the NGS datasheets service was not called"),
            "txdot_points": not_screened(TXDOT_POINTS_PENDING),
            "recovery_risk": not_screened(
                detail or "no marks were fetched, so nothing was counted"
            ),
        }
    counted = recovery_risk(marks)
    # Marks the service sent with no point on them. Recorded next to the count
    # they are missing from, so the total is readable as what it is.
    counted["marks_without_position"] = without_position
    return {
        "ngs_marks": marks,
        "txdot_points": not_screened(TXDOT_POINTS_PENDING),
        "recovery_risk": counted,
    }
