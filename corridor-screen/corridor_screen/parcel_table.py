"""The flagged parcel table -- which tracts cost time, and how much.

Specification section 2: "It does not produce the bid memo, the parcel table,
or the crew-day build-up. Those are separate jobs that read this file. **One
fetch, many renderings.**" This is the second of the three.

Like the bid memo it reads ``screening.json`` and calls no service, and nothing
in it is written by hand: a number not in the run does not appear here.

----

Why this one is drawn as well as written
========================================

Issue #23 asks for a table "readable from the back of a conference room" that
"fits on screen without scrolling during the demo." A Markdown file cannot
honestly promise either, because whatever renders it decides the type size.

Specification section 9 already settled how this repo answers that: **SVG** --
"a drawing stored as plain text rather than as pixels ... It stays sharp on a
projector at any size. It needs nothing installed." So this writes both. The
Markdown is the artifact a reader keeps and a pull request can diff. The drawing
is the thing on the projector at 1:18.

----

The column that has no number in it
===================================

**Seven of the eight flagged parcels on SH16 have no lead time at all**, and
that is not a gap in the run. ``docs/corridor-screen/lead-times.md`` looked for a
school notice period and did not find one, because
`Tex. Educ. Code § 22.0834 <https://statutes.capitol.texas.gov/Docs/ED/htm/ED.22.htm>`_
is a background-check rule rather than a notice period. That page is blunt about
what the tool then does: "It is not reported as clear. It is reported as
unmeasured, which is a different thing, and it is the same distinction as
`unknown` against `no`."

A blank cell, a dash or a zero would undo that on the biggest screen in the
room, in front of the people most likely to quote it. So the wait column never
holds any of the three. It holds a number with the days it counts, or the words
"not found" with the flag nobody could price.

**That is also why the unmeasured rows sort to the top.** A parcel whose wait
nobody has measured needs a phone call before a parcel whose wait is a known 14
days, because the call is what turns the unknown into a date. Sorting them to
the bottom would read, correctly enough for a room at a glance, as "these are
the easy ones."
"""

import argparse
import json
import sys
from pathlib import Path

from .cache import long_path, write_text
from .sources import FLAG_SOURCES

TABLE_NAME = "flagged-parcels.md"
DRAWING_NAME = "flagged-parcels.svg"

# The flag types the tool knows how to look for, read off the same place the
# run reads them. A copy of this list here would silently report a fifth type as
# screened the day somebody added one, which is the failure this whole file is
# about. `bid_memo` derives it the same way.
ALL_FLAG_TYPES = tuple(kind for _, kind in FLAG_SOURCES)

# What a value reads as when the run did not record it. Never a zero, never a
# dash: a reader has to be able to tell "none" from "not measured".
UNRECORDED = "not recorded"

# 16:9, the shape of every projector this will meet. The viewBox is what makes
# the drawing resolution-independent: every number below is a coordinate space
# rather than pixels, so one file is sharp on a laptop and on a 30-foot screen.
WIDTH, HEIGHT = 1920, 1080

# How many rows the drawing has room for at a size that reads from the back of
# a room: ten at 60 apart, under a title and above the citations and the run
# stamp. A corridor with more says how many more rather than quietly showing the
# first ten, and `_for_screen` decides *which* ten.
ROWS_ON_SCREEN = 10

# Where the rows sit, how far apart, and how far apart the citation lines are.
# Named rather than scattered because the citation block is laid out **upward**
# from the warning line, so the two can meet in the middle if these drift apart.
# There is a test on that.
ROW_TOP, ROW_STEP, CITE_STEP = 284, 60, 26

# The warning line, and the floor the citation block is stacked up from.
NOTE_Y = HEIGHT - 72

# The four columns: heading, where it starts, how wide. Four because a fifth
# stops being readable from the back, and these four answer what the room is
# asking -- which tract, whose, what is on it, how long is the wait.
#
# The last one ends exactly on the right margin: 1460 + 400 = 1860 = WIDTH - 60.
# Text is clipped to these widths, so a column that overran would not look
# wrong; it would silently shorten whatever sat inside it.
COLUMNS = (
    ("Parcel", 60, 300),
    ("Owner", 380, 520),
    ("What is on it", 920, 520),
    ("Longest wait", 1460, 400),
)


def _screened_types(document):
    return list((document.get("run") or {}).get("screened_for") or [])


def rows(document):
    """The flagged parcels, in the order somebody should start work on them.

    Unmeasured first, then longest known wait first, then by parcel id so two
    runs of the same corridor put the same tract in the same place.
    """
    flagged = [p for p in (document.get("parcels") or []) if p.get("flags")]
    return sorted(
        flagged,
        key=lambda p: (
            p.get("max_lead_time_days") is not None,
            -(p.get("max_lead_time_days") or 0),
            str(p.get("id") or ""),
        ),
    )


def wait_cell(parcel, with_driver=True):
    """The longest wait on this tract, or the words saying nobody found one.

    Never blank, never a dash, never a zero. See this module's own docstring:
    those three are how a table turns "we did not find a number" into "there is
    no delay," and they are not the same statement.

    ``with_driver`` names which flag set the number -- worth having in the
    Markdown, where a tract may carry two flags and a reader wants to know which
    one drove the wait. The drawing turns it off, because the column beside it
    already says `cemetery (on)` and the repetition cost the one confirmed
    statutory figure on SH16 its last three characters.
    """
    days = parcel.get("max_lead_time_days")
    unpriced = parcel.get("lead_time_not_found") or []

    if days is not None:
        basis = parcel.get("max_lead_time_basis") or "days, basis not recorded"
        driver = parcel.get("lead_time_driver")
        cell = f"{days} {basis}" + (f" ({driver})" if with_driver and driver else "")
        # **And**, not instead. `lead-times.md`: a parcel with a cemetery and a
        # school shows 14 days *and* `school` in the not-found list, "because 14
        # is the longest number anybody can stand behind and it is not the whole
        # answer." Returning only the number here would report an unknown as
        # settled, on the row where a reader is least likely to look twice.
        return cell + (f" + {', '.join(unpriced)} not found" if unpriced else "")

    # Falling back to the flag types on the parcel matters: a flag type with no
    # row in the lead time table at all would otherwise leave this cell with
    # nothing to say.
    unpriced = unpriced or sorted(
        {f.get("type") for f in parcel.get("flags") or [] if f.get("type")}
    )
    return "not found — " + ", ".join(unpriced) if unpriced else "not found"


def flag_cell(parcel):
    """What is on the tract, and whether it is on it or beside it.

    The relation is carried rather than summarized. "On" and "adjacent" are
    different jobs: one of them needs a right of entry on that tract and the
    other may not.
    """
    parts = []
    for flag in parcel.get("flags") or []:
        kind = flag.get("type") or "flag"
        relation = flag.get("relation") or ""
        distance = flag.get("distance_ft")
        if relation == "adjacent" and distance is not None:
            parts.append(f"{kind} (adjacent, {distance:.0f} ft)")
        elif relation:
            parts.append(f"{kind} ({relation})")
        else:
            parts.append(kind)
    return ", ".join(parts)


def _unscreened(document):
    """Flag types this run never checked for.

    A type missing from ``screened_for`` is unknown on every parcel, never
    clear. The bid memo learned this the same way and says so too.
    """
    return sorted(set(ALL_FLAG_TYPES) - set(_screened_types(document)))


def _types_on(table):
    """The flag types that actually appear on this corridor's table.

    Used to keep the citation list to the numbers a reader can see. A source
    list carrying railroads a corridor does not have is noise, and noise is how
    a citation block stops being read.
    """
    return sorted({flag.get("type") for parcel in table
                   for flag in parcel.get("flags") or [] if flag.get("type")})


def citations(document, table=None):
    """The source behind every number on the table, and behind every gap.

    **This is not decoration and it is not a footnote.** CLAUDE.md: "Numbers
    with legal consequence -- accuracy tolerances, notice periods, fees -- get a
    source link next to them." ``docs/corridor-screen/lead-times.md`` puts it
    harder: "a lead time is worth exactly what its citation is worth."

    The first draft of this file printed ``14 calendar days`` in both outputs
    and cited it in neither -- the single confirmed statutory figure in the run
    was the one number with no source beside it, and on the projector it stood
    bare in front of the people most likely to quote it. The same miss had
    already been caught once, on #22, which is why it is a seam with tests
    rather than a line in a template.

    A "not found" is cited too. Without where it looked, "not found" is not a
    finding -- it is a shrug.
    """
    table = rows(document) if table is None else table
    published = (document.get("run") or {}).get("lead_times") or {}
    out = []
    for kind in _types_on(table):
        entry = published.get(kind) or {}
        days = entry.get("lead_time_days")
        basis = entry.get("lead_time_basis") or ""
        wait = f"{days} {basis}".strip() if days is not None else "not found"
        out.append({
            "type": kind,
            "label": entry.get("label") or kind.title(),
            "wait": wait,
            "source": entry.get("source") or "no source recorded in the run",
            "url": entry.get("url"),
            "not_found": entry.get("not_found"),
        })
    return out


# ----------------------------------------------------------------- the Markdown


def _corridor_lines(document):
    """Flags recorded against the run rather than against any one tract.

    A pipeline crossing forty parcels is one of these. An earlier draft of the
    bid memo read only the per-parcel flags, so a corridor carrying one would
    have been described as carrying nothing. That mistake is not repeated here.
    """
    flags = document.get("corridor_flags") or []
    if not flags:
        return []
    lines = ["## Across the corridor, not on one tract", ""]
    for flag in flags:
        name = flag.get("name") or flag.get("type") or "unnamed"
        crossed = flag.get("parcels_crossed")
        days = flag.get("lead_time_days")
        basis = flag.get("lead_time_basis") or ""
        wait = f"{days} {basis}".strip() if days is not None else "not found"
        where = f", crossing {crossed} parcels" if crossed is not None else ""
        lines.append(f"- **{name}** — {flag.get('type', 'flag')}{where}. Wait: {wait}")
    return lines + [""]


def build(document):
    """The Markdown table, and what has to be said around it to be honest."""
    run = document.get("run") or {}
    alignment = document.get("alignment") or {}
    table = rows(document)

    lines = [f"# Flagged parcels — {alignment.get('source_path', 'this corridor')}", ""]

    if run.get("status") != "complete":
        # Plain blockquote rather than an admonition, for the reason
        # `bid_memo` records: this file is read on GitHub, where MkDocs'
        # `!!! warning` comes out as literal text and an indented code block.
        # The one sentence that must be unmissable would be the one rendered as
        # noise.
        lines += [
            f"> ## ⚠ This run was recorded as **{run.get('status', 'incomplete')}**",
            ">",
            "> Some services were never reached, so this table is a floor rather than",
            "> a count. What was missed is in the screening file's own honesty block.",
            "",
        ]

    lines += [
        f"**{len(table)} of {len(document.get('parcels') or [])} parcels in the corridor "
        f"carry something that costs time.** Sorted so the tract needing a phone "
        f"call soonest is first.",
        "",
    ]

    unscreened = _unscreened(document)
    if unscreened:
        lines += [
            f"**Not checked at all: {', '.join(unscreened)}.** No parcel below is "
            "reported as clear of these. They were not looked for.",
            "",
        ]

    lines += ["| Parcel | Owner | What is on it | Longest wait |", "|---|---|---|---|"]
    for parcel in table:
        lines.append(
            f"| `{parcel.get('id', '')}` | {parcel.get('owner') or UNRECORDED} "
            f"| {flag_cell(parcel)} | {wait_cell(parcel)} |"
        )
    lines.append("")

    unmeasured = [p for p in table if p.get("max_lead_time_days") is None]
    if unmeasured:
        lines += [
            f"**{len(unmeasured)} of these {len(table)} have no number**, and that is "
            "a finding rather than a gap. Where a wait says *not found*, this repo "
            "looked for a published notice period and did not find one — see "
            "[lead times](../docs/corridor-screen/lead-times.md), which records "
            "where it looked. It is not a shorter wait. It is an unmeasured one, "
            "and somebody has to make the call that turns it into a date.",
            "",
        ]

    lines += _corridor_lines(document)

    cited = citations(document, table)
    if cited:
        lines += [
            "## Where these numbers come from",
            "",
            "A lead time is worth exactly what its citation is worth. Every URL below",
            "was opened and read on the date the run records.",
            "",
            "| Flag | Wait | Source |",
            "|---|---|---|",
        ]
        for entry in cited:
            source = (f"[{entry['source']}]({entry['url']})" if entry["url"]
                      else entry["source"])
            lines.append(f"| {entry['label']} | {entry['wait']} | {source} |")
        lines.append("")
        for entry in cited:
            if entry["not_found"]:
                lines += [f"**{entry['label']} — where we looked.** {entry['not_found']}", ""]

    lines += [
        "---",
        "",
        f"Run `{run.get('mode', '?')}`, finished {run.get('finished_at', 'not recorded')}. "
        f"Corridor half-width {run.get('half_width_ft', '?')} ft, adjacent within "
        f"{run.get('adjacent_distance_ft', '?')} ft. Nothing here was typed by hand; "
        "every value is read from `screening.json`.",
    ]
    return "\n".join(lines).rstrip() + "\n"


# ------------------------------------------------------------------- the drawing


def _escape(text):
    """Text safe to drop into XML.

    Bexar owner names really do carry ampersands, and one unescaped `&` makes
    the whole drawing fail to parse -- which on a projector means a blank
    rectangle rather than an error anybody can read.
    """
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _fit(text, width, size=26):
    """Clip a string to a column, with an ellipsis when it had to be cut.

    Rough, because the drawing uses one common font stack and the exact glyph
    widths are not knowable here. A character averages a little over half the
    type size, so that is the ratio used, and the ellipsis is what says a name
    was shortened rather than being that short.
    """
    room = max(4, int(width / (size * 0.55)))
    text = str(text)
    return text if len(text) <= room else text[: room - 1].rstrip() + "…"


def _for_screen(table):
    """Which rows the drawing has room for, and how many it leaves off.

    **A date somebody is bound by does not come off the screen to make room for
    a date nobody has found yet.** The sort in ``rows`` puts unmeasured waits
    first, because those are the ones needing a phone call today, and that is
    right for a file nobody has to fit on a screen. Applied to a capped drawing
    it meant the single confirmed statutory deadline on a busy corridor was the
    **first** row cut, silently, from the projector.

    So confirmed waits are seated first -- longest first, since ``rows`` already
    ordered them that way -- and whatever room is left goes to the unmeasured
    ones. Display order is unchanged: the table still reads in the order
    ``rows`` chose.
    """
    confirmed = [p for p in table if p.get("max_lead_time_days") is not None]
    unmeasured = [p for p in table if p.get("max_lead_time_days") is None]
    seated = confirmed[:ROWS_ON_SCREEN]
    seated += unmeasured[: max(0, ROWS_ON_SCREEN - len(seated))]
    keep = {id(p) for p in seated}
    return [p for p in table if id(p) in keep], max(0, len(table) - len(seated))


def svg(document):
    """The projector rendering. Specification section 9's format, and its reason.

    One screen, no scrolling: a corridor with more flagged parcels than fit is
    capped, and the drawing says how many it did not show. Twelve of two hundred
    shown silently would be the quiet wrong answer, on the biggest surface in
    the room.
    """
    run = document.get("run") or {}
    alignment = document.get("alignment") or {}
    table = rows(document)
    shown, hidden = _for_screen(table)
    title = _escape(_fit(alignment.get("source_path") or "Flagged parcels", 1800, 46))
    standfirst = _escape(
        f"{len(table)} of {len(document.get('parcels') or [])} parcels "
        f"carry something that costs time"
    )

    out = [
        # `viewBox` and no width or height. That is what makes one file fill a
        # projector, a slide and a docs page without being re-exported for
        # each -- specification section 9's "stays sharp on a projector at any
        # size". A fixed pixel width would pin it to one of the three.
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        f'<text x="60" y="86" font-size="46" font-weight="700" fill="#111827">{title}</text>',
        f'<text x="60" y="136" font-size="30" fill="#4b5563">{standfirst}</text>',
    ]

    # Column headings, then a rule under them.
    for label, x, _width in COLUMNS:
        out.append(f'<text x="{x}" y="212" font-size="27" font-weight="700" '
                   f'fill="#374151">{_escape(label)}</text>')
    out.append(f'<line x1="60" y1="232" x2="{WIDTH - 60}" y2="232" '
               f'stroke="#d1d5db" stroke-width="2"/>')

    for index, parcel in enumerate(shown):
        y = ROW_TOP + index * ROW_STEP
        if index % 2:
            out.append(f'<rect x="44" y="{y - 40}" width="{WIDTH - 88}" height="56" '
                       f'fill="#f9fafb"/>')
        unmeasured = parcel.get("max_lead_time_days") is None
        cells = (
            parcel.get("id") or "",
            parcel.get("owner") or UNRECORDED,
            flag_cell(parcel),
            wait_cell(parcel, with_driver=False),
        )
        for (label, x, width), value in zip(COLUMNS, cells):
            # The unmeasured wait is the one cell that earns a color, because it
            # is the one a reader is most likely to mistake for "nothing to do".
            fill = "#b45309" if (label == "Longest wait" and unmeasured) else "#111827"
            weight = "600" if label == "Longest wait" else "400"
            out.append(f'<text x="{x}" y="{y}" font-size="26" fill="{fill}" '
                       f'font-weight="{weight}">{_escape(_fit(value, width))}</text>')

    footer = (
        f"Run {run.get('mode', '?')}, finished {run.get('finished_at', 'not recorded')}. "
        f"Half-width {run.get('half_width_ft', '?')} ft."
    )
    if hidden:
        footer = (f"{hidden} more flagged parcels are not shown here; the Markdown "
                  f"beside this carries all {len(table)}. ") + footer
    unscreened = _unscreened(document)
    if unscreened:
        footer = f"Not checked at all: {', '.join(unscreened)}. " + footer

    # **The source goes on the screen, not only in the file.** A URL cannot be
    # read from the back of a room, but a section number can, and a notice
    # period shown without one is exactly the thing a room full of licensed
    # surveyors should not be invited to write down. The full links are in the
    # Markdown beside this.
    #
    # One line per flag type, laid out upward from the note. Joining them into
    # one line is what the first draft did, and it clipped `Tex. Educ. Code
    # § 22.0834` mid-citation -- which is worse than no citation, because it
    # looks like one.
    cited = citations(document, table)
    for index, entry in enumerate(cited):
        y = NOTE_Y - 38 - (len(cited) - 1 - index) * CITE_STEP
        line = f"{entry['label']} — {entry['wait']}: {entry['source']}"
        out.append(f'<text x="60" y="{y}" font-size="20" fill="#6b7280">'
                   f'{_escape(_fit(line, 1800, 20))}</text>')

    # The one sentence that has to survive being read from the back of a room.
    note = _escape(_fit(
        "A wait reading “not found” is unmeasured, not zero. "
        "Somebody has to make that call.", 1800, 23))
    out.append(f'<text x="60" y="{NOTE_Y}" font-size="23" fill="#b45309">{note}</text>')
    out.append(f'<text x="60" y="{HEIGHT - 36}" font-size="21" fill="#6b7280">'
               f'{_escape(_fit(footer, 1800, 21))}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def write(document, out_dir):
    """Both renderings, and the paths they went to."""
    table_path = Path(out_dir) / TABLE_NAME
    drawing_path = Path(out_dir) / DRAWING_NAME
    write_text(table_path, build(document))
    write_text(drawing_path, svg(document))
    return [table_path, drawing_path]


def main(argv=None):
    """``python -m corridor_screen.parcel_table --out ../project-sh16``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen parcel-table",
        description="Write the flagged parcel table from a screening run.",
    )
    parser.add_argument("--out", required=True,
                        help="The project directory holding screening.json")
    args = parser.parse_args(argv)

    source = Path(args.out) / "screening.json"
    with open(long_path(source), "r", encoding="utf-8") as handle:
        document = json.load(handle)

    table = rows(document)
    for path in write(document, args.out):
        print(f"  written  {path}")
    unmeasured = sum(1 for p in table if p.get("max_lead_time_days") is None)
    print(f"  flagged  {len(table)} parcels, {unmeasured} with no published wait")
    if len(table) > ROWS_ON_SCREEN:
        print(f"  note     the drawing shows {ROWS_ON_SCREEN} and says so; "
              f"the Markdown carries all {len(table)}")
    if document["run"]["status"] != "complete":
        print("  note     the run was incomplete, and the table says so at the top")
    return 0


if __name__ == "__main__":
    sys.exit(main())
