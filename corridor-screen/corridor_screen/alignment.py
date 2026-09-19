"""The centerline of the corridor, and where it starts and stops.

This first pass reads one of the five input forms in the specification: a route
name and two DFO numbers. DFO is Distance From Origin, TxDOT's measure along a
route, and it is the thing a surveyor already has when they describe a job as
"SH16 from Loop 410 to Old Bandera Rd".

TxDOT publishes the route geometry with M values attached, and those M values
are the DFO. So the limits are not guessed at from coordinates -- the route is
cut at the two numbers given, on TxDOT's own measure.

The other four input forms -- GeoJSON, KML, KMZ and shapefile -- are specified
in ``docs/corridor-screen/spec.md`` section 3 and are not built yet.
"""

from . import geometry

# How far apart two vertices may be and still count as the same run. Well under
# a foot at this latitude, so it only ever catches a genuine jump.
JOIN_TOLERANCE_DEG = 1e-9


def _interpolate(a, b, measure):
    """The point on segment a-b at a given measure."""
    m1, m2 = a[2], b[2]
    if m2 == m1:
        return [a[0], a[1], measure]
    t = (measure - m1) / (m2 - m1)
    return [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), measure]


def _same_point(a, b):
    return abs(a[0] - b[0]) < JOIN_TOLERANCE_DEG and abs(a[1] - b[1]) < JOIN_TOLERANCE_DEG


# How close two measures must be, in miles, to count as the same point on the
# route. 1e-6 miles is about six thousandths of a foot -- far tighter than
# anything TxDOT publishes a DFO to, and far looser than float noise.
JOIN_TOLERANCE_MI = 1e-6


def _join_touching(runs):
    """Runs that meet end to end are one run. Runs with a gap are not.

    **This is the difference between counting records and counting road.**
    ``TxDOT_Roadways`` answered a corridor with a single record, so the two
    numbers were the same and nothing had to choose between them. The layer that
    replaced it under
    [#180](https://github.com/RickSmith/survey-recon/issues/180) cuts the same
    road into inventory segments -- forty of them on SH16 -- that touch end to
    end. Counted as records, one continuous corridor reads as forty breaks in
    the road, and that number is printed on the wrong-file check, which is the
    first screen anybody reads.

    ``feature_count`` still says how many records answered. ``run_count`` says
    how many separate stretches of centerline they describe. They are different
    questions and now they have different answers.

    **A real gap is never closed.** TxDOT publishes ``SH0016-KG`` in seven
    stretches that do not join, because a route can leave the state highway
    system and come back. Joining across one of those would invent centerline
    TxDOT never published, which is the rule ``clip_path_by_measure`` already
    states and this function keeps.

    ``runs`` must already be ascending and sorted by starting measure.
    """
    joined = []
    for run in runs:
        previous = joined[-1] if joined else None
        if previous is not None and abs(run[0][2] - previous[-1][2]) <= JOIN_TOLERANCE_MI:
            # The last vertex of one segment and the first of the next are the
            # same point on the ground. Keeping both would put a zero-length
            # step in the middle of a run.
            previous.extend(run[1:] if _same_point(previous[-1], run[0]) else run)
        else:
            joined.append(list(run))
    return joined


def clip_path_by_measure(path, lo, hi):
    """Cut one run of vertices down to the measures between lo and hi.

    Returns a list of runs, because a route can leave the window and come back
    into it. Runs are never joined across a gap -- a corridor with a break in
    it is legitimate, and closing the gap would invent centerline that TxDOT
    never published.
    """
    if hi < lo:
        lo, hi = hi, lo
    runs = []
    current = []

    def close():
        if len(current) >= 2:
            runs.append(list(current))

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        seg_lo, seg_hi = sorted((a[2], b[2]))
        window_lo = max(seg_lo, lo)
        window_hi = min(seg_hi, hi)
        if window_hi < window_lo:
            close()
            current = []
            continue
        first, last = (window_lo, window_hi) if a[2] <= b[2] else (window_hi, window_lo)
        start_point = _interpolate(a, b, first)
        end_point = _interpolate(a, b, last)
        if not current:
            current = [start_point]
        elif not _same_point(current[-1], start_point):
            close()
            current = [start_point]
        if not _same_point(current[-1], end_point):
            current.append(end_point)
    close()
    return runs


def _ascending(run):
    """Point a run the way DFO increases, so both ends can be named."""
    return run if run[0][2] <= run[-1][2] else list(reversed(run))


class Alignment:
    """One corridor centerline, ready to be buffered."""

    def __init__(self, paths, source_kind, source_path, feature_count, crs_in, dropped_z=False, dropped_m=False):
        self.paths = paths
        self.source_kind = source_kind
        self.source_path = source_path
        self.feature_count = feature_count
        self.crs_in = crs_in
        self.dropped_z = dropped_z
        self.dropped_m = dropped_m

    @property
    def flat_paths(self):
        """The same runs with the measure dropped, which is what a service wants."""
        return [[[pt[0], pt[1]] for pt in run] for run in self.paths]

    @property
    def length_mi(self):
        return geometry.paths_length_miles(self.flat_paths)

    @property
    def start(self):
        return self.paths[0][0][:2]

    @property
    def end(self):
        return self.paths[-1][-1][:2]

    @property
    def bbox(self):
        return geometry.bbox_of(self.flat_paths)

    def to_esri_polyline(self):
        return {"paths": self.flat_paths, "spatialReference": {"wkid": 4326}}

    def describe(self):
        """The alignment block of the output file."""
        return {
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "feature_count": self.feature_count,
            "run_count": len(self.paths),
            "length_mi": round(self.length_mi, 3),
            "start": [round(v, 6) for v in self.start],
            "end": [round(v, 6) for v in self.end],
            "bbox": [round(v, 6) for v in self.bbox],
            "crs_in": self.crs_in,
            "dropped_z": self.dropped_z,
            "dropped_m": self.dropped_m,
        }


class AlignmentError(Exception):
    """The alignment could not be read, so nothing after it is worth doing."""


def from_route_features(features, route, begin_dfo, end_dfo):
    """Build an alignment from TxDOT route segments cut at two DFO values.

    Every returned segment is cut to the window and the surviving runs are put
    in DFO order, so the alignment starts at the lower of the two numbers given
    however the service happened to return its records.
    """
    lo, hi = sorted((float(begin_dfo), float(end_dfo)))
    if lo == hi:
        raise AlignmentError("the two DFO limits are the same, so there is no corridor between them")

    runs = []
    used_features = 0
    for feature in features:
        paths = (feature.get("geometry") or {}).get("paths") or []
        clipped = []
        for path in paths:
            if path and len(path[0]) < 3:
                raise AlignmentError(
                    "the route geometry came back without M values, so it cannot be cut by DFO"
                )
            clipped.extend(clip_path_by_measure(path, lo, hi))
        if clipped:
            used_features += 1
            runs.extend(clipped)

    if not runs:
        raise AlignmentError(
            f"no part of {route} lies between DFO {lo} and DFO {hi}; "
            f"check the route name and the two limits"
        )

    runs = [_ascending(run) for run in runs]
    runs.sort(key=lambda run: run[0][2])
    runs = _join_touching(runs)
    return Alignment(
        paths=runs,
        source_kind="route-dfo",
        source_path=f"{route} DFO {lo} to {hi}",
        feature_count=used_features,
        crs_in="EPSG:4326, requested from the service",
        dropped_z=False,
        dropped_m=True,
    )
