"""THROWAWAY. A rough job page, three ways, so somebody can react to it.

Issue #194 asks what sections the job page has, in what order, and what
happens when a principal clicks one of the eight flagged tracts. It says to
make a rough one and react to it. This is the rough one.

The plan, in one line:

    Three variants of the job page, switchable via ``?variant=``, in one
    self-contained HTML file built from the committed SH16 run.

This is prototype code under the rules in ``/prototype``: no tests, no error
handling beyond what makes it run, no abstractions worth keeping. It lives on
a ``prototype/`` branch and it is not merged into ``main``. When a variant
wins, the winner gets written properly somewhere else and this file stays here
as the record of what was tried.

----

What the three variants disagree about
======================================

They are not three color schemes. Each one gives a different answer to the
five open questions, and the answers are incompatible on purpose:

===========================  =========================  =========================  =========================
Question                     A -- The map is the page   B -- The list is the page  C -- The page is questions
===========================  =========================  =========================  =========================
What a principal sees first  The map, full width        Five numbers, then the     A question, in words, with
                                                        eight tracts               a one-line answer
Clicking a flagged tract     Opens its card below the   Expands the row in place   Opens a drawer over the
                             map and scrolls to it      and marks the small map    page, one tract at a time
Toggling a layer             The map only               The whole page -- turning  Neither. Sections collapse
                                                        off control removes the    instead, and the map has
                                                        control section            no toggles
The bid memo                 All of it, at the bottom   None of it. Links out      All of it -- the page IS
                                                        instead                    the memo, with the map in it
Crew safety                  Its own section, low       One line in the number      Its own question, last
                             down                       strip, which expands
===========================  =========================  =========================  =========================

----

Where the numbers come from
===========================

The same place the drawings get them: the committed run in
``project-sh16/screening.json`` and the cached service responses beside it.
Nothing on the page is typed in by hand. A prototype that invents its own
numbers teaches the wrong thing about density, and this repo does not invent
numbers anywhere else.

Run it with::

    python corridor-screen/prototypes/job_page_prototype.py

It writes ``corridor-screen/prototypes/job-page-prototype.html``. Open that
file. No server, nothing installed, works with the Wi-Fi off -- which is the
constraint the real page has to meet, so the prototype meets it too.
"""

import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
REPO = PACKAGE_ROOT.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from corridor_screen import drawings  # noqa: E402

PROJECT = REPO / "project-sh16"
OUT = HERE / "job-page-prototype.html"

# The map box. Wider than tall, because the corridor is nine miles of road and
# a browser window is wider than it is tall.
BOX = (0, 0, 1200, 760)


# ---------------------------------------------------------------- the facts
def facts(document, capture):
    """Every number the page shows, read out of the run once."""
    run = document["run"]
    alignment = document["alignment"]
    control = document["control"]
    rows = drawings.flagged(document)
    sh16 = document["row_maps"]["by_route"].get("SH0016", {})
    return {
        "run_id": run["run_id"],
        "screened_on": run["finished_at"][:10],
        "mode": run["mode"],
        "half_width_ft": run["half_width_ft"],
        "map_link": run["map_link"],
        "not_screenable": run["not_screenable"],
        "lead_times": run["lead_times"],
        "corridor": alignment["source_path"],
        "length_mi": alignment["length_mi"],
        "area_sq_mi": document["corridor"]["area_sq_mi"],
        "tracts": len(document["parcels"]),
        "flagged": rows,
        "marks": control["recovery_risk"]["marks_in_corridor"],
        "not_found": control["recovery_risk"]["mark_not_found"],
        "ngs_marks": control["ngs_marks"],
        "txdot_monuments": control["txdot_control"]["distinct_stations"],
        "sheets": document["row_maps"]["sheet_count"],
        "sheet_from": document["row_maps"]["date_range"]["from"],
        "sheet_to": document["row_maps"]["date_range"]["to"],
        "sh16_sheets": sh16.get("sheet_count"),
        "sh16_from": (sh16.get("date_range") or {}).get("from"),
        "sh16_to": (sh16.get("date_range") or {}).get("to"),
        "safety": document["crew_safety"],
        "roadway": document["roadway"],
        "tool_version": run["tool_version"],
    }


def longest_wait(rows):
    """The longest measured wait on any one tract, and the tract it is on."""
    measured = [p for p in rows if p.get("max_lead_time_days") is not None]
    if not measured:
        return None
    best = max(measured, key=lambda p: p["max_lead_time_days"])
    return best


def unmeasured_waits(rows):
    """The kinds of flag that carry no published number of days."""
    kinds = set()
    for parcel in rows:
        for flag in parcel.get("flags", []):
            if flag.get("lead_time_days") is None:
                kinds.add(flag.get("type"))
    return sorted(kinds)


# ------------------------------------------------------------------ the map
def safety_rays(frame, document):
    """Each safety place as a short ray from the nearer end of the corridor.

    The nearest hospital is two miles off the end of an eight-mile corridor.
    Drawing it in place would shrink the corridor to a smear, so the ray says
    which way and how far instead. Whether that is honest enough is one of the
    things the prototype is for.
    """
    body = []
    ends = drawings.ends(document)
    for kind, word in drawings.SAFETY_KINDS:
        place = (document["crew_safety"]["by_type"].get(kind) or {}).get("nearest")
        if not place:
            continue
        from_start = place["distance_from_start_mi"]
        from_end = place["distance_from_end_mi"]
        anchor = ends[0] if from_start <= from_end else ends[1]
        miles = min(from_start, from_end)
        ax, ay = frame.xy(*anchor["point"])
        px, py = frame.xy(place["longitude"], place["latitude"])
        dx, dy = px - ax, py - ay
        span = max((dx * dx + dy * dy) ** 0.5, 1e-6)
        dx, dy = dx / span, dy / span
        tipx, tipy = ax + dx * 120, ay + dy * 120
        body.append(
            f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{tipx:.1f}" y2="{tipy:.1f}" '
            f'stroke="{drawings.VIOLET}" stroke-width="2.5" '
            f'stroke-dasharray="7 5" stroke-linecap="round"/>'
        )
        anchor_at = "end" if dx < 0 else "start"
        body.append(drawings.text(
            tipx + (8 if dx >= 0 else -8), tipy - 6,
            f"{word}: {place['name']}", size=17, fill=drawings.VIOLET,
            weight="600", anchor=anchor_at,
        ))
        body.append(drawings.text(
            tipx + (8 if dx >= 0 else -8), tipy + 14,
            f"{miles:.2f} mi from this end", size=15, fill=drawings.MUTED,
            anchor=anchor_at,
        ))
    return body


def spread(points, apart=38, rounds=90):
    """Move numbered dots off one another, keeping each near where it belongs.

    Four of the eight flagged tracts sit within a few hundred feet of each
    other, so three of the numbers were drawn underneath the others and could
    be neither read nor clicked. This pushes any pair closer than ``apart``
    pixels away from each other, and the caller draws a leader line back to
    the tract each moved number came from.
    """
    seats = [None if p is None else [p[0], p[1]] for p in points]
    live = [i for i, s in enumerate(seats) if s]
    for _ in range(rounds):
        moved = False
        for a in range(len(live)):
            for b in range(a + 1, len(live)):
                one, two = seats[live[a]], seats[live[b]]
                dx, dy = two[0] - one[0], two[1] - one[1]
                gap = (dx * dx + dy * dy) ** 0.5
                if gap >= apart:
                    continue
                if gap < 1e-6:
                    dx, dy, gap = 1.0, 0.0, 1.0
                push = (apart - gap) / 2
                ux, uy = dx / gap, dy / gap
                one[0] -= ux * push
                one[1] -= uy * push
                two[0] += ux * push
                two[1] += uy * push
                moved = True
        if not moved:
            break
    return [None if s is None else (s[0], s[1]) for s in seats]


def map_svg(document, capture, f):
    """The corridor map with no side panel, in layers a reader can switch off.

    Issue #191 settled that the job page gets a browser frame from the same
    generator as the page and slide frames. This is a rough stand-in for that
    frame: same shapes, same projection, no baked-in panel, and every flagged
    tract carrying the tract id so a click can find it.
    """
    frame = drawings.Frame(document["corridor"]["bbox"], BOX, pad=90)
    rings_by_id = {p.get("id"): rings
                   for p, rings in drawings.parcel_rings(document, capture)}

    body = [f'<svg xmlns="http://www.w3.org/2000/svg" id="jobmap" '
            f'viewBox="0 0 {BOX[2]} {BOX[3]}" font-family="{drawings.FONT}" '
            f'role="img" aria-label="The corridor, its tracts, and the eight '
            f'flagged tracts">']
    body.append(f'<rect width="{BOX[2]}" height="{BOX[3]}" fill="{drawings.PAPER}"/>')

    # Every tract the run counted.
    body.append('<g data-layer="tracts">')
    for _, rings in drawings.parcel_rings(document, capture):
        if rings:
            body.append(drawings.polygon(
                frame, rings, drawings.PARCEL_FILL, drawings.PARCEL_LINE,
                width=1.0, cls="parcel"))
    body.append("</g>")

    # The ribbon and the centerline. Not a layer: switch these off and the
    # drawing stops being a map of this job.
    body.append('<g data-layer="base">')
    body.append(drawings.polygon(frame, drawings.ribbon(document, capture),
                                 drawings.TEAL_FILL, drawings.TEAL, width=2.0,
                                 cls="ribbon", opacity=0.55))
    body.append(drawings.polyline(frame, drawings.centerline(document, capture),
                                  drawings.TEAL, width=3.5, cls="centerline"))
    for end in drawings.ends(document):
        x, y = frame.xy(*end["point"])
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" '
                    f'fill="{drawings.TEAL}" stroke="{drawings.PAPER}" '
                    f'stroke-width="3"/>')
    body += drawings.end_labels(frame, document, clamp=True)
    body += drawings.scale_bar(frame, BOX[0] + 30, BOX[1] + BOX[3] - 30)
    body += drawings.north_arrow(BOX[0] + BOX[2] - 44, BOX[1] + 46)
    body.append("</g>")

    # The published marks, and what condition they are recorded in.
    body.append('<g data-layer="control">')
    for mark in document["control"]["ngs_marks"]:
        x, y = frame.xy(mark["longitude"], mark["latitude"])
        body.append(drawings.marker_x(x, y, cls="mark"))
    for point in drawings.distinct_monuments(document["control"]["txdot_points"]):
        x, y = frame.xy(point["longitude"], point["latitude"])
        body.append(drawings.marker_triangle(x, y, cls="mark"))
    body.append("</g>")

    # Which way the help is, and how far.
    body.append('<g data-layer="safety">')
    body += safety_rays(frame, document)
    body.append("</g>")

    # The eight. Each one carries its tract id, so a click anywhere -- the
    # shape or the numbered dot -- finds the same tract.
    body.append('<g data-layer="flags">')
    for place in drawings.flag_points(document, capture):
        x, y = frame.xy(place["lon"], place["lat"])
        if place["type"] == "cemetery":
            body.append(drawings.marker_cross(x, y, cls="place"))
        else:
            body.append(drawings.marker_square(x, y, cls="place"))
    # Where each number sits, before anything is moved.
    homes = []
    for parcel in f["flagged"]:
        at = drawings.centroid(rings_by_id.get(parcel["id"]) or [])
        homes.append(frame.xy(*at) if at else None)
    seats = spread(homes, apart=38)

    for number, parcel in enumerate(f["flagged"], start=1):
        tract = parcel["id"]
        kinds = ", ".join(sorted({fl["type"] for fl in parcel["flags"]}))
        body.append(
            f'<g class="hot" data-tract="{escape(tract)}" tabindex="0" '
            f'role="button" aria-label="Tract {escape(tract)}, '
            f'{escape(kinds)}, number {number} of {len(f["flagged"])}">')
        rings = rings_by_id.get(tract) or []
        if rings:
            body.append(drawings.polygon(frame, rings, drawings.AMBER_FILL,
                                         drawings.AMBER, width=2.0, cls="flagged"))
        home, seat = homes[number - 1], seats[number - 1]
        if home and seat:
            if (home[0] - seat[0]) ** 2 + (home[1] - seat[1]) ** 2 > 4:
                body.append(
                    f'<line x1="{home[0]:.1f}" y1="{home[1]:.1f}" '
                    f'x2="{seat[0]:.1f}" y2="{seat[1]:.1f}" '
                    f'stroke="{drawings.AMBER}" stroke-width="1.5"/>')
            body.append(drawings.numbered_dot(seat[0], seat[1], number,
                                              radius=15, size=19))
        body.append("</g>")
    body.append("</g>")

    body.append("</svg>")
    return "\n".join(body)


# ------------------------------------------------------- reading the memo in
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
CODE = re.compile(r"`([^`]+)`")


def inline(words):
    out = escape(words)
    out = INLINE_LINK.sub(r'<a href="\2" rel="noreferrer">\1</a>', out)
    out = BOLD.sub(r"<strong>\1</strong>", out)
    out = CODE.sub(r"<code>\1</code>", out)
    return out


def markdown_to_html(markdown):
    """Enough markdown for the memo. Throwaway, and it shows."""
    html, bullets = [], []

    def flush():
        if bullets:
            html.append("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith("### "):
            flush()
            html.append(f"<h4>{inline(stripped[4:])}</h4>")
        elif stripped.startswith("## "):
            flush()
            html.append(f"<h3>{inline(stripped[3:])}</h3>")
        elif stripped.startswith("# "):
            flush()
            html.append(f"<h2>{inline(stripped[2:])}</h2>")
        elif stripped.startswith("- "):
            bullets.append(inline(stripped[2:]))
        elif stripped == "---":
            flush()
            html.append("<hr>")
        else:
            flush()
            html.append(f"<p>{inline(stripped)}</p>")
    flush()
    return "\n".join(html)


def memo_section(markdown, heading):
    """One `##` section of the memo, heading included."""
    lines = markdown.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == f"## {heading}")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return markdown_to_html("\n".join(lines[start:end]))


# ------------------------------------------------- one tract, told in full
def flag_words(flag):
    """What this flag is, in the words a reader would use for it."""
    distance = flag.get("distance_ft")
    where = flag.get("relation") or "near"
    if distance is not None:
        where = f"{where}, {distance:.0f} ft away"
    return f"{flag['type'].title()} &mdash; {escape(flag['name'])} ({where})"


def wait_words(parcel):
    """The wait on this tract, or the reason there is no number for it."""
    days = parcel.get("max_lead_time_days")
    if days is not None:
        return (f'<span class="wait known">{days} '
                f'{escape(parcel.get("max_lead_time_basis") or "days")}</span>')
    kinds = sorted({f["type"] for f in parcel["flags"]
                    if f.get("lead_time_days") is None})
    return f'<span class="wait unknown">no published wait &mdash; {escape(", ".join(kinds))}</span>'


def tract_detail(parcel, number, total):
    """Why this tract is flagged, and what is still unknown about it.

    This block is the same in all three variants on purpose. The variants
    disagree about where it appears and how it is opened, not about what a
    principal needs to read once it is open.
    """
    out = [f'<div class="detail" id="detail-{escape(parcel["id"])}">']
    out.append(f'<p class="crumb">Tract {number} of {total}</p>')
    out.append(f'<h4>{escape(parcel["id"])} &middot; {escape(parcel["owner"])}</h4>')
    out.append(f'<p class="situs">{escape(parcel.get("situs") or "no address recorded")}</p>')

    out.append('<dl class="pairs">')
    out.append(f"<dt>Legal description</dt><dd>{escape(parcel['legal_description'])}</dd>")
    out.append(f"<dt>Acres on the roll</dt><dd>{parcel['legal_acres']}</dd>")
    out.append(f"<dt>Use code</dt><dd>{escape(parcel['property_use'])}</dd>")
    out.append(f"<dt>Longest wait</dt><dd>{wait_words(parcel)}</dd>")
    out.append("</dl>")

    out.append("<h5>Why it is flagged</h5>")
    for flag in parcel["flags"]:
        out.append('<div class="why">')
        out.append(f"<p class=\"what\">{flag_words(flag)}</p>")
        if flag.get("lead_time_days") is not None:
            out.append(f"<p><strong>{flag['lead_time_days']} "
                       f"{escape(flag.get('lead_time_basis') or 'days')}</strong> "
                       f"of notice.</p>")
        elif flag.get("lead_time_not_found"):
            out.append(f"<p class=\"notfound\">{inline(flag['lead_time_not_found'])}</p>")
        if flag.get("lead_time_driver_detail"):
            out.append(f"<p>What the wait is for: "
                       f"{escape(flag['lead_time_driver_detail'])}.</p>")
        if flag.get("lead_time_note"):
            out.append(f"<p class=\"note\">{inline(flag['lead_time_note'])}</p>")
        if flag.get("lead_time_source"):
            source = inline(flag["lead_time_source"])
            if flag.get("lead_time_url"):
                source = (f'<a href="{escape(flag["lead_time_url"])}" '
                          f'rel="noreferrer">{source}</a>')
            out.append(f'<p class="source">Authority: {source}'
                       f'{" &middot; checked " + escape(flag["lead_time_verified_on"]) if flag.get("lead_time_verified_on") else ""}</p>')
        out.append(f'<p class="source">Found in: '
                   f'{escape(flag.get("source_service") or "not recorded")}</p>')
        out.append("</div>")

    out.append("<h5>What this run did not measure on this tract</h5>")
    out.append("<ul class=\"gaps\">")
    out.append(f"<li>Right of entry: <strong>{escape(parcel.get('roe_required') or 'unknown')}"
               f"</strong>. No parcel polygon grants one.</li>")
    if parcel.get("acres_in_corridor") is None:
        out.append("<li>How much of this tract the corridor takes: <strong>not "
                   "measured</strong>.</li>")
    if parcel.get("txdot_owned") is None:
        out.append("<li>Whether TxDOT already owns it: <strong>not checked</strong>.</li>")
    out.append("</ul>")
    out.append("</div>")
    return "\n".join(out)


def safety_rows(f):
    out = []
    for kind, word in drawings.SAFETY_KINDS:
        place = (f["safety"]["by_type"].get(kind) or {}).get("nearest")
        if not place:
            out.append(f"<tr><th>{word}</th><td colspan=\"2\">None found within "
                       f"{f['safety']['search_radius_mi']} miles.</td></tr>")
            continue
        out.append(
            f"<tr><th>{word}</th><td>{escape(place['name'])}<br>"
            f"<span class=\"muted\">{escape(place['address'])}, "
            f"{escape(place['city'])}</span></td>"
            f"<td class=\"num\">{place['distance_from_centerline_mi']:.2f} mi<br>"
            f"<span class=\"muted\">from the centerline</span></td></tr>")
    return "\n".join(out)


def number_strip(f):
    longest = longest_wait(f["flagged"])
    cells = [
        (f"{f['length_mi']}", "miles of corridor"),
        (f"{f['tracts']}", "tracts touched"),
        (f"{len(f['flagged'])}", "carry something that costs time"),
        (f"{f['not_found']} of {f['marks']}", "NGS marks recorded MARK NOT FOUND"),
        (f"{f['sheets']}", f"ROW map sheets, {f['sheet_from']} to {f['sheet_to']}"),
    ]
    if longest:
        cells.append((f"{longest['max_lead_time_days']} days",
                      "longest measured wait on one tract"))
    return "\n".join(
        f'<div class="stat"><span class="big">{escape(big)}</span>'
        f'<span class="small">{escape(small)}</span></div>'
        for big, small in cells)


def layer_controls(scope):
    """The four layers a reader can switch off. ``scope`` is what it means."""
    layers = [("tracts", "All 524 tracts", "on"),
              ("flags", "The 8 flagged tracts", "on"),
              ("control", "Published control marks", "off"),
              ("safety", "Nearest help", "off")]
    out = [f'<div class="layers" data-scope="{scope}">',
           '<span class="layers-label">Layers</span>']
    for key, word, state in layers:
        checked = " checked" if state == "on" else ""
        out.append(f'<label><input type="checkbox" data-layer-toggle="{key}"'
                   f'{checked}> {word}</label>')
    out.append("</div>")
    return "\n".join(out)


def header(f, subtitle):
    return f"""
<header class="masthead">
  <p class="eyebrow">Desktop reconnaissance &middot; corridor screening</p>
  <h1>SH0016, Bexar County</h1>
  <p class="lede">{escape(f['corridor'])} &middot; {f['length_mi']} miles &middot;
     screened {f['half_width_ft']} ft either side of the centerline.</p>
  <p class="stamp">Screened <strong>{escape(f['screened_on'])}</strong> from public
     map services. Reference <code>{escape(f['run_id'])}</code>.
     <a href="{escape(f['map_link'])}" rel="noreferrer">Confirm the location on a
     map</a> before reading further &mdash; a corridor drawn from the wrong route
     looks exactly like this one.</p>
  <p class="variant-note">{subtitle}</p>
</header>
"""


def signature():
    return """
<footer class="signature">
  <p><strong>An RPLS reads this and decides.</strong> Nothing here was measured on
     the ground, nobody has walked the corridor, and this is not a right of entry.
     The licensed surveyor who signs the work remains accountable for every number
     that reaches a client.</p>
</footer>
"""


# --------------------------------------------------------------- variant A
def variant_a(f, map_markup, memo):
    """The map is the page. Click a tract, its card opens below the map."""
    total = len(f["flagged"])
    cards = "\n".join(
        f'<article class="card" data-tract-card="{escape(p["id"])}" hidden>'
        f'<button class="close" data-close-card>Close</button>'
        f'{tract_detail(p, i, total)}</article>'
        for i, p in enumerate(f["flagged"], start=1))
    return f"""
{header(f, "Variant A &mdash; the map is the page. Everything hangs off it.")}
<section class="mapwrap wide">
  {layer_controls("map")}
  <div class="map">{map_markup}</div>
  <p class="hint">Click any amber tract, or its number, to open it.
     <span class="print-only">In print, every tract is open below.</span></p>
</section>
<section class="cards" id="cards-a">
  <h2>The eight tracts that cost time</h2>
  <p class="muted">Nothing is open until you click the map. Printing opens all of them.</p>
  {cards}
</section>
<section>
  <h2>Control</h2>
  <p>Every one of the {f['not_found']} NGS marks in this corridor is recorded
     <strong>MARK NOT FOUND</strong>. Somebody has looked for each of them and could
     not find it. On this evidence the control work is setting new, not recovering
     existing.</p>
  <p>TxDOT publishes {f['txdot_monuments']} distinct monuments in the corridor. The
     two counts are never added together.</p>
</section>
<section>
  <h2>Right-of-way records</h2>
  <p><strong>{f['sheets']} sheets</strong> reach this corridor, dating
     {escape(f['sheet_from'])} to {escape(f['sheet_to'])}.
     {f['sh16_sheets']} of them are SH0016's own, dating {escape(f['sh16_from'])} to
     {escape(f['sh16_to'])}. The rest belong to routes that cross it.</p>
</section>
<section>
  <h2>Crew safety</h2>
  <p class="muted">Where the nearest help is, if the crew needs it.</p>
  <table class="grid">{safety_rows(f)}</table>
</section>
<section class="memo">
  <h2>The memo, in full</h2>
  {memo}
</section>
{signature()}
"""


# --------------------------------------------------------------- variant B
def variant_b(f, map_markup, memo):
    """The list is the page. The map follows it, small. Layers filter the page."""
    total = len(f["flagged"])
    rows = []
    for i, p in enumerate(f["flagged"], start=1):
        kinds = ", ".join(sorted({fl["type"] for fl in p["flags"]}))
        rows.append(f"""
<div class="row" data-tract-row="{escape(p['id'])}">
  <button class="rowhead" data-expand="{escape(p['id'])}" aria-expanded="false">
    <span class="num">{i}</span>
    <span class="who"><strong>{escape(p['owner'])}</strong>
      <span class="muted">{escape(p['id'])} &middot; {escape(kinds)}</span></span>
    {wait_words(p)}
    <span class="chev" aria-hidden="true">+</span>
  </button>
  <div class="rowbody" hidden>{tract_detail(p, i, total)}</div>
</div>""")
    safety = (f["safety"]["by_type"].get("hospital") or {}).get("nearest") or {}
    return f"""
{header(f, "Variant B &mdash; the list is the page. No map until you have read the eight.")}
<section class="strip">{number_strip(f)}</section>
<section data-section="flags">
  <h2>The eight tracts that cost time</h2>
  <p class="muted">Open one to see why it is flagged and what is still unknown about it.</p>
  <div class="rows">{"".join(rows)}</div>
</section>
<section class="mapwrap narrow" data-section="map">
  <h2>Where they are</h2>
  {layer_controls("page")}
  <p class="hint">These switches change the whole page, not only the map.
     Switch off control and the control section goes with it.</p>
  <div class="map">{map_markup}</div>
</section>
<section data-section="control">
  <h2>Control</h2>
  <p>{f['not_found']} of {f['marks']} NGS marks in this corridor are recorded
     <strong>MARK NOT FOUND</strong>. TxDOT publishes {f['txdot_monuments']} distinct
     monuments. Setting new, not recovering.</p>
</section>
<section data-section="tracts">
  <h2>All {f['tracts']} tracts</h2>
  <p>{f['tracts']} tracts touch the corridor. The {total} above are the ones carrying
     something that costs time. The other {f['tracts'] - total} are listed in the
     screening file rather than on this page.</p>
</section>
<section data-section="safety">
  <h2>Nearest help</h2>
  <p>Nearest hospital: <strong>{escape(safety.get('name', 'not found'))}</strong>,
     {safety.get('distance_from_centerline_mi', 0):.2f} miles from the centerline.</p>
  <details><summary>The other three kinds</summary>
    <table class="grid">{safety_rows(f)}</table></details>
</section>
<section>
  <h2>The memo</h2>
  <p>It is not on this page. It is its own document, and it is the one that gets
     read line by line.</p>
  <p><a class="bigcta" href="../../project-sh16/bid-memo.md">Open the bid memo</a>
     <a class="bigcta" href="../../project-sh16/crew-day.md">Open the crew-day build-up</a></p>
</section>
{signature()}
"""


# --------------------------------------------------------------- variant C
def variant_c(f, map_markup, memo):
    """The page is the questions a principal asks, in order. Detail is a drawer."""
    total = len(f["flagged"])
    unknown = ", ".join(unmeasured_waits(f["flagged"]))
    longest = longest_wait(f["flagged"])
    chips = "\n".join(
        f'<button class="chip" data-open-drawer="{escape(p["id"])}">'
        f'<span class="num">{i}</span> {escape(p["owner"])}</button>'
        for i, p in enumerate(f["flagged"], start=1))
    drawers = "\n".join(
        f'<div class="drawerbody" data-drawer="{escape(p["id"])}" hidden>'
        f'{tract_detail(p, i, total)}</div>'
        for i, p in enumerate(f["flagged"], start=1))
    safety = (f["safety"]["by_type"].get("hospital") or {}).get("nearest") or {}
    return f"""
{header(f, "Variant C &mdash; the page answers questions in the order they get asked. No layer switches.")}
<section class="q">
  <h2>Where is the job?</h2>
  <p class="answer">{escape(f['corridor'])}. {f['length_mi']} miles of SH16 through
     Bexar County, screened {f['half_width_ft']} feet either side &mdash;
     {f['area_sq_mi']} square miles of ground.</p>
  <div class="map">{map_markup}</div>
</section>
<section class="q">
  <h2>What will slow it down?</h2>
  <p class="answer">{total} of {f['tracts']} tracts carry something that costs time.
     The longest measured wait is {longest['max_lead_time_days']} calendar days on one
     tract. The {escape(unknown)} tracts carry no published number of days at all,
     which is not the same as none.</p>
  <p class="muted">Pick one to read it in full.</p>
  <div class="chips">{chips}</div>
</section>
<section class="q">
  <h2>Can we get on the land?</h2>
  <p class="answer">Unknown on every tract, and deliberately so. Texas has no
     self-executing right of entry for a surveyor. Nothing in this screening should be
     read as permission to enter.</p>
</section>
<section class="q">
  <h2>What control do we have?</h2>
  <p class="answer">None you can stand on. All {f['not_found']} of the {f['marks']} NGS
     marks in this corridor are recorded MARK NOT FOUND. TxDOT publishes
     {f['txdot_monuments']} distinct monuments. Price this as setting new.</p>
</section>
<section class="q">
  <h2>What records have to be retraced?</h2>
  <p class="answer">{f['sheets']} ROW map sheets reach the corridor, dating
     {escape(f['sheet_from'])} to {escape(f['sheet_to'])}. Sheets of that age mean hand
     retracement from scans that may be hard to read.</p>
</section>
<section class="q">
  <h2>Where does a hurt crew member go?</h2>
  <p class="answer">{escape(safety.get('name', 'Not found'))},
     {safety.get('distance_from_centerline_mi', 0):.2f} miles from the centerline.</p>
  <table class="grid">{safety_rows(f)}</table>
</section>
<section class="q memo">
  <h2>The memo is the rest of this page</h2>
  {memo}
</section>
{signature()}
<div class="drawer" id="drawer" hidden>
  <div class="drawerpanel" role="dialog" aria-modal="true" aria-label="One flagged tract">
    <button class="close" data-close-drawer>Back to the list</button>
    {drawers}
  </div>
</div>
"""


# ---------------------------------------------------------------- the page
CSS = """
:root { --ink:#111827; --muted:#4b5563; --faint:#9ca3af; --rule:#e5e7eb;
        --paper:#ffffff; --stripe:#f9fafb; --teal:#0f766e; --amber:#b45309;
        --amber-fill:#fde68a; --red:#b91c1c; --violet:#6d28d9; }
* { box-sizing: border-box; }
body { margin:0; background:var(--stripe); color:var(--ink);
       font:17px/1.6 "Segoe UI", Helvetica, Arial, sans-serif; }
main { max-width:1180px; margin:0 auto; padding:0 24px 160px; background:var(--paper); }
h1 { font-size:2.3rem; margin:.2em 0 .1em; }
h2 { font-size:1.5rem; margin:2em 0 .4em; }
h3 { font-size:1.2rem; margin:1.6em 0 .3em; }
h4 { font-size:1.05rem; margin:.8em 0 .2em; }
h5 { font-size:.95rem; margin:1.2em 0 .3em; text-transform:uppercase;
     letter-spacing:.06em; color:var(--muted); }
p { margin:.5em 0; }
a { color:var(--teal); }
code { background:var(--stripe); padding:1px 5px; border-radius:4px; font-size:.9em; }
.muted, .small { color:var(--muted); }
section { border-top:1px solid var(--rule); padding-top:.6em; }
.masthead { border:0; padding:32px 0 12px; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.75rem;
           color:var(--faint); margin:0; }
.lede { font-size:1.12rem; color:var(--muted); margin:.2em 0; }
.stamp { font-size:.93rem; color:var(--muted); background:var(--stripe);
         border-left:4px solid var(--teal); padding:10px 14px; margin-top:14px; }
.variant-note { font-size:.9rem; color:var(--violet); font-weight:600; }
.map { border:1px solid var(--rule); background:var(--paper); }
.map svg { display:block; width:100%; height:auto; }
.mapwrap.narrow .map { max-width:760px; }
.hint { font-size:.9rem; color:var(--muted); }
.print-only { display:none; }
.layers { display:flex; flex-wrap:wrap; gap:14px; align-items:center;
          padding:10px 0; font-size:.92rem; }
.layers-label { text-transform:uppercase; letter-spacing:.08em; font-size:.72rem;
                color:var(--faint); }
.layers label { display:flex; gap:6px; align-items:center; cursor:pointer; }
.strip { display:flex; flex-wrap:wrap; gap:8px; border:0; padding:18px 0; }
.stat { flex:1 1 170px; background:var(--stripe); border:1px solid var(--rule);
        border-radius:8px; padding:12px 14px; }
.stat .big { display:block; font-size:1.7rem; font-weight:700; }
.stat .small { display:block; font-size:.82rem; color:var(--muted); line-height:1.35; }
.wait { font-size:.85rem; padding:2px 9px; border-radius:99px; white-space:nowrap; }
.wait.known { background:#ccfbf1; color:#134e4a; }
.wait.unknown { background:var(--amber-fill); color:#78350f; }
.card { border:2px solid var(--amber); border-radius:10px; padding:18px 20px;
        margin:16px 0; position:relative; background:#fffdf5; }
.close { position:absolute; top:12px; right:12px; border:1px solid var(--rule);
         background:var(--paper); border-radius:6px; padding:4px 10px; cursor:pointer; }
.crumb { font-size:.75rem; text-transform:uppercase; letter-spacing:.08em;
         color:var(--faint); margin:0; }
.situs { color:var(--muted); margin-top:0; }
.pairs { display:grid; grid-template-columns:auto 1fr; gap:4px 16px; margin:12px 0; }
.pairs dt { color:var(--muted); font-size:.88rem; }
.pairs dd { margin:0; }
.why { border-left:3px solid var(--amber); padding:2px 0 2px 14px; margin:10px 0; }
.why .what { font-weight:700; margin:0; }
.notfound { color:var(--amber); }
.note { font-size:.93rem; color:var(--muted); }
.source { font-size:.85rem; color:var(--faint); }
.gaps li { margin:.2em 0; }
.rows { border:1px solid var(--rule); border-radius:10px; overflow:hidden; }
.row + .row { border-top:1px solid var(--rule); }
.rowhead { display:flex; gap:14px; align-items:center; width:100%; text-align:left;
           background:var(--paper); border:0; padding:14px 16px; cursor:pointer;
           font:inherit; }
.rowhead:hover { background:var(--stripe); }
.rowhead .num { width:28px; height:28px; border-radius:99px; flex:none;
                background:var(--amber-fill); color:#78350f; font-weight:700;
                display:grid; place-items:center; font-size:.9rem; }
.rowhead .who { flex:1; display:flex; flex-direction:column; }
.rowhead .who .muted { font-size:.83rem; }
.rowhead .chev { color:var(--faint); font-size:1.3rem; width:1em; }
.rowbody { padding:0 16px 16px 58px; background:var(--stripe); }
.chips { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; }
.chip { display:flex; gap:8px; align-items:center; border:1px solid var(--amber);
        background:#fffdf5; border-radius:99px; padding:7px 15px; cursor:pointer;
        font:inherit; font-size:.9rem; }
.chip:hover { background:var(--amber-fill); }
.chip .num { font-weight:700; color:#78350f; }
.q .answer { font-size:1.15rem; }
.grid { border-collapse:collapse; width:100%; margin:10px 0; }
.grid th, .grid td { border-bottom:1px solid var(--rule); padding:9px 10px;
                     text-align:left; vertical-align:top; font-size:.94rem; }
.grid th { width:120px; color:var(--muted); font-weight:600; }
.grid .num { text-align:right; white-space:nowrap; }
.bigcta { display:inline-block; border:1px solid var(--teal); border-radius:8px;
          padding:10px 16px; margin-right:10px; text-decoration:none; }
.memo h3 { border-top:1px solid var(--rule); padding-top:.8em; }
.signature { border-top:3px solid var(--ink); margin-top:2.5em; padding-top:1em;
             font-size:.95rem; }
.drawer { position:fixed; inset:0; background:rgba(17,24,39,.45); z-index:40;
          display:grid; place-items:end center; }
/* `display:grid` above beats the browser's own rule for `hidden`, so the
   drawer opened itself on load until this line existed. */
.drawer[hidden] { display:none; }
.drawerpanel { background:var(--paper); width:min(720px,100%); max-height:92vh;
               overflow:auto; border-radius:14px 14px 0 0; padding:44px 26px 26px;
               position:relative; }
/* The map's own behavior. */
#jobmap .hot { cursor:pointer; }
#jobmap .hot:hover .flagged, #jobmap .hot:focus .flagged { fill:#fbbf24; }
#jobmap .hot.picked .flagged { fill:#f59e0b; stroke:#7c2d12; stroke-width:4; }
#jobmap g[data-layer].off { display:none; }
section.off { display:none; }
/* The floating switcher. Obviously not part of the design being judged. */
#switcher { position:fixed; left:50%; bottom:18px; transform:translateX(-50%);
            z-index:90; display:flex; align-items:center; gap:4px;
            background:#111827; color:#fff; border-radius:99px; padding:6px 8px;
            box-shadow:0 10px 30px rgba(0,0,0,.35); font-size:.9rem; }
#switcher button { background:#374151; color:#fff; border:0; border-radius:99px;
                   width:32px; height:32px; cursor:pointer; font-size:1rem; }
#switcher .label { padding:0 12px; white-space:nowrap; }
#switcher .tag { font-weight:700; }
@media print {
  body { background:#fff; }
  main { max-width:none; padding:0; }
  #switcher, .layers, .close, .chev { display:none !important; }
  .print-only { display:inline; }
  .card, .rowbody { display:block !important; }
  /* A drawer is the one pattern of the three that does not print by itself.
     A and B print because their detail is already in the flow and only
     hidden; C's detail sits inside a closed overlay, and the rule that keeps
     the overlay shut on screen keeps it shut on paper too. This is the print
     equivalent the constraint asks for, and it had to be written by hand. */
  .drawer, .drawer[hidden] { position:static; background:none;
                             display:block !important; }
  .drawerbody, .drawerbody[hidden] { display:block !important; }
  .drawerpanel { max-height:none; width:auto; padding:0; }
  .card, .detail, .row { break-inside:avoid; }
  a[href^="http"]::after { content:" (" attr(href) ")"; font-size:.75em;
                           color:#555; word-break:break-all; }
}
"""

JS = """
(function () {
  var VARIANTS = [
    ["A", "The map is the page"],
    ["B", "The list is the page"],
    ["C", "The page is questions"]
  ];
  var params = new URLSearchParams(location.search);
  var current = (params.get("variant") || "A").toUpperCase();
  if (!VARIANTS.some(function (v) { return v[0] === current; })) current = "A";

  // Show the chosen variant, and move the one shared map into it. The map is
  // 280 KB of tract paths; three copies would be a prototype about file size.
  var map = document.getElementById("mapsource");
  document.querySelectorAll("[data-variant]").forEach(function (node) {
    var on = node.getAttribute("data-variant") === current;
    node.hidden = !on;
    if (on) {
      var slot = node.querySelector(".map");
      if (slot && map) slot.appendChild(map);
    }
  });

  // ---- the switcher
  function go(step) {
    var i = VARIANTS.findIndex(function (v) { return v[0] === current; });
    var next = VARIANTS[(i + step + VARIANTS.length) % VARIANTS.length][0];
    location.search = "?variant=" + next;
  }
  var bar = document.getElementById("switcher");
  bar.querySelector("[data-prev]").addEventListener("click", function () { go(-1); });
  bar.querySelector("[data-next]").addEventListener("click", function () { go(1); });
  var name = VARIANTS.filter(function (v) { return v[0] === current; })[0];
  bar.querySelector(".label").innerHTML =
    '<span class="tag">' + name[0] + '</span> &mdash; ' + name[1];
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    if (e.key === "ArrowLeft") go(-1);
    if (e.key === "ArrowRight") go(1);
    if (e.key === "Escape") closeDrawer();
  });

  // ---- clicking a tract on the map
  function pick(id) {
    document.querySelectorAll("#jobmap .hot").forEach(function (g) {
      g.classList.toggle("picked", g.getAttribute("data-tract") === id);
    });
  }
  document.addEventListener("click", function (e) {
    var hot = e.target.closest ? e.target.closest("#jobmap .hot") : null;
    if (hot) onTract(hot.getAttribute("data-tract"));
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var hot = e.target.closest ? e.target.closest("#jobmap .hot") : null;
    if (hot) { e.preventDefault(); onTract(hot.getAttribute("data-tract")); }
  });

  function onTract(id) {
    pick(id);
    if (current === "A") openCard(id);
    if (current === "B") expandRow(id, true);
    if (current === "C") openDrawer(id);
  }

  // ---- A: a card below the map
  function openCard(id) {
    document.querySelectorAll("[data-tract-card]").forEach(function (card) {
      card.hidden = card.getAttribute("data-tract-card") !== id;
    });
    var open = document.querySelector("[data-tract-card='" + id + "']");
    if (open) open.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (e.target.closest("[data-close-card]")) {
      e.target.closest("[data-tract-card]").hidden = true;
      pick(null);
    }
  });

  // ---- B: the row expands where it is
  function expandRow(id, scroll) {
    var head = document.querySelector("[data-expand='" + id + "']");
    if (!head) return;
    var row = head.parentElement;
    var body = row.querySelector(".rowbody");
    var open = body.hidden;
    body.hidden = !open;
    head.setAttribute("aria-expanded", String(open));
    head.querySelector(".chev").textContent = open ? "\\u2212" : "+";
    if (open && scroll) row.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  document.addEventListener("click", function (e) {
    var head = e.target.closest ? e.target.closest("[data-expand]") : null;
    if (head) { var id = head.getAttribute("data-expand"); expandRow(id, false); pick(id); }
  });

  // ---- C: a drawer over the page
  function openDrawer(id) {
    var drawer = document.getElementById("drawer");
    if (!drawer) return;
    drawer.querySelectorAll("[data-drawer]").forEach(function (d) {
      d.hidden = d.getAttribute("data-drawer") !== id;
    });
    drawer.hidden = false;
    drawer.querySelector(".close").focus();
  }
  function closeDrawer() {
    var drawer = document.getElementById("drawer");
    if (drawer) drawer.hidden = true;
    pick(null);
  }
  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (e.target.closest("[data-open-drawer]")) {
      var id = e.target.closest("[data-open-drawer]").getAttribute("data-open-drawer");
      pick(id); openDrawer(id);
    }
    if (e.target.closest("[data-close-drawer]")) closeDrawer();
    if (e.target.id === "drawer") closeDrawer();
  });

  // ---- layers. What a switch reaches is the thing the variants disagree on.
  document.addEventListener("change", function (e) {
    var box = e.target.closest ? e.target.closest("[data-layer-toggle]") : null;
    if (!box) return;
    var key = box.getAttribute("data-layer-toggle");
    var scope = box.closest(".layers").getAttribute("data-scope");
    var layer = document.querySelector("#jobmap g[data-layer='" + key + "']");
    if (layer) layer.classList.toggle("off", !box.checked);
    if (scope === "page") {
      var section = document.querySelector("section[data-section='" + key + "']");
      if (section) section.classList.toggle("off", !box.checked);
    }
  });

  // Start with the two layers that are off in the markup actually off.
  document.querySelectorAll("[data-layer-toggle]").forEach(function (box) {
    if (!box.checked) {
      var layer = document.querySelector("#jobmap g[data-layer='" +
        box.getAttribute("data-layer-toggle") + "']");
      if (layer) layer.classList.add("off");
    }
  });
})();
"""


def page(f, variants, map_markup):
    bodies = "\n".join(
        f'<div data-variant="{key}" hidden>{markup}</div>'
        for key, markup in variants)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PROTOTYPE &mdash; job page, SH0016 Bexar County</title>
<style>{CSS}</style>
</head>
<body>
<div id="mapsource-holder" hidden><div id="mapsource">{map_markup}</div></div>
<main>{bodies}</main>
<div id="switcher" aria-label="Prototype variant switcher">
  <button data-prev aria-label="Previous variant">&#8592;</button>
  <span class="label"></span>
  <button data-next aria-label="Next variant">&#8594;</button>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    document, capture = drawings.load(PROJECT)
    f = facts(document, capture)
    markup = map_svg(document, capture, f)
    memo_markdown = (PROJECT / "bid-memo.md").read_text(encoding="utf-8")
    memo = "\n".join([
        memo_section(memo_markdown, "What is not known, and why"),
        memo_section(memo_markdown, "What was found"),
        memo_section(memo_markdown, "What this memo is not"),
    ])
    variants = [
        ("A", variant_a(f, "", memo)),
        ("B", variant_b(f, "", memo)),
        ("C", variant_c(f, "", memo)),
    ]
    OUT.write_text(page(f, variants, markup), encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT} ({size / 1024:.0f} KB)")
    print("open it, then use the bar at the bottom or the left and right arrow keys")
    print("  ?variant=A  the map is the page")
    print("  ?variant=B  the list is the page")
    print("  ?variant=C  the page is questions")


if __name__ == "__main__":
    main()
