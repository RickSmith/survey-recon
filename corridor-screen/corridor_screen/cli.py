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
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__, checks, corridor as corridor_mod, output, parcels
from .alignment import AlignmentError, from_route_features
from .arcgis import MODES, Fetcher, ServiceDown, ServiceError
from .cache import Cache
from .geometry import grow_bbox, point_in_bbox
from .sources import GEOMETRY, PARCELS, ROADWAYS

DEFAULT_HALF_WIDTH_FT = 300
DEFAULT_ADJACENT_FT = 100


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
            "How far each side of the centerline counts as inside the corridor, in US survey "
            f"feet. Stated, never derived. Default {DEFAULT_HALF_WIDTH_FT}."
        ),
    )
    parser.add_argument("--mode", choices=MODES, default="cache-first", help="Whether the run may reach the network")
    parser.add_argument("--out", required=True, help="Where the output file and the cache are written")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Do not ask about a dead service; stop the run instead. Use for unattended runs.",
    )
    return parser.parse_args(argv)


def _slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", str(text)).strip("-").lower()


def _say(message=""):
    print(message, flush=True)


def _report_wrong_file_check(alignment, corridor):
    """The cheapest protection in the whole tool.

    A misread route does not look like a subtle error. It looks like a
    four-thousand-mile corridor on line one.
    """
    _say()
    _say("  Wrong-file check -- read these three numbers before anything else")
    _say(f"    corridor length   {alignment.length_mi:.2f} miles")
    _say(f"    starts at         {alignment.start[1]:.6f}, {alignment.start[0]:.6f}")
    _say(f"    ends at           {alignment.end[1]:.6f}, {alignment.end[0]:.6f}")
    _say(f"    separate runs     {len(alignment.paths)}")
    if corridor is not None:
        _say(f"    corridor area     {corridor.area_sq_mi:.2f} square miles")
    _say(f"    check the map     {output.map_link(alignment.bbox)}")
    _say()


def _with_a_person_asked(label, attempt, unattended):
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
    run_id = f"texas-bexar-{_slug(args.route)}-{started_at.strftime('%Y%m%dT%H%M%S')}"
    out_dir = Path(args.out)
    cache = Cache(out_dir / "cache")
    fetcher = Fetcher(cache, mode=args.mode)

    _say(f"corridor-screen {__version__}  run {run_id}  mode {args.mode}")

    # 1 -- reachability, in seconds, before any real work
    pings = {}
    for source in (ROADWAYS, GEOMETRY, PARCELS):
        pings[source.name] = fetcher.ping(source)
        result = pings[source.name]
        _say(f"  ping  {source.name:<18} {result['ping']:<8} {result['ms']} ms  {result['detail']}")
    blocked = [name for name, r in pings.items() if r["ping"] == "blocked"]
    if blocked:
        _say()
        _say(f"  {', '.join(blocked)} is not answering today. Nothing has been fetched.")
        _say("  Try again, or run with --mode cache-only if this corridor was captured before.")
        return 2

    services = []
    warnings = []
    alignment = None
    corridor = None

    try:
        # 2 -- the wrong layer answers without complaining, so check first
        for source in (ROADWAYS, PARCELS):
            metadata, _ = _with_a_person_asked(
                "field list", lambda s=source: fetcher.layer_metadata(s), args.yes
            )
            checks.confirm_fields(source, metadata)
        _say("  field lists confirmed on every layer")

        # 3 -- the alignment
        features, road_records = _with_a_person_asked("route", lambda: fetcher.query_all(
            ROADWAYS,
            {
                "where": f"RTE_NM='{args.route}' AND BEGIN_DFO<={args.end_dfo} AND END_DFO>={args.begin_dfo}",
                "outFields": "RTE_NM,BEGIN_DFO,END_DFO",
                "returnGeometry": "true",
                "returnM": "true",
                "outSR": 4326,
                "f": "json",
            },
            readable=f"route-{_slug(args.route)}",
        ), args.yes)
        alignment = from_route_features(features, args.route, args.begin_dfo, args.end_dfo)
        services.append(
            output.service_entry(ROADWAYS, pings[ROADWAYS.name], "ok", road_records, len(features))
        )

        # 4 -- the corridor polygon, fetched once and cached
        corridor, buffer_record = _with_a_person_asked(
            "buffer", lambda: corridor_mod.build(fetcher, GEOMETRY, alignment, args.half_width), args.yes
        )
        services.append(
            output.service_entry(GEOMETRY, pings[GEOMETRY.name], "ok", [buffer_record], len(corridor.rings))
        )
        _report_wrong_file_check(alignment, corridor)

        # 5 -- parcels, the spine everything joins to
        parcel_features, parcel_records = _with_a_person_asked("parcels", lambda: fetcher.query_all(
            PARCELS,
            {
                "geometry": _polyline_json(alignment),
                "geometryType": "esriGeometryPolyline",
                "inSR": 4326,
                "outSR": 4326,
                "spatialRel": "esriSpatialRelIntersects",
                "distance": args.half_width,
                "units": "esriSRUnit_Foot",
                "outFields": ",".join(PARCELS.required_fields),
                "returnGeometry": "false",
                "returnCentroid": "true",
                "f": "json",
            },
            readable="parcels",
        ), args.yes)
        rows = parcels.to_rows(parcel_features)

        centroids = [c for c in (parcels.centroid_of(f) for f in parcel_features) if c]
        parcel_warnings = checks.collect(
            checks.check_paging_cap(PARCELS.name, len(parcel_features)),
            checks.check_parcel_density(PARCELS.name, len(parcel_features), corridor.area_sq_mi),
            checks.check_centroids_near_corridor(
                PARCELS.name, centroids, corridor.bbox, grow_bbox, point_in_bbox
            ),
            checks.check_impossible_acres(PARCELS.name, rows),
        )
        warnings.extend(parcel_warnings)
        services.append(
            output.service_entry(
                PARCELS, pings[PARCELS.name], "ok", parcel_records, len(parcel_features), parcel_warnings
            )
        )

        status, stopped_at = "complete", None

    except (ServiceDown, ServiceError, AlignmentError, corridor_mod.CorridorError) as exc:
        # A stopped run still writes its output, marked incomplete, naming what
        # stopped it. The responses already fetched are already cached, so a
        # re-run in cache-first mode resumes almost free.
        _say()
        _say(f"  run stopped: {exc}")
        status = "incomplete"
        stopped_at = getattr(exc, "service", type(exc).__name__)
        rows = []
        for source in (ROADWAYS, GEOMETRY, PARCELS):
            if not any(s["name"] == source.name for s in services):
                services.append(output.skipped_service(source, "the run stopped before this service was asked"))

    document = output.build(
        run_id=run_id,
        started_at=started_at,
        mode=args.mode,
        half_width_ft=args.half_width,
        adjacent_distance_ft=DEFAULT_ADJACENT_FT,
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
    for w in warnings:
        _say(f"    - {w['check']}: {w['detail']}")
    _say(f"  written     {written}")
    _say(f"  cache index {index}")
    return 0 if status == "complete" else 1


def _polyline_json(alignment):
    import json

    return json.dumps(alignment.to_esri_polyline())


def main(argv=None):
    args = parse_args(argv)
    try:
        return run(args)
    except checks.FieldListError as exc:
        _say()
        _say(f"  stopped before any query: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
