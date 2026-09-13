"""What about a parcel costs time, and how many days of notice it needs.

This is the money feature. A parcel you cannot enter for 45 days is a schedule
problem the day you bid, not the day you mobilize.

A flag is one feature -- a school, a cemetery, a railroad, a pipeline -- joined
to one parcel, with the lead time that feature carries and the citation for
that lead time. The rules it follows are all from
``docs/corridor-screen/spec.md`` section 10, and three of them are worth
repeating here because breaking any one of them puts a wrong number in front of
a licensed surveyor.

**``on`` and ``adjacent`` are recorded separately and never merged.** A feature
inside the parcel is ``on`` it. The same feature within the stated neighbor
distance is ``adjacent``. A party chief needs to know about both. An estimator
must not count both.

**``screened_for`` is built from the services that actually answered**, never
from the list of types this tool knows about. A railroad that was not looked
for is not a railroad absent. That is the difference between ``unknown`` and
``no``, and one of those two words sends a crew to a locked gate.

**A lead time that could not be confirmed says "not found" and says where it
looked.** It never becomes a blank, because a blank reads as "no delay".

----

Why a distance decides the relation
===================================

``on`` against ``adjacent`` is decided from one measured distance rather than
from a separate inside-or-outside test. Zero is ``on``. Anything up to the
stated neighbor distance is ``adjacent``. Beyond that the feature is not this
parcel's problem.

One number deciding both means the two answers cannot disagree with each other,
which is exactly what happens when a containment test and a distance test are
written separately and then drift apart under maintenance.
"""

from . import geometry, lead_times as lead_times_mod
from .geometry import FEET_PER_MILE
from .sources import FLAG_FIELDS

# How many parcels one feature has to cross before it is ALSO recorded against
# the run as a whole. Stated, never derived, like the half-width beside it.
#
# Specification section 10 gives "a pipeline easement crossing many of them" as
# the example of a corridor-level flag, so a feature that crosses many parcels
# has to reach that block -- otherwise the spec's own example never gets there.
# It stays on each parcel as well, because a party chief needs to know which
# parcels, and it is recorded once at run level because an estimator must not
# count one pipeline's 48 hours thirty times.
DEFAULT_CORRIDOR_FLAG_PARCELS = 5


def attribute(attributes, name):
    """Read one field, whatever case the service answered in.

    The trap this exists for is recorded at the bottom of ``sources.py``: the
    USGS structures layers publish their fields as ``NAME`` and
    ``PERMANENT_IDENTIFIER`` and then answer a query with ``name`` and
    ``permanent_identifier``. A plain dictionary lookup finds nothing, raises
    nothing, and every school comes out unnamed.

    A blank string from a database is an absent value, not an empty answer.
    """
    attributes = attributes or {}
    if name in attributes:
        value = attributes[name]
    else:
        wanted = name.lower()
        value = next((v for k, v in attributes.items() if k.lower() == wanted), None)
    if isinstance(value, str):
        return value.strip() or None
    return value


def _relation(distance_miles, adjacent_distance_ft):
    """``on``, ``adjacent`` or nothing at all, from one measured distance."""
    if distance_miles is None:
        return None, None
    if distance_miles <= 0.0:
        return "on", None
    feet = distance_miles * FEET_PER_MILE
    if feet <= adjacent_distance_ft:
        return "adjacent", round(feet, 1)
    return None, None


def describe(source, flag_type, feature, relation, distance_ft, table, parcel_count=None):
    """One flag, in the shape the output file uses.

    The lead-time half of it comes straight out of ``lead_times.toml`` and is
    not computed here. Code that works out a statutory notice period is code
    that can be wrong about the law without anybody noticing.
    """
    fields = FLAG_FIELDS.get(source.name, {})
    attributes = feature.get("attributes") or {}
    name = attribute(attributes, fields.get("name", "NAME"))
    operator = attribute(attributes, fields["operator"]) if fields.get("operator") else None
    if operator and name and operator != name:
        name = f"{name} ({operator})"
    entry = table.get(flag_type)

    flag = {
        "type": flag_type,
        "relation": relation,
        # Recorded only when adjacent. A feature on the parcel has no distance
        # to report, and a zero there would read as a measurement.
        "distance_ft": distance_ft,
        "name": name or operator,
        "source_service": source.name,
        "source_feature_id": _identifier(attributes, fields),
        "screenable": True,
        # Corridor-level only: how many parcels in this corridor it crosses.
        # The number is what stops an estimator counting one easement once per
        # parcel, so it is on the record rather than left to be worked out.
        "parcels_crossed": parcel_count,
    }
    if entry is None:
        # A flag type with no row in the table. The loader would have caught a
        # malformed row, so this can only be a type nobody wrote a row for --
        # which is a gap, and is reported as one rather than as no delay.
        flag.update(
            {
                "lead_time_days": None,
                "lead_time_basis": None,
                "lead_time_confirmed": False,
                "lead_time_not_found": (
                    f"not found: no row for '{flag_type}' in the lead-time table. "
                    "Looked in: corridor_screen/lead_times.toml."
                ),
            }
        )
        return flag
    flag.update(entry.describe())
    return flag


def _identifier(attributes, fields):
    value = attribute(attributes, fields.get("id", "OBJECTID"))
    return str(value) if value is not None else None


def _shapes(features):
    """Every feature as ``(feature, shape, bounding box)``, drawn once.

    A flag feature is compared against every nearby parcel, so its shape and
    its box are worked out once here rather than once per comparison.
    """
    prepared = []
    for feature in features:
        shape = geometry.shape_of(feature.get("geometry"))
        if shape[0] is None:
            continue
        prepared.append((feature, shape, geometry.bbox_of_shape(shape)))
    return prepared


def attach(rows, rings_by_id, found, adjacent_distance_ft, alignment_paths,
           corridor_half_width_ft, plane, table=None,
           corridor_flag_parcels=DEFAULT_CORRIDOR_FLAG_PARCELS):
    """Hang every flag on every parcel it touches, and total up the wait.

    ``found`` is one entry per service that answered: ``(source, flag_type,
    features)``. A service that was skipped or that died is simply not in the
    list, which is what keeps ``screened_for`` honest -- it is built from this
    list and never from the set of types the tool knows about.

    Returns ``(corridor_flags, counts)``.

    ``corridor_flags`` are features that cost time but belong to no **single**
    parcel, and there are two ways for that to be true.

    A feature can land on **no** parcel while still being in the corridor -- a
    pipeline in a road right of way that no appraisal district taxes. Nothing
    gets quietly dropped for being hard to attach.

    Or a feature can land on **many** parcels, which is the example
    specification section 10 gives: "a pipeline easement crossing many of them."
    Such a feature stays on every parcel it touches, because a party chief needs
    to know which parcels -- and it is recorded once more at run level, because
    an estimator adding one pipeline's notice period thirty times has the wrong
    number. The two records are separate and are never merged, for the same
    reason ``on`` and ``adjacent`` are.

    ``counts`` is per flag type: how many records the service returned, how many
    landed on parcels, how many became corridor flags, and how many were used
    for neither. That last number is not a failure. The services are asked about
    a box drawn around every parcel in the corridor, which is wider than the
    ribbon, so a school at the far corner of the box is a normal answer to the
    question that was asked and is simply not this corridor's problem. It is
    counted rather than hidden, so the honesty block can say "39 returned, 3
    used" instead of "3".
    """
    table = table if table is not None else lead_times_mod.load()
    screened = sorted(flag_type for _, flag_type, _ in found)

    parcels = [
        (r, rings_by_id.get(r["id"]) or [])
        for r in rows
    ]
    reach_miles = adjacent_distance_ft / FEET_PER_MILE
    boxes = [
        geometry.grow_bbox(geometry.bbox_of(rings), reach_miles) if rings else None
        for _, rings in parcels
    ]

    corridor_limit_miles = float(corridor_half_width_ft) / FEET_PER_MILE
    corridor_flags = []
    counts = {}

    for row, _ in parcels:
        row["screened_for"] = list(screened)

    for source, flag_type, features in found:
        returned = len(features)
        on_parcels = 0
        as_corridor = 0
        # Counted apart from `as_corridor`, because a feature that crosses many
        # parcels is recorded in both places on purpose. Only a feature on no
        # parcel at all is the difference between "returned" and "used", so
        # only that one may come off the unused figure -- otherwise the four
        # numbers stop adding up and the honesty block stops being readable.
        corridor_only = 0
        for feature, shape, box in _shapes(features):
            reach = geometry.grow_bbox(box, reach_miles)
            landed = 0
            for (row, rings), parcel_box in zip(parcels, boxes):
                if not rings or parcel_box is None:
                    continue
                if not geometry.boxes_overlap(reach, parcel_box):
                    continue
                distance = geometry.shape_to_rings_miles(shape, rings, plane)
                relation, distance_ft = _relation(distance, adjacent_distance_ft)
                if relation is None:
                    continue
                row["flags"].append(describe(source, flag_type, feature, relation, distance_ft, table))
                landed += 1
            if landed:
                on_parcels += 1
                if landed >= corridor_flag_parcels:
                    corridor_flags.append(
                        describe(source, flag_type, feature, "corridor", None, table,
                                 parcel_count=landed)
                    )
                    as_corridor += 1
                continue
            # Nothing to hang it on. It is only the run's problem if it is
            # actually in the corridor -- see the docstring.
            to_centerline = geometry.shape_to_paths_miles(shape, alignment_paths, plane)
            if to_centerline is not None and to_centerline <= corridor_limit_miles:
                corridor_flags.append(
                    describe(source, flag_type, feature, "corridor", None, table)
                )
                as_corridor += 1
                corridor_only += 1
        counts[flag_type] = {
            "returned": returned,
            "on_parcels": on_parcels,
            "corridor": as_corridor,
            "unused": returned - on_parcels - corridor_only,
        }

    for row, _ in parcels:
        _total(row)

    return corridor_flags, counts


def _total(row):
    """Put the longest wait, and what could not be measured, on the row itself.

    The longest lead time on a parcel has to be visible without doing
    arithmetic. ``lead_time_not_found`` sits beside it because a parcel whose
    only flag is a school would otherwise show no number and read as clear. It
    is not clear. It is unmeasured, which is a different thing, and the same
    distinction as ``unknown`` against ``no``.
    """
    days, driver, basis = lead_times_mod.longest(row["flags"])
    row["max_lead_time_days"] = days
    # Which days. Two working days and two calendar days are different
    # promises, and a bare number beside them is the sort of thing a reader
    # turns into a date and gets wrong.
    row["max_lead_time_basis"] = basis
    row["lead_time_driver"] = driver
    row["lead_time_not_found"] = lead_times_mod.unconfirmed_types(row["flags"])
