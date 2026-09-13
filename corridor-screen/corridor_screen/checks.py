"""Blunt tests for answers that arrive looking fine and are not.

There are two kinds of check here and the difference is deliberate. It is
recorded in ``docs/adr/0001-sanity-checks-warn-dead-services-stop.md``.

**The field list check is a hard error.** It runs before any query is sent and
it stops the run. Pointing at the wrong layer is a configuration bug, it costs
nothing to catch, and it is the trap this repo keeps pointing at: TxDOT's
control points are layer 67 and its land parcels are layer 328. A tool that
assumes layer 0 does not error. It returns the wrong data, quietly.

**Every other check records a warning and the run carries on.** A screening
run that halts on a doubt produces nothing. A screening run that reports its
doubts beside the data produces something an RPLS can read and judge. The
warning is written into the output next to the data it doubts. The tool does
not hide it and does not fix it.
"""

from .geometry import shape_is_within_miles

# ArcGIS servers cap how many records they will hand over at once. A count that
# lands exactly on a cap is far more likely to be the cap than a coincidence.
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

FEET_PER_MILE = 5280.0


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


def collect(*results):
    """Drop the checks that did not trip."""
    return [r for r in results if r]
