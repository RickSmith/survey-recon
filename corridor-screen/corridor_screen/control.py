"""The control along the corridor, and what state it was left in.

Two services, asked separately and reported separately: the **NGS survey
marks** (issue #14) and **TxDOT's own primary control points** (issue #15).

Recovery against setting new is what drives an estimate, so ``condition`` is
the whole reason to pull either of them. A mark stamped ``MARK NOT FOUND`` is
recovery risk. A monument TxDOT calls ``Destroyed`` is recovery risk. Neither
is control you have.

**The two counts are never summed.** 98 of TxDOT's 766 records carry an NGS
PID, so some monuments are on both lists, and one total would count those
twice. The output file keeps them apart for the same reason it keeps ``on`` and
``adjacent`` apart: an estimator must not count both.

Three rules shape this file, and breaking any of them puts a wrong number in
front of a licensed surveyor.

**``condition`` is carried through verbatim, never dropped and never
interpreted away.** ``MARK NOT FOUND`` is named, because the whole ticket is
about that one value. Every other condition NGS publishes is reported as it
came and left to the person who signs. This tool does not decide what ``POOR``
means for your crew.

**A blank condition is unknown, never a mark you have.** The NGS service
publishes a single space for six records around Bexar County; TxDOT writes the
three characters ``N/A`` on 24 of its conditions. Read carelessly both are
non-empty strings, and a monument nobody has visited since 1952 goes into an
estimate as recoverable. Same distinction as ``unknown`` against ``no`` in
``CONTEXT.md``, and the same consequence: one of those two words sends a crew
somewhere for nothing.

**A run that never asked is not a run that found nothing.** Zero and
never-looked are different answers, so ``ngs_marks`` and ``txdot_points`` are
each a list when their service answered and a ``not-screened`` block when it
did not. One of the two being blocked never blanks the other.

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

from datetime import datetime, timezone

from .arcgis import attribute
from .geometry import FEET_PER_MILE, point_to_paths_miles
from .output import not_screened
from .sources import NGS_MARK_FIELDS, TXDOT_CONTROL_FIELDS

# The one condition value this tool names. Confirmed twice on 2026-09-12: the
# datasheets feature service publishes it in ``LAST_COND``, and the NGS Data
# Explorer API publishes the same string in ``condition`` for the same PID.
# See ``docs/data-sources/ngs-datasheets.md``.
CONDITION_NOT_FOUND = "MARK NOT FOUND"

# The condition TxDOT publishes for a monument that is gone. Read live on
# 2026-09-12: 18 of the 766 records on layer 67 say it. See
# ``docs/data-sources/txdot-control-points.md``.
CONDITION_DESTROYED = "DESTROYED"

# The condition TxDOT publishes when it has nothing to say. Nine records say
# this word, and 24 more say ``N/A``. Both are unknown.
CONDITION_UNKNOWN = "UNKNOWN"

# What this tool says about recovering a monument. Four answers, never fewer.
#
# ``mark not found`` and ``monument destroyed`` are kept apart on purpose. NGS's
# ``MARK NOT FOUND`` says somebody looked and could not find it. TxDOT's
# ``Destroyed`` says it is gone. They cost a crew the same trip, and folding
# them together would lose which of the two was actually said -- and the second
# is the stronger claim, so it is the one a reader is entitled to see as it was
# written.
RECOVERY_NOT_FOUND = "mark not found"
RECOVERY_DESTROYED = "monument destroyed"
RECOVERY_REPORTED = "condition reported"
RECOVERY_UNKNOWN = "condition unknown"

# The string TxDOT writes where it has nothing. It is not whitespace, so
# ``arcgis.attribute`` cannot strip it away, and read as a value it turns a
# monument nobody has assessed into control you have. See ``published``.
NOT_APPLICABLE = "N/A"

# How a blank condition appears in the tally. A missing key in a count table
# reads as a rounding error; a named row reads as the gap it is.
NO_CONDITION = "(none published)"

# The mark's full NGS datasheet: position, recovery history, and the description
# of how to find it. `MARK NOT FOUND` is the beginning of a decision, not the end
# of one, and this is where the rest of the story is.
#
# Checked on 2026-09-12 and the answer is cached at
# `ngs-datasheet-page/ds-mark-plain-get-ay0713`: a plain link returns the whole
# datasheet, carrying the PID, the designation `T 481` and `MARK NOT FOUND`.
#
# An earlier pass of this ticket wrote the opposite into the documentation --
# that the page needed a POST and answered a plain link with an empty body. That
# came from a `curl` in this repo's own working notes whose output path did not
# exist, so nothing was written and nothing was downloaded, and the zero was
# read as the server's answer. It was the measuring instrument. Re-running the
# same request through this tool's own fetcher is what caught it.
DATASHEET_URL = "https://geodesy.noaa.gov/cgi-bin/ds_mark.prl?PidBox={pid}"


def published(value):
    """What the service actually published, with its placeholder removed.

    TxDOT's layer 67 writes the three characters ``N/A`` where it has nothing.
    ``arcgis.attribute`` already drops a blank and the single space the NGS
    service writes, but ``N/A`` survives that, and a condition of ``N/A`` read
    as a value becomes "condition reported" -- a monument nobody has assessed,
    counted as control you have. Same consequence as ``unknown`` against ``no``
    in ``CONTEXT.md``, reached by a different route.

    Applied on the TxDOT read path only. The NGS service does not use this
    placeholder, and a mark whose stamping is genuinely the letters ``N/A``
    would be a real answer there rather than a blank.
    """
    if isinstance(value, str) and value.strip().upper() == NOT_APPLICABLE:
        return None
    return value


def recovery_of(condition):
    """What this tool is willing to say about getting this monument back.

    Three condition values are named, because each one answers the question the
    ticket asked. NGS's ``MARK NOT FOUND`` and TxDOT's ``DESTROYED`` are both
    recovery risk and are reported as the different claims they are. ``UNKNOWN``
    is reported as unknown rather than as a condition somebody assessed.

    Nothing else is interpreted: ``POOR``, ``GOOD``, ``MONUMENTED`` and ``SEE
    DESCRIPTION`` are all reported, and what they are worth to a particular
    crew is the sealing surveyor's call, not this tool's.

    One function for both services, because the values are disjoint and both
    mean the same thing to a surveyor. Compared in capitals because NGS answers
    ``GOOD`` and TxDOT answers ``Good``.
    """
    if condition is None:
        return RECOVERY_UNKNOWN
    upper = condition.upper()
    if upper == CONDITION_NOT_FOUND:
        return RECOVERY_NOT_FOUND
    if upper == CONDITION_DESTROYED:
        return RECOVERY_DESTROYED
    if upper == CONDITION_UNKNOWN:
        return RECOVERY_UNKNOWN
    return RECOVERY_REPORTED


def _recovered_on(value):
    """The recovery date, as a date a person can read.

    The service publishes ``19950413``. That is a date, and on a projector it
    reads as a number. Eight digits are written out as ``1995-04-13``; anything
    else is passed through exactly as the service sent it, because a value this
    code does not recognize is not a value it should be rewriting.

    The date matters as much as the condition beside it. ``GOOD`` recovered in
    1952 and ``GOOD`` recovered in 2019 are not the same promise.

    This is the one field in a mark that is not verbatim, and the trade is the
    same one ``output.write`` already makes with ``ensure_ascii=False``: the
    output file is meant to be read by a person, so readability wins where the
    change is total and the fallback is obvious. Both halves are testable and
    the raw value is in the cached response either way.
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


def to_mark(feature, point, distance_ft, source_name=None):
    """One NGS mark, in the shape the output file uses.

    Built complete. The position and the measured distance are passed in rather
    than filled in afterwards, so no half-made record ever crosses a function
    boundary waiting for somebody to finish it.
    """
    attributes = feature.get("attributes") or {}

    def read(key):
        """One output field, from whichever service field ``sources.py`` names."""
        return attribute(attributes, NGS_MARK_FIELDS[key])

    condition = read("condition")
    pid = read("pid")
    return {
        "pid": pid,
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
        # Where the rest of the story is: position, recovery history, and the
        # description of how to find it. `MARK NOT FOUND` starts a decision
        # rather than ending one, and this is what the decision gets made from.
        "datasheet_url": DATASHEET_URL.format(pid=pid) if pid else None,
        "longitude": point[0],
        "latitude": point[1],
        # How far off the centerline the crew will be walking. Zero means the
        # mark is on the line, and is written as a measurement rather than left
        # blank, because a blank in this column would read as unmeasured.
        "distance_from_centerline_ft": distance_ft,
        "source_service": source_name,
        "warnings": [],
    }


def _in_corridor(features, alignment_paths, half_width_ft, plane):
    """Every returned point that is inside the ribbon, and how far off it sits.

    Returns ``(placed, without_position)``. ``placed`` is a list of
    ``(feature, point, distance_ft)``, ready for whichever service's row builder
    is being used. ``without_position`` is the records the service sent with no
    point on them -- they cannot be placed in the corridor or out of it, so they
    are counted and reported rather than dropped, and the caller turns a
    non-zero count into a recorded warning.

    Records that came back and sit outside the corridor are a different thing
    and are not counted here. The query asks about a box around the corridor,
    which is wider than the ribbon, so a record at the corner of that box is a
    correct answer to the question that was asked and simply is not in the
    corridor. The honesty block counts those, the same way it does for the flag
    services: "54 returned, 12 used."

    Both control services share this because both return points and both are
    held to the strict test in specification section 8. What they do not share
    is what a row looks like afterwards, which is why the builder stays out.
    """
    limit_miles = float(half_width_ft) / FEET_PER_MILE
    placed = []
    without_position = 0
    for feature in features:
        point = _point_of(feature)
        if point is None:
            without_position += 1
            continue
        miles = point_to_paths_miles(point, alignment_paths, plane)
        if miles is None or miles > limit_miles:
            continue
        placed.append((feature, point, round(miles * FEET_PER_MILE, 1)))
    return placed, without_position


def select(features, alignment_paths, half_width_ft, plane, source_name=None):
    """Every returned mark that is actually in the corridor, nearest first.

    Nearest the centerline first, then by PID. The output file is committed to
    git, so the order has to be the same every run or every run shows a diff.
    """
    placed, without_position = _in_corridor(features, alignment_paths, half_width_ft, plane)
    marks = [to_mark(f, point, distance, source_name) for f, point, distance in placed]
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


# -- TxDOT primary control points --------------------------------------------
#
# Issue #15. TxDOT's own control, beside the NGS marks above. A corridor with
# TxDOT primary control already in it is one where a crew ties into something
# that exists. A corridor without it is one where control gets set, and that is
# a different line on an estimate.
#
# Why layer 67 and not layer 0, what the service's title says about its
# coverage, and why `N/A` had to be handled are all in the long note in
# `sources.py`, beside the field mapping they apply to.


def _epoch_date(value):
    """The recovery date, as a date a person can read.

    This service publishes ``1159660800000`` -- milliseconds since 1970 -- where
    the NGS service publishes the string ``19950413``. Two services, two shapes,
    and neither of them is a date on a projector. Both are written out as
    ``2006-10-01``.

    Set on only 14 of the 766 records read on 2026-09-12. The other 752 publish
    nothing, and nothing stays nothing: a missing date must never arrive in an
    estimate as New Year's Day 1970.

    Same trade as ``_recovered_on`` above, for the same reason: the change is
    total, the fallback is obvious, and the raw value is in the cached response
    either way.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()
    return value


def attachment_url(layer_url, object_id, attachment_id):
    """Where a control point's own control sheet actually lives.

    The research note lists ``SRVY_CTRL_DCMNT_ADDR`` as "(PDF link)". Read on
    2026-09-12, **that field is null on all 766 records.** ``PDF_Filename`` does
    carry a name -- ``SCP_32.pdf`` -- but it is a bare filename, and TxDOT
    publishes no base address to hang it on. Neither field gets a reader to the
    document.

    The sheet is an attachment. The layer answers ``hasAttachments: true``, and
    ``queryAttachments`` resolves every point in the corridor in one request, so
    the link below is built from an answer rather than guessed. Confirmed for
    ``SCP_32.pdf`` on 2026-09-12 and cached with every other response.

    This matters for the same reason the NGS datasheet link does. ``Destroyed``
    is the beginning of a decision, not the end of one, and the sheet carries
    the to-reach description, the adjustment and the scale factors the decision
    gets made from.
    """
    return f"{layer_url}/{object_id}/attachments/{attachment_id}"


def to_txdot_point(feature, point, distance_ft, source_name=None, pdf_url=None):
    """One TxDOT primary control point, in the shape the output file uses.

    Built complete, for the same reason ``to_mark`` is: no half-made record ever
    crosses a function boundary waiting for somebody to finish it.
    """
    attributes = feature.get("attributes") or {}

    def read(key):
        """One output field, with this service's ``N/A`` placeholder removed."""
        return published(attribute(attributes, TXDOT_CONTROL_FIELDS[key]))

    condition = read("condition")
    return {
        # This service publishes no identifier of its own beyond the station
        # name, so the station name is what a point is quoted by.
        "station": read("station"),
        # The field this block exists for. Verbatim, or absent where the service
        # published nothing -- never rewritten into a shorter list of values.
        "condition": condition,
        "recovery": recovery_of(condition),
        "last_recovered": _epoch_date(read("last_recovered")),
        # Where a TxDOT monument and an NGS mark are the same monument. Set on
        # 98 of 766 records; the rest say `N/A` or nothing, and neither is a PID.
        "ngs_pid": read("ngs_pid"),
        "stamping": read("stamping"),
        "marker": read("marker"),
        "monument_logo": read("monument_logo"),
        "stability": read("stability"),
        "quality_level": read("quality_level"),
        # TxDOT requires primary control in intervisible pairs, so who this
        # monument's partner is belongs on the row rather than in a footnote.
        "intervisible_station": read("intervisible_station"),
        "intervisible_distance": read("intervisible_distance"),
        "horizontal_datum": read("horizontal_datum"),
        "vertical_datum": read("vertical_datum"),
        "spc_zone": read("spc_zone"),
        "geoid": read("geoid"),
        # Grid coordinates, in the units the service names beside them.
        "northing": read("northing"),
        "easting": read("easting"),
        "elevation": read("elevation"),
        "units": read("units"),
        # TxDOT requires all control coordinates in surface and grid both. These
        # are the numbers that convert between the two.
        #
        # Reported, never applied. Survey Manual Ch. 3 (Control Points) is blunt:
        # "TxDOT will not accept any datum transformations for control"
        # -- https://www.txdot.gov/manuals/row/ess/index.html. A screening run is
        # not control work, and a tool that quietly reprojects teaches the wrong
        # habit. Specification section 3 makes the same point.
        "grid_scale_factor": read("grid_scale_factor"),
        "elevation_factor": read("elevation_factor"),
        "combined_scale_factor": read("combined_scale_factor"),
        # The service's own published position, carried beside the geometry it
        # returned so the two can be compared. The layer's own coordinates are
        # WKID 103161, and a query that forgot `outSR=4326` would answer in feet
        # that read as nonsense degrees. See `checks.check_published_position`.
        "published_latitude": read("published_latitude"),
        "published_longitude": read("published_longitude"),
        # How to find it on the ground, in TxDOT's own words.
        "to_reach": read("to_reach"),
        "route": read("route"),
        "county": read("county"),
        "district": read("district"),
        "pdf_filename": read("pdf_filename"),
        # The control sheet itself, where the run resolved one. `None` rather
        # than a guessed address when it did not -- a broken link in a document
        # a surveyor seals is worse than an absent one.
        "control_sheet_url": pdf_url,
        "longitude": point[0],
        "latitude": point[1],
        "distance_from_centerline_ft": distance_ft,
        "source_service": source_name,
        "warnings": [],
    }


def select_txdot(features, alignment_paths, half_width_ft, plane, source_name=None, pdf_urls=None):
    """Every returned control point that is actually in the corridor, nearest first.

    ``pdf_urls`` maps a record's ``OBJECTID`` to its resolved control sheet
    address. A point whose sheet was not resolved carries ``None`` rather than a
    guess.

    Nearest the centerline first, then by station name, so the output file shows
    the same order every run.

    **This is where the strict corridor test is applied**, through
    ``_in_corridor`` -- the point's own position against the half-width, no
    margin. Specification section 8's amended note asks for that form on the
    services that return points, "under #14 or #15," and the reasoning for it
    living here as the filter rather than in ``checks.py`` as a warning is in
    this module's own docstring: a warning that re-tests the rule the selection
    already applied could never trip, and a check that cannot fail teaches a
    reader to skip checks. What ``checks.py`` tests for this service is the
    different question of whether it answered about the box it was asked about.
    """
    pdf_urls = pdf_urls or {}
    placed, without_position = _in_corridor(features, alignment_paths, half_width_ft, plane)
    points = []
    for feature, point, distance in placed:
        object_id = attribute(feature.get("attributes"), "OBJECTID")
        points.append(
            to_txdot_point(feature, point, distance, source_name, pdf_urls.get(object_id))
        )
    points.sort(key=lambda p: (p["distance_from_centerline_ft"], p["station"] or ""))
    return points, without_position


def txdot_recovery_risk(points):
    """The counts an estimator reads before pricing TxDOT control.

    ``destroyed`` is the headline, and it is the same kind of number as
    ``mark_not_found`` on the NGS side: control that is on the map and is not on
    the ground. ``condition_unknown`` sits beside it rather than inside it,
    because a monument nobody has assessed is not a monument somebody found
    gone -- and neither of them is control you have.

    ``by_condition`` tallies every value the service actually returned,
    including the ones this tool does not name, so a condition it has never seen
    is visible in that table rather than quietly folded into "reported".

    ----

    Why there are two totals and not one
    ====================================

    ``points_in_corridor`` counts records. ``distinct_stations`` counts the
    monuments those records name, and on this service the two are not the same
    number.

    Read on 2026-09-12, layer 67 holds **766 records carrying 492 distinct
    station names**: 274 names appear twice, which is 548 of the 766 records. On
    the SH16 corridor it comes out as four records naming two monuments, roughly
    half a foot apart, with different object ids and different control sheets.

    A crew drives to the monument, not to the record. Reporting four where there
    are two doubles the control an estimator believes is already set, and that
    is a discount on a price nobody chose to give.

    So both numbers are reported and no record is dropped. Every one of the 274
    duplicated pairs agrees on condition, so there is no call to be made about
    which record to believe -- only a count to be honest about. The remaining
    figures below count records, and ``distinct_stations`` beside them is what
    says by how much.
    """
    tally = {}
    for point in points:
        key = point["condition"] or NO_CONDITION
        tally[key] = tally.get(key, 0) + 1
    return {
        "points_in_corridor": len(points),
        # The monuments, as against the records. See the note above.
        "distinct_stations": len({p["station"] for p in points if p["station"]}),
        "destroyed": sum(1 for p in points if p["recovery"] == RECOVERY_DESTROYED),
        "condition_unknown": sum(1 for p in points if p["recovery"] == RECOVERY_UNKNOWN),
        "by_condition": tally,
    }


def block(
    marks,
    txdot_points=None,
    detail=None,
    without_position=0,
    txdot_detail=None,
    txdot_without_position=0,
):
    """The ``control`` block of the output file.

    ``marks`` and ``txdot_points`` are each the list found in the corridor, or
    ``None`` when that service was never asked. Those two are different answers
    and the file says which it is: a run that found nothing writes an empty
    list, and a run that never looked writes a ``not-screened`` block naming
    why.

    **The two services are reported independently.** A blocked NGS host does not
    hide the TxDOT control points a run did retrieve, and neither one blanks the
    other's count. Each was a separate question and each gets its own answer.

    ----

    A difference from the specification, recorded rather than quietly made
    ====================================================================

    Until 2026-09-13, specification section 11 said ``ngs_marks`` and
    ``txdot_points`` were "each an **array**." Here each is an array only when
    its service was asked. When it was not -- either one on a run whose host was
    blocking -- it is a ``not-screened`` block instead.

    An empty array would be the one thing this whole tool exists to avoid: it
    reads as "we looked and there is no control here," on a corridor nobody
    looked at. That is ``unknown`` reported as ``no``, and ``CONTEXT.md`` is
    blunt about which of those two words sends a crew somewhere for nothing.

    Amending a settled specification is not the agent's call -- the precedent
    is ``AcctNumb`` on PR #52 and ``NPMS`` on PR #53, both raised rather than
    patched over. This was raised on
    [PR #54](https://github.com/RickSmith/survey-recon/pull/54), and Rick ruled
    on 2026-09-13 that each is an array when its service answered and a
    ``not-screened`` block when it did not. Section 11 now says so, with a note
    recording the amendment, so this code and the specification agree again.

    ----

    Keys in this block the specification does not name
    ==================================================

    Section 11 names ``ngs_marks``, ``txdot_points`` and ``recovery_risk``.
    Issue #15 added three things beside them, and they are listed here rather
    than left for a reader to notice, which is the precedent PR #53 set for
    additions "the file has carried and this section never named."

    - ``txdot_control`` -- the counts for the TxDOT points, a sibling of
      ``recovery_risk`` rather than part of it. Section 11 says "``recovery_risk``
      counts them," of both services. Counting them together would sum two
      overlapping lists, and 98 of TxDOT's 766 records carry an NGS PID. One
      number would quietly double some monuments.
    - ``distinct_stations``, inside ``txdot_control`` -- the monuments, as
      against the records. See ``txdot_recovery_risk``.
    - ``points_without_position`` -- the mirror of ``marks_without_position``,
      which section 11 does not name either.

    None of the three is a change to something the specification settled; each
    is a number it had no row for. Raised on issue #15 rather than slipped in,
    and **Rick ruled on 2026-09-13 that all three stay**. Section 11 now names
    them, with a note recording the amendment, so this code and the
    specification agree again.
    """
    if marks is None:
        ngs_block = not_screened(detail or "the NGS datasheets service was not called")
        recovery = not_screened(detail or "no marks were fetched, so nothing was counted")
    else:
        ngs_block = marks
        recovery = recovery_risk(marks)
        # Marks the service sent with no point on them. Recorded next to the
        # count they are missing from, so the total is readable as what it is.
        recovery["marks_without_position"] = without_position

    if txdot_points is None:
        points_block = not_screened(
            txdot_detail or "the TxDOT primary control points service was not called"
        )
        txdot_counted = not_screened(
            txdot_detail or "no control points were fetched, so nothing was counted"
        )
    else:
        points_block = txdot_points
        txdot_counted = txdot_recovery_risk(txdot_points)
        txdot_counted["points_without_position"] = txdot_without_position

    return {
        "ngs_marks": ngs_block,
        "txdot_points": points_block,
        "recovery_risk": recovery,
        # TxDOT's own control counted apart from the NGS marks, never summed
        # with them. The two services overlap -- 98 of 766 TxDOT records carry
        # an NGS PID -- so one total would count some monuments twice, and a
        # doubled control count is a discount on an estimate nobody chose.
        "txdot_control": txdot_counted,
    }
