"""Widening the centerline into a ribbon.

The buffer is done by a service, not by us. ArcGIS publishes a geometry
operation that takes a line, a distance and a unit and returns the polygon, so
no geometry library has to be installed for the one job that would otherwise
need one.

The polygon is fetched once and cached. The parcel query does its own
buffering from the same line and distance -- that is how the specification has
it, in section 4 -- but there still has to be a real corridor shape to draw, to
stamp into the output, and to hand to somebody later.

One risk, stated openly. If a server ignores the distance we get a whole county
back and it looks fine. That is what the sanity checks in ``checks.py`` are for.
"""

import json

from . import geometry

# The international foot, EPSG unit code 9002, named explicitly rather than
# left to anybody's default.
#
# It is worth saying why this is not the US survey foot, because TxDOT's Survey
# Manual does require US survey feet in deliverables (Ch. 3, Control Points:
# https://www.txdot.gov/manuals/row/ess/index.html). Screening is not a
# deliverable, and the parcel query and the buffer have to agree on one foot or
# the drawn corridor is not the ribbon the parcels came from. The parcel query
# endpoint accepts only `esriSRUnit_Foot`; it rejects `esriSRUnit_SurveyFoot`
# outright. So the international foot is the only unit both endpoints share.
#
# At a 300 ft half-width the two feet differ by about six ten-thousandths of a
# foot, which changes nothing a screening run decides.
#
# **The trap, recorded.** Passing the numeric code `9003` to the parcel query's
# `units` parameter does not error. It answered with 2,132 parcels where
# `esriSRUnit_Foot` answered with 658 -- the same ratio as feet to meters, so
# the server appears to read an unrecognized unit as meters and say nothing.
# That is the third example in this repo of a service returning a plausible
# wrong answer rather than an error. Tested live, 2026-09-12.
INTERNATIONAL_FOOT = 9002

# What the parcel query must be asked for, so it buffers in the same foot.
QUERY_FOOT_UNITS = "esriSRUnit_Foot"


class Corridor:
    """The ribbon, as a polygon."""

    def __init__(self, rings, half_width_ft, cache_key):
        self.rings = rings
        self.half_width_ft = half_width_ft
        self.cache_key = cache_key

    @property
    def area_sq_mi(self):
        return geometry.polygon_area_sq_miles(self.rings)

    @property
    def bbox(self):
        return geometry.bbox_of(self.rings)

    def to_esri_polygon(self):
        return {"rings": self.rings, "spatialReference": {"wkid": 4326}}

    def describe(self):
        return {
            "half_width_ft": self.half_width_ft,
            "area_sq_mi": round(self.area_sq_mi, 4),
            "bbox": [round(v, 6) for v in self.bbox],
            "ring_count": len(self.rings),
            "polygon_cache_key": self.cache_key,
        }


class CorridorError(Exception):
    """The buffer came back as something that is not a corridor."""


def build(fetcher, source, alignment, half_width_ft):
    """Ask the geometry service for the corridor polygon, once."""
    params = {
        "geometries": json.dumps(
            {"geometryType": "esriGeometryPolyline", "geometries": [alignment.to_esri_polyline()]}
        ),
        "inSR": 4326,
        "outSR": 4326,
        "bufferSR": 4326,
        "distances": half_width_ft,
        "unit": INTERNATIONAL_FOOT,
        "unionResults": "true",
        "geodesic": "true",
        "f": "json",
    }
    data, record = fetcher.get_json(
        source.name,
        f"corridor-buffer-{half_width_ft:g}ft",
        f"{source.base_url}/buffer",
        params,
        method="POST",
        count_records=lambda d: len(d.get("geometries", [])),
    )
    geometries = data.get("geometries") or []
    if not geometries or not geometries[0].get("rings"):
        raise CorridorError(
            "the geometry service returned no corridor polygon for this alignment"
        )
    return Corridor(geometries[0]["rings"], half_width_ft, record["cache_key"]), record
