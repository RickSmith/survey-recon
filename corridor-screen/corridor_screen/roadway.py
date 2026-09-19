"""What TxDOT publishes about the road itself, over this corridor.

Specification section 5 names step 5 as "Roadway facts -- ROW_MIN, lanes,
traffic." It was never built, and the ``roadway`` block was a constant saying
so, naming a service the tool did not call.

**It costs no request.** The layer the run already asks for the alignment
publishes all three, so the only change is a longer ``outFields`` on a query
that was being made anyway. Built under
[#183](https://github.com/RickSmith/survey-recon/issues/183).

----

Three rules shape this file
===========================

**A corridor is many segments, and they disagree.** TxDOT holds a route in
short inventory segments, forty of them over the SH16 corridor. Read live on
2026-09-19 they carry one right-of-way width along the whole length and
**three different lane counts** -- 4, 5 and 6. Reporting the first segment's
answer would say "four lanes" about a road that is six lanes in places.
So every number here is a low and a high, and ``varies`` says out loud
whether the two differ rather than leaving a reader to compare them.

**Empty is not zero.** ``ROW_MIN`` is published on on-system highways and
nowhere else. A corridor on a county road gets nothing at all, and a zero
would say "this road has no right of way" when the truth is "TxDOT publishes
no width for this road." Missing values are counted in
``segments_without_a_value`` and never folded into the numbers.

**Nothing here is a measurement.** These are inventory attributes. The
corridor stays a stated half-width either side of the centerline, which
specification section 3 is explicit about: the width is "reported as a fact
about the road. It does not set the buffer." The notes say so in the file
rather than only in the documentation, because the reader who needs that
caveat is the one about to quote the number.

----

The units, which the service does not publish
=============================================

``ROW_MIN`` arrives with no alias, no description and no units. Its alias is
the field name, so ``180`` is a bare number sitting next to the words "right
of way" -- exactly the kind of number ``CLAUDE.md`` says must carry its source.

TxDOT publishes the answer in its file format specification, and it is quoted
in ``WIDTH_UNITS_DETAIL`` below rather than summarized.
"""

from .arcgis import attribute
from .output import not_screened
from .sources import ROADWAY_FACT_FIELDS

# The things a reader has to know before quoting any of these numbers. Kept as
# constants so the tests name them rather than quoting prose back, the same way
# ``row_maps`` does.
NOTE_WIDTH_UNITS = "what the width is measured in"
NOTE_COVERAGE = "where this width is published and where it is not"
NOTE_NOT_A_BOUNDARY = "these are not measurements, and none of them set the corridor"
NOTE_FIELD_GONE = "this layer no longer publishes a field this block reports"

FIELD_GONE_DETAIL = (
    "The route layer's own field list no longer includes {fields}, so this run "
    "asked for a column that is not there. Every segment therefore came back "
    "with no value, which is the same thing a corridor with nothing published "
    "looks like, and the two are nothing alike. Treat any figure above that "
    "reads as not published as unknown rather than as absent, and read the "
    "field list before quoting this block. These fields are asked for but not "
    "required, so the run continued rather than stopping -- nothing else in it "
    "depends on them."
)

# TxDOT's own item number for the width, so a reader can find the line rather
# than take this page's word for it.
ROW_MIN_ITEM = "5.10"
ROW_MIN_SPEC = (
    "TxDOT Roadway Inventory Specifications 2023, page 11, revised 09/03/2024, "
    "https://gis-txdot.opendata.arcgis.com/documents/5592b6569dd54884b9de9e9341435bf9"
)

# How far the field reaches, counted live on 2026-09-19 rather than inferred
# from the specification's wording. Named here so the note and this repo's
# documentation cannot drift apart.
COUNTY_ROAD_RECORDS = 302900
COUNTY_ROAD_RECORDS_WITH_A_WIDTH = 0
SERVICE_RECORDS = 1027891
RECORDS_WITHOUT_A_WIDTH = 743679

WIDTH_UNITS_DETAIL = (
    "In feet. The service publishes no units, no alias and no description for "
    "ROW_MIN, so the number arrives bare. TxDOT's file format specification "
    f"gives item {ROW_MIN_ITEM}, RIGHT-OF-WAY-WIDTH-MINIMUM, format N4, as "
    f"'0001 - 9999 [in feet]'. {ROW_MIN_SPEC}"
)

COVERAGE_DETAIL = (
    f"TxDOT publishes this width on on-system highways only. It is empty on "
    f"{RECORDS_WITHOUT_A_WIDTH:,} of the service's {SERVICE_RECORDS:,} records, "
    f"and on {COUNTY_ROAD_RECORDS_WITH_A_WIDTH} of {COUNTY_ROAD_RECORDS:,} "
    "county road records -- not patchy, but on-system or nothing. The "
    "specification marks the field 'On-System only beginning YE2021'. So a "
    "corridor with no width here is a corridor TxDOT publishes no width for, "
    "and never a corridor with no right of way. Counted live on 2026-09-19."
)

NOT_A_BOUNDARY_DETAIL = (
    "Every number in this block is an attribute TxDOT records about the road, "
    "not a measurement anybody made of it. None of them set the corridor: that "
    "is the stated half-width either side of the centerline, which the run was "
    "given and never derives. Where the right of way actually runs is drawn on "
    "the ROW map sheets, and this width is not a substitute for reading them."
)


def _values(features, key):
    """Every published value of one field, and how many segments had none.

    ``None`` is absence and ``0`` is a value. Keeping them apart is the whole
    point: a width TxDOT never published would otherwise be reported as a road
    with no right of way.
    """
    field = ROADWAY_FACT_FIELDS[key]
    found = []
    missing = 0
    for feature in features:
        value = attribute(feature.get("attributes") or {}, field)
        if value is None:
            missing += 1
        else:
            found.append(value)
    return found, missing


def _spread(features, key, published_fields=None):
    """One fact across the corridor, as a low, a high and what was missing.

    Both ends rather than one number, because the corridor is many segments and
    they disagree. ``varies`` is said rather than left to be worked out -- two
    numbers that differ are easy to miss in a file this size, and the reader
    who misses it quotes one end as though it were the road.

    ``published_by_the_layer`` is the difference between a county road and a
    renamed column. Both make every segment come back empty, and they are
    nothing alike: one is TxDOT publishing no width for that road, the other is
    this tool asking for something that no longer exists and reporting the
    silence as an answer. ``None`` when no field list was read, because a
    caller who did not look should not be given a claim either way.
    """
    found, missing = _values(features, key)
    published = None
    if published_fields is not None:
        published = ROADWAY_FACT_FIELDS[key] in set(published_fields)
    return {
        "low": min(found) if found else None,
        "high": max(found) if found else None,
        "varies": len(set(found)) > 1,
        "segments_without_a_value": missing,
        "published_by_the_layer": published,
    }


def _traffic_year(features):
    """The year the traffic count belongs to, or the span of years.

    A traffic count with no year is not a number anybody can quote, and a
    corridor whose segments were counted in different years should say so
    rather than have one year chosen for it.
    """
    found, _ = _values(features, "traffic_year")
    years = sorted({int(y) for y in found})
    if not years:
        return None
    if len(years) == 1:
        return years[0]
    return f"{years[0]} to {years[-1]}"


def _fields_gone(published_fields):
    """Fact fields the layer no longer publishes, in the output's own order."""
    if published_fields is None:
        return []
    have = set(published_fields)
    return [name for name in ROADWAY_FACT_FIELDS.values() if name not in have]


def block(features, detail=None, published_fields=None):
    """The ``roadway`` block of the output file.

    ``features`` is the inventory segments the alignment step already fetched,
    or ``None`` when the run never got that far. Those are different answers
    and the file says which: a run that stopped before the alignment writes a
    ``not-screened`` block naming why, the same way the control, ROW map and
    crew safety blocks do.

    There is no third case here. If the run has an alignment at all, it has
    these records, because they are the same records.
    """
    if features is None:
        return not_screened(detail or "the run did not reach the route service")
    traffic = _spread(features, "traffic", published_fields)
    traffic["year"] = _traffic_year(features)
    notes = [
        {"topic": NOTE_WIDTH_UNITS, "detail": WIDTH_UNITS_DETAIL},
        {"topic": NOTE_COVERAGE, "detail": COVERAGE_DETAIL},
        {"topic": NOTE_NOT_A_BOUNDARY, "detail": NOT_A_BOUNDARY_DETAIL},
    ]
    gone = _fields_gone(published_fields)
    if gone:
        # Said at the top, because every number below it is affected and a
        # reader who meets this note last has already read the wrong thing.
        notes.insert(0, {"topic": NOTE_FIELD_GONE, "detail": FIELD_GONE_DETAIL.format(
            fields=", ".join(gone)
        )})
    return {
        "segment_count": len(features),
        # The half of this block a surveyor reads first, and the one that most
        # needs its units and its caveats travelling with it.
        "row_width_ft": _spread(features, "row_width", published_fields),
        "lanes": _spread(features, "lanes", published_fields),
        "traffic_aadt": traffic,
        "notes": notes,
    }
