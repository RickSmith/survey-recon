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

from . import __version__, checks, corridor as corridor_mod, output, parcels
from .alignment import AlignmentError, from_route_features
from .arcgis import MODES, Fetcher, ServiceDown, ServiceError
from .cache import Cache, slug
from .geometry import LocalPlane
from .sources import GEOMETRY, PARCELS, ROADWAYS

DEFAULT_HALF_WIDTH_FT = 300
DEFAULT_ADJACENT_FT = 100

# Pinged in this order, and skipped in this order if the run never reaches them.
SOURCES = (ROADWAYS, GEOMETRY, PARCELS)

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


def _run_stage(label, attempt, unattended):
    """Run one stage. If the service is dead, a person decides -- if one is there.

    Three automatic retries have already happened inside the fetcher by the
    time this sees anything. Section 7 of the specification: then ask, and if
    nobody is at the keyboard exit rather than wait, because a tool that hangs
    forever in an unattended run is a broken tool.

    Skipping is not offered here. Every stage in this first pass is the spine --
    skipping the route leaves no alignment to buffer, and skipping the buffer
    leaves no corridor to find parcels in. So the two honest answers are try
    again or stop.
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
            if input("  try again? [y/N] ").strip().lower() not in ("y", "yes"):
                raise


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
    status = "complete"
    stopped_at = None

    # 1 -- reachability, in seconds, before any real work
    pings = {}
    for source in SOURCES:
        pings[source.name] = fetcher.ping(source)
        result = pings[source.name]
        _say(f"  ping  {source.name:<18} {result['ping']:<8} {result['ms']} ms  {result['detail']}")
    blocked = [name for name, result in pings.items() if result["ping"] == "blocked"]

    if blocked:
        _say()
        _say(f"  {', '.join(blocked)} is not answering today. Nothing was fetched.")
        _say("  Try again, or use --mode cache-only if this corridor was captured before.")
        status = "incomplete"
        stopped_at = blocked[0]
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
