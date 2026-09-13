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
