"""The drawings of a screening run: three maps, a diagram, and a sheet.

Surveyors read drawings. Every job they have priced came with a sheet, and
until this file the SH16 job came with a JSON file and three pages of prose. A
reader who wanted to know where the corridor was, where the eleven missing
marks sat, or why the nearest hospital is two miles away and also eight, had to
build the map in their head.

This writes it down instead. Issue #154.

----

What is drawn, and from where
=============================

Nothing here is drawn from memory. Every shape is read from the committed
capture in the project folder -- ``screening.json`` and the cached service
responses beside it -- and every number on a drawing is a number the run
recorded. That is the same rule the bid memo and the crew-day build-up already
keep, and the tests read the numbers back out of the SVG to hold it.

``corridor-map.svg``
    The centerline, the 300-foot ribbon, every tract the run counted, the
    flagged tracts picked out and numbered, and the schools and cemetery that
    flagged them.

``control-map.svg``
    The same corridor with the published NGS marks, each labeled with its PID
    and its recorded condition, and the TxDOT monuments beside them.

``crew-safety-map.svg``
    The corridor with the nearest hospital, ambulance, fire station and police
    station, and a straight line from each to the nearer end of the corridor
    with the distance written on it.

``how-it-works.svg``
    A diagram of the tool: a centerline goes in, a ribbon is drawn, the public
    services are asked, one file comes out, three documents are written from
    it, and a licensed surveyor reads them.

``crew-day-sheet.svg``
    The crew-day build-up as a sheet: what went in, the lines with their rate
    handles, and the lines that have no total shown as having no total.

----

Why SVG, and why the standard library
=====================================

Specification section 9 settled the format for the parcel table and the reason
holds here: an SVG is a drawing stored as plain text. It stays sharp on a
projector at any size, it commits to git as a diff, and Python writes it with
nothing installed. ``CLAUDE.md`` is blunt that attendees need git, a GitHub
account and the Claude desktop app and nothing else, so there is no plotting
library in here and there will not be one.

The maps use the simplest projection that is honest at this scale: longitude
is scaled by the cosine of the corridor's middle latitude and both axes are
scaled the same, so a mile north is as long on the page as a mile east. Over
nine miles at 29.5 degrees north that is within a hair of State Plane, and it
is the same arithmetic ``geometry.LocalPlane`` uses for every distance the run
reports.

----

The copies under ``docs/``
==========================

The drawings are written into ``project-sh16/drawings/`` beside the other
produced artifacts. The site cannot see that folder, so ``--copy-to`` writes a
second copy where a page can show it, and a test holds each copy byte-for-byte
to its source. A re-run that changes a drawing fails the build until the copy
is refreshed, which is the honest state: the site never shows an older drawing
than the run it describes.
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from . import crew_day
from .alignment import from_route_features
from .cache import long_path, write_text
from .geometry import haversine_miles
from .sources import ROADWAYS

WIDTH = 1920
HEIGHT = 1080
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

NAMES = {
    "corridor": "corridor-map.svg",
    "control": "control-map.svg",
    "safety": "crew-safety-map.svg",
    "how": "how-it-works.svg",
    "sheet": "crew-day-sheet.svg",
    # The same three maps again, for a projector. Same data, same frame, no
    # side panel, and nothing on them under 32 pixels of type, because a room
    # reads a slide from forty feet and a page from fourteen inches.
    "corridor_slide": "corridor-slide.svg",
    "control_slide": "control-slide.svg",
    "safety_slide": "safety-slide.svg",
}

# The smallest type on a slide map. 32 px on a 1920-wide canvas is what the
# deck's own theme floors at (28 pt), and a map label is not exempt from it.
SLIDE_TYPE = 32

# The same ink the parcel table uses, plus the few colors a map needs. Teal is
# the site's own primary; amber is its accent and is what a flag reads as.
INK = "#111827"
MUTED = "#4b5563"
FAINT = "#9ca3af"
RULE = "#d1d5db"
PAPER = "#ffffff"
STRIPE = "#f9fafb"
TEAL = "#0f766e"
TEAL_FILL = "#ccfbf1"
PARCEL_FILL = "#f3f4f6"
PARCEL_LINE = "#d1d5db"
AMBER = "#b45309"
AMBER_FILL = "#fde68a"
RED = "#b91c1c"
GREEN = "#15803d"
VIOLET = "#6d28d9"

# What a value reads as when the run did not measure it. The crew-day sheet
# borrows the build-up's own word so the two never disagree.
UNMEASURED = crew_day.UNMEASURED

# The four kinds of place the crew safety block looks for, in the order a party
# chief asks about them, with the word a reader sees.
SAFETY_KINDS = (
    ("hospital", "Hospital"),
    ("ambulance", "Ambulance"),
    ("fire_ems", "Fire / EMS"),
    ("police", "Police"),
)

# How the alignment names itself in the run: the route, then the DFO pair.
# `alignment.source_path` is written by the tool, so the shape is known.
SOURCE_PATH = re.compile(r"^(?P<route>\S+) DFO (?P<begin>[\d.]+) to (?P<end>[\d.]+)$")


class DrawingError(Exception):
    """The run does not hold what a drawing needs, and the drawing says which."""


# ------------------------------------------------------------------ reading


def load(out_dir):
    """The run, and a way to open the cached responses it names."""
    out_dir = Path(out_dir)
    source = out_dir / "screening.json"
    with open(long_path(source), "r", encoding="utf-8") as handle:
        document = json.load(handle)
    return document, Capture(out_dir / "cache", document)


class Capture:
    """The cached service responses a run wrote, opened by the run's own names.

    A drawing never globs the cache folder. It asks for the file the run says
    it used, so a drawing of a run and the run itself cannot quietly read two
    different responses.
    """

    def __init__(self, cache_dir, document):
        self.cache_dir = Path(cache_dir)
        self.document = document

    def entry(self, cache_key):
        path = self.cache_dir / f"{cache_key}.json"
        # `long_path` on the check as well as the open: this repo's folder name
        # is long enough that `Path.is_file` says no to a file that is there.
        if not os.path.isfile(long_path(path)):
            raise DrawingError(
                f"the run names {cache_key} and it is not in {self.cache_dir}"
            )
        with open(long_path(path), "r", encoding="utf-8") as handle:
            return json.load(handle)

    def service(self, name):
        """The first cached response of a named service, or None if it has none."""
        for service in self.document.get("services", []):
            if service.get("name") == name and service.get("cache_files"):
                return self.entry(service["cache_files"][0])
        return None

    def features(self, name):
        answer = self.service(name)
        if not answer:
            return []
        return answer.get("features", [])


def centerline(document, capture):
    """The corridor's centerline, clipped to the run's own DFO pair."""
    alignment = document["alignment"]
    found = SOURCE_PATH.match(alignment.get("source_path") or "")
    if not found:
        raise DrawingError(
            "the alignment does not name a route and a DFO pair, so the "
            f"centerline cannot be clipped: {alignment.get('source_path')!r}"
        )
    # Named from ``sources.ROADWAYS`` rather than spelled here. The service
    # this reads was withdrawn by TxDOT on 2026-09-19 and the replacement has a
    # different name, so a second copy of that name in this file is a second
    # place to forget -- and it forgets quietly. A drawing that cannot find the
    # centerline does not draw a wrong map; it stops, which is right, but it
    # stops long after the run that could have said so.
    features = capture.features(ROADWAYS.name)
    if not features:
        raise DrawingError(f"the run has no cached {ROADWAYS.name} response")
    clipped = from_route_features(
        features,
        found.group("route"),
        float(found.group("begin")),
        float(found.group("end")),
    )
    return clipped.flat_paths


def ribbon(document, capture):
    """The corridor polygon the run buffered, as rings of [lon, lat]."""
    key = document["corridor"].get("polygon_cache_key")
    if not key:
        raise DrawingError("the run does not name its corridor polygon")
    answer = capture.entry(key)
    geometries = answer.get("geometries") or []
    if not geometries:
        raise DrawingError(f"{key} holds no geometry")
    return geometries[0].get("rings", [])


def parcel_rings(document, capture):
    """Every tract the run counted, with its rings, in the run's order.

    The service answered with more features than the run kept -- 530 against
    524 on SH16 -- because the run tests each one against the ribbon exactly.
    Only the ones the run kept are drawn. A drawing of 530 tracts under a
    title that says 524 would be the drawing lying.
    """
    by_id = {}
    for feature in capture.features("BCAD_Parcels"):
        attributes = feature.get("attributes", {})
        geometry = feature.get("geometry", {})
        for field in ("Geo_id", "PropID"):
            value = attributes.get(field)
            if value is not None:
                by_id.setdefault(str(value), geometry.get("rings", []))
    found = []
    for parcel in document.get("parcels", []):
        rings = by_id.get(str(parcel.get("id")))
        found.append((parcel, rings or []))
    return found


def flag_points(document, capture):
    """The places that put a flag on a tract, each once, with its position."""
    seen = {}
    for parcel in document.get("parcels", []):
        for flag in parcel.get("flags", []):
            key = (flag.get("source_service"), flag.get("source_feature_id"))
            if key in seen or not all(key):
                continue
            for feature in capture.features(key[0]):
                attributes = feature.get("attributes", {})
                if str(attributes.get("permanent_identifier")) == str(key[1]):
                    geometry = feature.get("geometry", {})
                    seen[key] = {
                        "type": flag.get("type"),
                        "name": flag.get("name"),
                        "lon": geometry.get("x"),
                        "lat": geometry.get("y"),
                    }
                    break
    return [p for p in seen.values() if p["lon"] is not None and p["lat"] is not None]


def flagged(document):
    """The flagged tracts, in the order the parcel table shows them."""
    rows = [p for p in document.get("parcels", []) if p.get("flags")]
    # Unmeasured waits first, for the parcel table's own reason: the tract
    # whose wait nobody has measured needs a phone call before the tract whose
    # wait is a known fourteen days.
    rows.sort(key=lambda p: (p.get("max_lead_time_days") is not None,
                             -(p.get("max_lead_time_days") or 0), p.get("id") or ""))
    return rows


def distinct_monuments(points):
    """TxDOT publishes a record per attachment, so one monument appears twice."""
    seen = {}
    for point in points:
        station = point.get("station")
        if station and station not in seen:
            seen[station] = point
    return list(seen.values())


# ------------------------------------------------------------------ the page


class Frame:
    """Longitude and latitude onto a box of pixels, a mile the same length either way.

    ``bbox`` is ``[west, south, east, north]``. ``box`` is ``(x, y, width,
    height)`` in pixels. The shape is centered in the box and scaled to fit
    with ``pad`` pixels clear on every side.
    """

    def __init__(self, bbox, box, pad=40):
        west, south, east, north = bbox
        x, y, width, height = box
        self.lon0 = (west + east) / 2
        self.lat0 = (south + north) / 2
        self.k = math.cos(math.radians(self.lat0))
        span_x = max((east - west) * self.k, 1e-9)
        span_y = max(north - south, 1e-9)
        self.scale = min((width - 2 * pad) / span_x, (height - 2 * pad) / span_y)
        self.cx = x + width / 2
        self.cy = y + height / 2
        self.box = box

    def xy(self, lon, lat):
        return (
            self.cx + (lon - self.lon0) * self.k * self.scale,
            self.cy - (lat - self.lat0) * self.scale,
        )

    def pixels_per_mile(self):
        """Measured, not assumed: a degree of latitude at this frame's middle."""
        one_degree = haversine_miles((self.lon0, self.lat0), (self.lon0, self.lat0 + 1))
        return self.scale / one_degree


def bbox_of_points(points):
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return [min(lons), min(lats), max(lons), max(lats)]


def grow(bbox, fraction):
    west, south, east, north = bbox
    dx = (east - west) * fraction
    dy = (north - south) * fraction
    return [west - dx, south - dy, east + dx, north + dy]


def union(*boxes):
    return [
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes),
    ]


def centroid(rings):
    points = [pt for ring in rings for pt in ring]
    if not points:
        return None
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


# ------------------------------------------------------------------ SVG pieces


def _n(value):
    return f"{value:.1f}"


def text(x, y, words, size=24, fill=INK, weight="400", anchor="start", extra=""):
    return (
        f'<text x="{_n(x)}" y="{_n(y)}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{escape(str(words))}</text>'
    )


def path_d(frame, ring, close=True):
    parts = []
    for i, pt in enumerate(ring):
        x, y = frame.xy(pt[0], pt[1])
        parts.append(f"{'M' if i == 0 else 'L'}{_n(x)},{_n(y)}")
    if close:
        parts.append("Z")
    return " ".join(parts)


def polygon(frame, rings, fill, stroke, width=1.0, cls=None, opacity=None):
    d = " ".join(path_d(frame, ring) for ring in rings if ring)
    cls = f' class="{cls}"' if cls else ""
    opacity = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"'
            f'{cls}{opacity} fill-rule="evenodd"/>')


def polyline(frame, paths, stroke, width=3.0, cls=None):
    d = " ".join(path_d(frame, run, close=False) for run in paths if run)
    cls = f' class="{cls}"' if cls else ""
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{cls}/>')


def wrap(words, width):
    """Lines of at most ``width`` characters, broken at spaces."""
    lines, line = [], ""
    for word in str(words).split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines


def header(title, subtitle):
    return [
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>',
        text(60, 78, title, size=44, weight="700"),
        text(60, 122, subtitle, size=26, fill=MUTED),
    ]


def footer(document, drawn_from):
    run = document.get("run", {})
    stamp = (f"Run {run.get('run_id', '?')}, finished {run.get('finished_at', '?')}. "
             f"Drawn from {drawn_from}. Nothing here was drawn by hand.")
    return [text(60, HEIGHT - 30, stamp, size=18, fill=FAINT)]


def scale_bar(frame, x, y, size=20):
    """One mile, measured on this frame, drawn where the eye expects it."""
    length = frame.pixels_per_mile()
    return [
        f'<line x1="{_n(x)}" y1="{_n(y)}" x2="{_n(x + length)}" y2="{_n(y)}" '
        f'stroke="{INK}" stroke-width="4"/>',
        f'<line x1="{_n(x)}" y1="{_n(y - 10)}" x2="{_n(x)}" y2="{_n(y + 10)}" stroke="{INK}" stroke-width="3"/>',
        f'<line x1="{_n(x + length)}" y1="{_n(y - 10)}" x2="{_n(x + length)}" y2="{_n(y + 10)}" '
        f'stroke="{INK}" stroke-width="3"/>',
        text(x + length / 2, y - 16, "1 mile", size=size, anchor="middle"),
    ]


def north_arrow(x, y, size=24):
    return [
        f'<path d="M{_n(x)},{_n(y - 40)} L{_n(x + 14)},{_n(y + 10)} L{_n(x)},{_n(y)} '
        f'L{_n(x - 14)},{_n(y + 10)} Z" fill="{INK}"/>',
        text(x, y + 38, "N", size=size, weight="700", anchor="middle"),
    ]


def marker_x(x, y, size=10, stroke=RED, cls=None):
    cls = f' class="{cls}"' if cls else ""
    return (f'<g{cls}><line x1="{_n(x - size)}" y1="{_n(y - size)}" x2="{_n(x + size)}" '
            f'y2="{_n(y + size)}" stroke="{stroke}" stroke-width="4"/>'
            f'<line x1="{_n(x - size)}" y1="{_n(y + size)}" x2="{_n(x + size)}" '
            f'y2="{_n(y - size)}" stroke="{stroke}" stroke-width="4"/></g>')


def marker_triangle(x, y, size=12, fill=GREEN, cls=None):
    cls = f' class="{cls}"' if cls else ""
    return (f'<path{cls} d="M{_n(x)},{_n(y - size)} L{_n(x + size)},{_n(y + size)} '
            f'L{_n(x - size)},{_n(y + size)} Z" fill="{fill}" stroke="{PAPER}" stroke-width="2"/>')


def marker_square(x, y, size=9, fill=AMBER, cls=None):
    cls = f' class="{cls}"' if cls else ""
    return (f'<rect{cls} x="{_n(x - size)}" y="{_n(y - size)}" width="{_n(2 * size)}" '
            f'height="{_n(2 * size)}" fill="{fill}" stroke="{PAPER}" stroke-width="2"/>')


def marker_cross(x, y, size=11, stroke=AMBER, cls=None):
    cls = f' class="{cls}"' if cls else ""
    return (f'<g{cls}><line x1="{_n(x)}" y1="{_n(y - size)}" x2="{_n(x)}" y2="{_n(y + size)}" '
            f'stroke="{stroke}" stroke-width="5"/><line x1="{_n(x - size * 0.7)}" '
            f'y1="{_n(y - size * 0.4)}" x2="{_n(x + size * 0.7)}" y2="{_n(y - size * 0.4)}" '
            f'stroke="{stroke}" stroke-width="5"/></g>')


def numbered_dot(x, y, number, fill=AMBER, cls=None, radius=16, size=20):
    cls = f' class="{cls}"' if cls else ""
    return (f'<g{cls}><circle cx="{_n(x)}" cy="{_n(y)}" r="{radius}" fill="{fill}" '
            f'stroke="{PAPER}" stroke-width="3"/>'
            + text(x, y + size * 0.35, number, size=size, fill=PAPER, weight="700",
                   anchor="middle")
            + "</g>")


def svg(body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>\n"
    )


def corridor_title(document):
    alignment = document.get("alignment", {})
    return (f"{alignment.get('source_path', 'the corridor')}, "
            f"{alignment.get('length_mi', '?')} miles")


def ends(document):
    """The two ends of the corridor, with the road each one is nearest.

    The corridor is the DFO pair. The road names are a label for it, and the
    label has been wrong once, so they are kept short and the DFO is on them.
    """
    alignment = document.get("alignment", {})
    found = SOURCE_PATH.match(alignment.get("source_path") or "")
    begin = found.group("begin") if found else "?"
    end = found.group("end") if found else "?"
    return (
        {"point": alignment.get("start"), "label": f"Old Bandera Rd end (DFO {begin})"},
        {"point": alignment.get("end"), "label": f"Loop 410 end (DFO {end})"},
    )


def base_map(frame, document, capture, parcels=True, faint=False):
    """The layers every map shares: tracts, the ribbon, the centerline."""
    body = []
    if parcels:
        for parcel, rings in parcel_rings(document, capture):
            if rings:
                body.append(polygon(
                    frame, rings, PARCEL_FILL if not faint else PAPER,
                    PARCEL_LINE if not faint else "#e5e7eb", width=1.0, cls="parcel",
                ))
    body.append(polygon(frame, ribbon(document, capture), TEAL_FILL, TEAL,
                        width=2.0, cls="ribbon", opacity=0.55))
    body.append(polyline(frame, centerline(document, capture), TEAL, width=3.5,
                         cls="centerline"))
    for end in ends(document):
        if end["point"]:
            x, y = frame.xy(*end["point"])
            body.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="9" fill="{TEAL}" '
                        f'stroke="{PAPER}" stroke-width="3"/>')
    return body


def end_labels(frame, document, above_first=True, size=22, clamp=False):
    """The two ends named. ``clamp`` keeps a label inside the frame's box when
    the end it names sits near an edge, which the slide maps need and the page
    maps do not."""
    body = []
    left, top, width, height = frame.box
    for i, end in enumerate(ends(document)):
        if not end["point"]:
            continue
        x, y = frame.xy(*end["point"])
        dy = -size if (i == 0) == above_first else size + 18
        anchor = "middle"
        if clamp:
            half = 0.52 * size * len(end["label"]) / 2
            if x - half < left:
                anchor, x = "start", left
            elif x + half > left + width:
                anchor, x = "end", left + width
        body.append(text(x, y + dy, end["label"], size=size, weight="600", anchor=anchor,
                         extra=' class="end-label"'))
    return body


# ------------------------------------------------------------------ the corridor map


def corridor_map(document, capture):
    box = (60, 150, 1000, 870)
    frame = Frame(document["corridor"]["bbox"], box, pad=70)
    rows = flagged(document)
    points = flag_points(document, capture)

    body = header(
        "Where the job is",
        f"{corridor_title(document)}. {len(document.get('parcels', []))} tracts touch "
        f"the {document['corridor'].get('half_width_ft', '?')}-foot ribbon; "
        f"{len(rows)} of them carry something that costs time.",
    )
    body += base_map(frame, document, capture)

    # The places that raised the flags, then the flagged tracts numbered so the
    # list on the right and the map agree.
    for place in points:
        x, y = frame.xy(place["lon"], place["lat"])
        if place["type"] == "cemetery":
            body.append(marker_cross(x, y, cls="place"))
        else:
            body.append(marker_square(x, y, cls="place"))
    rings_by_id = {p.get("id"): rings for p, rings in parcel_rings(document, capture)}
    for number, parcel in enumerate(rows, start=1):
        rings = rings_by_id.get(parcel.get("id")) or []
        if rings:
            body.append(polygon(frame, rings, AMBER_FILL, AMBER, width=2.0, cls="flagged"))
        at = centroid(rings)
        if at:
            x, y = frame.xy(*at)
            body.append(numbered_dot(x, y, number, cls="flag-number"))

    body += end_labels(frame, document)
    body += scale_bar(frame, box[0] + 40, box[1] + box[3] - 40)
    body += north_arrow(box[0] + box[2] - 50, box[1] + 60)

    # The right-hand panel: what the numbers are, and what the symbols mean.
    px = 1120
    y = 190
    body.append(text(px, y, "The flagged tracts", size=28, weight="700"))
    y += 44
    for number, parcel in enumerate(rows, start=1):
        what = ", ".join(
            f"{f.get('type')} ({f.get('relation')}"
            + (f", {f.get('distance_ft'):.0f} ft" if f.get("distance_ft") else "")
            + ")" for f in parcel.get("flags", [])
        )
        wait = parcel.get("max_lead_time_days")
        if wait is None:
            missing = ", ".join(sorted({f.get("type") for f in parcel.get("flags", [])
                                        if f.get("lead_time_days") is None}))
            wait_words = f"wait not found: {missing}"
            wait_fill = AMBER
        else:
            wait_words = f"{wait} {parcel.get('max_lead_time_basis') or 'days'}"
            wait_fill = INK
        body.append(numbered_dot(px + 16, y - 8, number))
        body.append(text(px + 48, y, f"{parcel.get('id')}  {parcel.get('owner', '')}",
                         size=21, weight="600", extra=' class="flag-row"'))
        body.append(text(px + 48, y + 26, f"{what}  ·  ", size=19, fill=MUTED))
        body.append(text(px + 48 + 0.52 * 19 * (len(what) + 5), y + 26, wait_words, size=19,
                         fill=wait_fill, weight="600"))
        y += 60

    y += 4
    body.append(f'<line x1="{px}" y1="{y}" x2="{WIDTH - 60}" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    y += 40
    body.append(text(px, y, "Reading the map", size=28, weight="700"))
    y += 38
    legend = [
        (f'<rect x="{px}" y="{y - 18}" width="34" height="22" fill="{TEAL_FILL}" '
         f'stroke="{TEAL}" stroke-width="2"/>',
         f"The ribbon: {document['corridor'].get('half_width_ft', '?')} ft either side of "
         "TxDOT's own centerline"),
        (f'<rect x="{px}" y="{y + 26}" width="34" height="22" fill="{PARCEL_FILL}" '
         f'stroke="{PARCEL_LINE}" stroke-width="2"/>',
         "A tract the ribbon touches, from the county appraisal district"),
        (f'<rect x="{px}" y="{y + 70}" width="34" height="22" fill="{AMBER_FILL}" '
         f'stroke="{AMBER}" stroke-width="2"/>',
         "A tract carrying something that costs time"),
        (marker_square(px + 17, y + 125),
         "A school, from the USGS structures layer"),
        (marker_cross(px + 17, y + 169),
         "A cemetery, from the same"),
    ]
    for i, (symbol, words) in enumerate(legend):
        body.append(symbol)
        body.append(text(px + 50, y + i * 44, words, size=20, fill=MUTED))
    y += len(legend) * 44 + 6
    for line in wrap(
        "No basemap and no street names, because the tool never had any. The map link in "
        "the bid memo shows the ground.", 72,
    ):
        body.append(text(px, y, line, size=18, fill=FAINT))
        y += 25

    body += footer(document, "the roadway, buffer, parcel and flag responses in the cache")
    return svg(body)


# ------------------------------------------------------------------ the control map


def control_map(document, capture):
    box = (60, 150, 1000, 870)
    frame = Frame(document["corridor"]["bbox"], box, pad=70)
    control = document.get("control", {})
    marks = list(control.get("ngs_marks", []))
    monuments = distinct_monuments(control.get("txdot_points", []))
    risk = control.get("recovery_risk", {})

    body = header(
        "What control is published here",
        f"{len(marks)} NGS marks in the ribbon, {risk.get('mark_not_found', '?')} of them "
        f"recorded MARK NOT FOUND. {len(monuments)} TxDOT monuments, all reported "
        f"{', '.join(sorted(control.get('txdot_control', {}).get('by_condition', {})) ) or '?'}.",
    )
    body += base_map(frame, document, capture, faint=True)

    for mark in marks:
        if mark.get("longitude") is None or mark.get("latitude") is None:
            continue
        x, y = frame.xy(mark["longitude"], mark["latitude"])
        body.append(marker_x(x, y, cls="mark"))
        body.append(text(x + 16, y - 10, mark.get("pid", "?"), size=19, fill=RED, weight="700"))
    for monument in monuments:
        if monument.get("longitude") is None or monument.get("latitude") is None:
            continue
        x, y = frame.xy(monument["longitude"], monument["latitude"])
        body.append(marker_triangle(x, y, cls="monument"))
        body.append(text(x + 18, y + 26, monument.get("station", "?"), size=19,
                         fill=GREEN, weight="700"))

    body += end_labels(frame, document)
    body += scale_bar(frame, box[0] + 40, box[1] + box[3] - 40)
    body += north_arrow(box[0] + box[2] - 50, box[1] + 60)

    px = 1120
    y = 190
    body.append(text(px, y, "The NGS marks, oldest report first", size=28, weight="700"))
    y += 40
    body.append(text(px, y, "PID", size=19, fill=MUTED, weight="700"))
    body.append(text(px + 100, y, "Name", size=19, fill=MUTED, weight="700"))
    body.append(text(px + 200, y, "Last looked for", size=19, fill=MUTED, weight="700"))
    body.append(text(px + 380, y, "Condition", size=19, fill=MUTED, weight="700"))
    body.append(text(px + 620, y, "Offset from CL", size=19, fill=MUTED, weight="700"))
    y += 12
    body.append(f'<line x1="{px}" y1="{y}" x2="{WIDTH - 60}" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    y += 32
    ordered = sorted(marks, key=lambda m: (m.get("last_recovered") or "", m.get("pid") or ""))
    for i, mark in enumerate(ordered):
        if i % 2 == 1:
            body.append(f'<rect x="{px - 12}" y="{y - 24}" width="{WIDTH - 60 - px + 12}" '
                        f'height="34" fill="{STRIPE}"/>')
        body.append(text(px, y, mark.get("pid", "?"), size=20, weight="600",
                         extra=' class="mark-row"'))
        body.append(text(px + 100, y, mark.get("designation") or "", size=20))
        body.append(text(px + 200, y, mark.get("last_recovered") or "never", size=20))
        body.append(text(px + 380, y, mark.get("condition") or "unknown", size=20,
                         fill=RED if (mark.get("condition") or "").upper() == "MARK NOT FOUND" else INK,
                         weight="600"))
        feet = mark.get("distance_from_centerline_ft")
        body.append(text(px + 620, y, f"{feet:.0f} ft" if feet is not None else "?", size=20))
        y += 34

    y += 30
    body.append(text(px, y, "The TxDOT monuments", size=28, weight="700"))
    y += 40
    for monument in monuments:
        feet = monument.get("distance_from_centerline_ft")
        body.append(marker_triangle(px + 10, y - 8, size=9))
        body.append(text(px + 34, y, f"{monument.get('station', '?')}  {monument.get('condition', '?')}, "
                         f"{monument.get('marker') or 'marker not recorded'}, "
                         f"{feet:.0f} ft from the centerline" if feet is not None else
                         f"{monument.get('station', '?')}  {monument.get('condition', '?')}",
                         size=20, extra=' class="monument-row"'))
        y += 34

    y += 24
    for line in wrap(
        "MARK NOT FOUND is a report with a date on it, not a verdict. Somebody looked on "
        "that day and did not find it. Whether to look again, or to set new control "
        "instead, is the surveyor's call and the largest single judgment in the estimate.",
        62,
    ):
        body.append(text(px, y, line, size=19, fill=MUTED))
        y += 27

    body += footer(document, "the control block of screening.json")
    return svg(body)


# ------------------------------------------------------------------ the crew safety map


def nearest_places(document):
    """The nearest place of each kind, with the corridor end it is nearer to."""
    safety = document.get("crew_safety", {})
    by_type = safety.get("by_type", {})
    alignment = document.get("alignment", {})
    found = []
    for kind, label in SAFETY_KINDS:
        nearest = (by_type.get(kind) or {}).get("nearest")
        if not nearest or nearest.get("longitude") is None:
            continue
        from_start = nearest.get("distance_from_start_mi")
        from_end = nearest.get("distance_from_end_mi")
        to_start = from_start is not None and (from_end is None or from_start <= from_end)
        found.append({
            "kind": kind,
            "label": label,
            "place": nearest,
            "end_point": alignment.get("start") if to_start else alignment.get("end"),
            "end_name": "the Old Bandera Rd end" if to_start else "the Loop 410 end",
            "end_miles": from_start if to_start else from_end,
            "other_miles": from_end if to_start else from_start,
            "other_name": "the Loop 410 end" if to_start else "the Old Bandera Rd end",
        })
    return found


def crew_safety_map(document, capture):
    box = (60, 150, 1000, 870)
    places = nearest_places(document)
    points = [(p["place"]["longitude"], p["place"]["latitude"]) for p in places]
    bbox = document["corridor"]["bbox"]
    if points:
        bbox = union(bbox, bbox_of_points(points))
    frame = Frame(grow(bbox, 0.06), box, pad=50)
    radius = document.get("crew_safety", {}).get("search_radius_mi")

    body = header(
        "How far help is",
        f"The nearest of each kind within {radius:g} miles, as a straight line to the "
        f"nearer end of the corridor. A straight line is not a drive."
        if radius else "The nearest of each kind, as a straight line to the nearer end of the corridor.",
    )
    body += base_map(frame, document, capture, faint=True)

    colors = {"hospital": VIOLET, "ambulance": RED, "fire_ems": AMBER, "police": TEAL}
    for place in places:
        x, y = frame.xy(place["place"]["longitude"], place["place"]["latitude"])
        color = colors.get(place["kind"], INK)
        if place["end_point"]:
            ex, ey = frame.xy(*place["end_point"])
            body.append(f'<line x1="{_n(x)}" y1="{_n(y)}" x2="{_n(ex)}" y2="{_n(ey)}" '
                        f'stroke="{color}" stroke-width="3" stroke-dasharray="10 8" class="help-line"/>')
            mx, my = (x + ex) / 2, (y + ey) / 2
            words = f"{place['end_miles']:.2f} mi"
            body.append(f'<rect x="{_n(mx - 52)}" y="{_n(my - 18)}" width="104" height="30" '
                        f'rx="6" fill="{PAPER}" stroke="{color}" stroke-width="2"/>')
            body.append(text(mx, my + 5, words, size=19, fill=color, weight="700",
                             anchor="middle", extra=' class="help-distance"'))
        body.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="13" fill="{color}" '
                    f'stroke="{PAPER}" stroke-width="3" class="help-place"/>')
        body.append(text(x + 20, y + 7, place["label"], size=20, fill=color, weight="700"))

    body += end_labels(frame, document, above_first=True)
    body += scale_bar(frame, box[0] + 40, box[1] + box[3] - 40)
    body += north_arrow(box[0] + box[2] - 50, box[1] + 60)

    px = 1120
    y = 190
    body.append(text(px, y, "The nearest of each kind", size=28, weight="700"))
    y += 48
    for place in places:
        color = colors.get(place["kind"], INK)
        p = place["place"]
        body.append(f'<circle cx="{px + 12}" cy="{y - 8}" r="11" fill="{color}"/>')
        body.append(text(px + 36, y, f"{place['label']}: {p.get('name', '?')}", size=22,
                         weight="600", extra=' class="help-row"'))
        y += 28
        address = ", ".join(str(p[k]) for k in ("address", "city") if p.get(k))
        body.append(text(px + 36, y, address, size=18, fill=MUTED))
        y += 28
        body.append(text(
            px + 36, y,
            f"{place['end_miles']:.2f} mi to {place['end_name']}, "
            f"{place['other_miles']:.2f} mi to {place['other_name']}",
            size=19, fill=INK,
        ))
        y += 26
        body.append(text(px + 36, y, f"{p.get('distance_from_centerline_mi', 0):.2f} mi to the "
                         "nearest point of the road", size=19, fill=INK))
        y += 44

    y += 4
    body.append(f'<line x1="{px}" y1="{y}" x2="{WIDTH - 60}" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
    y += 44
    body.append(text(px, y, "Two things to know", size=28, weight="700"))
    y += 38
    notes = document.get("crew_safety", {}).get("notes", [])[:2]
    for note in notes:
        body.append(text(px, y, note.get("topic", ""), size=20, weight="600"))
        y += 27
        # Each note is a paragraph. The first two sentences carry the point;
        # the rest is in the crew_safety block, which the footer names.
        sentences = re.split(r"(?<=[.!?])\s+", note.get("detail", ""))
        for line in wrap(" ".join(sentences[:2]), 80):
            body.append(text(px, y, line, size=17, fill=MUTED))
            y += 23
        y += 8

    body += footer(document, "the crew_safety block of screening.json")
    return svg(body)


# ------------------------------------------------------------------ how it works


def how_it_works(document, capture=None):
    """The tool in one picture. The counts on it are the run's, not typed."""
    services = document.get("services", [])
    by_purpose = {}
    for service in services:
        by_purpose.setdefault(service.get("purpose") or "other", []).append(service)
    parcels = document.get("parcels", [])
    flagged_count = len([p for p in parcels if p.get("flags")])
    control = document.get("control", {})
    marks = control.get("recovery_risk", {}).get("marks_in_corridor", "?")
    sheets = document.get("row_maps", {}).get("sheet_count", "?")
    half = document.get("corridor", {}).get("half_width_ft", "?")

    body = header(
        "How the screening works",
        "One line goes in. One file comes out. Three documents are written from it, and a "
        "licensed surveyor reads them.",
    )

    def box(x, y, w, h, title, lines, accent=TEAL, fill=PAPER):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
               f'stroke="{accent}" stroke-width="3"/>',
               f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="{accent}"/>',
               text(x + 24, y + 52, title, size=26, weight="700")]
        ty = y + 88
        for line in lines:
            out.append(text(x + 24, ty, line, size=20, fill=MUTED))
            ty += 28
        return out

    def arrow(x1, y1, x2, y2):
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" '
                f'stroke-width="3" marker-end="url(#head)"/>')

    body.append('<defs><marker id="head" markerWidth="12" markerHeight="12" refX="10" '
                'refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="' + INK + '"/></marker></defs>')

    top = 190
    body += box(60, top, 330, 210, "1. A centerline", [
        "TxDOT's own, by route and mile.",
        f"{document.get('alignment', {}).get('length_mi', '?')} miles on this job.",
    ])
    body.append(arrow(390, top + 105, 440, top + 105))
    body += box(440, top, 330, 210, "2. A ribbon", [
        f"{half} feet either side.",
        "The ground the job touches.",
    ])
    body.append(arrow(770, top + 105, 820, top + 105))
    body += box(820, top, 400, 210, "3. Public services asked", [
        f"{len(services)} of them, in a fixed order.",
        "Every answer saved with its date",
        "and the exact request.",
    ])
    body.append(arrow(1220, top + 105, 1270, top + 105))
    body += box(1270, top, 330, 210, "4. One file", [
        "screening.json.",
        "Every answer, and every",
        "question nobody could answer.",
    ])
    body.append(arrow(1435, top + 210, 1435, top + 260))

    # The services, under box 3, grouped by what the run asked them for.
    words = {
        "alignment": "the centerline", "buffer": "the ribbon", "parcels": "the tracts",
        "flags": "what costs time", "flag": "what costs time", "control": "the control",
        "row_maps": "the ROW map sheets", "safety": "how far help is",
        "roadway": "the road itself", "other": "the rest",
    }
    sy = top + 250
    body.append(text(60, sy, "The services, by what they were asked for", size=24, weight="700"))
    sy += 36
    col_x = 60
    col_w = 390
    per_col = 5
    entries = []
    for purpose, group in by_purpose.items():
        entries.append((words.get(purpose, purpose), None))
        for service in group:
            count = service.get("record_count")
            entries.append((service.get("name", "?"), count))
    columns = [entries[i:i + per_col * 2] for i in range(0, len(entries), per_col * 2)]
    for column in columns[:3]:
        cy = sy
        for name, count in column:
            if count is None:
                body.append(text(col_x, cy, name, size=19, weight="700", fill=TEAL))
            else:
                body.append(text(col_x + 16, cy, f"{name}  {count} returned", size=18, fill=MUTED,
                                 extra=' class="service"'))
            cy += 26
        col_x += col_w

    # The three documents, and the person.
    dy = 720
    body += box(1270, dy - 190, 330, 160, "5. Three documents", [
        "The bid memo.", "The flagged parcel table.", "The crew-day build-up.",
    ], accent=AMBER)
    body.append(arrow(1435, dy - 30, 1435, dy + 20))
    body += box(1270, dy + 20, 330, 150, "6. A surveyor decides", [
        f"{len(parcels)} tracts, {flagged_count} flagged, {marks} marks,",
        f"{sheets} sheets. The tool decides nothing.",
    ], accent=INK, fill=STRIPE)

    body += footer(document, "the services block of screening.json")
    return svg(body)


# ------------------------------------------------------------------ the crew-day sheet


def crew_day_sheet(document, capture=None, rates=None):
    """The build-up as a sheet. Every number is the build-up's own."""
    rates = rates or crew_day.load_rates()
    built = crew_day.lines(document, rates)
    inputs = crew_day.counts(document)
    field_hours, field_blocked = crew_day.hours_for("field", built)
    office_hours, office_blocked = crew_day.hours_for("office", built)
    per_crew_day = rates["field_hours_per_crew_day"]
    per_office_day = rates["office_hours_per_day"]
    crew = rates["crew_size"]
    field_days = crew_day.days(field_hours, per_crew_day.value)
    office_days = crew_day.days(office_hours, per_office_day.value)
    unmeasured = [c for c in inputs if not c.get("measured")]

    body = header(
        "The crew-day build-up, as a sheet",
        f"{corridor_title(document)}. Not an estimate: an estimate somebody can argue with, "
        "one rate at a time.",
    )

    # Left column: what went in.
    lx = 60
    y = 180
    body.append(text(lx, y, "What went in", size=28, weight="700"))
    y += 40
    for i, item in enumerate(inputs):
        if i % 2 == 1:
            body.append(f'<rect x="{lx - 12}" y="{y - 24}" width="720" height="34" fill="{STRIPE}"/>')
        body.append(text(lx, y, item.get("label", ""), size=19, extra=' class="input"'))
        if item.get("measured"):
            value = crew_day._quantity(item.get("value"), item.get("unit"))
            body.append(text(lx + 690, y, value, size=19, weight="600", anchor="end"))
        else:
            body.append(text(lx + 690, y, UNMEASURED, size=19, weight="700", fill=AMBER,
                             anchor="end", extra=' class="unmeasured-input"'))
        y += 34
    y += 12
    for line in wrap(
        f"{len(unmeasured)} of these {len(inputs)} inputs were never measured, and they are "
        "not zero. Each one is a question somebody still has to answer.", 70,
    ):
        body.append(text(lx, y, line, size=19, fill=AMBER, weight="600"))
        y += 27

    # Right column: the lines, then the totals.
    rx = 860
    y = 180

    def block(title, kind):
        nonlocal y
        body.append(text(rx, y, title, size=28, weight="700"))
        y += 40
        for line in built:
            if line["kind"] != kind:
                continue
            blocked = line["hours"] is None
            handles = ", ".join(
                f.get("source", "").split("(")[0].replace("rate ", "").strip()
                for f in line["factors"] if f.get("source", "").startswith("rate ")
            )
            body.append(text(rx, y, line["label"], size=21, weight="600", extra=' class="line"'))
            body.append(text(WIDTH - 60, y, handles, size=18, fill=FAINT, anchor="end"))
            y += 28
            arithmetic = crew_day._arithmetic(line, times="×")
            body.append(text(rx + 24, y, arithmetic, size=19,
                             fill=AMBER if blocked else MUTED, weight="600" if blocked else "400",
                             extra=' class="blocked-line"' if blocked else ""))
            y += 26
            if blocked:
                body.append(text(rx + 24, y, f"No total: {line['blocked_by']} was never measured.",
                                 size=18, fill=AMBER))
                y += 26
            y += 8

    block("Field hours", "field")
    y += 6
    block("Office hours", "office")

    # The totals box.
    ty = y + 10
    floor = field_blocked + office_blocked
    body.append(f'<rect x="{rx - 20}" y="{ty}" width="{WIDTH - 60 - rx + 20}" '
                f'height="{196 if floor else 150}" rx="12" '
                f'fill="{STRIPE}" stroke="{RULE}" stroke-width="2"/>')
    ty += 44
    body.append(text(rx, ty, f"Field  {field_hours:.2f} hours  =  {field_days} crew-days of "
                     f"{crew.value:g} {crew.unit}, rounded up",
                     size=22, weight="700", extra=' class="field-total"'))
    ty += 36
    body.append(text(rx, ty, f"Office  {office_hours:.2f} hours  =  {office_days} days, rounded up",
                     size=22, weight="700", extra=' class="office-total"'))
    ty += 32
    body.append(text(rx, ty, "The two are never added together. They are bought from different people.",
                     size=19, fill=MUTED))
    ty += 34
    if floor:
        words = (f"Both are floors. {len(floor)} line{'s' if len(floor) > 1 else ''} above "
                 f"ha{'ve' if len(floor) > 1 else 's'} no total, and those hours are missing "
                 "from the figure rather than zero in it.")
        for i, line in enumerate(wrap(words, 78)):
            body.append(text(rx, ty, line, size=19, fill=AMBER, weight="600",
                             extra=' class="floor"' if i == 0 else ""))
            ty += 26

    body += footer(document, "crew_day.lines() and crew_rates.toml")
    return svg(body)


# ------------------------------------------------------------------ writing


# ------------------------------------------------------------------ the slide maps


SLIDE_BOX = (60, 170, 1000, 850)
SLIDE_PANEL = 1120


def slide_header(title, subtitle):
    return [
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>',
        text(60, 84, title, size=56, weight="700"),
        text(60, 138, subtitle, size=36, fill=MUTED),
    ]


def slide_footer(document, drawn_from):
    run = document.get("run", {})
    return [
        text(60, HEIGHT - 60, f"Drawn from {drawn_from}. Nothing here was drawn by hand.",
             size=28, fill=FAINT),
        text(60, HEIGHT - 24, f"Run {run.get('run_id', '?')}, finished {run.get('finished_at', '?')}.",
             size=28, fill=FAINT),
    ]


def slide_furniture(frame, document, above_first=True):
    """End labels, a scale bar and a north arrow, at slide size."""
    box = frame.box
    return (end_labels(frame, document, above_first=above_first, size=SLIDE_TYPE + 2, clamp=True)
            + scale_bar(frame, box[0] + 40, box[1] + box[3] - 40, size=SLIDE_TYPE)
            + north_arrow(box[0] + box[2] - 50, box[1] + 70, size=SLIDE_TYPE + 4))


def stat(x, y, big, small, fill=INK, cls=None):
    """One figure and the words under it, for the right of a slide map."""
    extra = f' class="{cls}"' if cls else ""
    return [
        text(x, y, big, size=64, weight="700", fill=fill, extra=extra),
        text(x, y + 46, small, size=SLIDE_TYPE + 2, fill=MUTED),
    ]


def corridor_slide(document, capture):
    """The corridor map for a projector: the ribbon, the tracts, the flags."""
    frame = Frame(document["corridor"]["bbox"], SLIDE_BOX, pad=90)
    rows = flagged(document)
    parcels = document.get("parcels", [])
    body = slide_header(
        "Where the job is",
        f"{corridor_title(document)}. {document['corridor'].get('half_width_ft', '?')} feet "
        "either side of TxDOT's own centerline.",
    )
    body += base_map(frame, document, capture)
    for place in flag_points(document, capture):
        x, y = frame.xy(place["lon"], place["lat"])
        body.append(marker_cross(x, y, size=16, cls="place") if place["type"] == "cemetery"
                    else marker_square(x, y, size=13, cls="place"))
    # The flagged tracts are filled and outlined, and not numbered: five of
    # the eight on SH16 sit within a few hundred feet of each other, and eight
    # numbered dots on a slide would cover the tracts they point at. The page
    # map numbers them, because it has a list beside it to match them to.
    rings_by_id = {p.get("id"): rings for p, rings in parcel_rings(document, capture)}
    for parcel in rows:
        rings = rings_by_id.get(parcel.get("id")) or []
        if rings:
            body.append(polygon(frame, rings, AMBER_FILL, AMBER, width=4.0, cls="flagged"))
    body += slide_furniture(frame, document)

    kinds = {}
    for parcel in rows:
        for flag in parcel.get("flags", []):
            kinds[flag.get("type")] = kinds.get(flag.get("type"), 0) + 1
    x, y = SLIDE_PANEL, 260
    body += stat(x, y, f"{len(parcels)}", "tracts touch the ribbon", cls="stat-tracts")
    y += 150
    body += stat(x, y, f"{len(rows)}", "of them carry something that costs time",
                 fill=AMBER, cls="stat-flagged")
    y += 150
    words = "  ·  ".join(
        f"{count} {kind}{'' if count == 1 or kind.endswith('s') else 's'}"
        for kind, count in sorted(kinds.items(), key=lambda item: -item[1])
    )
    body.append(text(x, y, words, size=SLIDE_TYPE + 6, fill=INK, weight="600"))
    y += 110
    legend = [
        (f'<rect x="{x}" y="{y - 30}" width="52" height="36" fill="{TEAL_FILL}" stroke="{TEAL}" stroke-width="3"/>',
         "the ribbon"),
        (f'<rect x="{x}" y="{y + 40}" width="52" height="36" fill="{PARCEL_FILL}" stroke="{PARCEL_LINE}" stroke-width="3"/>',
         "a tract the ribbon touches"),
        (f'<rect x="{x}" y="{y + 110}" width="52" height="36" fill="{AMBER_FILL}" stroke="{AMBER}" stroke-width="3"/>',
         "a tract that costs time"),
        (marker_square(x + 26, y + 168, size=14), "a school"),
        (marker_cross(x + 26, y + 238, size=17), "a cemetery"),
    ]
    for i, (symbol, label) in enumerate(legend):
        body.append(symbol)
        body.append(text(x + 76, y + i * 70, label, size=SLIDE_TYPE + 2, fill=MUTED))
    body += slide_footer(document, "the roadway, buffer, parcel and flag responses in the cache")
    return svg(body)


def control_slide(document, capture):
    """The control map for a projector: every mark, its PID, its condition."""
    frame = Frame(document["corridor"]["bbox"], SLIDE_BOX, pad=90)
    control = document.get("control", {})
    marks = list(control.get("ngs_marks", []))
    monuments = distinct_monuments(control.get("txdot_points", []))
    risk = control.get("recovery_risk", {})
    not_found = risk.get("mark_not_found", 0)
    years = sorted({(m.get("last_recovered") or "")[:4] for m in marks if m.get("last_recovered")})
    conditions = sorted(control.get("txdot_control", {}).get("by_condition", {}))

    body = slide_header(
        "What control is published here",
        f"{len(marks)} NGS marks in the ribbon. {len(monuments)} TxDOT monuments.",
    )
    body += base_map(frame, document, capture, faint=True)
    ordered = sorted(marks, key=lambda m: m.get("latitude") or 0, reverse=True)
    for i, mark in enumerate(ordered):
        if mark.get("longitude") is None or mark.get("latitude") is None:
            continue
        x, y = frame.xy(mark["longitude"], mark["latitude"])
        body.append(marker_x(x, y, size=15, cls="mark"))
        # Labels alternate sides of the line so neighbours do not overprint.
        side = 1 if i % 2 == 0 else -1
        body.append(text(x + side * 24, y + 12, mark.get("pid", "?"), size=SLIDE_TYPE,
                         fill=RED, weight="700", anchor="start" if side > 0 else "end"))
    for monument in monuments:
        if monument.get("longitude") is None or monument.get("latitude") is None:
            continue
        x, y = frame.xy(monument["longitude"], monument["latitude"])
        body.append(marker_triangle(x, y, size=18, cls="monument"))
        body.append(text(x + 26, y + 40, monument.get("station", "?"), size=SLIDE_TYPE,
                         fill=GREEN, weight="700"))
    body += slide_furniture(frame, document)

    x, y = SLIDE_PANEL, 260
    body += stat(x, y, f"{len(marks)}", "NGS marks published in the ribbon", cls="stat-marks")
    y += 150
    body += stat(x, y, f"{not_found} of {len(marks)}", "recorded MARK NOT FOUND", fill=RED,
                 cls="stat-not-found")
    y += 110
    if years:
        span = years[0] if len(years) == 1 else f"{years[0]} to {years[-1]}"
        body.append(text(x, y, f"Last looked for {span}", size=SLIDE_TYPE + 4, fill=MUTED))
        y += 100
    body += stat(x, y, f"{len(monuments)}", "TxDOT monuments, reported "
                 + (", ".join(conditions) if conditions else "?"), fill=GREEN,
                 cls="stat-monuments")
    y += 150
    for line in wrap("MARK NOT FOUND is a report with a date on it, not a verdict. "
                     "Whether to look again or set new control is the surveyor's call.", 40):
        body.append(text(x, y, line, size=SLIDE_TYPE, fill=MUTED))
        y += 44
    body += slide_footer(document, "the control block of screening.json")
    return svg(body)


def safety_slide(document, capture):
    """The crew safety map for a projector: four places, four straight lines."""
    places = nearest_places(document)
    points = [(p["place"]["longitude"], p["place"]["latitude"]) for p in places]
    bbox = document["corridor"]["bbox"]
    if points:
        bbox = union(bbox, bbox_of_points(points))
    # A narrower box than the other two slide maps: the labels on this one
    # stick out past the dots they name, and the panel on the right needs
    # its room.
    left, top, width, height = SLIDE_BOX
    frame = Frame(grow(bbox, 0.06), (left, top, width - 120, height), pad=70)
    body = slide_header(
        "How far help is",
        "Straight lines to the nearer end of the corridor. A straight line is not a drive.",
    )
    body += base_map(frame, document, capture, faint=True)
    colors = {"hospital": VIOLET, "ambulance": RED, "fire_ems": AMBER, "police": TEAL}
    # Where each label sits relative to its dot. Three of the four nearest
    # places on SH16 are within a mile of the same end of the corridor, so
    # labels all set to the right of their dots overprint each other. Each
    # kind takes its own side, and a line too short to carry a distance box
    # in its middle carries the distance on the label instead.
    sides = {"hospital": "right", "police": "left", "ambulance": "below", "fire_ems": "right"}
    for place in places:
        x, y = frame.xy(place["place"]["longitude"], place["place"]["latitude"])
        color = colors.get(place["kind"], INK)
        distance = f"{place['end_miles']:.2f} mi"
        label = place["label"]
        if place["end_point"]:
            ex, ey = frame.xy(*place["end_point"])
            body.append(f'<line x1="{_n(x)}" y1="{_n(y)}" x2="{_n(ex)}" y2="{_n(ey)}" '
                        f'stroke="{color}" stroke-width="5" stroke-dasharray="14 10" class="help-line"/>')
            if math.hypot(ex - x, ey - y) >= 220:
                mx, my = (x + ex) / 2, (y + ey) / 2
                body.append(f'<rect x="{_n(mx - 80)}" y="{_n(my - 26)}" width="160" height="46" '
                            f'rx="8" fill="{PAPER}" stroke="{color}" stroke-width="3"/>')
                body.append(text(mx, my + 9, distance, size=SLIDE_TYPE, fill=color, weight="700",
                                 anchor="middle", extra=' class="help-distance"'))
            else:
                label = f"{label} · {distance}"
        body.append(f'<circle cx="{_n(x)}" cy="{_n(y)}" r="18" fill="{color}" '
                    f'stroke="{PAPER}" stroke-width="4" class="help-place"/>')
        side = sides.get(place["kind"], "right")
        if side == "left":
            body.append(text(x - 28, y + 11, label, size=SLIDE_TYPE, fill=color, weight="700",
                             anchor="end"))
        elif side == "below":
            body.append(text(x, y + 60, label, size=SLIDE_TYPE, fill=color, weight="700",
                             anchor="middle"))
        else:
            body.append(text(x + 28, y + 11, label, size=SLIDE_TYPE, fill=color, weight="700"))
    # The end labels sit to the right of their dots on this map rather than
    # above and below, because the places cluster at the Loop 410 end and a
    # label under that dot lands on top of the ambulance.
    box = frame.box
    for i, end in enumerate(ends(document)):
        if end["point"]:
            x, y = frame.xy(*end["point"])
            if i == 0:
                body.append(text(x + 40, y + 12, end["label"], size=SLIDE_TYPE + 2, weight="600",
                                 extra=' class="end-label"'))
            else:
                body.append(text(x - 40, y + 12, end["label"], size=SLIDE_TYPE + 2, weight="600",
                                 anchor="end", extra=' class="end-label"'))
    body += scale_bar(frame, box[0] + 40, box[1] + box[3] - 40, size=SLIDE_TYPE)
    body += north_arrow(box[0] + box[2] - 50, box[1] + 70, size=SLIDE_TYPE + 4)

    x, y = SLIDE_PANEL, 250
    for place in places:
        color = colors.get(place["kind"], INK)
        p = place["place"]
        body.append(f'<circle cx="{x + 16}" cy="{y - 12}" r="16" fill="{color}"/>')
        for i, line in enumerate(wrap(f"{place['label']}: {p.get('name', '?')}", 36)):
            body.append(text(x + 48, y, line, size=SLIDE_TYPE + 2, weight="700",
                             extra=' class="help-row"' if i == 0 else ""))
            y += 44
        body.append(text(x + 48, y, f"{place['end_miles']:.2f} mi to {place['end_name']}",
                         size=SLIDE_TYPE, fill=INK))
        y += 42
        body.append(text(x + 48, y, f"{place['other_miles']:.2f} mi to {place['other_name']}",
                         size=SLIDE_TYPE, fill=MUTED))
        y += 76
    body += slide_footer(document, "the crew_safety block of screening.json")
    return svg(body)


DRAWINGS = (
    ("corridor", corridor_map),
    ("control", control_map),
    ("safety", crew_safety_map),
    ("how", how_it_works),
    ("sheet", crew_day_sheet),
    ("corridor_slide", corridor_slide),
    ("control_slide", control_slide),
    ("safety_slide", safety_slide),
)


def draw_all(document, capture):
    """Every drawing, by its file name."""
    return {NAMES[key]: draw(document, capture) for key, draw in DRAWINGS}


def write(out_dir, copy_to=None):
    """Write the drawings into ``<out_dir>/drawings/`` and, if asked, a second copy."""
    document, capture = load(out_dir)
    drawn = draw_all(document, capture)
    folder = Path(out_dir) / "drawings"
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in drawn.items():
        path = folder / name
        write_text(path, content)
        written.append(path)
    if copy_to:
        copies = Path(copy_to)
        copies.mkdir(parents=True, exist_ok=True)
        for name, content in drawn.items():
            path = copies / name
            write_text(path, content)
            written.append(path)
    return written


def main(argv=None):
    """``python -m corridor_screen.drawings --out ../project-sh16 --copy-to ../docs/scenarios/sh16/img``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen drawings",
        description="Draw the maps and the sheet from a screening run.",
    )
    parser.add_argument("--out", required=True,
                        help="The project directory holding screening.json and its cache")
    parser.add_argument("--copy-to", default=None,
                        help="A second folder to write the same drawings into, for the site")
    args = parser.parse_args(argv)
    try:
        for path in write(args.out, args.copy_to):
            print(f"  written  {path}")
    except DrawingError as problem:
        print(f"  could not draw: {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
