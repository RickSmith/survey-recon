"""The parcel rows -- the spine everything else joins to.

Parcels come first because the output is a flagged parcel list. Every flag
added later joins to a parcel, so nothing useful exists until these rows do.

Which service field becomes which output field is decided in one place,
``sources.BEXAR_PARCEL_FIELDS``. That block, and the correction recorded above
it, is the thing to read before pointing this tool at another county.

Two words that must never blur into each other, from ``CONTEXT.md``: a parcel
that could not be checked is ``unknown``. It is never ``no``. One of those two
words sends a crew to a locked gate.
"""

import hashlib
import json

from .sources import BEXAR_PARCEL_FIELDS

# A parcel is never reported as clear of something that was not looked for, so
# a row starts screened for nothing at all. ``flags.attach`` fills this in from
# the services that actually answered -- never from the list of flag types the
# tool knows about. A run that stops before the flag services leaves it empty,
# which is the honest answer: nothing was checked.
FLAG_TYPES_SCREENED = []


def _synthetic_id(feature):
    """An identifier made from the parcel's own shape.

    Used only when the appraisal district gives no usable key. Always marked
    synthetic in the row, because it is ours and not the district's, and
    nobody should ever quote it back to Bexar County.
    """
    shape = json.dumps(feature.get("geometry") or {}, sort_keys=True)
    return "synthetic-" + hashlib.sha256(shape.encode("utf-8")).hexdigest()[:12]


def _clean(value):
    """Blank strings from a database are absent values, not empty answers."""
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


def rings_of(feature):
    """The parcel's outline, as the service drew it.

    A list of rings, each a list of ``[lon, lat]`` corners. Empty when the
    service sent no shape, which the sanity check treats as nothing to check
    rather than as a failure.

    The whole outline is kept, not a center point, because the question asked
    of a parcel is whether any part of it meets the corridor.
    """
    return ((feature.get("geometry") or {}).get("rings")) or []


def id_of(feature, fields=None):
    """The identifier this parcel's row will carry, and which field gave it.

    ``Geo_id`` is the appraisal district's own geographic identifier and is what
    a parcel should be quoted by. Some records publish none -- road slivers and
    similar -- so ``PropID`` is tried next, and a parcel with neither gets an
    identifier made from its shape.

    Split out from ``to_row`` because the identifier is wanted on its own in two
    other places, and building five hundred whole rows to read one field of each
    is five hundred rows nobody keeps.
    """
    fields = fields or BEXAR_PARCEL_FIELDS
    attributes = feature.get("attributes") or {}
    for key in ("id", "id_fallback"):
        found = _clean(attributes.get(fields[key]))
        if found is not None:
            return str(found), fields[key]
    return _synthetic_id(feature), "synthetic"


def shapes_of(features):
    """Every returned parcel as ``(identifier, rings)``, for the sanity check."""
    return [(id_of(f)[0], rings_of(f)) for f in features]


def to_row(feature, fields=None):
    """One parcel, in the shape the output file uses.

    Fields that this pass does not fill are present and empty rather than
    absent. An estimator reading the file should see that the column exists
    and that nothing has been put in it yet.
    """
    fields = fields or BEXAR_PARCEL_FIELDS
    attributes = feature.get("attributes") or {}

    identifier, id_source = id_of(feature, fields)

    return {
        "id": identifier,
        "id_source": id_source,
        "owner": _clean(attributes.get(fields["owner"])),
        "situs": _clean(attributes.get(fields["situs"])),
        "legal_description": _clean(attributes.get(fields["legal_description"])),
        "legal_acres": _clean(attributes.get(fields["legal_acres"])),
        "property_use": _clean(attributes.get(fields["property_use"])),
        # Not computed in this pass. Clipping a parcel to the ribbon is real
        # geometry work and is not part of the first path through the tool.
        "acres_in_corridor": None,
        "fraction_in_corridor": None,
        # Needs the TxDOT land layer, which this pass does not call.
        "txdot_owned": None,
        # Texas has no self-executing right of entry for surveyors. The default
        # is unknown and it only becomes "no" where the TxDOT land layer
        # confirms the parcel. See spec section 11.
        "roe_required": "unknown",
        "screened_for": list(FLAG_TYPES_SCREENED),
        "flags": [],
        "max_lead_time_days": None,
        # Which days the number above counts. Two working days and two calendar
        # days are different promises, and a bare number is the sort of thing a
        # reader turns into a date and gets wrong.
        "max_lead_time_basis": None,
        "lead_time_driver": None,
        # Flag types on this parcel whose lead time could not be confirmed.
        # It sits beside max_lead_time_days because a parcel whose only flag is
        # a school would otherwise show no number and read as clear. It is not
        # clear. It is unmeasured, which is a different thing.
        "lead_time_not_found": [],
        "warnings": [],
    }


def to_rows(features, fields=None):
    """Every parcel the service returned, de-duplicated by identifier.

    A parcel can come back twice when the corridor crosses it in two places.
    The row is the parcel, not the crossing, so the second copy is dropped.
    """
    rows = {}
    for feature in features:
        row = to_row(feature, fields)
        rows.setdefault(row["id"], row)
    return list(rows.values())
