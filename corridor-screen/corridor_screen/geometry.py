"""Plane and sphere arithmetic, with nothing installed.

Everything here works on longitude/latitude pairs in WGS 84, because that is
what every service in this tool is asked to return. A point is ``[lon, lat]``,
which is the order ArcGIS uses -- easting before northing, the opposite of how
a latitude/longitude is spoken aloud. Getting that backwards puts a Bexar
County corridor in the Indian Ocean, so it is stated once here and relied on
everywhere else.

None of this is survey-grade and none of it is meant to be. Screening asks
"is this parcel in the ribbon, roughly how long is this corridor" and a
sub-foot answer would cost a projection library the tool is not allowed to
have. The TxDOT Survey Manual rule against datum transformations is in
``docs/corridor-screen/spec.md`` section 3.2; the short version is that a tool
which quietly reprojects teaches the wrong habit.
"""

import math

EARTH_RADIUS_MI = 3958.7613
SQ_MI_PER_ACRE = 1.0 / 640.0

# One home. Every distance in this tool is measured in miles, and every stated
# distance a person types is in feet, so the conversion belongs beside the
# arithmetic rather than copied into each module that needs it.
FEET_PER_MILE = 5280.0


def haversine_miles(a, b):
    """Great-circle distance between two ``[lon, lat]`` points, in miles."""
    lon1, lat1 = math.radians(a[0]), math.radians(a[1])
    lon2, lat2 = math.radians(b[0]), math.radians(b[1])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MI * math.asin(min(1.0, math.sqrt(h)))


def path_length_miles(path):
    """Length along one run of vertices, in miles."""
    return sum(haversine_miles(path[i], path[i + 1]) for i in range(len(path) - 1))


def paths_length_miles(paths):
    """Length of every run added together.

    Gaps between runs are not measured. A corridor with a break in it is
    legitimate -- see spec section 3.3 -- so the gap is neither closed nor
    counted.
    """
    return sum(path_length_miles(p) for p in paths)


def bbox_of(paths):
    """Corner coordinates around every vertex given.

    Returned as ``[min_lon, min_lat, max_lon, max_lat]``, which is the order
    ArcGIS and GeoJSON both use for a bounding box.
    """
    pts = [pt for path in paths for pt in path]
    if not pts:
        raise ValueError("no vertices to take a bounding box from")
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    return [min(lons), min(lats), max(lons), max(lats)]


class LocalPlane:
    """Longitude and latitude flattened onto a plane measured in miles.

    Everything in this tool happens inside one corridor a few miles long, so a
    single flat plane fitted at the corridor's own latitude is accurate to far
    better than anything a screening run decides. Fitting it once and reusing it
    also means every distance in a run is measured the same way.

    This is not a projection in the surveying sense and must never be used as
    one. It measures how far apart two things are. It does not produce a
    coordinate anybody should write down.
    """

    MILES_PER_DEGREE_LAT = 69.055

    def __init__(self, latitude_deg):
        self.scale_lon = 69.172 * math.cos(math.radians(latitude_deg))
        self.scale_lat = self.MILES_PER_DEGREE_LAT

    def xy(self, point):
        return point[0] * self.scale_lon, point[1] * self.scale_lat


def _point_to_segment_miles(plane, point, start, end):
    """Shortest distance from a point to a line segment, in miles."""
    px, py = plane.xy(point)
    ax, ay = plane.xy(start)
    bx, by = plane.xy(end)
    dx, dy = bx - ax, by - ay
    length_squared = dx * dx + dy * dy
    if length_squared == 0.0:
        return math.hypot(px - ax, py - ay)
    # How far along the segment the nearest point sits, clamped to its ends.
    t = ((px - ax) * dx + (py - ay) * dy) / length_squared
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _segments(paths):
    for path in paths:
        for i in range(len(path) - 1):
            yield path[i], path[i + 1]


def _bbox_of_points(points):
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return [min(lons), min(lats), max(lons), max(lats)]


def boxes_overlap(a, b):
    """True when two bounding boxes touch or overlap.

    Public because two other modules need it to skip comparisons that cannot
    possibly be close. A cheap first pass before any real measuring.
    """
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _side_of(a, b, c):
    """Which side of the line a-b the point c falls on, by sign."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(p1, p2, p3, p4):
    """True when two segments properly cross each other.

    Done on the raw longitude and latitude rather than on the local plane,
    because scaling the axes cannot change whether two lines cross.

    Segments that merely touch end to end, or lie along each other, fall
    through to the distance tests, which measure them as zero apart anyway.
    """
    d1 = _side_of(p3, p4, p1)
    d2 = _side_of(p3, p4, p2)
    d3 = _side_of(p1, p2, p3)
    d4 = _side_of(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def shape_is_within_miles(rings, paths, limit_miles, plane):
    """True when any part of a shape comes within a distance of a line.

    "Any part" means what it says, and there are three ways for it to be true.
    The line can run through the shape. The line can cross one of its edges.
    Or the two can pass close without meeting.

    All three are tested because each one alone lets a real parcel through. A
    check on corners only would call a big ranch far from the road while its
    fence line ran along the pavement. A check on distance only would miss a
    tract the highway runs straight down the middle of, because every corner of
    it is half a mile from the centerline.

    Stops as soon as anything is close enough, so a parcel sitting on the road
    costs one comparison.
    """
    if not rings or not paths:
        return True
    shape_points = [pt for ring in rings for pt in ring]
    if not shape_points:
        return True

    reach = grow_bbox(_bbox_of_points(shape_points), limit_miles)
    near_segments = [
        (start, end)
        for start, end in _segments(paths)
        if boxes_overlap(reach, _bbox_of_points([start, end]))
    ]
    if not near_segments:
        return False

    # The line running through the shape rather than near its edges.
    for start, end in near_segments:
        if point_in_rings(start, rings) or point_in_rings(end, rings):
            return True

    for ring in rings:
        if len(ring) < 2:
            continue
        for i in range(len(ring)):
            edge_start, edge_end = ring[i], ring[(i + 1) % len(ring)]
            for start, end in near_segments:
                if _segments_cross(edge_start, edge_end, start, end):
                    return True
                if (
                    _point_to_segment_miles(plane, edge_start, start, end) <= limit_miles
                    or _point_to_segment_miles(plane, start, edge_start, edge_end) <= limit_miles
                    or _point_to_segment_miles(plane, end, edge_start, edge_end) <= limit_miles
                ):
                    return True
    return False


def grow_bbox(bbox, miles):
    """The same corner coordinates, pushed out by a stated distance."""
    min_lon, min_lat, max_lon, max_lat = bbox
    mid_lat = math.radians((min_lat + max_lat) / 2)
    pad_lat = miles / 69.055
    pad_lon = miles / max(1e-6, 69.172 * math.cos(mid_lat))
    return [min_lon - pad_lon, min_lat - pad_lat, max_lon + pad_lon, max_lat + pad_lat]


def point_in_bbox(point, bbox):
    """True when a point falls within the corner coordinates given."""
    return bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]


def point_in_ring(point, ring):
    """True when the point falls inside one closed run of vertices.

    Ray casting: count how many times a line drawn east from the point crosses
    the ring. Odd means inside. A point exactly on the boundary may land either
    way, which is acceptable here -- this is used as a sanity check, not to
    decide whether a crew can stand somewhere.
    """
    x, y = point[0], point[1]
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        if (y1 > y) != (y2 > y):
            x_cross = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_cross:
                inside = not inside
    return inside


def point_in_rings(point, rings):
    """True when the point is inside an ArcGIS polygon.

    An ArcGIS polygon is a list of rings. Outer rings are wound clockwise and
    holes counter-clockwise, but rather than trust the winding we count: inside
    an odd number of rings means inside the polygon, which handles a hole
    without needing to know which ring is which.
    """
    hits = sum(1 for ring in rings if point_in_ring(point, ring))
    return hits % 2 == 1


def ring_area_sq_miles(ring):
    """Area of one closed run of vertices, in square miles.

    The ring is flattened onto a local plane first: longitude is squeezed by
    the cosine of the middle latitude, then the shoelace formula does the rest.
    Over a corridor a few miles across the error is far below anything that
    would change a decision here.
    """
    if len(ring) < 3:
        return 0.0
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    deg_lat_mi = 69.055
    deg_lon_mi = 69.172 * math.cos(lat0)
    xs = [p[0] * deg_lon_mi for p in ring]
    ys = [p[1] * deg_lat_mi for p in ring]
    total = 0.0
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        total += xs[i] * ys[j] - xs[j] * ys[i]
    return abs(total) / 2.0


def polygon_area_sq_miles(rings):
    """Area of an ArcGIS polygon, holes subtracted.

    Which ring is a hole is decided by containment, not by size. A ring that
    sits inside an odd number of other rings is a hole and comes off; a ring
    that sits inside none of them is a separate piece and goes on. A buffer
    around a corridor with a break in it comes back in two pieces, and calling
    the second piece a hole would report less area than the first piece alone.
    """
    total = 0.0
    real = [r for r in rings if len(r) >= 3]
    for i, ring in enumerate(real):
        depth = sum(1 for j, other in enumerate(real) if j != i and point_in_ring(ring[0], other))
        area = ring_area_sq_miles(ring)
        total += -area if depth % 2 else area
    return total


# -- How far apart two things are -------------------------------------------
#
# Everything a flag does rests on one question asked four ways: how far is this
# feature from this parcel? Zero means the feature is **on** the parcel. A small
# number means **adjacent**. A big number means it belongs to neither, and the
# feature is not this parcel's problem.
#
# Deciding `on` against `adjacent` from a measured distance, rather than from a
# separate inside/outside test, is deliberate. One number decides both, so the
# two answers cannot disagree with each other -- which is what happens when a
# containment test and a distance test are written separately and drift apart.
#
# Every one of these returns None when there is nothing to measure. None is not
# zero. Zero means touching, which is the opposite of the truth.


def _segment_to_segment_miles(plane, a1, a2, b1, b2):
    """Shortest distance between two line segments, in miles."""
    if _segments_cross(a1, a2, b1, b2):
        return 0.0
    return min(
        _point_to_segment_miles(plane, a1, b1, b2),
        _point_to_segment_miles(plane, a2, b1, b2),
        _point_to_segment_miles(plane, b1, a1, a2),
        _point_to_segment_miles(plane, b2, a1, a2),
    )


def _ring_edges(rings):
    for ring in rings:
        if len(ring) < 2:
            continue
        for i in range(len(ring)):
            yield ring[i], ring[(i + 1) % len(ring)]


def point_to_rings_miles(point, rings, plane):
    """How far a point sits from a polygon, in miles. Inside is zero.

    A point in a hole is outside the polygon, and is measured to the hole's
    edge. A well inside a doughnut is not on the doughnut.
    """
    if not rings or point is None:
        return None
    if point_in_rings(point, rings):
        return 0.0
    edges = list(_ring_edges(rings))
    if not edges:
        return None
    return min(_point_to_segment_miles(plane, point, start, end) for start, end in edges)


def point_to_paths_miles(point, paths, plane):
    """How far a point sits from a line, in miles.

    Measured square to the nearest segment, clamped to its ends -- otherwise a
    short line would measure as if it ran on forever.
    """
    if not paths or point is None:
        return None
    segments = list(_segments(paths))
    if not segments:
        return None
    return min(_point_to_segment_miles(plane, point, start, end) for start, end in segments)


def paths_to_rings_miles(paths, rings, plane):
    """How far a line sits from a polygon, in miles. Crossing or inside is zero.

    Two ways for the answer to be zero, and both are tested, because either one
    alone lets a real feature through. A vertex of the line can sit inside the
    polygon. Or the line can cross one of its edges without any vertex being
    inside at all -- which is the case a vertex-only check misses. A railroad
    drawn with one vertex either side of a city lot runs straight through the
    back yard while every vertex it has is somewhere else.
    """
    if not paths or not rings:
        return None
    segments = list(_segments(paths))
    edges = list(_ring_edges(rings))
    if not segments or not edges:
        return None
    for start, _end in segments:
        if point_in_rings(start, rings):
            return 0.0
    if segments and point_in_rings(segments[-1][1], rings):
        return 0.0
    best = None
    for start, end in segments:
        for edge_start, edge_end in edges:
            d = _segment_to_segment_miles(plane, start, end, edge_start, edge_end)
            if d == 0.0:
                return 0.0
            best = d if best is None else min(best, d)
    return best


def paths_to_paths_miles(a_paths, b_paths, plane):
    """How far one line sits from another, in miles. Crossing is zero."""
    if not a_paths or not b_paths:
        return None
    a_segments = list(_segments(a_paths))
    b_segments = list(_segments(b_paths))
    if not a_segments or not b_segments:
        return None
    best = None
    for a1, a2 in a_segments:
        for b1, b2 in b_segments:
            d = _segment_to_segment_miles(plane, a1, a2, b1, b2)
            if d == 0.0:
                return 0.0
            best = d if best is None else min(best, d)
    return best


def point_of(feature):
    """A returned feature's own point, or nothing at all.

    Services that answer with one point per record -- NGS marks, TxDOT control,
    the crew safety layers -- all need this same two-line read, and a record
    with no point on it has to come back as ``None`` rather than raising, so the
    caller can count it and say so out loud.

    It lives here rather than in any one of the three modules that read points,
    for the same reason ``arcgis.attribute`` lives where it does: all three read
    features the same way and none of them owns the shape.
    """
    geometry = feature.get("geometry") or {}
    lon = geometry.get("x")
    lat = geometry.get("y")
    if lon is None or lat is None:
        return None
    return [lon, lat]


def shape_of(geometry):
    """Which of the three shapes ArcGIS drew, and the shape itself.

    A service answers with a point, a line or a polygon, and each is drawn a
    different way in the JSON. Naming the three in one place means nothing
    downstream has to guess, and a fourth shape is an honest ``(None, None)``
    rather than a crash.
    """
    geometry = geometry or {}
    if "x" in geometry and "y" in geometry and geometry.get("x") is not None:
        return "point", [geometry["x"], geometry["y"]]
    if geometry.get("paths"):
        return "paths", geometry["paths"]
    if geometry.get("rings"):
        return "rings", geometry["rings"]
    return None, None


def shape_to_rings_miles(shape, rings, plane):
    """How far any of the three shapes sits from a parcel, in miles.

    One door, so that attaching a flag to a parcel does not have to know
    whether the flag is a school (a point), a railroad (a line) or something
    drawn as an area.
    """
    kind, value = shape
    if kind == "point":
        return point_to_rings_miles(value, rings, plane)
    if kind == "paths":
        return paths_to_rings_miles(value, rings, plane)
    if kind == "rings":
        # Measured by its outline. Two areas that overlap have edges that
        # cross, so the answer is zero without a separate overlap test.
        outline = [r for r in value if len(r) >= 2]
        if not outline:
            return None
        closed = [r + [r[0]] for r in outline]
        return paths_to_rings_miles(closed, rings, plane)
    return None


def shape_to_paths_miles(shape, paths, plane):
    """How far any of the three shapes sits from the centerline, in miles.

    Used by the sanity check, which asks the same question of a returned record
    that the query was asked: does any part of it come near the corridor.
    """
    kind, value = shape
    if kind == "point":
        return point_to_paths_miles(value, paths, plane)
    if kind == "paths":
        return paths_to_paths_miles(value, paths, plane)
    if kind == "rings":
        outline = [r for r in value if len(r) >= 2]
        if not outline:
            return None
        return paths_to_paths_miles([r + [r[0]] for r in outline], paths, plane)
    return None


def bbox_of_shape(shape):
    """Corner coordinates around any of the three shapes."""
    kind, value = shape
    if kind == "point":
        return [value[0], value[1], value[0], value[1]]
    if kind == "paths":
        return bbox_of(value)
    if kind == "rings":
        return bbox_of(value)
    return None
