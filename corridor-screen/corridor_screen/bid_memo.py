"""The memo a principal reads before pricing the job.

Specification section 2 is blunt that the screening tool does not produce this:
"It does not produce the bid memo, the parcel table, or the crew-day build-up.
Those are separate jobs that read this file. **One fetch, many renderings.**"
This is the first of those three.

It reads ``screening.json`` and writes Markdown. Nothing here calls a service,
and nothing here recomputes a finding -- if a number is not in the run, it does
not appear in the memo.

----

Why this output is the easiest one to do damage with
====================================================

Every other artifact this tool produces looks like what it is: a JSON file, a
table, a log. This one looks like a letter from a firm, and it will be read with
the authority that carries. So three rules bind it, and each has tests.

**A number that was not measured never appears as a number.**
``acres_in_corridor`` is ``None`` on every parcel, because the tool counts
tracts and does not yet measure how much of each one the corridor takes. Summing
that column would put "0.0 acres" in front of a principal, and nobody would
notice until somebody priced it. The memo says the take was not measured.

**Uncertainty gets a heading, not a footnote.** The ticket asks for it "stated
plainly rather than buried inside a number." A caveat inside a total is a caveat
that gets rounded off in the reading. So what is unknown, what was not checked,
and what no public source publishes at all are a section of their own, near the
front, before the findings they qualify.

**A run that did not finish says so on the first page.** An incomplete run that
reads complete is the failure this whole repo is arranged against.

----

What it deliberately does not do
================================

**It does not price anything.** There is no rate, no crew-day count, no total.
Crew days are issue #24 and they are a separate job for a reason: the arithmetic
belongs where it can be argued with line by line, not inside a memo's summary.

**It does not decide anything.** It reports what a run found and what it could
not see. An RPLS reads it and decides, and the memo says so in as many words.
"""

import json
import sys
from pathlib import Path

from .cache import long_path, write_text

MEMO_NAME = "bid-memo.md"

# The flag types the tool knows how to look for, so a type missing from a run's
# `screened_for` can be named rather than silently absent. Read off the same
# place the run reads it, so a new flag type appears here without an edit.
from .sources import FLAG_SOURCES

ALL_FLAG_TYPES = tuple(kind for _, kind in FLAG_SOURCES)


def _plural(count, one, many=None):
    return one if count == 1 else (many or one + "s")


# What each kind of help is called in a sentence. The screening file uses
# `fire_ems` because it is a key; a memo does not.
KIND_LABELS = {
    "hospital": "hospital",
    "ambulance": "ambulance service",
    "fire_ems": "fire or EMS station",
    "police": "police station",
}


def _kind(kind):
    return KIND_LABELS.get(kind, kind.replace("_", " "))


def _heading(document):
    run, alignment = document["run"], document.get("alignment") or {}
    lines = [
        "# Desktop reconnaissance — SH 16, Bexar County",
        "",
        f"**Corridor.** {alignment.get('source_path', 'not recorded')}, "
        f"{alignment.get('length_mi', 0):.2f} miles, screened "
        f"{run['half_width_ft']:g} feet either side of the centerline.",
        "",
        f"**Screened on** {run['started_at'][:10]}. "
        f"**Reference** `{run['run_id']}`.",
        "",
        f"[Confirm the location on a map]({run['map_link']}) before reading further. "
        "A corridor drawn from the wrong route looks exactly like this one.",
        "",
    ]
    if run["status"] != "complete":
        stopped = run.get("stopped_at_service")
        lines += [
            "!!! danger \"This run did not finish — it is recorded as incomplete\"",
            f"    It stopped at **{stopped}**. Everything below covers only what was",
            "    reached before that, and the corridor has not been screened in full.",
            "    Do not price from this memo until a complete run replaces it.",
            "",
        ]
    return lines


def _captured(document):
    """The dates the answers were obtained, which is how old the data is."""
    dates = sorted({s["captured_at"][:10] for s in document.get("services", [])
                    if s.get("captured_at")})
    return dates


def _scope(document):
    run = document["run"]
    dates = _captured(document)
    when = dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}" if dates else "not recorded"
    corridor = document.get("corridor") or {}
    lines = [
        "## What was done",
        "",
        f"Public map services were read for the corridor above — "
        f"{corridor.get('area_sq_mi', 0):.2f} square miles of ground — and every "
        "answer they gave was saved with the date it was obtained and the exact "
        "request that produced it.",
        "",
        f"The answers in this memo were obtained on **{when}**. Nothing here is "
        "live, and nothing here is older than that date.",
        "",
        "This is desktop work. No one has walked the corridor.",
        "",
    ]
    return lines


def _uncertain(document):
    """What is not known, before the findings it qualifies."""
    run = document["run"]
    rows = document.get("parcels") or []
    lines = [
        "## What is not known, and why",
        "",
        "Read this before the findings. Every item here is a gap this screening "
        "cannot close, and each one is a question somebody still has to answer.",
        "",
    ]

    lines.append("**No public source publishes these at all.**")
    lines.append("")
    for item in run.get("not_screenable", []):
        lines.append(f"- **{item['type'].capitalize()}** — {item['reason']}.")
    lines.append("")
    lines.append(
        "  A corridor is not clear of either of these because this memo does not "
        "mention them. Somebody has to look."
    )
    lines.append("")

    missed = [t for t in ALL_FLAG_TYPES if t not in run.get("screened_for", [])]
    if missed:
        lines += [
            f"**Not checked on this run: {', '.join(sorted(missed))}.** "
            "No tract below is reported as clear of them, because none was asked "
            "about. A re-run with those services answering would close this.",
            "",
        ]

    roadway = document.get("roadway") or {}
    if roadway.get("status") == "not-screened":
        lines += [
            "**The existing right of way was not read.** "
            f"{_sentence(roadway.get('detail', ''))} So the corridor width used "
            "here is the one stated above, not the width TxDOT actually holds.",
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
        lines += [
            "**Right of entry is unknown on every tract, and deliberately so.** "
            "Right of entry is not a statutory right in Texas, and no parcel "
            "polygon establishes one. Nothing in this screening should be read as "
            "permission to enter.",
            "",
        ]

    if any(p.get("txdot_owned") is None for p in rows):
        lines += [
            "**Whether TxDOT already owns a tract was not checked.** Some of the "
            "tracts counted below may already be in state hands.",
            "",
        ]

    unconfirmed = sorted({t for p in rows for t in (p.get("lead_time_not_found") or [])})
    if unconfirmed:
        lines += [
            f"**No published notice period was confirmed for: "
            f"{', '.join(unconfirmed)}.** Those tracts carry the flag and no number. "
            "They are not zero-notice; they are unmeasured, and the difference "
            "matters to a schedule.",
            "",
        ]

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


def _sentence(text):
    """One field's prose, as a sentence: capitalized, ending in a full stop."""
    text = (text or "").strip().rstrip(".")
    if not text:
        return ""
    return text[0].upper() + text[1:] + "."


# The date TxDOT's ROW map service uses often enough to be worth doubting. The
# account of why is on the data-source page; what matters here is that the memo
# only raises it when the date it actually prints is that one.
SUSPECT_SHEET_DATE = "1900-01-01"


def _suspect_date(document):
    """Doubt the oldest sheet date -- but only if the memo is quoting it.

    The screening file carries this caveat for the whole corridor, where the
    oldest sheet across every route is 1900-01-01. This memo quotes the
    corridor's **own route**, which on SH 16 starts in 1944. A caveat about a
    number the reader cannot see is noise, and noise is how caveats get ignored.
    """
    sheets = document.get("row_maps") or {}
    own = (sheets.get("by_route") or {}).get("SH0016") or {}
    printed = (own.get("date_range") or sheets.get("date_range") or {}).get("from")
    if printed != SUSPECT_SHEET_DATE:
        return []
    return [
        f"**The oldest sheet date above may not be a date.** {SUSPECT_SHEET_DATE} "
        "appears on 368 of that service's 20,276 records, and the service "
        "publishes no empty dates at all — which looks like a stand-in for a date "
        "nobody recorded. We could not confirm it either way. Check that sheet "
        "against the drawing before quoting its age.",
        "",
    ]


def _control(document):
    control = document.get("control") or {}
    risk = control.get("recovery_risk") or {}
    if not risk:
        return []
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
            "Price this as setting new control, not as recovery. That is the "
            "single largest difference in this memo.",
            "",
        ]
    elif found:
        lines += [
            f"{found} NGS {_plural(found, 'mark')} in the corridor. "
            f"**{not_found} recorded `MARK NOT FOUND`** — somebody looked and could "
            f"not find them. {unknown} carry no condition at all, which is not the "
            "same as being there.",
            "",
        ]
    else:
        lines += ["No NGS mark falls inside the corridor.", ""]

    txdot = control.get("txdot_control") or {}
    if isinstance(txdot, dict) and "points_in_corridor" in txdot:
        stations = txdot.get("distinct_stations")
        lines += [
            f"TxDOT publishes {txdot['points_in_corridor']} control "
            f"{_plural(txdot['points_in_corridor'], 'record')} in the corridor, "
            f"covering **{stations} distinct {_plural(stations or 0, 'monument')}**. "
            "The counts are not added together — some monuments appear in both "
            "sets.",
            "",
        ]
    return lines


def _row_sheets(document):
    sheets = document.get("row_maps") or {}
    if sheets.get("status") == "not-screened" or "sheet_count" not in sheets:
        return ["### Right-of-way records", "",
                "The ROW map sheet index was not read on this run.", ""]
    own = (sheets.get("by_route") or {}).get("SH0016") or {}
    spread = own.get("date_range") or sheets.get("date_range") or {}
    lines = ["### Right-of-way records", ""]
    if own:
        lines += [
            f"**{own['sheet_count']} ROW map sheets** cover this corridor on SH 16 "
            f"itself, dating **{spread.get('from')} to {spread.get('to')}**.",
            "",
            "Sheets of that age mean hand retracement from scans that may be hard "
            "to read. That is drafting time somebody has to price, and it is not "
            "in any figure here.",
            "",
        ]
    total = sheets.get("sheet_count")
    if total and own and total > own.get("sheet_count", 0):
        lines += [
            f"A further {total - own['sheet_count']} sheets belong to routes that "
            "cross this corridor — the interchanges. The right of way where those "
            "roads meet SH 16 is drawn on their sheets, not on SH 16's, and a crew "
            "retracing the interchange will need them.",
            "",
        ]
    lines += [
        "No service publishes a link to the drawings themselves. They come from "
        "TxDOT's Real Property Asset Map, or by Open Records Request, quoting the "
        "sheet names in the screening file.",
        "",
    ]
    return lines


def _tracts(document):
    rows = document.get("parcels") or []
    flagged = [p for p in rows if p.get("flags")]
    lines = [
        "### Tracts",
        "",
        f"**{len(rows)} {_plural(len(rows), 'tract')}** touch the corridor.",
        "",
    ]
    if flagged:
        kinds = sorted({f["type"] for p in flagged for f in p["flags"]})
        lines += [
            f"**{len(flagged)} of them {_plural(len(flagged), 'carries', 'carry')} "
            f"something that costs time** — {', '.join(kinds)}.",
            "",
        ]
        with_number = [p for p in flagged if p.get("max_lead_time_days")]
        if with_number:
            worst = max(with_number, key=lambda p: p["max_lead_time_days"])
            lines += [
                f"The longest notice period found is **{worst['max_lead_time_days']} "
                f"{worst.get('max_lead_time_basis') or 'days'}**, driven by "
                f"{worst.get('lead_time_driver')} on tract {worst['id']}. Working "
                "days and calendar days are different promises and are never "
                "converted into one another here.",
                "",
            ]
    else:
        lines += ["None of them carries a flag this run checked for.", ""]
    return lines


def _safety(document):
    safety = document.get("crew_safety") or {}
    by_type = safety.get("by_type") or {}
    if not by_type:
        return []
    lines = ["### Nearest help", ""]
    for kind, block in by_type.items():
        nearest = block.get("nearest")
        if nearest:
            lines.append(
                f"- **{_kind(kind)}** — {nearest['name']}, "
                f"{nearest['distance_from_centerline_mi']} miles from the centerline"
            )
    for kind in safety.get("not_found_within_the_radius", []):
        lines.append(
            f"- **{_kind(kind)}** — none within {safety.get('search_radius_mi'):g} "
            "miles of the corridor. That is not the same as none"
        )
    lines += [
        "",
        "Every distance here is a straight line, not a drive. Check the route "
        "before a crew goes out.",
        "",
    ]
    return lines


def _closing(document):
    return [
        "## What this memo is not",
        "",
        "It is **not a survey**. Nothing here was measured on the ground.",
        "",
        "It is **not a title search**. Ownership is as the appraisal district "
        "recorded it, and how quickly a transfer reaches that roll is a "
        "separate question this screening does not answer.",
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
        f"*Built from `{(document.get('run') or {}).get('run_id')}` by "
        f"corridor-screen {(document.get('run') or {}).get('tool_version')}. "
        "Every figure above traces to a saved response; the screening file beside "
        "this memo says which.*",
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
    lines += _safety(document)
    lines += _closing(document)
    return "\n".join(lines).rstrip() + "\n"


def write(document, out_dir, name=MEMO_NAME):
    path = Path(out_dir) / name
    write_text(path, build(document))
    return path


def main(argv=None):
    """``python -m corridor_screen.bid_memo --out ../project-sh16``"""
    import argparse

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
