"""The memo a principal reads before pricing the job.

Specification section 2 is blunt that the screening tool does not produce this:
"It does not produce the bid memo, the parcel table, or the crew-day build-up.
Those are separate jobs that read this file. **One fetch, many renderings.**"
This is the first of those three.

It reads ``screening.json`` and writes Markdown. Nothing here calls a service,
and **nothing here is written by hand** -- if a number is not in the run, it does
not appear in the memo.

----

Why this output is the easiest one to do damage with
====================================================

Every other artifact this tool produces looks like what it is: a JSON file, a
table, a log. This one looks like a letter from a firm, and it will be read with
the authority that carries. Four rules bind it, and each has tests.

**A number nobody measured never appears as a number.** ``acres_in_corridor`` is
``None`` on every parcel, because the tool counts tracts and does not yet measure
how much of each one the corridor takes. Summing that column would put "0.0
acres" in front of a principal and nobody would notice until it was priced. The
same rule kills defaults: a missing length prints "not recorded", never "0.00
miles".

**A notice period never appears without its citation.** CLAUDE.md: "Numbers with
legal consequence -- accuracy tolerances, notice periods, fees -- get a source
link next to them." ``docs/corridor-screen/lead-times.md`` puts it harder: "a
lead time is worth exactly what its citation is worth." The run carries the
source and URL for every one; this memo prints them.

**Nothing found gets quietly dropped.** A pipeline crossing forty parcels is
recorded against the run rather than any one tract, and an earlier draft of this
file read only the per-parcel flags -- so that corridor would have been described
as carrying nothing. Anything the run recorded and this memo cannot place still
gets said.

**Uncertainty gets a heading, not a footnote.** The ticket asks for it "stated
plainly rather than buried inside a number." So what is unknown, what was not
checked, and what no public source publishes at all come **before** the findings
they qualify.

----

What it deliberately does not do
================================

**It does not price anything.** No rate, no crew-day count, no total. Crew days
are issue #24 and belong where the arithmetic can be argued with line by line.

**It does not carry the crew safety sheet.** Specification section 10 is
explicit that the nearest hospital and the rest are "a party chief's output
rather than an estimator's" and that "an estimator never reads it at all." A bid
memo is the estimator's document. The block is in the screening file for whoever
does need it.

**It does not decide anything.** An RPLS reads it and decides, and it says so.
"""

import argparse
import json
import sys
from pathlib import Path

from . import row_maps
from .cache import long_path, write_text
from .sources import FLAG_SOURCES

MEMO_NAME = "bid-memo.md"

# The flag types the tool knows how to look for, read off the same place the run
# reads them, so a type missing from `screened_for` can be named rather than
# being silently absent.
ALL_FLAG_TYPES = tuple(kind for _, kind in FLAG_SOURCES)

# What a value reads as when the run did not record it. Never a zero, never a
# dash: a reader has to be able to tell "none" from "not measured".
UNRECORDED = "not recorded"


def _plural(count, one, many=None):
    return one if count == 1 else (many or one + "s")


def _number(value, spec="", fallback=UNRECORDED):
    """A figure, or a word saying there is no figure. Never a default zero."""
    if value is None:
        return fallback
    return format(value, spec) if spec else str(value)


def _sentence(text):
    """One field's prose as a sentence: capitalized, ending in a full stop."""
    text = (text or "").strip().rstrip(".")
    return text[0].upper() + text[1:] + "." if text else ""


def _route_key(document):
    """The corridor's own route, as the ROW map service spells it.

    The run records ``SH0016-KG DFO 347.7 to 356.367``; the sheets are grouped
    under ``SH0016``. The suffix is the roadbed -- ``KG`` for single roadbed --
    and is documented on
    ``docs/data-sources/txdot-roadways.md``. Derived rather than hard-coded, so
    this memo is not a memo about SH 16 that happens to compile for anything
    else.
    """
    source = ((document.get("alignment") or {}).get("source_path") or "").strip()
    if not source:
        return None
    return source.split()[0].split("-")[0] or None


def _title(document):
    """What the memo is about, from the run rather than from this file."""
    route = _route_key(document)
    area = (document.get("run") or {}).get("area", "")
    where = area.replace("texas-", "").replace("-", " ").title()
    if route and where:
        return f"# Desktop reconnaissance — {route}, {where} County"
    return "# Desktop reconnaissance"


def _heading(document):
    run, alignment = document["run"], document.get("alignment") or {}
    length = _number(alignment.get("length_mi"), ".2f")
    lines = [
        _title(document),
        "",
        f"**Corridor.** {alignment.get('source_path', UNRECORDED)}, {length} miles, "
        f"screened {_number(run.get('half_width_ft'), 'g')} feet either side of "
        "the centerline.",
        "",
        f"**Screened on** {run['started_at'][:10]}. **Reference** `{run['run_id']}`.",
        "",
        f"[Confirm the location on a map]({run['map_link']}) before reading further. "
        "A corridor drawn from the wrong route looks exactly like this one.",
        "",
    ]
    if run["status"] != "complete":
        # Plain bold rather than an admonition. This file is read on GitHub,
        # where MkDocs' `!!! danger` renders as literal text and an indented
        # code block -- so the one sentence that must be unmissable would have
        # been the one that came out as noise.
        lines += [
            "> ## ⚠ This run did not finish — it is recorded as incomplete",
            ">",
            f"> It stopped at **{run.get('stopped_at_service')}**. Everything below "
            "covers only what was reached before that, and the corridor has **not "
            "been screened in full**.",
            ">",
            "> Do not price from this memo until a complete run replaces it.",
            "",
        ]
    return lines


def _scope(document):
    dates = sorted({s["captured_at"][:10] for s in document.get("services", [])
                    if s.get("captured_at")})
    when = dates[0] if len(dates) == 1 else (
        f"{dates[0]} to {dates[-1]}" if dates else UNRECORDED)
    corridor = document.get("corridor") or {}
    return [
        "## What was done",
        "",
        "Public map services were read for the corridor above — "
        f"{_number(corridor.get('area_sq_mi'), '.2f')} square miles of ground — and "
        "every answer they gave was saved with the date it was obtained and the "
        "exact request that produced it.",
        "",
        f"The answers in this memo were obtained on **{when}**. Nothing here is "
        "live, and nothing here is older than that date.",
        "",
        "This is desktop work. No one has walked the corridor.",
        "",
    ]


def _roe_note():
    """Right of entry, with the sections that actually say so.

    An earlier draft said "right of entry is not a statutory right in Texas,"
    flat. That is wrong for an LSLS, and specification section 11 is more
    careful than the draft was.
    """
    return [
        "**Right of entry is unknown on every tract, and deliberately so.** Texas "
        "has no self-executing right of entry for a surveyor: an RPLS refused "
        "permission **may seek** a court order (Tex. Occ. Code § 1071.3585), while "
        "an LSLS acting officially **is entitled to** one (Tex. Occ. Code "
        "§ 1071.358). No parcel polygon establishes either. Nothing in this "
        "screening should be read as permission to enter.",
        "",
    ]


def _suspect_date(document):
    """Doubt the oldest sheet date -- but only if the memo is quoting it.

    The screening file carries this caveat for the corridor as a whole. This
    memo only raises it when the date it actually prints is that one, because a
    warning about a number the reader cannot see is noise, and noise is how
    warnings get ignored.

    The figures are the named constants ``row_maps`` uses for its own note --
    facts about the service, like its paging cap, rather than hand-written
    numbers. The sentence is written for a principal rather than for a
    reader of the screening file.
    """
    sheets = document.get("row_maps") or {}
    spread = sheets.get("date_range") or {}
    if spread.get("from") != row_maps.SUSPECT_DATE:
        return []
    oldest = spread.get("oldest_sheet")
    names_it = f" That date is on sheet {oldest}." if oldest else ""
    return [
        f"**The oldest sheet date below may not be a date at all.** "
        f"{row_maps.SUSPECT_DATE} appears on {row_maps.SUSPECT_DATE_RECORDS} of "
        f"that service's {row_maps.SERVICE_RECORDS:,} records, and the service "
        "publishes no empty dates anywhere — which looks like a stand-in for a "
        "date nobody recorded. We could not confirm it: the same records include "
        f"{row_maps.EARLY_DATED_RECORDS} dated after {row_maps.SUSPECT_DATE} and "
        f"before 1917.{names_it} Check it against the drawing before quoting the "
        "age of these records.",
        "",
    ]


def _uncertain(document):
    run = document["run"]
    rows = document.get("parcels") or []
    lines = [
        "## What is not known, and why",
        "",
        "Read this before the findings. Every item here is a gap this screening "
        "cannot close, and each one is a question somebody still has to answer.",
        "",
        "**No public source publishes these at all.**",
        "",
    ]
    for item in run.get("not_screenable", []):
        lines.append(f"- **{item['type'].capitalize()}** — {item['reason']}.")
    lines += [
        "",
        "A corridor is not clear of either of these because this memo does not "
        "mention them. Somebody has to look.",
        "",
    ]

    missed = [t for t in ALL_FLAG_TYPES if t not in run.get("screened_for", [])]
    if missed:
        lines += [
            f"**Not checked on this run: {', '.join(sorted(missed))}.** No tract "
            "below is reported as clear of them, because none was asked about.",
            "",
        ]

    # **This caveat appears either way, and that is the point of it.** It used
    # to print only when the roadway block was never screened, so filling that
    # block in deleted the sentence from a client-facing memo -- at the exact
    # moment a real TxDOT width appeared in the file and became something a
    # reader could mistake for the corridor. Caught on the review of
    # [#183](https://github.com/RickSmith/survey-recon/issues/183).
    roadway = document.get("roadway") or {}
    if roadway.get("status") == "not-screened":
        lines += [
            "**The existing right-of-way width was not read**, nor the lane count "
            "or the traffic. So the corridor width used here is the one stated "
            "above — a number somebody chose — and not the width TxDOT holds.",
            "",
        ]
    else:
        width = (roadway.get("row_width_ft") or {}).get("low")
        held = f"{width:,} ft" if width is not None else "no width at all"
        lines += [
            f"**TxDOT publishes {held} of right of way over this corridor, and "
            "that is not the corridor used here.** The width above is the one "
            "stated for this run — a number somebody chose — and the two are "
            "different things. Neither is a boundary: where the right of way "
            "actually runs is drawn on the ROW map sheets, and nothing in this "
            "memo has been measured against them.",
            "",
        ]

    if any(p.get("acres_in_corridor") is None for p in rows):
        lines += [
            "**How much of each tract the corridor takes was not measured.** The "
            "tracts were counted and identified; the area of the take was not "
            "calculated. A count of tracts is not an acreage, and this memo does "
            "not offer one.",
            "",
        ]

    if rows and all((p.get("roe_required") or "unknown") == "unknown" for p in rows):
        lines += _roe_note()

    if any(p.get("txdot_owned") is None for p in rows):
        lines += [
            "**Whether TxDOT already owns a tract was not checked.** Some of the "
            "tracts counted below may already be in state hands.",
            "",
        ]

    lines += _unconfirmed_lead_times(document, rows)
    lines += _suspect_date(document)

    warnings = document.get("warnings") or []
    if warnings:
        lines += ["**The run doubted its own answers in these places.**", ""]
        for warning in warnings:
            lines.append(
                f"- *{warning['check']}* on {warning['service']} — "
                f"{warning['detail']} {warning.get('what_to_do', '')}".rstrip()
            )
        lines.append("")
    return lines


def _unconfirmed_lead_times(document, rows):
    """Flag types carrying no number, with where somebody already looked.

    The run's lead-time table records a full account of the search for each
    one. Reducing that to "not confirmed" would throw away the most useful part
    -- somebody re-doing this work needs to know which sources were already
    tried.
    """
    unconfirmed = sorted({t for p in rows for t in (p.get("lead_time_not_found") or [])})
    if not unconfirmed:
        return []
    table = (document.get("run") or {}).get("lead_times") or {}
    lines = [
        f"**No published notice period was confirmed for: "
        f"{', '.join(unconfirmed)}.** Those tracts carry the flag and no number. "
        "They are not zero-notice; they are unmeasured, and the difference "
        "matters to a schedule.",
        "",
    ]
    for kind in unconfirmed:
        entry = table.get(kind) or {}
        if entry.get("not_found"):
            lines += [f"- **{entry.get('label', kind)}** — {entry['not_found']}", ""]
    return lines


def _cite(entry):
    """One lead time's source, as a link a reader can follow."""
    if not entry:
        return ""
    source, url = entry.get("source"), entry.get("url")
    if source and url:
        return f" ([{source}]({url}))"
    return f" ({source})" if source else ""


def _control(document):
    control = document.get("control") or {}
    if control.get("status") == "not-screened":
        return [
            "### Control",
            "",
            f"**The control services were not read on this run.** "
            f"{_sentence(control.get('detail', ''))} No mark is reported present "
            "and none is reported absent — this corridor's control is simply "
            "unknown, and it is the largest single thing missing from this memo.",
            "",
        ]
    risk = control.get("recovery_risk") or {}
    if not isinstance(risk, dict) or "marks_in_corridor" not in risk:
        return ["### Control", "",
                "**No control was reported by this run.** Nothing is said here about "
                "what is or is not in the corridor.", ""]

    found = risk.get("marks_in_corridor", 0)
    not_found = risk.get("mark_not_found", 0)
    unknown = risk.get("condition_unknown", 0)
    lines = ["### Control", ""]
    if found and not_found == found:
        lines += [
            f"**Every one of the {found} NGS marks in this corridor is recorded "
            "`MARK NOT FOUND`.** Somebody has looked for each of them and could "
            "not find it. These are not marks you have.",
            "",
            "On this evidence the control work is setting new, not recovering "
            "existing. That is the largest single difference in this memo, and it "
            "is a judgment for the surveyor who signs rather than a conclusion "
            "this tool draws.",
            "",
        ]
    elif found:
        lines += [
            f"{found} NGS {_plural(found, 'mark')} in the corridor. **{not_found} "
            f"recorded `MARK NOT FOUND`** — somebody looked and could not find "
            f"them. {unknown} carry no condition at all, which is not the same as "
            "being there.",
            "",
        ]
    else:
        lines += ["No NGS mark falls inside the corridor.", ""]

    txdot = control.get("txdot_control") or {}
    if isinstance(txdot, dict) and "points_in_corridor" in txdot:
        stations = txdot.get("distinct_stations")
        destroyed = txdot.get("destroyed")
        unknown_condition = txdot.get("condition_unknown")
        lines += [
            f"TxDOT publishes {txdot['points_in_corridor']} control "
            f"{_plural(txdot['points_in_corridor'], 'record')} in the corridor, "
            f"covering **{stations} distinct {_plural(stations or 0, 'monument')}**. "
            "The two counts are never added together — some monuments appear in "
            "both sets.",
            "",
        ]
        if destroyed or unknown_condition:
            lines += [
                f"Of those, {destroyed} recorded destroyed and {unknown_condition} "
                "with no condition recorded. A monument with no condition is not a "
                "monument you have.",
                "",
            ]
    return lines


def _row_sheets(document):
    sheets = document.get("row_maps") or {}
    if sheets.get("status") == "not-screened" or "sheet_count" not in sheets:
        return [
            "### Right-of-way records",
            "",
            f"**The ROW map sheet index was not read on this run.** "
            f"{_sentence(sheets.get('detail', ''))} How many record drawings cover "
            "this corridor, and how old they are, is unknown.",
            "",
        ]
    total = sheets.get("sheet_count", 0)
    spread = sheets.get("date_range") or {}
    route = _route_key(document)
    own = (sheets.get("by_route") or {}).get(route) or {}
    lines = [
        "### Right-of-way records",
        "",
        # The corridor total leads, which is what Rick settled on PR #56 --
        # a ruling made with this memo explicitly in mind.
        f"**{total} ROW map sheets** reach this corridor, dating "
        f"**{spread.get('from', UNRECORDED)} to {spread.get('to', UNRECORDED)}**.",
        "",
    ]
    if own:
        own_spread = own.get("date_range") or {}
        lines += [
            f"{own['sheet_count']} of them are {route}'s own, dating "
            f"**{own_spread.get('from', UNRECORDED)} to "
            f"{own_spread.get('to', UNRECORDED)}**. The rest belong to routes that "
            "cross this corridor — the interchanges. The right of way where those "
            "roads meet is drawn on their sheets, not on this route's, and a crew "
            "retracing an interchange will need them.",
            "",
        ]
    lines += [
        "Sheets of that age mean hand retracement from scans that may be hard to "
        "read. That is drafting time somebody has to price, and it is in no figure "
        "here.",
        "",
        "No service publishes a link to the drawings themselves. They come through "
        "RPAM, TxDOT's Real Property Asset Map, or by Open Records Request, "
        "quoting the sheet names in the screening file.",
        "",
    ]
    return lines


def _longest_notice(flagged, table):
    """The longest notice period, per basis, never compared across bases.

    Two working days and two calendar days are different promises, and
    specification section 13 forbids converting one into the other. So the
    longest is reported **within** each basis rather than by taking a maximum
    over numbers that do not share a unit.
    """
    by_basis = {}
    for parcel in flagged:
        days, basis = parcel.get("max_lead_time_days"), parcel.get("max_lead_time_basis")
        if not days or not basis:
            continue
        if basis not in by_basis or days > by_basis[basis]["max_lead_time_days"]:
            by_basis[basis] = parcel
    if not by_basis:
        return []
    lines = []
    for basis in sorted(by_basis):
        parcel = by_basis[basis]
        driver = parcel.get("lead_time_driver")
        lines.append(
            f"- **{parcel['max_lead_time_days']} {basis}** — {driver} on tract "
            f"{parcel['id']}{_cite(table.get(driver))}"
        )
    return [
        "The longest notice period on any one tract, by the kind of days it "
        "counts:",
        "",
        *lines,
        "",
        "Working days and calendar days are different promises and are never "
        "converted into one another here.",
        "",
    ]


def _tracts(document):
    rows = document.get("parcels") or []
    table = (document.get("run") or {}).get("lead_times") or {}
    flagged = [p for p in rows if p.get("flags")]
    lines = ["### Tracts", "",
             f"**{len(rows)} {_plural(len(rows), 'tract')}** touch the corridor.", ""]
    if flagged:
        kinds = sorted({f["type"] for p in flagged for f in p["flags"]})
        lines += [
            f"**{len(flagged)} of them {_plural(len(flagged), 'carries', 'carry')} "
            f"something that costs time** — {', '.join(kinds)}.",
            "",
        ]
        lines += _longest_notice(flagged, table)
    else:
        lines += ["No tract carries a flag this run checked for.", ""]
    lines += _corridor_flags(document, table)
    return lines


def _corridor_flags(document, table):
    """Things that cost time and belong to no single tract.

    A pipeline easement crossing forty parcels is recorded once against the run
    rather than forty times, so that one notice period is not counted forty
    times over. An earlier draft of this file read only the per-parcel flags,
    which meant a corridor whose only finding was corridor-wide would have been
    described as carrying nothing at all.
    """
    corridor_flags = document.get("corridor_flags") or []
    if not corridor_flags:
        return []
    lines = [
        f"**{len(corridor_flags)} further "
        f"{_plural(len(corridor_flags), 'thing')} "
        f"{_plural(len(corridor_flags), 'crosses', 'cross')} the corridor without "
        "belonging to any one tract** — a pipeline easement or a railway runs "
        "through many, and its notice period is owed once, not once per tract:",
        "",
    ]
    for flag in corridor_flags:
        kind = flag.get("type", "feature")
        name = flag.get("name") or flag.get("id") or "unnamed"
        count = flag.get("parcel_count")
        across = f", across {count} tracts" if count else ""
        lines.append(f"- **{kind}** — {name}{across}{_cite(table.get(kind))}")
    lines.append("")
    return lines


def _closing(document):
    run = document.get("run") or {}
    return [
        "## What this memo is not",
        "",
        "It is **not a survey**. Nothing here was measured on the ground.",
        "",
        "It is **not a title search**. Ownership is as the appraisal district "
        "recorded it, and how quickly a transfer reaches that roll is a separate "
        "question this screening does not answer.",
        "",
        "It is **not a right of entry**, and it is not advice that one is not "
        "needed.",
        "",
        "It is desktop reconnaissance: a first pass, from public data, to price a "
        "job against. **An RPLS reads it and decides.** The screening tool does "
        "not decide anything, and the licensed surveyor who signs the work "
        "remains accountable for every number that reaches a client.",
        "",
        "---",
        "",
        f"*Built from `{run.get('run_id')}` by corridor-screen "
        f"{run.get('tool_version')}. Every figure above is read from that run, and "
        "every answer that run received is saved with the date it was obtained — "
        "the screening file beside this memo says which.*",
    ]


def build(document):
    """The whole memo, as Markdown, from one screening document."""
    lines = []
    lines += _heading(document)
    lines += _scope(document)
    lines += _uncertain(document)
    lines += ["## What was found", ""]
    lines += _control(document)
    lines += _row_sheets(document)
    lines += _tracts(document)
    lines += _closing(document)
    return "\n".join(lines).rstrip() + "\n"


def write(document, out_dir, name=MEMO_NAME):
    path = Path(out_dir) / name
    write_text(path, build(document))
    return path


def main(argv=None):
    """``python -m corridor_screen.bid_memo --out ../project-sh16``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen bid-memo",
        description="Write the bid memo from a screening run.",
    )
    parser.add_argument("--out", required=True,
                        help="The project directory holding screening.json")
    args = parser.parse_args(argv)

    source = Path(args.out) / "screening.json"
    with open(long_path(source), "r", encoding="utf-8") as handle:
        document = json.load(handle)
    path = write(document, args.out)
    print(f"  written  {path}")
    if document["run"]["status"] != "complete":
        print("  note     the run was incomplete, and the memo says so at the top")
    return 0


if __name__ == "__main__":
    sys.exit(main())
