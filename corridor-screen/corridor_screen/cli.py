"""The command line, and the order the work happens in.

The order is from ``docs/corridor-screen/spec.md`` section 5, and the reasons
are recorded there. Shortened to the steps that exist in this first pass:

1. Reachability ping -- every service, seconds, before any real work
2. Field list check -- refuse to run against the wrong layer
3. Read the alignment, plus the wrong-file check
4. Buffer -- fetch and cache the corridor polygon
5. Parcels -- the spine everything joins to
6. Flags -- what about each parcel costs time
7. Control -- the NGS marks and TxDOT's own points, and what condition they are in
8. ROW map sheets -- how many drawings there are and how far back they go
9. Crew safety -- where the nearest help is, for the people on the road

The ping exists because last is not soon enough to find out. The field list
check exists because a query against the wrong layer answers without
complaining. Both cost seconds and both stop a run that was going to be wrong.

**However a run ends, it writes an output file.** Half an answer that says so
beats no answer, and a run that stops without a record teaches nobody anything.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import (
    __version__,
    checks,
    control as control_mod,
    corridor as corridor_mod,
    flags as flags_mod,
    lead_times as lead_times_mod,
    output,
    parcels,
    row_maps as row_maps_mod,
    safety as safety_mod,
)
from .alignment import AlignmentError, from_route_features
from .arcgis import MODES, Fetcher, ServiceDown, ServiceError, attribute
from .cache import Cache, slug
from .geometry import LocalPlane, bbox_of, grow_bbox, shape_of
from .sources import (
    FLAG_FIELDS,
    FLAG_SOURCES,
    GEOMETRY,
    NGS_MARK_FIELDS,
    NGS_MARKS,
    PARCELS,
    ROADWAYS,
    ROW_MAP_FIELDS,
    ROW_MAPS,
    SAFETY_FIELDS,
    SAFETY_SOURCES,
    TXDOT_CONTROL,
    TXDOT_CONTROL_FIELDS,
)

DEFAULT_HALF_WIDTH_FT = 300
DEFAULT_ADJACENT_FT = 100

# The spine. Nothing useful exists without all three, so any one of them dying
# stops the run -- the alignment has nothing to buffer, the buffer has nothing
# to find parcels in, and the parcels are what every flag joins to.
SPINE_SOURCES = (ROADWAYS, GEOMETRY, PARCELS)

# The flag services are not the spine. A flag service that is blocked today
# costs its own flag type and nothing else: that type simply does not appear in
# `screened_for`, so no parcel is ever reported as clear of it. The run is
# marked incomplete and the honesty block names what was missed. Half an answer
# that says so beats no answer.
FLAG_SOURCE_LIST = tuple(source for source, _ in FLAG_SOURCES)

# Control is not the spine either, and it is not even joined to the parcels --
# a mark is in the corridor or it is not, whoever owns the ground. So it goes
# after the flags, which is where specification section 5 puts it, and for the
# reason recorded there: "Control and ROW sheets are independent of the parcel
# list, so a failure there costs the least."
#
# Two services, asked separately and reported separately. They overlap -- 98 of
# the 766 TxDOT records carry an NGS PID -- so their counts are never summed,
# and one of them being blocked never blanks the other.
CONTROL_SOURCE_LIST = (NGS_MARKS, TXDOT_CONTROL)

# The ROW map sheets go last, and specification section 5 says why in as many
# words: `maps.dot.state.tx.us` is "the least reliable host, deliberately
# last." This repo's own research recorded it failing and then succeeding
# minutes later. Last is where a host like that costs the least, and the
# reachability ping is doing real work on this one.
ROW_MAP_SOURCE_LIST = (ROW_MAPS,)

# The crew safety sheet. Not the spine, not joined to a parcel, and not a bid
# question at all -- issue #18 is blunt that it is a different output. It goes
# last because nothing else waits on it, and because a blocked host here must
# cost this sheet and nothing else.
SAFETY_SOURCE_LIST = tuple(source for source, _ in SAFETY_SOURCES)

# Pinged in this order, and skipped in this order if the run never reaches them.
SOURCES = (
    SPINE_SOURCES
    + FLAG_SOURCE_LIST
    + CONTROL_SOURCE_LIST
    + ROW_MAP_SOURCE_LIST
    + SAFETY_SOURCE_LIST
)

# What went wrong is worth recording; how the tool crashed is not. Anything in
# here becomes an incomplete run with a readable reason rather than a traceback.
EXPECTED_FAILURES = (
    ServiceDown,
    ServiceError,
    AlignmentError,
    corridor_mod.CorridorError,
    checks.FieldListError,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="corridor-screen",
        description=(
            "Desktop reconnaissance for a corridor. A route and its limits go in; "
            "a parcel list comes out, with every response saved."
        ),
    )
    parser.add_argument("--route", required=True, help="TxDOT route name, for example SH0016-KG")
    parser.add_argument("--begin-dfo", required=True, type=float, help="Distance From Origin at one limit")
    parser.add_argument("--end-dfo", required=True, type=float, help="Distance From Origin at the other limit")
    parser.add_argument(
        "--half-width",
        type=float,
        default=DEFAULT_HALF_WIDTH_FT,
        help=(
            "How far each side of the centerline counts as inside the corridor, in "
            f"feet. Stated, never derived. Default {DEFAULT_HALF_WIDTH_FT}."
        ),
    )
    parser.add_argument(
        "--sanity-margin-ft",
        type=float,
        default=checks.DEFAULT_SANITY_MARGIN_FT,
        help=(
            "How far outside the ribbon any part of a parcel may sit before the run "
            "doubts it, in feet. Slack for a filter that is working, not a second "
            f"corridor. Default {checks.DEFAULT_SANITY_MARGIN_FT:g}."
        ),
    )
    parser.add_argument(
        "--adjacent-distance-ft",
        type=float,
        default=DEFAULT_ADJACENT_FT,
        help=(
            "How close a feature must be to a parcel to earn an `adjacent` flag, in "
            f"feet. Default {DEFAULT_ADJACENT_FT}. `on` and `adjacent` are recorded "
            "separately and never merged."
        ),
    )
    parser.add_argument(
        "--corridor-flag-parcels",
        type=int,
        default=flags_mod.DEFAULT_CORRIDOR_FLAG_PARCELS,
        help=(
            "How many parcels one feature must cross before it is also recorded "
            "against the run as a whole. Stated, never derived. Default "
            f"{flags_mod.DEFAULT_CORRIDOR_FLAG_PARCELS}. It stays on each parcel "
            "either way; the run-level record is what stops one pipeline's notice "
            "period being counted once per parcel."
        ),
    )
    parser.add_argument(
        "--safety-search-miles",
        type=float,
        default=safety_mod.DEFAULT_SEARCH_RADIUS_MI,
        help=(
            "How far around the corridor to look for the nearest hospital, ambulance, "
            "fire or EMS station and police station, in miles. Stated, never derived. "
            f"Default {safety_mod.DEFAULT_SEARCH_RADIUS_MI:g}. Raise it on a rural "
            "corridor: nothing found inside this radius is reported as nothing found "
            "inside this radius, never as nothing there."
        ),
    )
    parser.add_argument("--mode", choices=MODES, default="cache-first", help="Whether the run may reach the network")
    parser.add_argument("--out", required=True, help="Where the output file and the cache are written")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Do not ask about a dead service; stop the run instead. Use for unattended runs.",
    )
    args = parser.parse_args(argv)
    if args.sanity_margin_ft < 0:
        # Slack cannot be negative. A margin below zero would make the check
        # doubt parcels the query was right to return, which is a warning that
        # teaches the reader to ignore warnings.
        parser.error("--sanity-margin-ft is slack outside the ribbon and cannot be negative")
    if args.half_width <= 0:
        parser.error("--half-width must be greater than zero; there is no corridor otherwise")
    if args.adjacent_distance_ft < 0:
        parser.error("--adjacent-distance-ft is a distance from a parcel and cannot be negative")
    if args.corridor_flag_parcels < 1:
        parser.error("--corridor-flag-parcels is a count of parcels and must be at least 1")
    if args.safety_search_miles <= 0:
        # A radius of zero would report every corridor as having no hospital,
        # which is the one thing the crew safety sheet must never do.
        parser.error("--safety-search-miles must be greater than zero; nothing would be found otherwise")
    return args


def _say(message=""):
    print(message, flush=True)


def _report_wrong_file_check(alignment):
    """The cheapest protection in the whole tool.

    Printed as soon as the alignment is read and before the corridor is built,
    so a corridor from the wrong route is obvious before any of the fan-out
    happens. A misread route does not look like a subtle error. It looks like a
    four-thousand-mile corridor on line one.
    """
    _say()
    _say("  Wrong-file check -- read these numbers before anything else")
    _say(f"    corridor length   {alignment.length_mi:.2f} miles")
    _say(f"    starts at         {alignment.start[1]:.6f}, {alignment.start[0]:.6f}")
    _say(f"    ends at           {alignment.end[1]:.6f}, {alignment.end[0]:.6f}")
    _say(f"    separate runs     {len(alignment.paths)}")
    _say(f"    check the map     {output.map_link(alignment.bbox)}")
    _say()


class Skipped(Exception):
    """A service a person chose to go on without."""


def _run_stage(label, attempt, unattended, skip_label=None):
    """Run one stage. If the service is dead, a person decides -- if one is there.

    Three automatic retries have already happened inside the fetcher by the
    time this sees anything. Section 7 of the specification: then ask, and if
    nobody is at the keyboard exit rather than wait, because a tool that hangs
    forever in an unattended run is a broken tool.

    Section 7 offers three answers -- retry, skip this service, or abort -- and
    which of them are honest depends on the stage. **Skipping is offered only
    where the skip costs nothing but itself**, which means the flag services
    and control. Skipping the route leaves no alignment to buffer and skipping
    the buffer leaves no corridor to find parcels in, so for the spine the only
    two honest answers are try again or stop.

    ``skip_label`` is what the person is being offered, in their words -- "this
    flag type", "the NGS marks". Passing it is what makes skipping available at
    all, so a stage that must not be skipped cannot accidentally offer it, and
    a stage that may be skipped cannot mislabel what is being given up.
    """
    while True:
        try:
            return attempt()
        except ServiceDown as exc:
            if unattended or not sys.stdin.isatty():
                raise
            _say()
            _say(f"  {label}: {exc.service} did not answer after {exc.attempts} attempts")
            _say(f"    {exc.detail}")
            choices = (
                f"[r]etry, [s]kip {skip_label}, or [a]bort? " if skip_label else "try again? [y/N] "
            )
            answer = input(f"  {choices}").strip().lower()
            if skip_label and answer in ("s", "skip"):
                raise Skipped(
                    f"{exc.service} did not answer after {exc.attempts} attempts, "
                    "and this run was told to go on without it"
                ) from exc
            if answer not in ("y", "yes", "r", "retry"):
                raise


def _rings_by_id(parcel_features):
    """Every parcel's outline, by the identifier its row carries.

    The whole outline, not a center point -- a flag is ``on`` a parcel when it
    is anywhere inside it, and the biggest tracts are exactly the ones whose
    center is nowhere near the road.
    """
    rings = {}
    for feature in parcel_features:
        identifier, _ = parcels.id_of(feature)
        rings.setdefault(identifier, parcels.rings_of(feature))
    return rings


def _parcel_extent(parcel_features, adjacent_distance_ft):
    """The box the flag services are asked about.

    **Not the corridor.** A flag is ``on`` a parcel, and a parcel reaches well
    past the ribbon -- a cemetery at the back of a tract whose frontage is on
    the pavement is on that tract and belongs on that row. So the extent is a
    box around every parcel in the corridor, grown by the neighbor distance so
    that ``adjacent`` features just outside it are caught too.

    An envelope, rather than a line and a distance, and that is not a style
    choice. Asked with a polyline and a distance, the USGS structures service
    returned schools in Fredericksburg and Kerrville -- sixty miles up SH16 --
    for a query whose geometry stopped inside Bexar County, and returned no
    error. Asked with an envelope it answered correctly every time. Tested live
    on 2026-09-12 and written up in ``docs/data-sources/flag-services.md``.
    """
    outlines = [rings for rings in (parcels.rings_of(f) for f in parcel_features) if rings]
    if not outlines:
        return None
    box = bbox_of([ring for rings in outlines for ring in rings])
    return grow_bbox(box, float(adjacent_distance_ft) / checks.FEET_PER_MILE)


def _extent_query(source, extent):
    """One query about a box, for any service that answers about an area.

    Used for the flag services, which are asked about a box around every parcel
    in the corridor, and for the NGS marks, which are asked about a box around
    the corridor itself. One shape of query, so the envelope finding in
    ``docs/data-sources/flag-services.md`` protects both.
    """
    return {
        "geometry": json.dumps(
            {
                "xmin": extent[0],
                "ymin": extent[1],
                "xmax": extent[2],
                "ymax": extent[3],
                "spatialReference": {"wkid": 4326},
            }
        ),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "outSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "where": "1=1",
        "outFields": ",".join(source.required_fields),
        # The shape, not a center point. Which parcel a railroad touches cannot
        # be answered from where the middle of the railroad happens to be.
        "returnGeometry": "true",
        "f": "json",
    }


def _identifier(feature, field):
    """The feature's own identifier, read whatever case the service answered in."""
    found = attribute(feature.get("attributes"), field)
    return str(found) if found is not None else "(unidentified)"


def _flag_id(source, feature):
    """A flag feature's identifier, for the sanity check to name."""
    fields = FLAG_FIELDS.get(source.name, {})
    return _identifier(feature, fields.get("id", "OBJECTID"))


def _go_on_without(source, args, what, skip_label):
    """Ask whether to go on without a service the ping already found blocking.

    Section 7 says a person decides. Unattended, the run goes on without this
    step rather than hanging, and says so twice -- in the honesty block, and by
    leaving the step out of whatever list says what was checked.
    """
    if args.yes or not sys.stdin.isatty():
        return
    _say()
    _say(f"  {what}: {source.name} was not answering at the ping")
    answer = input(f"  [s]kip {skip_label}, or [a]bort the run? ").strip().lower()
    if answer in ("a", "abort"):
        raise ServiceDown(
            source.name,
            "the host was not answering at the ping, and this run was told to stop",
            attempts=1,
        )


def _ask_about_extent(fetcher, args, source, extent, readable, what, skip_label):
    """Confirm the layer, then ask it what is inside a box.

    The two steps every service asked about an area goes through, in the order
    specification section 8 puts them: the field list first, because a query
    against the wrong layer answers without complaining.

    ``checks.FieldListError`` is deliberately allowed out rather than turned
    into a skipped service. A host that is blocking is the network's problem
    and costs one step. A layer that is not the layer we think it is is **our**
    problem, and section 8 makes it a hard error "because it is a configuration
    bug and free to catch." Swallowing it here would turn the layer-67-not-0
    trap into a quietly shorter screening, which is the one failure this repo
    exists to teach people to look for.
    """
    metadata, _ = _run_stage(
        f"{what} field list",
        lambda: fetcher.layer_metadata(source),
        args.yes,
        skip_label=skip_label,
    )
    checks.confirm_fields(source, metadata)
    return _run_stage(
        what,
        lambda: fetcher.query_all(source, _extent_query(source, extent), readable=readable),
        args.yes,
        skip_label=skip_label,
    )


def _screen_flags(fetcher, args, pings, blocked_hosts, parcel_features, plane):
    """Ask each flag service what sits on the corridor's parcels.

    Returns ``(found, service_entries, warnings)``. ``found`` carries only the
    services that actually answered, and that is what keeps ``screened_for``
    honest: a service that was blocked, skipped, or pointed at a layer that is
    not what we think it is simply is not in the list, so its flag type is
    never reported as clear on any parcel.
    """
    extent = _parcel_extent(parcel_features, args.adjacent_distance_ft)
    found = []
    entries = []
    warnings = []

    for source, flag_type in FLAG_SOURCES:
        ping = pings.get(source.name, {})
        if extent is None:
            entries.append(
                output.skipped_service(
                    source, "no parcel in this corridor has an outline to search around", ping
                )
            )
            continue
        if source.name in blocked_hosts:
            _go_on_without(source, args, flag_type, "this flag type")
            entries.append(
                output.skipped_service(
                    source,
                    f"the host was not answering when the run began, so {flag_type} was "
                    "not checked and no parcel is reported as clear of it",
                    ping,
                )
            )
            _say(f"  flag  {flag_type:<10} not checked -- the host was blocking at the ping")
            continue
        try:
            features, records = _ask_about_extent(
                fetcher, args, source, extent, f"flag-{flag_type}", flag_type, "this flag type"
            )
        except (ServiceDown, ServiceError, Skipped) as exc:
            # A blocked host costs one flag type and nothing else. A wrong layer
            # is not caught here on purpose -- see `_ask_about_extent`.
            entries.append(output.skipped_service(source, str(exc), ping))
            _say(f"  flag  {flag_type:<10} not checked -- {exc}")
            continue

        shapes = [(_flag_id(source, f), shape_of(f.get("geometry"))) for f in features]
        tripped = checks.collect(
            checks.check_paging_cap(source.name, len(features)),
            checks.check_records_in_requested_extent(
                source.name, shapes, extent, args.sanity_margin_ft, plane
            ),
        )
        warnings.extend(tripped)
        fetcher.note_warnings(records, tripped)
        found.append((source, flag_type, features))
        entries.append(output.service_entry(source, ping, "ok", records, len(features), tripped))
    return found, entries, warnings


def _record_counts(services, found, counts):
    """Put "39 returned, 3 used" into the honesty block."""
    by_name = {source.name: flag_type for source, flag_type, _ in found}
    for entry in services:
        flag_type = by_name.get(entry["name"])
        if flag_type and flag_type in counts:
            entry["records_used"] = counts[flag_type]


def _report_flags(rows, corridor_flags, counts, screened_for):
    """What the run found, printed while somebody is still watching."""
    _say()
    _say("  Flags")
    for flag_type in sorted(counts):
        c = counts[flag_type]
        _say(
            f"    {flag_type:<10} {c['returned']:>4} returned  {c['on_parcels']:>3} on parcels  "
            f"{c['corridor']:>3} corridor-wide  {c['unused']:>4} on no parcel in this corridor"
        )
    flagged = [r for r in rows if r["flags"]]
    _say(f"    parcels flagged   {len(flagged)} of {len(rows)}")
    if corridor_flags:
        _say(f"    corridor flags    {len(corridor_flags)}")
    with_a_number = [r for r in rows if r["max_lead_time_days"]]
    if with_a_number:
        top = max(with_a_number, key=lambda r: r["max_lead_time_days"])
        _say(
            f"    longest wait      {top['max_lead_time_days']} {top['max_lead_time_basis']} "
            f"on {top['id']} -- {top['lead_time_driver']}"
        )
    unconfirmed = sorted({t for r in rows for t in r["lead_time_not_found"]})
    if unconfirmed:
        _say(f"    no number found   {', '.join(unconfirmed)} -- see lead_time_not_found on the rows")
    _say(f"    screened for      {', '.join(screened_for) or 'nothing'}")
    _say()


def _corridor_extent(alignment, half_width_ft):
    """The box asked about by every step that is not joined to a parcel.

    A box around the corridor itself, not around the parcels. Three steps use
    it and none of them hangs off a parcel: an NGS mark is in the corridor or
    it is not, whoever owns the ground; so is a TxDOT control point; and a ROW
    sheet draws the strip of ground the parcels sit beside. So the corridor is
    what all three questions are about, and ``_parcel_extent`` is the one the
    flag services use instead.

    An envelope, for the reason written up in
    ``docs/data-sources/flag-services.md``: asked with a polyline and a
    distance, a service can buffer into the wrong county and answer without
    erroring. Asked with an envelope it answers about the envelope, and
    ``checks.check_records_in_requested_extent`` tests that it did.
    """
    return grow_bbox(alignment.bbox, float(half_width_ft) / checks.FEET_PER_MILE)


def _screen_control(fetcher, args, pings, blocked_hosts, alignment, plane):
    """Ask NGS which marks are in the corridor, and what condition they are in.

    Returns ``(marks, without_position, entry, warnings)``. ``marks`` is
    ``None`` when the service was never asked, and a list -- possibly an empty
    one -- when it was. Those are different answers and the output file says
    which it is, so a blocked host never reads as a corridor with no control.
    """
    source = NGS_MARKS
    ping = pings.get(source.name, {})
    extent = _corridor_extent(alignment, args.half_width)

    if source.name in blocked_hosts:
        _go_on_without(source, args, "control", "the NGS marks")
        reason = (
            "the host was not answering when the run began, so no NGS mark was "
            "checked and this corridor is not reported as having no control"
        )
        _say("  ctrl  ngs marks  not checked -- the host was blocking at the ping")
        return None, 0, output.skipped_service(source, reason, ping), []

    try:
        features, records = _ask_about_extent(
            fetcher, args, source, extent, "ngs-marks", "ngs marks", "the NGS marks"
        )
    except (ServiceDown, ServiceError, Skipped) as exc:
        # A blocked host costs the marks and nothing else. A wrong layer is not
        # caught here on purpose -- see `_ask_about_extent`.
        _say(f"  ctrl  ngs marks  not checked -- {exc}")
        return None, 0, output.skipped_service(source, str(exc), ping), []

    marks, without_position = control_mod.select(
        features, alignment.flat_paths, args.half_width, plane, source_name=source.name
    )
    shapes = [
        (_identifier(f, NGS_MARK_FIELDS["pid"]), shape_of(f.get("geometry")))
        for f in features
    ]
    tripped = checks.collect(
        checks.check_paging_cap(source.name, len(features)),
        checks.check_records_in_requested_extent(
            source.name, shapes, extent, args.sanity_margin_ft, plane
        ),
        checks.check_records_without_position(source.name, without_position, len(features)),
    )
    fetcher.note_warnings(records, tripped)
    entry = output.service_entry(
        source,
        ping,
        "ok",
        records,
        len(features),
        tripped,
        # "54 returned, 12 used", the same pair the flag services report. The
        # box is wider than the ribbon, so a mark at its corner is a correct
        # answer to the question asked and simply is not in the corridor.
        used={
            "returned": len(features),
            "in_corridor": len(marks),
            "without_position": without_position,
            "unused": len(features) - len(marks) - without_position,
        },
    )
    return marks, without_position, entry, tripped


def _control_sheet_urls(fetcher, source, features):
    """Where each returned control point's own control sheet lives.

    One request for the whole corridor. ``queryAttachments`` takes a list of
    object ids and answers with the attachment on each, so eight points cost one
    call rather than eight.

    **The sheets are the reason this is worth a request at all.** The field the
    research note calls a PDF link, ``SRVY_CTRL_DCMNT_ADDR``, is null on all 766
    records, and ``PDF_Filename`` is a bare filename with no published base
    address. Without this call a reader has the word ``Destroyed`` and no way to
    read what TxDOT actually recorded about the monument.

    A failure here costs the links and nothing else. The points, their
    conditions and their positions are already in hand, and a run that reports
    them without sheet links is far better than a run that reports nothing
    because an attachments endpoint was slow. So this one swallows what the
    other stages let out.
    """
    object_ids = [
        attribute(f.get("attributes"), "OBJECTID")
        for f in features
    ]
    object_ids = [str(oid) for oid in object_ids if oid is not None]
    if not object_ids:
        return {}, []
    params = {"objectIds": ",".join(object_ids), "returnUrl": "false", "f": "json"}
    try:
        data, record = fetcher.get_json(
            source.name,
            "txdot-control-attachments",
            f"{source.layer_url}/queryAttachments",
            params,
            method="POST",
            layer_id=source.layer_id,
        )
    except (ServiceDown, ServiceError) as exc:
        _say(f"  ctrl  txdot sheets  not resolved -- {exc}")
        return {}, []
    urls = {}
    for group in data.get("attachmentGroups", []):
        parent = group.get("parentObjectId")
        for info in group.get("attachmentInfos", []) or []:
            if info.get("contentType") == "application/pdf":
                urls[parent] = control_mod.attachment_url(
                    source.layer_url, parent, info.get("id")
                )
                break
    return urls, [record]


def _screen_txdot_control(fetcher, args, pings, blocked_hosts, alignment, plane):
    """Ask TxDOT which of its own primary control points are in the corridor.

    Returns ``(points, without_position, entry, warnings)``, the same shape
    ``_screen_control`` returns and for the same reason: ``points`` is ``None``
    when the service was never asked, and a list -- possibly empty -- when it
    was. A blocked host must never read as a corridor with no TxDOT control.

    Asked about the same box as the NGS marks, because the question is the same
    question: a monument is in the corridor or it is not, whoever owns the
    ground it sits on.
    """
    source = TXDOT_CONTROL
    ping = pings.get(source.name, {})
    extent = _corridor_extent(alignment, args.half_width)

    if source.name in blocked_hosts:
        _go_on_without(source, args, "control", "the TxDOT control points")
        reason = (
            "the host was not answering when the run began, so no TxDOT control "
            "point was checked and this corridor is not reported as having none"
        )
        _say("  ctrl  txdot ctrl  not checked -- the host was blocking at the ping")
        return None, 0, output.skipped_service(source, reason, ping), []

    try:
        features, records = _ask_about_extent(
            fetcher, args, source, extent, "txdot-control", "txdot control", "the TxDOT control points"
        )
    except (ServiceDown, ServiceError, Skipped) as exc:
        # A blocked host costs the control points and nothing else. A wrong
        # layer is not caught here on purpose -- see `_ask_about_extent`, and
        # this is the service the layer-67 rule was written about.
        _say(f"  ctrl  txdot ctrl  not checked -- {exc}")
        return None, 0, output.skipped_service(source, str(exc), ping), []

    sheet_urls, sheet_records = _control_sheet_urls(fetcher, source, features)
    records = records + sheet_records
    points, without_position = control_mod.select_txdot(
        features, alignment.flat_paths, args.half_width, plane,
        source_name=source.name, pdf_urls=sheet_urls,
    )
    shapes = [
        (_identifier(f, TXDOT_CONTROL_FIELDS["station"]), shape_of(f.get("geometry")))
        for f in features
    ]
    tripped = checks.collect(
        checks.check_paging_cap(source.name, len(features)),
        checks.check_records_in_requested_extent(
            source.name, shapes, extent, args.sanity_margin_ft, plane
        ),
        checks.check_records_without_position(source.name, without_position, len(features)),
        # The projection trap. This layer stores its geometry in US Survey Feet
        # and publishes its own degrees beside it, so the run can hold one
        # against the other.
        checks.check_published_position(
            source.name,
            [
                (p["station"], [p["longitude"], p["latitude"]],
                 [p["published_longitude"], p["published_latitude"]])
                for p in points
            ],
            plane,
        ),
    )
    fetcher.note_warnings(records, tripped)
    entry = output.service_entry(
        source,
        ping,
        "ok",
        records,
        len(features),
        tripped,
        used={
            "returned": len(features),
            "in_corridor": len(points),
            "without_position": without_position,
            "unused": len(features) - len(points) - without_position,
        },
    )
    return points, without_position, entry, tripped


def _report_control(marks, without_position, returned, points=None,
                    points_without_position=0, points_returned=0):
    """What the control says about recovery, printed while somebody is watching."""
    _say()
    _say("  Control")
    if marks is None:
        _say("    ngs marks         not checked -- no mark is reported present or absent")
    else:
        counted = control_mod.recovery_risk(marks)
        _say(
            f"    ngs marks         {returned:>4} returned  "
            f"{counted['marks_in_corridor']:>3} in the corridor"
        )
        _say(f"    mark not found    {counted['mark_not_found']:>4} -- recovery risk, not marks you have")
        _say(f"    condition unknown {counted['condition_unknown']:>4} -- never counted as found")
        if without_position:
            _say(f"    no position       {without_position:>4} -- could not be placed in or out")
        for condition, count in sorted(counted["by_condition"].items()):
            _say(f"      {condition:<18} {count:>4}")

    if points is None:
        _say("    txdot control     not checked -- no point is reported present or absent")
        _say()
        return
    tallied = control_mod.txdot_recovery_risk(points)
    _say(
        f"    txdot control     {points_returned:>4} returned  "
        f"{tallied['points_in_corridor']:>3} in the corridor"
    )
    # Records against monuments. This service holds two records for 274 of its
    # stations, so a crew driving to the record count would drive twice.
    _say(
        f"    distinct stations {tallied['distinct_stations']:>4} -- "
        "the monuments a crew drives to, not the records"
    )
    _say(f"    destroyed         {tallied['destroyed']:>4} -- on the map, not on the ground")
    _say(f"    condition unknown {tallied['condition_unknown']:>4} -- never counted as found")
    if points_without_position:
        _say(f"    no position       {points_without_position:>4} -- could not be placed in or out")
    for condition, count in sorted(tallied["by_condition"].items()):
        _say(f"      {condition:<18} {count:>4}")
    # The two counts are never summed. 98 of the 766 TxDOT records carry an NGS
    # PID, so some monuments are on both lists, and one total would count those
    # twice.
    _say("    the two counts overlap and are never added -- some monuments are on both")
    _say()


def _screen_row_maps(fetcher, args, pings, blocked_hosts, alignment, plane):
    """Ask TxDOT which ROW map sheets cover the corridor, and how old they are.

    Returns ``(sheets, without_shape, entry, warnings)``. ``sheets`` is
    ``None`` when the service was never asked, and a list -- possibly an empty
    one -- when it was. Those are different answers and the output file says
    which it is, so a blocked host never reads as a corridor with no ROW record.

    The same box the marks are asked about: a box around the corridor, not
    around the parcels. A ROW sheet is not joined to a parcel -- it draws the
    right of way, which is the strip of ground the parcels sit beside.
    """
    source = ROW_MAPS
    ping = pings.get(source.name, {})
    extent = _corridor_extent(alignment, args.half_width)

    if source.name in blocked_hosts:
        _go_on_without(source, args, "row maps", "the ROW map sheets")
        reason = (
            "the host was not answering when the run began, so no ROW map sheet "
            "was checked and this corridor is not reported as having no ROW record"
        )
        _say("  row   map sheets not checked -- the host was blocking at the ping")
        return None, 0, output.skipped_service(source, reason, ping), []

    try:
        features, records = _ask_about_extent(
            fetcher, args, source, extent, "row-map-sheets", "row map sheets", "the ROW map sheets"
        )
    except (ServiceDown, ServiceError, Skipped) as exc:
        # A blocked host costs the sheets and nothing else. A wrong layer is
        # not caught here on purpose -- see `_ask_about_extent`.
        _say(f"  row   map sheets not checked -- {exc}")
        return None, 0, output.skipped_service(source, str(exc), ping), []

    sheets, without_shape = row_maps_mod.select(
        features, alignment.flat_paths, args.half_width, plane, source_name=source.name
    )
    shapes = [
        (_identifier(f, ROW_MAP_FIELDS["map_name"]), shape_of(f.get("geometry")))
        for f in features
    ]
    tripped = checks.collect(
        checks.check_paging_cap(source.name, len(features)),
        checks.check_records_in_requested_extent(
            source.name, shapes, extent, args.sanity_margin_ft, plane
        ),
        checks.check_records_without_position(source.name, without_shape, len(features)),
    )
    fetcher.note_warnings(records, tripped)
    entry = output.service_entry(
        source,
        ping,
        "ok",
        records,
        len(features),
        tripped,
        # "69 returned, 69 used", the same pair every service asked about a box
        # reports. The box is wider than the ribbon, so a sheet at its corner is
        # a correct answer to the question asked and simply is not over the
        # corridor.
        used={
            "returned": len(features),
            "over_corridor": len(sheets),
            "without_shape": without_shape,
            "unused": len(features) - len(sheets) - without_shape,
        },
    )
    return sheets, without_shape, entry, tripped


def _report_row_maps(sheets, without_shape, returned):
    """What the sheets say about retracement, printed while somebody is watching.

    The route breakdown is printed rather than just the total, because the
    total mixes the corridor's own route with the crossing routes whose right
    of way is drawn at the interchanges. Both are records somebody may have to
    pull; only one of them is what a reader means by "the SH16 sheets".
    """
    _say()
    _say("  ROW map sheets")
    if sheets is None:
        _say("    map sheets        not checked -- no sheet is reported present or absent")
        _say()
        return
    spread = row_maps_mod.date_range(sheets)
    _say(f"    map sheets        {returned:>4} returned  {len(sheets):>3} over the corridor")
    if spread["from"]:
        _say(f"    date range        {spread['from']} to {spread['to']}")
        _say(f"    oldest sheet      {spread['oldest_sheet']}")
        if spread["from"] == row_maps_mod.SUSPECT_DATE:
            # Said here and not only in the output file, because this is the
            # line somebody reads off a screen. Whether this date is real or a
            # stand-in for a blank could not be confirmed, so it is doubted out
            # loud rather than quietly reported as the oldest drawing.
            _say(
                f"      {row_maps_mod.SUSPECT_DATE} is on 368 of this service's 20,276 "
                "records and may be a stand-in for no date -- unconfirmed, so check it "
                "against the drawing before quoting it"
            )
    if spread["sheets_without_a_date"]:
        _say(f"    no date           {spread['sheets_without_a_date']:>4} -- left out of the range above")
    if without_shape:
        _say(f"    no shape          {without_shape:>4} -- could not be placed over the corridor or off it")
    for route, summary in row_maps_mod.by_route(sheets).items():
        years = summary["date_range"]
        span = f"{years['from']} to {years['to']}" if years["from"] else "no dated sheet"
        _say(f"      {route:<10} {summary['sheet_count']:>4}  {span}")
    _say("    drawings          no direct link published -- RPAM, TxDOT's Real Property")
    _say("                      Asset Map, or an Open Records Request. See the notes")
    _say()


def _safety_extent(alignment, search_miles):
    """The box the crew safety services are asked about.

    **Much wider than every other extent in this tool, and deliberately so.**
    Every other step asks what is *in* the corridor. This one asks where the
    nearest help is, and the nearest hospital to a rural corridor is not in the
    corridor. A box sized to the ribbon would find nothing and that nothing
    would read as an answer.

    An envelope, for the reason written up in
    ``docs/data-sources/flag-services.md``: asked with a polyline and a
    distance, this exact server buffered into the wrong county and answered
    without erroring.
    """
    return grow_bbox(alignment.bbox, float(search_miles))


def _screen_safety(fetcher, args, pings, blocked_hosts, alignment, plane):
    """Ask where the nearest hospital, ambulance, fire or EMS and police are.

    Returns ``(by_type, service_entries, warnings)``. ``by_type`` holds a key
    only for a type whose service actually answered, which is what keeps the
    sheet honest: a blocked host leaves its type out entirely, and
    ``safety.block`` then names it under ``not_checked`` rather than reporting
    it as absent. A crew that believes it has no cover because a web server was
    down is the failure this shape exists to prevent.
    """
    extent = _safety_extent(alignment, args.safety_search_miles)
    by_type = {}
    entries = []
    warnings = []

    for source, kind in SAFETY_SOURCES:
        ping = pings.get(source.name, {})
        if source.name in blocked_hosts:
            _go_on_without(source, args, kind, "this kind of help")
            entries.append(
                output.skipped_service(
                    source,
                    f"the host was not answering when the run began, so the nearest "
                    f"{kind} was not looked for and none is reported as absent",
                    ping,
                )
            )
            _say(f"  crew  {kind:<10} not checked -- the host was blocking at the ping")
            continue
        try:
            features, records = _ask_about_extent(
                fetcher, args, source, extent, f"safety-{kind}", kind, "this kind of help"
            )
        except (ServiceDown, ServiceError, Skipped) as exc:
            # A blocked host costs this one kind of help and nothing else. A
            # wrong layer is not caught here on purpose -- see
            # `_ask_about_extent`.
            entries.append(output.skipped_service(source, str(exc), ping))
            _say(f"  crew  {kind:<10} not checked -- {exc}")
            continue

        places, without_position = safety_mod.nearest(
            features,
            alignment.flat_paths,
            alignment.start,
            alignment.end,
            plane,
            source_name=source.name,
        )
        tripped = checks.collect(
            checks.check_paging_cap(source.name, len(features)),
            checks.check_records_without_position(source.name, without_position, len(features)),
        )
        # `check_records_in_requested_extent` is deliberately not run here. Every
        # other step asks about a box and doubts a record outside it; this step
        # asks about a box precisely because the answer may be far away, and the
        # places kept are the nearest few rather than everything returned. The
        # check that matters for this sheet is the paging cap, because a cap hit
        # means the nearest place may not have been among the records returned.
        warnings.extend(tripped)
        fetcher.note_warnings(records, tripped)
        by_type[kind] = (places, without_position)
        entries.append(
            output.service_entry(
                source,
                ping,
                "ok",
                records,
                len(features),
                tripped,
                # "33 returned, 3 kept". The box is wide on purpose, so most of
                # what comes back is correctly returned and simply is not among
                # the nearest -- the same honest pair every other step reports.
                used={
                    "returned": len(features),
                    "kept": len(places),
                    "without_position": without_position,
                    "unused": len(features) - len(places) - without_position,
                },
            )
        )
    return by_type, entries, warnings


def _report_safety(by_type, search_miles):
    """The sheet a party chief reads, printed while somebody is still watching.

    The straight-line warning is printed every time, not only when something
    looks odd. It is the caveat most likely to matter and least likely to be
    read off a page somebody opened once.
    """
    _say()
    _say("  Crew safety")
    if by_type is None:
        _say("    nearest help      not checked -- nothing is reported as absent")
        _say()
        return
    for kind in safety_mod.SAFETY_TYPES:
        if kind not in by_type:
            _say(f"    {kind:<10} not checked -- no answer either way")
            continue
        places, _ = by_type[kind]
        if not places:
            _say(f"    {kind:<10} none within {search_miles:g} miles -- not the same as none")
            continue
        first = places[0]
        _say(f"    {kind:<10} {first['distance_mi']:>6.2f} mi  {first['name'] or '(unnamed)'}")
        where = ", ".join(p for p in (first["address"], first["city"]) if p)
        if where:
            _say(f"               {'':>6}      {where}")
    _say(f"    searched          {search_miles:g} miles around the corridor")
    _say("    straight lines, not drive times -- check the route before the crew goes out")
    _say()


def run(args):
    started_at = datetime.now(timezone.utc).astimezone()
    run_id = f"texas-bexar-{slug(args.route)}-{started_at.strftime('%Y%m%dT%H%M%S')}"
    out_dir = Path(args.out)
    cache = Cache(out_dir / "cache")
    fetcher = Fetcher(cache, mode=args.mode)

    _say(f"corridor-screen {__version__}  run {run_id}  mode {args.mode}")

    services = []
    warnings = []
    rows = []
    alignment = None
    corridor = None
    corridor_flags = []
    screened_for = []
    status = "complete"
    stopped_at = None
    # `None` means the service was never asked, which is not the same as a
    # corridor with no control in it. The detail beside it is what the output
    # file says instead of a list. One pair per service, so a blocked NGS host
    # never blanks the TxDOT points a run did retrieve.
    control_marks = None
    control_without_position = 0
    control_detail = "the run stopped before the control step"
    txdot_points = None
    txdot_without_position = 0
    txdot_detail = "the run stopped before the control step"
    # Same rule as the marks above. `None` means the ROW map service was never
    # asked, which is not the same as a corridor with no ROW record over it --
    # and on the host specification section 5 calls the least reliable, that
    # distinction is the one most likely to be needed.
    row_map_sheets = None
    row_maps_without_shape = 0
    row_maps_detail = "the run stopped before the ROW map step"
    # Same rule again, and it matters most here. `None` means no safety service
    # was asked, which is not the same as a corridor with no hospital near it --
    # and a crew that believes it has no cover because a web server was down is
    # the worst answer this tool could give.
    safety_by_type = None
    safety_detail = "the run stopped before the crew safety step"

    # Read before anything is fetched. A table that cannot be quoted -- a row
    # with no citation, a "not found" that does not say where it looked -- is a
    # configuration mistake, and catching it now costs nothing. Catching it
    # after ninety seconds of fetching costs ninety seconds.
    table = lead_times_mod.load()

    # 1 -- reachability, in seconds, before any real work
    pings = {}
    for source in SOURCES:
        pings[source.name] = fetcher.ping(source)
        result = pings[source.name]
        _say(f"  ping  {source.name:<18} {result['ping']:<8} {result['ms']} ms  {result['detail']}")
    blocked = [name for name, result in pings.items() if result["ping"] == "blocked"]
    # A blocked flag or control service costs its own step. A blocked spine
    # service costs the run. The split is why the lists are separate.
    spine_blocked = [name for name in blocked if any(s.name == name for s in SPINE_SOURCES)]
    blocked_hosts = {name for name in blocked if name not in spine_blocked}

    if spine_blocked:
        _say()
        _say(f"  {', '.join(spine_blocked)} is not answering today. Nothing was fetched.")
        _say("  Try again, or use --mode cache-only if this corridor was captured before.")
        status = "incomplete"
        stopped_at = spine_blocked[0]
        control_detail = (
            f"{', '.join(spine_blocked)} was not answering, so the run never reached "
            "the control step and no NGS mark was checked"
        )
        row_maps_detail = (
            f"{', '.join(spine_blocked)} was not answering, so the run never reached "
            "the ROW map step and no map sheet was checked"
        )
        safety_detail = (
            f"{', '.join(spine_blocked)} was not answering, so the run never reached "
            "the crew safety step and no nearest help was looked for"
        )
        services = [
            output.skipped_service(
                source, "the host was not answering when the run began", pings[source.name]
            )
            for source in SOURCES
        ]
    else:
        try:
            # 2 -- the wrong layer answers without complaining, so check first
            for source in (ROADWAYS, PARCELS):
                metadata, _ = _run_stage(
                    "field list", lambda s=source: fetcher.layer_metadata(s), args.yes
                )
                checks.confirm_fields(source, metadata)
            _say("  field lists confirmed on every layer")

            # 3 -- the alignment, and the wrong-file check before anything wider
            features, road_records = _run_stage("route", lambda: fetcher.query_all(
                ROADWAYS,
                {
                    "where": f"RTE_NM='{args.route}' AND BEGIN_DFO<={args.end_dfo} AND END_DFO>={args.begin_dfo}",
                    "outFields": "RTE_NM,BEGIN_DFO,END_DFO",
                    "returnGeometry": "true",
                    "returnM": "true",
                    "outSR": 4326,
                    "f": "json",
                },
                readable=f"route-{slug(args.route)}",
            ), args.yes)
            alignment = from_route_features(features, args.route, args.begin_dfo, args.end_dfo)
            services.append(
                output.service_entry(ROADWAYS, pings[ROADWAYS.name], "ok", road_records, len(features))
            )
            _report_wrong_file_check(alignment)

            # 4 -- the corridor polygon, fetched once and cached
            corridor, buffer_record = _run_stage(
                "buffer", lambda: corridor_mod.build(fetcher, GEOMETRY, alignment, args.half_width), args.yes
            )
            services.append(
                output.service_entry(GEOMETRY, pings[GEOMETRY.name], "ok", [buffer_record], len(corridor.rings))
            )
            _say(f"  corridor area {corridor.area_sq_mi:.2f} square miles")

            # 5 -- parcels, the spine everything joins to
            parcel_features, parcel_records = _run_stage("parcels", lambda: fetcher.query_all(
                PARCELS,
                {
                    "geometry": json.dumps(alignment.to_esri_polyline()),
                    "geometryType": "esriGeometryPolyline",
                    "inSR": 4326,
                    "outSR": 4326,
                    "spatialRel": "esriSpatialRelIntersects",
                    "distance": args.half_width,
                    "units": corridor_mod.QUERY_FOOT_UNITS,
                    "outFields": ",".join(PARCELS.required_fields),
                    # The outline, not a center point. The sanity check asks
                    # whether any part of a parcel meets the corridor, which is
                    # the question the query itself was asked.
                    "returnGeometry": "true",
                    "f": "json",
                },
                readable="parcels",
            ), args.yes)
            rows = parcels.to_rows(parcel_features)

            # One flat plane fitted at the corridor's own latitude, so every
            # distance measured in this run is measured the same way.
            plane = LocalPlane((alignment.bbox[1] + alignment.bbox[3]) / 2)
            parcel_warnings = checks.collect(
                checks.check_paging_cap(PARCELS.name, len(parcel_features)),
                checks.check_parcel_density(PARCELS.name, len(parcel_features), corridor.area_sq_mi),
                checks.check_shapes_near_corridor(
                    PARCELS.name,
                    parcels.shapes_of(parcel_features),
                    alignment.flat_paths,
                    args.half_width,
                    args.sanity_margin_ft,
                    plane,
                ),
                checks.check_impossible_acres(PARCELS.name, rows),
            )
            warnings.extend(parcel_warnings)
            # Section 14 asks the provenance record to carry any sanity check
            # that tripped, so the doubt travels with the response it doubts.
            fetcher.note_warnings(parcel_records, parcel_warnings)
            services.append(
                output.service_entry(
                    PARCELS, pings[PARCELS.name], "ok", parcel_records, len(parcel_features), parcel_warnings
                )
            )

            # 6 -- flags. The money feature, and the first step that is not the
            # spine: any one of these can be missed without costing the rest.
            found, flag_services, flag_warnings = _screen_flags(
                fetcher, args, pings, blocked_hosts, parcel_features, plane
            )
            services.extend(flag_services)
            warnings.extend(flag_warnings)

            corridor_flags, counts = flags_mod.attach(
                rows,
                _rings_by_id(parcel_features),
                found,
                adjacent_distance_ft=args.adjacent_distance_ft,
                alignment_paths=alignment.flat_paths,
                corridor_half_width_ft=args.half_width,
                plane=plane,
                table=table,
                corridor_flag_parcels=args.corridor_flag_parcels,
            )
            screened_for = sorted(flag_type for _, flag_type, _ in found)
            _record_counts(services, found, counts)
            _report_flags(rows, corridor_flags, counts, screened_for)
            if len(screened_for) < len(FLAG_SOURCES):
                # Something was not checked. The output has to say so, and the
                # missing type stays off every parcel's `screened_for`.
                status = "incomplete"

            # 7 -- control. Independent of the parcel list, so it goes after
            # the flags and a failure here costs the least.
            control_marks, control_without_position, control_entry, control_warnings = (
                _screen_control(fetcher, args, pings, blocked_hosts, alignment, plane)
            )
            services.append(control_entry)
            warnings.extend(control_warnings)
            if control_marks is None:
                # The marks were not checked. Same rule as a missing flag type:
                # the run says so rather than reading as a clean corridor.
                control_detail = control_entry.get("detail", "the NGS marks were not checked")
                status = "incomplete"

            # TxDOT's own control, asked separately so that one of the two
            # services being blocked costs only its own half of the answer.
            txdot_points, txdot_without_position, txdot_entry, txdot_warnings = (
                _screen_txdot_control(fetcher, args, pings, blocked_hosts, alignment, plane)
            )
            services.append(txdot_entry)
            warnings.extend(txdot_warnings)
            if txdot_points is None:
                txdot_detail = txdot_entry.get(
                    "detail", "the TxDOT control points were not checked"
                )
                status = "incomplete"

            _report_control(
                control_marks,
                control_without_position,
                control_entry.get("record_count") or 0,
                points=txdot_points,
                points_without_position=txdot_without_position,
                points_returned=txdot_entry.get("record_count") or 0,
            )

            # 8 -- the ROW map sheets. Deliberately last, on the host the
            # specification names least reliable.
            row_map_sheets, row_maps_without_shape, row_map_entry, row_map_warnings = (
                _screen_row_maps(fetcher, args, pings, blocked_hosts, alignment, plane)
            )
            services.append(row_map_entry)
            warnings.extend(row_map_warnings)
            if row_map_sheets is None:
                # Not checked. Same rule as a missing flag type and as the
                # marks: the run says so rather than reading as a corridor
                # whose right of way was never drawn.
                row_maps_detail = row_map_entry.get("detail", "the ROW map sheets were not checked")
                status = "incomplete"
            _report_row_maps(
                row_map_sheets, row_maps_without_shape, row_map_entry.get("record_count") or 0
            )

            # 9 -- the crew safety sheet. Not a bid question, and the only
            # block here somebody reads before driving out rather than before
            # pricing.
            safety_by_type, safety_services, safety_warnings = _screen_safety(
                fetcher, args, pings, blocked_hosts, alignment, plane
            )
            services.extend(safety_services)
            warnings.extend(safety_warnings)
            if len(safety_by_type) < len(SAFETY_SOURCES):
                # A kind of help nobody could ask about. The run says so, and
                # `safety.block` keeps it out of the answer entirely rather
                # than letting it read as none nearby.
                status = "incomplete"
            _report_safety(safety_by_type, args.safety_search_miles)

        except EXPECTED_FAILURES as exc:
            # A stopped run still writes its output, marked incomplete, naming
            # what stopped it. The responses already fetched are already cached,
            # so a re-run in cache-first mode resumes almost free.
            _say()
            _say(f"  run stopped: {exc}")
            status = "incomplete"
            stopped_at = getattr(exc, "service", type(exc).__name__)
            # Whatever the control was going to say, the run did not get to ask.
            # The reason travels into the control block rather than leaving the
            # generic one there, which would name the wrong step. Both services
            # get it, because a run that stopped asked neither.
            control_marks = None
            control_detail = f"the run stopped before the control step finished: {exc}"
            txdot_points = None
            txdot_detail = control_detail
            row_map_sheets = None
            row_maps_detail = f"the run stopped before the ROW map step finished: {exc}"
            safety_by_type = None
            safety_detail = f"the run stopped before the crew safety step finished: {exc}"
            for source in SOURCES:
                if not any(entry["name"] == source.name for entry in services):
                    services.append(
                        output.skipped_service(
                            source, "the run stopped before this service was asked", pings.get(source.name)
                        )
                    )

    document = output.build(
        run_id=run_id,
        started_at=started_at,
        mode=args.mode,
        half_width_ft=args.half_width,
        adjacent_distance_ft=DEFAULT_ADJACENT_FT,
        sanity_margin_ft=args.sanity_margin_ft,
        tool_version=__version__,
        alignment=alignment,
        corridor=corridor,
        services=services,
        parcel_rows=rows,
        warnings=warnings,
        status=status,
        stopped_at_service=stopped_at,
        corridor_flags=corridor_flags,
        screened_for=screened_for,
        lead_time_table=lead_times_mod.citations(table, screened_for),
        control=control_mod.block(
            control_marks,
            txdot_points=txdot_points,
            detail=control_detail,
            without_position=control_without_position,
            txdot_detail=txdot_detail,
            txdot_without_position=txdot_without_position,
        ),
        row_maps=row_maps_mod.block(
            row_map_sheets, detail=row_maps_detail, without_shape=row_maps_without_shape
        ),
        crew_safety=safety_mod.block(
            safety_by_type, search_radius_mi=args.safety_search_miles, detail=safety_detail
        ),
    )
    written = output.write(document, out_dir)
    index = cache.write_index(f"{args.route} DFO {args.begin_dfo} to {args.end_dfo}")

    _say(f"  parcels     {len(rows)}")
    _say(f"  warnings    {len(warnings)}")
    for recorded in warnings:
        _say(f"    - {recorded['check']}: {recorded['detail']}")
    _say(f"  written     {written}")
    _say(f"  cache index {index}")
    if status != "complete":
        kept = out_dir / output.COMPLETE_NAME
        if kept.exists():
            _say(f"  left alone  {kept} is from an earlier run and was not overwritten")
    return 0 if status == "complete" else 1


def main(argv=None):
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
