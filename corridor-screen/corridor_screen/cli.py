"""The command line, and the order the work happens in.

The order is from ``docs/corridor-screen/spec.md`` section 5, and the reasons
are recorded there. Shortened to the steps that exist in this first pass:

1. Reachability ping -- every service, seconds, before any real work
2. Field list check -- refuse to run against the wrong layer
3. Read the alignment, plus the wrong-file check
4. Buffer -- fetch and cache the corridor polygon
5. Parcels -- the spine everything joins to

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
    corridor as corridor_mod,
    flags as flags_mod,
    lead_times as lead_times_mod,
    output,
    parcels,
)
from .alignment import AlignmentError, from_route_features
from .arcgis import MODES, Fetcher, ServiceDown, ServiceError
from .cache import Cache, slug
from .geometry import LocalPlane, bbox_of, grow_bbox, shape_of
from .sources import FLAG_FIELDS, FLAG_SOURCES, GEOMETRY, PARCELS, ROADWAYS

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

# Pinged in this order, and skipped in this order if the run never reaches them.
SOURCES = SPINE_SOURCES + FLAG_SOURCE_LIST

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


def _run_stage(label, attempt, unattended, allow_skip=False):
    """Run one stage. If the service is dead, a person decides -- if one is there.

    Three automatic retries have already happened inside the fetcher by the
    time this sees anything. Section 7 of the specification: then ask, and if
    nobody is at the keyboard exit rather than wait, because a tool that hangs
    forever in an unattended run is a broken tool.

    Section 7 offers three answers -- retry, skip this service, or abort -- and
    which of them are honest depends on the stage. **Skipping is offered only
    where it is offered**, which means the flag services. Skipping the route
    leaves no alignment to buffer and skipping the buffer leaves no corridor to
    find parcels in, so for the spine the only two honest answers are try again
    or stop. Skipping a flag service costs one flag type, and that type then
    stays off `screened_for`, so no parcel is reported as clear of it.
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
            choices = "[r]etry, [s]kip this flag type, or [a]bort? " if allow_skip else "try again? [y/N] "
            answer = input(f"  {choices}").strip().lower()
            if allow_skip and answer in ("s", "skip"):
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
        rings.setdefault(parcels.to_row(feature)["id"], parcels.rings_of(feature))
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


def _flag_query(source, extent):
    """One query, built from the box around the corridor's parcels."""
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


def _flag_id(source, feature):
    """The feature's own identifier, read whatever case the service answered in."""
    fields = FLAG_FIELDS.get(source.name, {})
    found = flags_mod.attribute(feature.get("attributes"), fields.get("id", "OBJECTID"))
    return str(found) if found is not None else "(unidentified)"


def _screen_flags(fetcher, args, pings, blocked_flags, parcel_features, plane):
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
        if source.name in blocked_flags:
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
            metadata, _ = _run_stage(
                f"{flag_type} field list",
                lambda s=source: fetcher.layer_metadata(s),
                args.yes,
                allow_skip=True,
            )
            checks.confirm_fields(source, metadata)
            features, records = _run_stage(
                flag_type,
                lambda s=source: fetcher.query_all(
                    s, _flag_query(s, extent), readable=f"flag-{flag_type}"
                ),
                args.yes,
                allow_skip=True,
            )
        except (ServiceDown, ServiceError, Skipped, checks.FieldListError) as exc:
            # Not the spine. This costs one flag type and nothing else.
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


def _citations(table, screened_for):
    """The lead time and its citation for every type this run screened for.

    Carried inside the output file so that somebody holding only the JSON can
    check a number against its source without this repo beside them. A lead
    time is worth exactly what its citation is worth.
    """
    wanted = set(screened_for)
    return {
        key: {
            "label": entry.label,
            "lead_time_days": entry.days,
            "lead_time_days_low": entry.days_low,
            "confirmed": entry.confirmed,
            "statutory": entry.statutory,
            "source": entry.source,
            "url": entry.url,
            "verified_on": str(entry.verified_on) if entry.verified_on else None,
            "not_found": entry.not_found,
        }
        for key, entry in table.items()
        if key in wanted
    }


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
            f"    longest wait      {top['max_lead_time_days']} days on {top['id']} "
            f"-- {top['lead_time_driver']}"
        )
    unconfirmed = sorted({t for r in rows for t in r["lead_time_not_found"]})
    if unconfirmed:
        _say(f"    no number found   {', '.join(unconfirmed)} -- see lead_time_not_found on the rows")
    _say(f"    screened for      {', '.join(screened_for) or 'nothing'}")
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
    # A blocked flag service costs its own flag type. A blocked spine service
    # costs the run. The split is the whole reason the two lists are separate.
    spine_blocked = [name for name in blocked if any(s.name == name for s in SPINE_SOURCES)]
    blocked_flags = {name for name in blocked if name not in spine_blocked}

    if spine_blocked:
        _say()
        _say(f"  {', '.join(spine_blocked)} is not answering today. Nothing was fetched.")
        _say("  Try again, or use --mode cache-only if this corridor was captured before.")
        status = "incomplete"
        stopped_at = spine_blocked[0]
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
                fetcher, args, pings, blocked_flags, parcel_features, plane
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
            )
            screened_for = sorted(flag_type for _, flag_type, _ in found)
            _record_counts(services, found, counts)
            _report_flags(rows, corridor_flags, counts, screened_for)
            if len(screened_for) < len(FLAG_SOURCES):
                # Something was not checked. The output has to say so, and the
                # missing type stays off every parcel's `screened_for`.
                status = "incomplete"

        except EXPECTED_FAILURES as exc:
            # A stopped run still writes its output, marked incomplete, naming
            # what stopped it. The responses already fetched are already cached,
            # so a re-run in cache-first mode resumes almost free.
            _say()
            _say(f"  run stopped: {exc}")
            status = "incomplete"
            stopped_at = getattr(exc, "service", type(exc).__name__)
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
        lead_time_table=_citations(table, screened_for),
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
