"""Blunt tests for answers that arrive looking fine and are not.

There are two kinds of check here and the difference is deliberate. It is
recorded in ``docs/adr/0001-sanity-checks-warn-dead-services-stop.md``.

**The field list check is a hard error.** It runs before any query is sent and
it stops the run. Pointing at the wrong layer is a configuration bug, and it
costs nothing to catch.

It is the trap this repo keeps pointing at: TxDOT's control points are layer 67
and its land parcels are layer 328. What this file used to say next was that "a
tool that assumes layer 0 does not error -- it returns the wrong data,
quietly." **Checked on 2026-09-12, that is not true of either of those two
services.** Both answer a request for layer 0 with HTTP 400, "The requested
layer (layerId: 0) was not found," because on each of them the numbered layer
is the only layer there is.

The quiet wrong answer is one step further out, and this check catches it just
the same. It is not the wrong layer, it is the wrong *service*:
``TxDOT_Control_Sections/FeatureServer/0`` exists, is layer 0, answers a
corridor query without erroring, and holds numbered highway segments rather
than survey monuments. Reading its field list is what stops that run. The whole
account is in ``sources.py`` and on the data-sources page for layer 67.

**Every other check records a warning and the run carries on.** A screening
run that halts on a doubt produces nothing. A screening run that reports its
doubts beside the data produces something an RPLS can read and judge. The
warning is written into the output next to the data it doubts. The tool does
not hide it and does not fix it.
"""

import math

from .geometry import (
    FEET_PER_MILE,
    bbox_of_shape,
    grow_bbox,
    shape_is_within_miles,
    shape_to_rings_miles,
)

# ArcGIS servers cap how many records they will hand over at once. A count that
# lands exactly on a cap is far more likely to be the cap than a coincidence.
# Specification section 8 names these three.
#
# TxDOT's ROW map server publishes a maxRecordCount of 5,000, and an earlier
# pass of issue #16 added it to this list. It was taken back out, for two
# reasons. It contradicted the specification's own list, which was not the
# agent's to amend. And it could never have fired: ``Fetcher.query_all`` always
# asks for 2,000 records a page, so no answer from any server reaches 5,000 in
# one page -- while a corridor whose pages happened to total exactly 5,000
# would have been doubted for no reason. A check that cannot trip teaches a
# reader to skip checks; one that trips wrongly teaches them to ignore
# warnings. Both are worse than not having it.
PAGING_CAPS = (500, 1000, 2000)

# How many parcels a square mile of Bexar County could plausibly hold. At this
# figure the average parcel is about a sixth of an acre, which is a small city
# lot -- so anything above it is not a dense corridor, it is the wrong extent.
# Blunt on purpose: this is here to catch a server that ignored the distance
# and returned the county, not to model San Antonio.
MAX_PARCELS_PER_SQ_MI = 4000

# How far outside the corridor any part of a returned record may sit before the
# record is doubted, in feet. Settable on the command line with
# --sanity-margin-ft, because the right slack depends on the corridor.
#
# It is measured from the edge of the ribbon, so at the default half-width a
# parcel is doubted only when every part of it is more than 800 ft from the
# centerline. This is slack for a filter that is working, not a second corridor.
DEFAULT_SANITY_MARGIN_FT = 500.0


class FieldListError(Exception):
    """A layer is not the layer we think it is. Nothing after this is safe."""


def warning(check, service, detail, what_to_do):
    """One recorded doubt, in the shape the output file uses."""
    return {
        "check": check,
        "service": service,
        "severity": "warning",
        "detail": detail,
        "what_to_do": what_to_do,
    }


def confirm_fields(source, metadata):
    """Read a layer's own field list and refuse to go on if it is wrong.

    Raises rather than warns. This runs before any real query, so stopping here
    costs one request and catches a whole run pointed at the wrong data.
    """
    published = {field["name"] for field in metadata.get("fields", [])}
    missing = [name for name in source.required_fields if name not in published]
    if missing:
        raise FieldListError(
            f"{source.name} layer {source.layer_id} does not publish "
            f"{', '.join(missing)}. Either the layer number is wrong or the "
            f"service changed its fields. Layer numbers are load-bearing: TxDOT "
            f"control is layer 67 and TxDOT land parcels is layer 328, and a "
            f"query against layer 0 would answer without complaining. "
            f"What this layer does publish: {', '.join(sorted(published)) or 'nothing'}."
        )
    return sorted(published)


def check_paging_cap(service, record_count):
    """A count that lands exactly on a server cap is probably the cap."""
    if record_count in PAGING_CAPS:
        return warning(
            "record count equals a paging cap",
            service,
            f"{service} returned exactly {record_count} records, which is one of "
            f"the counts ArcGIS servers cap at ({', '.join(str(c) for c in PAGING_CAPS)}).",
            "Check whether more records were available and the run stopped at the cap.",
        )
    return None


def check_parcel_density(service, record_count, corridor_area_sq_mi):
    """More parcels than a corridor this size can hold means the wrong extent."""
    if corridor_area_sq_mi <= 0:
        return None
    density = record_count / corridor_area_sq_mi
    if density > MAX_PARCELS_PER_SQ_MI:
        return warning(
            "more parcels than the corridor can hold",
            service,
            f"{record_count} parcels in {corridor_area_sq_mi:.2f} square miles is "
            f"{density:.0f} per square mile, above the {MAX_PARCELS_PER_SQ_MI} "
            f"this check treats as possible.",
            "The service may have ignored the corridor distance and answered for a "
            "wider area. Compare the parcel count against the corridor drawing.",
        )
    return None


def check_shapes_near_corridor(service, shapes, alignment_paths, half_width_ft, margin_ft, plane):
    """Every returned record should touch the ribbon, or very nearly.

    The 3DEP failure recorded in ``docs/txdot-research.md`` was a server
    quietly ignoring a parameter and answering anyway. This is the check that
    catches the same shape of failure here: a spatial filter that was not
    applied returns records from all over the county.

    **What is measured is any part of the parcel, not its center.** A parcel is
    a polygon, and the query asked which parcels *intersect* the corridor -- so
    the honest test of that answer is whether any part of the parcel comes near
    the corridor. A 189-acre tract clipped by a 600-foot ribbon belongs in the
    list, and its center point is a quarter of a mile outside. Testing centers
    would condemn exactly the parcels that matter most to an estimate.

    Distance is measured from the centerline and compared against the
    half-width plus the margin, which is the same as measuring from the edge of
    the ribbon outward.
    """
    if not shapes or not alignment_paths:
        return None
    limit_ft = float(half_width_ft) + float(margin_ft)
    limit_miles = limit_ft / FEET_PER_MILE
    far = [
        identifier
        for identifier, rings in shapes
        if rings and not shape_is_within_miles(rings, alignment_paths, limit_miles, plane)
    ]
    if not far:
        return None
    return warning(
        "records fall outside the corridor",
        service,
        f"{len(far)} of {len(shapes)} returned records have no part within "
        f"{limit_ft:g} ft of the centerline -- the {half_width_ft:g} ft half-width "
        f"plus a {margin_ft:g} ft margin -- including {far[0]}.",
        "The spatial filter may not have been applied. Compare the record count "
        "against the corridor drawing before using this run.",
    )


def check_impossible_acres(service, parcels):
    """Negative or absurd acreage means a unit or a coordinate was misread."""
    bad = [
        p["id"]
        for p in parcels
        if isinstance(p.get("legal_acres"), (int, float)) and p["legal_acres"] < 0
    ]
    if not bad:
        return None
    return warning(
        "impossible acreage",
        service,
        f"{len(bad)} parcels report negative acreage, including {bad[0]}.",
        "Treat the acreage column on this run as unreliable and check the source field.",
    )


def check_records_without_position(service, missing, total):
    """A record the service sent with no shape on it.

    A mark with no position cannot be placed inside the corridor or outside it.
    It is not a mark that is absent and it is not a mark that is present, so it
    is counted and said out loud rather than quietly falling out of the list --
    which is the same rule as ``unknown`` against ``no``.

    The same is true of a ROW map sheet with no line on it, which is why the
    wording says "shape" rather than "point". A mark is a point and a sheet is
    a line, and neither can be tested against the corridor without one.

    For neither service has this tripped in testing. It is here because "it has
    not happened yet" and "it cannot happen" are different claims, and only one
    of them is checkable.
    """
    if not missing:
        return None
    return warning(
        "records arrived with no shape",
        service,
        f"{missing} of {total} records came back with no shape on them, so they "
        f"could not be tested against the corridor.",
        "Those records are in neither the in-corridor list nor the count of ones "
        "outside it. Read them from the cached response before relying on the total.",
    )


# How far a service's own published coordinates may sit from the position it
# returned before the pair is doubted, in feet. Generous on purpose: this is
# here to catch a projection that was not applied, which is wrong by miles, not
# to audit a service's rounding.
DEFAULT_POSITION_TOLERANCE_FT = 100.0


def check_published_position(service, positions, plane, tolerance_ft=DEFAULT_POSITION_TOLERANCE_FT):
    """Where a service publishes its own coordinates, they should match the ones it returned.

    ``positions`` is a list of ``(identifier, returned_point, published_point)``,
    each point a ``[longitude, latitude]`` pair. Records that publish no
    position of their own are skipped -- there is nothing to compare.

    **This is the check for the projection trap.** TxDOT's layer 67 stores its
    geometry in WKID 103161, which is Texas South Central in US Survey Feet. Ask
    it for features without ``outSR=4326`` and it answers with coordinates like
    ``x: 2166836.612`` -- a real position, correctly returned, in the units it
    was stored in. Nothing errors. The tool then reads that as a longitude,
    every point lands far outside the corridor, and the corridor comes back with
    no control in it.

    The layer publishes ``STATN_LAT`` and ``STATN_LON`` as plain attributes as
    well, always in degrees. So the service answers the same question twice, in
    two ways, and the two answers can be held against each other. Two
    independent pieces of geometry agreeing is the strongest thing a screening
    run can say for itself -- the same argument the parcel check makes on
    PR #52.

    A warning rather than a hard error, like every check here but the field
    list. ADR 0001 has the reasoning.
    """
    if not positions:
        return None
    limit_miles = float(tolerance_ft) / FEET_PER_MILE
    apart = []
    for identifier, returned, declared in positions:
        if not returned or not declared:
            continue
        if declared[0] is None or declared[1] is None:
            continue
        rx, ry = plane.xy(returned)
        dx, dy = plane.xy(declared)
        if math.hypot(rx - dx, ry - dy) > limit_miles:
            apart.append(identifier)
    if not apart:
        return None
    return warning(
        "returned position disagrees with the published one",
        service,
        f"{len(apart)} of {len(positions)} records sit more than {tolerance_ft:g} ft "
        f"from the latitude and longitude the same record publishes -- including "
        f"{apart[0]}.",
        "The service may have answered in its own coordinate system -- state "
        "plane feet -- rather than in longitude and latitude. Treat every "
        "position on this run as unreliable until that is ruled out. In the "
        "cached request beside this warning, the parameter that asks for "
        "degrees is `outSR`, and it should read 4326.",
    )


def collect(*results):
    """Drop the checks that did not trip."""
    return [r for r in results if r]


def check_records_in_requested_extent(service, shapes, bbox, margin_ft, plane):
    """Every returned record should be inside the box we asked about.

    This is the section 8 check -- "any part of every returned record falls
    within a stated extent" -- applied to the flag services. They are asked
    about a box drawn around every parcel in the corridor rather than about the
    ribbon itself, because a flag can be `on` a parcel while sitting well
    outside the ribbon. So the box is what their answers are tested against.

    **This check is not hypothetical.** Asked with a polyline and a distance,
    the USGS `structures` service returned schools in Fredericksburg and
    Kerrville -- sixty miles up SH16 from the Bexar corridor -- for a query
    whose geometry stopped inside Bexar County. It returned no error. The same
    service asked with an envelope answered correctly, every time, which is why
    the flag queries are built from an envelope and why their answers are
    checked anyway. Tested live, 2026-09-12.

    It is the same shape of failure as the 3DEP one in
    ``docs/txdot-research.md``, and the same shape as the `9003` unit trap in
    ``corridor.py``: a server that quietly ignores a parameter and answers as
    if it had not.
    """
    if not shapes or not bbox:
        return None
    reach = grow_bbox(bbox, float(margin_ft) / FEET_PER_MILE)
    # The grown extent as a ring, so "any part of the record is inside it" is
    # one distance of zero rather than a box test. Comparing boxes would be the
    # same mistake the parcel check was amended for on PR #52: a long railroad
    # running past the corner of the extent has a box that overlaps while no
    # part of the line is inside. Measured, the answer is honest either way.
    ring = [
        [reach[0], reach[1]],
        [reach[0], reach[3]],
        [reach[2], reach[3]],
        [reach[2], reach[1]],
    ]
    outside = []
    for identifier, shape in shapes:
        if bbox_of_shape(shape) is None:
            continue
        if shape_to_rings_miles(shape, [ring], plane) != 0.0:
            outside.append(identifier)
    if not outside:
        return None
    return warning(
        "records fall outside the extent that was asked about",
        service,
        f"{len(outside)} of {len(shapes)} returned records lie entirely outside the "
        f"box this run asked about, grown by a {margin_ft:g} ft margin -- including "
        f"{outside[0]}.",
        "The service may have ignored the geometry filter and answered for a wider "
        "area. Those records were not attached to any parcel. Compare the record "
        "count in the honesty block against how many were used.",
    )
