"""The crew-day build-up -- how long the job takes, and why anybody should believe it.

Specification section 2: "It does not produce the bid memo, the parcel table,
or the crew-day build-up. Those are separate jobs that read this file. **One
fetch, many renderings.**" This is the third and last of them. Like the other
two it reads ``screening.json``, calls no service, and invents no count.

Issue #24 states the job in one line: "Build the crew-day estimate with the
arithmetic shown and open to argument. Not a single number." That word *open*
is the whole design.

----

Why a number is the wrong output
================================

The audience for this file is a room of firm owners, and they will argue with
whatever number is on the screen. That is not a problem to be managed. It is
the only thing that makes the number worth anything, because every one of them
prices work for a living and this tool has never been near the corridor.

So the output is not "38 crew-days." It is twelve labeled inputs, eight lines of
arithmetic, and two totals anybody can rebuild on the back of an envelope. A
surveyor who thinks the answer is wrong can put a finger on the row that is
wrong and say so, by its handle, out loud, in the room.

Four rules hold that together, and each has tests.

**Every rate is somebody's assumption, and says so.** TxDOT publishes no
production rates. The standard sheets say what devices go on the road and what
the crew wears; they do not say how long anything takes. So ``crew_rates.toml``
carries ``assumption = true`` on every row, each with a ``disagree_with`` line
naming the specific thing to push back on -- and the loader refuses a row that
will not say where its number came from.

**A source naming TxDOT has to prove it.** CLAUDE.md: "Never invent a TxDOT
requirement. Cite the manual section and its URL, or say you could not confirm
it." A rate table is exactly where a plausible "TxDOT requires ninety minutes
per setup" would arrive wearing a tie, so ``_check`` refuses a row whose
``source`` names TxDOT unless it carries the URL and the date somebody opened
it, and refuses to let such a row call itself an assumption.

**A count nobody measured never becomes a number.** The run does not count
manholes or culverts. Issue #24 asks for them anyway -- "popping manholes and
closing lanes is where time goes" -- so the arithmetic is wired and the
quantity is absent. That line reports no hours at all. Reporting zero would
price the most expensive thing on the job at nothing, on the page a principal
reads first.

**Field hours and office hours are never added together.** A crew-day is a
crew standing on a road. Hand retracement of 69 scanned ROW sheets is real time
and real money and it is not a crew-day. One combined total would be quoted as
though it were, by the person least able to tell the difference.

----

Where the traffic control comes from
====================================

Two documents, and the split matters. ``tcp-s-1-08a.md`` is TCP(S-1)-08A read
with that sheet open; ``tcp-s-family.md`` is the reading of all six. **Every
claim here about a sheet other than S-1 is sourced to the family document**,
because TCP(S-1) draws only the two shoulder cases and says so itself: "Do not
carry this paragraph across to another sheet." Both were written from rendered
pages rather than extracted text, which is how the drawn truck's TMA chevron —
the thing that actually decides the cost — was seen at all.

That distinction is not pedantry. Until 2026-09-13 this repo carried "a
20-minute shot on a 55-mph highway converts a two-person crew into a crew plus
shadow truck," read across from the mobile-operations standard TCP(3-1) because
TCP(S-1) could not be fetched. The sheet says nothing of the kind: the duration
line is **one hour**, crossing it costs a sign and a run of cones rather than a
truck, and **no posted speed anywhere in the six-sheet family triggers a shadow
vehicle.** There is a test here that this file never says otherwise.

The overcorrection is just as easy, and an earlier draft of this module made it:
"a lane closure is TCP(S-2) or TCP(S-3) work, and those sheets draw a shadow
vehicle." True of S-2b and both S-3 cases. **Flatly wrong about S-2a, which
draws no protective vehicle at all and uses flaggers.** So ``SHEET_CASES``
carries the whole table rather than a summary, because the summary is where the
error keeps happening.

----

Why there is no ``--write-fallback`` flag
=========================================

``manual_links`` and ``elevation_trap`` each grew one, and
`#67 <https://github.com/RickSmith/survey-recon/issues/67>`_ is open about
pulling that shape into one seam. This module deliberately does not add a third
copy of it.

It does not need one. A failure beat has a rendering step separate from its
writing step, so it needs a flag to say which you meant. This does not: the
console summary is just a second rendering of the same document, so ``write``
emits both every time. Issue #24 asks for "a fallback capture recorded as the
work happens," and a file written on every run is recorded more reliably than
one written when somebody remembers the flag.
"""

import argparse
import json
import math
import sys
import tomllib
from pathlib import Path

from . import beats
from .cache import long_path, write_text
# The same fold-a-TOML-string-into-one-line helper the lead-time table
# uses. Imported rather than copied: two identical private helpers reading
# two sibling TOML files is one helper with a duplicate.
from .lead_times import _tidy

BUILD_UP_NAME = "crew-day.md"

# The console rendering, written on every run. Issue #27 wants a capture "that
# can stand in if the live thing breaks," and this is this step's. Plain ASCII,
# because a default Windows console is cp1252 and a borrowed podium laptop has
# never been told otherwise.
FALLBACK_NAME = "crew-day.txt"

TABLE_PATH = Path(__file__).with_name("crew_rates.toml")

# What a value reads as when the run did not record it. Never a zero, never a
# dash: a reader has to be able to tell "none" from "not measured". The same
# constant, for the same reason, as in `bid_memo` and `parcel_table`.
UNMEASURED = "not measured"

# The rates the build-up consumes, in the order their handles are numbered.
# A1, A2, A3 and so on -- a handle exists so somebody can disagree with one rate
# out loud in a room without having to describe it first.
#
# This is the list the tests check the table against, so a rate deleted from the
# TOML fails loudly here rather than quietly dropping a line of arithmetic.
RATES_USED = (
    "hours_per_mark_recovery_attempt",
    "control_pairs_per_mile",
    "hours_per_control_pair",
    "hours_per_tract_corner_recovery",
    "hours_per_flagged_tract_access",
    "hours_per_road_occupation",
    "hours_per_centerline_mile",
    "hours_per_row_sheet_retracement",
    "office_hours_per_mile_drafting",
    "field_hours_per_crew_day",
    "office_hours_per_day",
    "crew_size",
)

# What a rate is for. `field` becomes crew-days, `office` never does, `day` says
# how many hours make one of either, and `condition` is stated rather than
# multiplied.
KINDS = ("field", "office", "day", "condition")

# Every row must carry these.
REQUIRED = ("label", "unit", "kind", "source", "why")

# Words in a `source` that turn the row into a claim about TxDOT. A sheet named
# in `why` is context; a sheet named in `source` says TxDOT published this
# number, and that needs a link somebody opened.
TXDOT_CLAIMS = ("txdot", "tcp(", "tmutcd")


# ------------------------------------------------------- what the sheet says

# TCP(S-1)-08A, read with the sheet open. See the module docstring, and
# `project-sh16/manual-pulls/tcp-s-1-08a.md` for the full account.
#
# The URL and the date are here because CLAUDE.md requires them of anything
# making a TxDOT claim, and because `_check` requires them of any *rate* that
# names TxDOT. A traffic-control section citing a local PDF and nothing else
# would hold this module to a lower standard than it holds its own data file.
# Both are read off `tcp-s-1-08a.pdf.meta.toml`, where the committed bytes were
# verified by sha256 against the fetched bytes.
TCP_SHEET = "TCP(S-1)-08A"
TCP_SHEET_PATH = "project-sh16/manual-pulls/tcp-s-1-08a.pdf"
TCP_SHEET_URL = (
    "https://ftp.txdot.gov/pub/txdot-info/cmd/cserve/standard/traffic/tcps1.pdf"
)
TCP_SHEET_VERIFIED_ON = "2026-09-13"

# The family, and `tcp-s-family.md` is where it was read. **Every claim about a
# sheet other than S-1 is sourced here rather than to S-1**, which draws only
# the two shoulder cases and says so: "Do not carry this paragraph across to
# another sheet."
TCP_FAMILY_PATH = "project-sh16/manual-pulls/tcp-s-family.md"

# The duration line for a survey crew, on every sheet in the family. Under it,
# the work is short duration; over it and inside one daylight period, short
# term stationary.
DURATION_LINE_HOURS = 1

# What each case *draws*, which is what decides the cost. The legend gives the
# truck mounted attenuator its own symbol, a small solid black chevron, and
# `tcp-s-family.md` is blunt that "the symbol, not the note wording, is what
# distinguishes a shadow vehicle from an ordinary work truck."
#
# This table is carried rather than summarized because the summary is where the
# error keeps happening. An earlier draft of this module said "TCP(S-2) or
# TCP(S-3) work, and those sheets draw a shadow vehicle" — true of S-2b and
# both S-3 cases, and flatly wrong about **S-2a, which draws no protective
# vehicle at all** and uses flaggers.
SHEET_CASES = (
    ("TCP(S-1a)", "Work off the shoulder or paved surface", "1 work vehicle"),
    ("TCP(S-1b)", "Work on the shoulder", "1 work vehicle"),
    ("TCP(S-2a)", "Road closed under 20 minutes, off-peak",
     "**none** — flaggers instead"),
    ("TCP(S-2b)", "Work in the roadway, off-peak",
     "**1 shadow vehicle with TMA**"),
    ("TCP(S-2c)", "A two-lane rural intersection, as determined by the Engineer",
     "1 work vehicle"),
    ("TCP(S-3a)", "Right lane closed", "**1 shadow vehicle with TMA**"),
    ("TCP(S-3b)", "Work on centerline", "**2 shadow vehicles with TMA**"),
    ("TCP(S-4a)", "Work off the right shoulder of a divided roadway",
     "1 work vehicle"),
    ("TCP(S-4b)", "Work in the median of a divided roadway",
     "2 work vehicles (1 where a median barrier protects a side, Note 2)"),
    ("TCP(S-5a)", "Work on the right shoulder of a divided roadway",
     "1 work vehicle — *but the notes disagree, see below*"),
    ("TCP(S-5b)", "Work on the median shoulder of a divided roadway",
     "1 work vehicle — *same disagreement*"),
)

TRAFFIC_CONTROL = (
    {
        "topic": "One hour is the line, not twenty minutes",
        "sheet": TCP_SHEET,
        "detail": (
            "Work occupying a location up to one hour is short duration. Past the "
            "hour, two reliefs lapse: the G20-2a END ROAD WORK sign may no longer "
            "be omitted (Note 1), and the channelizing devices on the shoulder "
            "taper and tangent section may no longer be omitted (Note 2). That is "
            "a sign, a run of cones, and the time to set and retrieve them. It is "
            "billable time, not a second vehicle."
        ),
    },
    {
        "topic": "Note 3 is the surveying-specific trap",
        "sheet": TCP_SHEET,
        "detail": (
            "Where line-of-sight requirements will not allow the work vehicle to "
            "park where it protects the crew, the channelizing devices of Note 2 "
            "are required — so the under-an-hour relief does not apply and the "
            "devices stand whatever the duration. Sighting down a line is the "
            "job, so on a survey this is the ordinary case rather than the "
            "exception. The build-up cannot charge for it, because the number of "
            "occupations is unmeasured, but a reader pricing this by hand should "
            "assume the setup happens on every one of them."
        ),
    },
    {
        "topic": "No posted speed puts a shadow truck on this job",
        "sheet": "all six sheets",
        "detail": (
            "Not found on any of the six TCP(S-*) sheets: 55 mph is an ordinary "
            "row in every spacing table. On TCP(S-1) the shadow vehicle with a "
            "truck mounted attenuator appears in Note 4 as a permitted substitute "
            "for the work vehicle, which is an option rather than a penalty the "
            "clock triggers."
        ),
    },
    {
        "topic": "Where the work is decides the cost, not how fast traffic moves",
        "sheet": "all six sheets",
        "detail": (
            "TCP(S-1) draws only the two shoulder cases, so it is the cheap one. "
            "A shadow vehicle with a truck mounted attenuator is drawn on exactly "
            "two sheets — TCP(S-2b) and both TCP(S-3) cases — and on those the "
            "permission to use an ordinary work vehicle instead is granted only "
            "for short duration work, so past the hour it lapses. The accurate "
            "sentence: **a survey crew working in a travel lane or on the "
            "centerline for more than an hour is looking at a shadow vehicle with "
            "a TMA, two of them on the centerline, unless the Engineer approves "
            "barricades instead.** On a shoulder, off the pavement, or at a "
            "two-lane rural intersection, it is not."
        ),
    },
    {
        "topic": "Conventional Roads Only",
        "sheet": "all six sheets",
        "detail": (
            "Every sheet in the family carries that footnote, and none uses the "
            "words freeway or controlled access. Whether this corridor is any of "
            "those was not read by this run. Freeway coverage is not found, which "
            "is not the same as absent."
        ),
    },
)

# The two cases that change **who is on the truck** rather than how many hours
# it takes. Both are quantities this run does not measure, and both are in the
# build-up anyway, because issue #24 wants an honest unknown in it rather than a
# tidy page: "The build-up is supposed to be arguable."
CREW_CHANGES = (
    {
        "trigger": "Work on the centerline",
        "sheet": "TCP(S-3b)",
        "becomes": "2 shadow vehicles with TMA, and somebody to drive each",
        "detail": (
            "One at each end of the work space, 30 ft minimum clearance to each, "
            "because traffic passes on both sides. It is the most expensive "
            "configuration in the family, and **it is the one a retracement crew "
            "chaining a centerline lands on.** Past one hour the drawn "
            "configuration stands unless the Engineer approves Type III "
            "barricades instead (S-3 Note 3) — which is a decision somebody else "
            "makes, not one this build-up may assume."
        ),
        "unmeasured": (
            "How much of this corridor's retracement falls on the centerline. "
            "Nothing in this run says. It is the line item that moves the number "
            "and this tool cannot put a quantity on it."
        ),
    },
    {
        "trigger": "Work on the shoulder of a divided roadway",
        "sheet": "TCP(S-5)",
        "becomes": "unresolved — the sheet contradicts itself",
        "detail": (
            "The **drawing** shows a plain work vehicle with no TMA chevron. The "
            "**notes** are written about \"*the* Shadow Vehicle with TMA,\" "
            "wording carried over verbatim from S-3, where one is actually drawn. "
            "Two readings, two day rates, and this build-up **does not pick "
            "one** — see "
            "[#72](https://github.com/RickSmith/survey-recon/issues/72), which "
            "asks the Engineer. Price it as a range: the low reading is the "
            "ordinary work truck already in the crew, the high reading adds a "
            "shadow vehicle with TMA and an operator for every day spent on a "
            "divided shoulder."
        ),
        "unmeasured": (
            "Whether this corridor is divided at all, and over how much of its "
            "length. The roadway block now reports TxDOT's lane count, but a "
            "lane count is not a median: a six-lane road may be divided or not, "
            "and the field that would say is one this run does not read. So the "
            "quantity this line item turns on is still unmeasured, and this "
            "build-up still does not put a number on it."
        ),
    },
)


class CrewRateTableError(Exception):
    """The rate table is not fit to quote. Nothing after this is safe."""


class Rate:
    """One row of the table: how long something takes, and who says so."""

    def __init__(self, key, row):
        self.key = key
        self.label = row["label"]
        self.value = row["value"]
        self.unit = row["unit"]
        self.kind = row["kind"]
        self.assumption = bool(row.get("assumption", False))
        self.source = row["source"]
        self.why = _tidy(row["why"])
        # What to push back on. Required on an assumption, meaningless without
        # one: a published figure is not somebody's opinion to argue with.
        self.disagree_with = _tidy(row.get("disagree_with"))
        self.url = row.get("url")
        self.verified_on = row.get("verified_on")


def _claims_txdot(source):
    lowered = str(source or "").lower()
    return any(word in lowered for word in TXDOT_CLAIMS)


def _check(key, row):
    """Refuse a row a reader could not hold anybody to.

    Same shape as ``lead_times._check`` and for the same reason: a
    configuration mistake costs nothing to catch before a run and a great deal
    after, and this table will be quoted by people who price work for a living.
    """
    missing = [name for name in REQUIRED if not row.get(name)]
    if missing:
        raise CrewRateTableError(
            f"crew rate [{key}] is missing {', '.join(sorted(set(missing)))}. "
            "Every rate must carry a label, the unit it counts, what kind of "
            "time it is, where the number came from and why it is what it is. "
            "A rate with no source is a number with no owner."
        )

    if row["kind"] not in KINDS:
        raise CrewRateTableError(
            f"crew rate [{key}] has kind {row['kind']!r}, which is not one of "
            f"{', '.join(KINDS)}. Field hours become crew-days and office hours "
            "never do, so a rate that will not say which is a rate that cannot "
            "be totaled."
        )

    value = row.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise CrewRateTableError(
            f"crew rate [{key}] has value {value!r}. A rate must be a number "
            "greater than zero. A zero rate silently deletes a whole line of "
            "the build-up, and the line it deletes is still real work."
        )

    if _claims_txdot(row["source"]):
        # CLAUDE.md's accuracy rule, made structural. See the module docstring.
        if row.get("assumption"):
            raise CrewRateTableError(
                f"crew rate [{key}] names TxDOT in its source and is also marked "
                "as an assumption. One of those is wrong and a reader cannot "
                "tell which. If TxDOT published the number, drop the assumption "
                "flag and cite it. If it did not, keep TxDOT out of `source` and "
                "put the sheet in `why` instead."
            )
        for needed in ("url", "verified_on"):
            if not row.get(needed):
                raise CrewRateTableError(
                    f"crew rate [{key}] claims a TxDOT source and has no "
                    f"`{needed}`. Never invent a TxDOT requirement: cite the "
                    "section and the URL somebody opened, with the date they "
                    "opened it, or say you could not confirm it."
                )
    elif not row.get("assumption"):
        raise CrewRateTableError(
            f"crew rate [{key}] is not marked as an assumption and does not "
            "name a published source. Every number in this build-up is one or "
            "the other."
        )

    if row.get("assumption") and not _tidy(row.get("disagree_with")):
        raise CrewRateTableError(
            f"crew rate [{key}] is an assumption with no `disagree_with`. The "
            "whole point of this build-up is that a surveyor can argue with one "
            "specific row, and a row that will not say what to argue with is a "
            "number wearing a lab coat."
        )


def load_rates(path=None, rows=None):
    """Read the rate table. Raises rather than returning one that cannot be quoted.

    ``rows`` is for tests: it takes an already-parsed mapping and skips the
    file, so a check on the rules does not need a temporary file on disk.
    """
    if rows is None:
        path = Path(path or TABLE_PATH)
        try:
            rows = tomllib.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise CrewRateTableError(f"the crew rate table is missing from {path}") from exc
        except tomllib.TOMLDecodeError as exc:
            raise CrewRateTableError(
                f"the crew rate table at {path} is not readable TOML: {exc}"
            ) from exc

    table = {}
    for key, row in rows.items():
        if not isinstance(row, dict):
            continue  # schema_version and anything else at the top level
        _check(key, row)
        table[key] = Rate(key, row)
    if not table:
        raise CrewRateTableError("the crew rate table has no rows")
    return table


def rate_handle(key):
    """The label a surveyor says out loud: A1, A2, A3.

    Returns ``None`` for a rate the build-up does not use, so a handle is never
    printed against a row nobody can see the effect of.
    """
    return f"A{RATES_USED.index(key) + 1}" if key in RATES_USED else None


# ------------------------------------------------------------------ the inputs


def _count(key, label, value, unit, source, why_not=None, context=False):
    """One labeled input, measured or not.

    ``value`` of ``None`` is the whole reason this helper exists: an unmeasured
    count carries the account of why nobody measured it, and never a zero.

    ``context`` marks a count the build-up shows but does not multiply by
    anything. A reader who cannot tell those apart will hunt the arithmetic for
    a row that is not there and conclude the page dropped it.
    """
    return {
        "key": key,
        "label": label,
        "value": value,
        "unit": unit,
        "source": source,
        "measured": value is not None,
        "why_not": why_not,
        "context": context,
    }


def counts(document):
    """Every quantity the arithmetic uses, labeled and traced to the run.

    Issue #24's first criterion: "Every input to the estimate is visible and
    labeled." ``source`` is the path in ``screening.json`` the number was read
    from, so a reader can check one without reading any Python.
    """
    alignment = document.get("alignment") or {}
    control = document.get("control") or {}
    recovery = control.get("recovery_risk") or {}
    txdot = control.get("txdot_control") or {}
    row_maps = document.get("row_maps") or {}
    parcels = document.get("parcels") or []
    roadway = document.get("roadway") or {}

    flagged = [p for p in parcels if p.get("flags")]

    return [
        _count("corridor_miles", "Corridor length", alignment.get("length_mi"),
               "miles", "alignment.length_mi"),
        _count("tracts", "Tracts the corridor touches", len(parcels),
               "tracts", "parcels[]"),
        _count("flagged_tracts", "Tracts carrying something that costs time",
               len(flagged), "tracts", "parcels[].flags"),
        _count("ngs_marks", "Published NGS marks in the corridor",
               recovery.get("marks_in_corridor"), "marks",
               "control.recovery_risk.marks_in_corridor"),
        _count("ngs_not_found", "Of those, recorded MARK NOT FOUND",
               recovery.get("mark_not_found"), "marks",
               "control.recovery_risk.mark_not_found", context=True),
        # Context, not a multiplier. Listed because a reader deciding whether
        # to argue with the new-control line needs to know what is already on
        # the ground; the arithmetic does not subtract it, because whether two
        # good TxDOT monuments can carry an 8.7-mile corridor is the surveyor's
        # call and not this tool's.
        _count("txdot_points", "Distinct TxDOT control monuments",
               txdot.get("distinct_stations"), "monuments",
               "control.txdot_control.distinct_stations", context=True),
        _count("row_sheets", "ROW map sheets reaching the corridor",
               row_maps.get("sheet_count"), "sheets", "row_maps.sheet_count"),
        # The five the run cannot supply. Issue #24 asks for the first two by
        # name, and the honest answer is that nobody published them.
        _count("manholes", "Manholes to pop", None, "manholes",
               "no service in this run publishes a manhole inventory",
               why_not="No public source screened here publishes manhole "
                       "locations. A count would have to come from a utility "
                       "owner, from as-builts, or from somebody driving it.",
               context=True),
        _count("culverts", "Culverts to locate", None, "culverts",
               "no service in this run publishes a culvert inventory",
               why_not="Same: not screened. TxDOT holds drainage inventories "
                       "that this pass does not call.",
               context=True),
        _count("road_occupations", "Times traffic control has to be set", None,
               "occupations",
               "derived from the manhole and culvert counts, which are unmeasured",
               why_not="This is what the two counts above are for. Each manhole "
                       "or culvert in or beside the travel way is an occupation "
                       "needing signing and devices. With neither count, this "
                       "number does not exist and the traffic-control line below "
                       "has no total."),
        # The line item issue #24's own comment says "moves the number", and
        # the one this tool is least able to measure. A retracement crew
        # chaining a centerline is on TCP(S-3b), which draws two shadow
        # vehicles with TMA -- the most expensive configuration in the family.
        _count("centerline_miles", "Miles worked on the centerline", None,
               "miles",
               "nothing in this run says where the retracement falls",
               why_not="Whether a crew works from the shoulder or down the "
                       "centerline is a methodology choice nobody has made yet, "
                       "and no map service publishes it. It decides which TCP "
                       "sheet applies, and the two sheets are not close in cost."),
        # **Relabeled on 2026-09-19, because the old label stopped being true.**
        # It read "Existing ROW width, lane count and traffic" and said those
        # were never called. The roadway block reports all three now, under
        # [#183](https://github.com/RickSmith/survey-recon/issues/183). What is
        # still unmeasured is narrower and is the thing this line item actually
        # turns on: a lane count is not a median, and a six-lane road may be
        # divided or not.
        _count("roadway", "Whether the roadway is divided, and over how much of it", None,
               "not screened", "roadway",
               why_not=roadway.get("detail") or
                       "TxDOT's right-of-way width, lane count and traffic are "
                       "reported in the roadway block. Which TCP sheet applies "
                       "turns on whether the road is divided, and that is a "
                       "field this run does not read.",
               context=True),
    ]


# -------------------------------------------------------------- the arithmetic


def _quantity(value, unit):
    """A number with its unit, reading as English rather than as a template.

    "1 tracts" on a page a principal reads is a small thing that makes a
    careful document look generated, which is the last impression this one can
    afford. Only touches a bare plural noun -- a compound unit like "hours per
    tract" is left exactly as the table wrote it.
    """
    if value is None:
        return UNMEASURED
    shown = f"{value:g}"
    if value == 1 and unit.endswith("s") and " " not in unit:
        unit = unit[:-1]
    return f"{shown} {unit}"


def _factor(label, value, unit, source):
    return {"label": label, "value": value, "unit": unit, "source": source}


def _rate_factor(rates, key):
    """One factor taken from the rate table, carrying its handle."""
    rate = rates[key]
    return _factor(rate.label, rate.value, rate.unit, f"rate {rate_handle(key)} ({key})")


def _sheet_age_note(document):
    """How old this corridor's ROW sheets are, read from the run.

    Derived rather than typed, on ``bid_memo._route_key``'s rule: "so this memo
    is not a memo about SH 16 that happens to compile for anything else." The
    first draft of this line said "1900 to 2005" in prose, in a file whose own
    last line promises nothing was typed by hand.
    """
    span = ((document.get("row_maps") or {}).get("date_range") or {})
    oldest, newest = span.get("from"), span.get("to")
    if not oldest or not newest:
        return ("How old this corridor's sheets are was not recorded by the run. "
                "Scan legibility is what this rate turns on, so check the dates "
                "before trusting it.")
    return (f"Sheets in this corridor run from {oldest} to {newest}. Scans of "
            "that age are read by eye, and the oldest date may not be a date at "
            "all — the bid memo says why.")


def _line(key, label, kind, factors, note=None):
    """One line of the build-up: a chain of factors and their product.

    ``hours`` is ``None`` when any factor has no value, and ``blocked_by`` then
    names the factor that stopped it. That is the manhole case, and it is the
    reason a line is modeled as a chain rather than as a number: the
    arithmetic can be shown complete while the answer is honestly absent.
    """
    missing = [f["label"] for f in factors if f["value"] is None]
    hours = None
    if not missing:
        product = 1.0
        for factor in factors:
            product *= factor["value"]
        hours = round(product, 2)
    return {
        "key": key,
        "label": label,
        "kind": kind,
        "factors": factors,
        "hours": hours,
        "blocked_by": missing[0] if missing else None,
        "note": note,
    }


def lines(document, rates=None):
    """The seven lines of the build-up, in the order they are argued about."""
    rates = rates or load_rates()
    measured = {c["key"]: c for c in counts(document)}

    def count_factor(key):
        entry = measured[key]
        return _factor(entry["label"], entry["value"], entry["unit"],
                       f"run {entry['source']}")

    not_found = measured["ngs_not_found"]["value"]
    marks = measured["ngs_marks"]["value"]

    return [
        _line(
            "mark_recovery", "Look for the published NGS marks", "field",
            [count_factor("ngs_marks"),
             _rate_factor(rates, "hours_per_mark_recovery_attempt")],
            note=(f"All {not_found} of the {marks} marks in this corridor are "
                  "already recorded MARK NOT FOUND. Somebody has looked for each "
                  "one and could not find it. Whether to look again is a "
                  "judgment for the surveyor who signs."
                  if not_found and marks and not_found == marks else None),
        ),
        _line(
            "new_control", "Set new control", "field",
            [count_factor("corridor_miles"),
             _rate_factor(rates, "control_pairs_per_mile"),
             _rate_factor(rates, "hours_per_control_pair")],
            note=("On this evidence the control work is setting new rather than "
                  "recovering existing. That is the largest single judgment in "
                  "this estimate and it is the surveyor's, not the tool's."),
        ),
        _line(
            "tract_corners", "Recover corners, tract by tract", "field",
            [count_factor("tracts"),
             _rate_factor(rates, "hours_per_tract_corner_recovery")],
            note=("The biggest line on the page, and the first one to argue "
                  "with."),
        ),
        _line(
            "flagged_access", "Extra time on the flagged tracts", "field",
            [count_factor("flagged_tracts"),
             _rate_factor(rates, "hours_per_flagged_tract_access")],
            note=("Field hours only. The days of notice before the crew may go "
                  "at all are in the flagged parcel table, and they are days "
                  "rather than hours."),
        ),
        _line(
            "road_occupations", "Set and retrieve traffic control", "field",
            [count_factor("road_occupations"),
             _rate_factor(rates, "hours_per_road_occupation")],
            note=("This line has no total, and that is the finding. Nothing in "
                  "this run counts manholes or culverts, so nobody knows how "
                  "many times the crew has to close down and set up. It is not "
                  "zero. It is unmeasured, and on a job like this it is where "
                  "the time goes."),
        ),
        _line(
            "centerline_work", "Chain the centerline", "field",
            [count_factor("centerline_miles"),
             _rate_factor(rates, "hours_per_centerline_mile")],
            note=("**This is the line item that moves the number, and it has no "
                  "total.** Work on the centerline is TCP(S-3b), which draws "
                  "**two** shadow vehicles with TMA rather than the crew's own "
                  "truck. Nothing in this run says how much of the retracement "
                  "falls there. See *What changes the crew* below — this is not "
                  "only more hours, it is a different crew."),
        ),
        _line(
            "row_retracement", "Hand-retrace the ROW map sheets", "office",
            [count_factor("row_sheets"),
             _rate_factor(rates, "hours_per_row_sheet_retracement")],
            note=_sheet_age_note(document),
        ),
        _line(
            "drafting", "Draft the deliverable", "office",
            [count_factor("corridor_miles"),
             _rate_factor(rates, "office_hours_per_mile_drafting")],
        ),
    ]


def hours_for(kind, built):
    """Total hours of one kind, and the lines that could not be totaled.

    Returns ``(hours, blocked)``. A blocked line is never counted as zero and
    never silently dropped: it comes back so the caller has to say something
    about it.
    """
    wanted = [line for line in built if line["kind"] == kind]
    hours = round(sum(line["hours"] for line in wanted if line["hours"] is not None), 2)
    return hours, [line for line in wanted if line["hours"] is None]


def days(hours, hours_per_day):
    """Hours into whole days, rounded up.

    Half a day in the field is a day. Nobody sends a crew home at noon, and
    rounding down is the quiet way an estimate turns optimistic -- once per
    line rather than once per estimate.
    """
    if not hours:
        return 0
    return math.ceil(hours / hours_per_day)


# ------------------------------------------------------------------ the Markdown


def _arithmetic(line, times="x"):
    """One line of the build-up as somebody would write it on an envelope."""
    parts = [_quantity(f["value"], f["unit"]) for f in line["factors"]]
    shown = f" {times} ".join(parts)
    answer = UNMEASURED if line["hours"] is None else f"{line['hours']:.2f} hours"
    return f"{shown} = {answer}"


def _block(built, kind, rates, heading, day_rate_key, day_word):
    """One half of the build-up: its lines, its total, and its day count."""
    hours, blocked = hours_for(kind, built)
    per_day = rates[day_rate_key]
    count = days(hours, per_day.value)

    out = [f"## {heading}", ""]
    for line in built:
        if line["kind"] != kind:
            continue
        out.append(f"**{line['label']}**")
        out.append("")
        out.append(f"> {_arithmetic(line, times='×')}")
        out.append("")
        for factor in line["factors"]:
            out.append(f"- {factor['label']} — {factor['source']}")
        if line["blocked_by"]:
            out.append(f"- **No total: {line['blocked_by']} was never measured.**")
        out.append("")
        if line["note"]:
            out.append(line["note"])
            out.append("")

    out += [
        f"**{heading} total: {hours:.2f} hours.**",
        "",
        f"{hours:.2f} hours ÷ {per_day.value:g} {per_day.unit} "
        f"= **{count} {day_word}**, rounded up.",
        "",
    ]
    if blocked:
        out += [
            f"**That total is a floor.** {len(blocked)} line"
            f"{'s' if len(blocked) > 1 else ''} above could not be totaled at "
            "all, and the hours are missing from this figure rather than being "
            "zero in it: "
            + ", ".join(f"*{line['label']}*" for line in blocked) + ".",
            "",
        ]
    return out, hours, count, blocked


def build(document, rates=None):
    """The build-up, in Markdown. Nothing here is typed by hand."""
    rates = rates or load_rates()
    run = document.get("run") or {}
    alignment = document.get("alignment") or {}
    built = lines(document, rates)
    measured = {c["key"]: c for c in counts(document)}

    out = [f"# Crew-day build-up — {alignment.get('source_path', 'this corridor')}", ""]

    if run.get("status") != "complete":
        # Plain blockquote rather than an MkDocs admonition, for the reason
        # `bid_memo` records: this file is read on GitHub, where `!!! warning`
        # renders as literal text.
        out += [
            f"> ## ⚠ This run was recorded as **{run.get('status', 'incomplete')}**",
            ">",
            "> Some services were never reached, so every count below is a floor",
            "> rather than a count, and so is every number built on one.",
            "",
        ]

    out += [
        "**This is not an estimate. It is an estimate somebody can argue with.**",
        "",
        "Every quantity below is read from `screening.json`. The rates are "
        "**not a published standard** — TxDOT publishes no production rates, and "
        "this tool has never been near the corridor. Nobody has walked it. Each "
        f"rate carries a handle, `A1` through `A{len(RATES_USED)}`, so a surveyor "
        "can disagree with one of them out loud, by name, rather than "
        "disagreeing with the total.",
        "",
        "An **RPLS** reads this and decides. The tool decides nothing.",
        "",
    ]

    # --- the inputs
    out += [
        "## What went in",
        "",
        "| Input | Value | Where it came from |",
        "|---|---|---|",
    ]
    for entry in measured.values():
        value = (_quantity(entry["value"], entry["unit"]) if entry["measured"]
                 else f"**{UNMEASURED}**")
        out.append(f"| {entry['label']} | {value} | {entry['source']} |")
    out.append("")

    unmeasured = [e for e in measured.values() if not e["measured"]]
    if unmeasured:
        out += [
            f"**{len(unmeasured)} of these {len(measured)} inputs were never "
            "measured**, and they are not zero. Each one below is a question "
            "somebody still has to answer, and the arithmetic that needs it is "
            "left without a total rather than given a convenient one.",
            "",
        ]
        for entry in unmeasured:
            out.append(f"- **{entry['label']}** — {entry['why_not']}")
        out.append("")

    # --- the two halves, never one total
    field_block, field_hours, field_days, field_blocked = _block(
        built, "field", rates, "Field hours", "field_hours_per_crew_day", "crew-days")
    office_block, office_hours, office_days, _ = _block(
        built, "office", rates, "Office hours", "office_hours_per_day", "office days")
    out += field_block + office_block

    crew = rates["crew_size"]
    out += [
        "## The two are not added together",
        "",
        f"**{field_days} crew-days in the field. {office_days} days in the "
        "office.** They are different things bought from different people, and "
        "adding them makes a number that cannot be checked against anything.",
        "",
        f"A crew-day here is **{crew.value:g} {crew.unit}** for "
        f"{rates['field_hours_per_crew_day'].value:g} productive hours. Putting a "
        "third person on the truck does not divide the hours by three, and this "
        "build-up will not pretend it does.",
        "",
    ]

    # --- traffic control
    out += [
        "## Traffic control, from the sheets themselves",
        "",
        f"**{TCP_SHEET}** was pulled by hand and is committed at "
        f"[`{TCP_SHEET_PATH}`](manual-pulls/tcp-s-1-08a.pdf), fetched from "
        f"[{TCP_SHEET_URL}]({TCP_SHEET_URL}) and verified byte for byte on "
        f"{TCP_SHEET_VERIFIED_ON}. **It covers the two shoulder cases and "
        "nothing else**, so every claim below about another sheet is sourced to "
        f"[`{TCP_FAMILY_PATH}`](manual-pulls/tcp-s-family.md), which is the "
        "reading of all six. Nothing is read across from a standard outside the "
        "family, which is how this repo got it wrong once already.",
        "",
        "**What each case draws**, because the drawn vehicle is what decides the "
        "cost and the note wording is what misleads:",
        "",
        "| Case | What it covers | Protective vehicle drawn |",
        "|---|---|---|",
    ]
    for case, covers, drawn in SHEET_CASES:
        out.append(f"| **{case}** | {covers} | {drawn} |")
    out.append("")

    for note in TRAFFIC_CONTROL:
        out += [f"**{note['topic']}** *({note['sheet']})*. {note['detail']}", ""]

    out += [
        f"The duration line is **{DURATION_LINE_HOURS} hour**. How often this "
        "corridor's work crosses it depends on counts nobody has — see the "
        "traffic-control and centerline lines above, neither of which has a "
        "total.",
        "",
        "## What changes the crew, not just the hours",
        "",
        "Two of the unmeasured inputs do something the arithmetic above cannot "
        "show. They do not make the days longer. They change **who has to be on "
        "the road**, and that is a different kind of cost. Both are in this "
        "build-up without numbers on purpose: an honest unknown belongs in a "
        "document that is supposed to be argued with.",
        "",
    ]
    for change in CREW_CHANGES:
        out += [
            f"### {change['trigger']} — {change['sheet']}",
            "",
            f"**The crew becomes: {change['becomes']}.**",
            "",
            change["detail"],
            "",
            f"**Not measured:** {change['unmeasured']}",
            "",
        ]

    # --- the assumptions, one row each
    #
    # **The standfirst is derived, not asserted.** It used to read "none of them
    # is published by TxDOT or by anybody else" unconditionally, while the table
    # below it renders a `Published:` cell for any row `_check` accepts as
    # non-assumption. Both could not be true at once, and the sentence a reader
    # trusts is the one above the table.
    published = [k for k in RATES_USED if not rates[k].assumption]
    out += [
        "## Every rate, with its handle",
        "",
        "Disagree with a row, not with the total. "
        + ("Every one of these is somebody's judgment, and **none of them is "
           "published by TxDOT or by anybody else** — the standard sheets say "
           "what goes on the road, not how long it takes to put it there."
           if not published else
           f"{len(RATES_USED) - len(published)} of these {len(RATES_USED)} are "
           f"somebody's judgment; {len(published)} carry a published source, "
           "named in the last column."),
        "",
        "| | Rate | Value | What to argue with |",
        "|---|---|---|---|",
    ]
    for key in RATES_USED:
        rate = rates[key]
        argue = rate.disagree_with if rate.assumption else (
            f"Published: {rate.source}"
            + (f" ([source]({rate.url}), read {rate.verified_on})"
               if rate.url else ""))
        out.append(f"| `{rate_handle(key)}` | {rate.label} | {rate.value:g} "
                   f"{rate.unit} | {argue} |")
    out.append("")
    out += [
        "The reasoning behind each one is in "
        "[`crew_rates.toml`](../corridor-screen/corridor_screen/crew_rates.toml), "
        "which is plain text a firm edits without touching any Python. **Replace "
        "these with your own rates before quoting anything.**",
        "",
    ]

    # --- what it is not
    out += [
        "## What this build-up is not",
        "",
        "It is **not a quote**. There is no rate per day here, and no total in "
        "dollars.",
        "",
        "It is **not a schedule**. Days of work are not days on the calendar: the "
        "notice periods that decide when a crew may go at all are in the flagged "
        "parcel table, counted in days of two different kinds.",
        "",
        "It is **not a measured job**. Nobody has walked this corridor. Every "
        "count came from a public map service on the date the run records.",
        "",
        "It is a first pass, with the arithmetic left open so somebody who knows "
        "the work can correct it. **An RPLS reads it and signs, and remains "
        "accountable for every number that reaches a client.**",
        "",
        "---",
        "",
        f"Run `{run.get('mode', '?')}`, finished "
        f"{run.get('finished_at', 'not recorded')}. Built by "
        f"corridor-screen {run.get('tool_version', '?')} from `screening.json` "
        f"and `crew_rates.toml`. Nothing here was typed by hand.",
    ]
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------ the console


def summary(document, rates=None):
    """The same build-up, as a console rendering and as the committed fallback.

    **Plain ASCII, deliberately**, and `beats.render` refuses anything else. An
    em dash here is a `UnicodeEncodeError` and a traceback on any Windows
    console that has not been told to use UTF-8 -- which is the default, and
    every borrowed podium laptop.

    **Note which of this module's two outputs that applies to.** The Markdown
    build-up beside this is written as UTF-8 and is full of multiplication and
    division signs and em dashes, correctly: it is read in an editor or on the
    site, not printed at a console. This one is printed, at 1:18, on somebody
    else's laptop. Same module, opposite rules.

    Issue #67 built the guard for the failure beats. This is not a beat -- it
    renders an estimate, and it has no captures and no `beat()` -- but the
    console it prints to is the same console.
    """
    rates = rates or load_rates()
    built = lines(document, rates)
    alignment = document.get("alignment") or {}
    run = document.get("run") or {}

    field_hours, field_blocked = hours_for("field", built)
    office_hours, _ = hours_for("office", built)
    field_days = days(field_hours, rates["field_hours_per_crew_day"].value)
    office_days = days(office_hours, rates["office_hours_per_day"].value)
    assumed = sum(1 for k in RATES_USED if rates[k].assumption)

    out = [
        f"  Crew-day build-up  {alignment.get('source_path', 'this corridor')}",
        f"  Run {run.get('mode', '?')}, finished {run.get('finished_at', 'not recorded')}",
        "",
    ]
    for kind, title in (("field", "FIELD"), ("office", "OFFICE")):
        out.append(f"  {title}")
        for line in built:
            if line["kind"] == kind:
                out.append(f"    {line['label']:<38} {_arithmetic(line)}")
        out.append("")

    out += [
        f"  field   {field_hours:>8.2f} hours  =  {field_days} crew-days "
        f"of {rates['crew_size'].value:g}",
        f"  office  {office_hours:>8.2f} hours  =  {office_days} office days",
        "  The two are never added together.",
        "",
    ]
    if field_blocked:
        count = len(field_blocked)
        out.append(f"  {count} line{'s' if count > 1 else ''} above "
                   f"{'have' if count > 1 else 'has'} no total at all, because")
        out.append("  an input was never measured. Those hours are missing from")
        out.append("  the figures above, not zero in them:")
        for line in field_blocked:
            out.append(f"    {line['label']}: {line['blocked_by']} is {UNMEASURED}")
        out.append("")

    out += [
        # Derived, for the reason the Markdown's own standfirst is derived: the
        # loader accepts a published row, so this may not assert there are none.
        f"  Every rate has a handle, A1 to A{len(RATES_USED)}. "
        + (f"{assumed} of them are" if assumed != len(RATES_USED) else "All are"),
        "  somebody's assumption, not TxDOT's. Argue with a row, not a total.",
        f"  Traffic control read from {TCP_SHEET}: the duration line is",
        f"  {DURATION_LINE_HOURS} hour, and no posted speed anywhere in the family",
        "  puts a shadow truck on the job.",
        "",
        "  An RPLS reads this and decides. Nobody has walked the corridor.",
    ]
    return beats.render(out) + "\n"


def write(document, out_dir, rates=None):
    """Both renderings, and the paths they went to.

    The fallback is written every run rather than on a flag. See the module
    docstring for why there is no ``--write-fallback`` here.
    """
    rates = rates or load_rates()
    build_up_path = Path(out_dir) / BUILD_UP_NAME
    fallback_path = Path(out_dir) / FALLBACK_NAME
    write_text(build_up_path, build(document, rates))
    write_text(fallback_path, summary(document, rates))
    return [build_up_path, fallback_path]


def main(argv=None):
    """``python -m corridor_screen.crew_day --out ../project-sh16``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen crew-day",
        description="Write the crew-day build-up from a screening run.",
    )
    parser.add_argument("--out", required=True,
                        help="The project directory holding screening.json")
    args = parser.parse_args(argv)

    source = Path(args.out) / "screening.json"
    with open(long_path(source), "r", encoding="utf-8") as handle:
        document = json.load(handle)

    rates = load_rates()
    for path in write(document, args.out, rates):
        print(f"  written  {path}")
    print()
    print(summary(document, rates), end="")
    if document["run"]["status"] != "complete":
        print("  note     the run was incomplete, and the build-up says so at the top")
    return 0


if __name__ == "__main__":
    sys.exit(main())
