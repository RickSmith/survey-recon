"""The right-of-entry letters, and the clock that writes the second one.

Issue #34. Six minutes on the day, and first on the cut line.

**Right of entry is not a statutory right in Texas.** You have to ask. An RPLS
who is refused *may seek* a court order -- Tex. Occ. Code § 1071.3585 -- and an
LSLS acting in an official capacity *is entitled to* one, § 1071.358. Neither is
a right to walk on. So the letter is real work, and the second letter is the
work that real firms forget.

TxDOT already knows this. The Surveyors' Toolkit ships **two** templates, a
first request letter (020-10-tem) and a **second** request letter (020-11-tem).
Non-response is not an exception the department planned around. It is the
baseline it designed for. This module does the part a person forgets: it
notices that the first letter has been out long enough and writes the second
one without being asked.

----

Where day 21 comes from
=======================

This is the whole segment, so it is worth being slow about.

**There is no published right-of-entry turn-around to quote.** Every TxDOT
manual this repo read was searched for one and none was found -- the account is
in `docs/txdot-research.md`, Part 3. The thirty-day windows in the acquisition
process are offer-stage and are a different thing. So the interval cannot be
cited. Writing ``21`` into this file would be inventing a requirement, which is
the one thing `CLAUDE.md` says never to do.

What can be done instead is to **derive** it from the firm's own checked-in
lead-time table, in three steps a person can argue with out loud:

1. **Take the longest confirmed lead time the table carries, counted in
   calendar days.** On the committed table that is the railroad's 45 days --
   Union Pacific's own published turn-around. It is the outer clock the
   corridor is planned against, so it is the schedule the letter is spending.
2. **Halve it.** A follow-up that fires later than half-way leaves the second
   letter less time to be answered than the first one had, which makes it a
   formality rather than a second ask. Half of 45 is 22 whole days.
3. **Round down to whole weeks.** A letter moves in weeks -- mail, an office
   cycle, a board that meets monthly. Rounding *down* fires earlier and never
   later, so the rule can only cost the tool time, never the schedule. 22 days
   is three whole weeks, which is **21**.

Change the table and the day changes with it. Put 60 days in the railroad row
and the follow-up moves to day 28. Take the railroad row out and the cemetery's
14 calendar days becomes the outer clock and the follow-up moves to day 7.
There is no 21 anywhere in this file, and `tests/test_roe.py` is mostly there to
prove it.

**Working-day rows are left out of the arithmetic.** The pipeline row counts
two *working* days, and turning those into calendar days would mean inventing a
calendar of weekends and Texas legal holidays this tool does not have and could
not check. That rule is already load-bearing in `lead_times.py`; halving a
number is not a good enough reason to break it here.

**A table that cannot produce a whole week says so.** Thirteen calendar days
halves to six, which is not a week, so there is no interval to derive. It
raises rather than answering zero, because zero days reads as "send both
letters at once" and that is not a plan. Same shape as *not found* everywhere
else in this repo.

----

What this does not do
=====================

**It does not mail anything.** It writes a letter into a file. There is no mail
server, no address book, no API key, and there is nothing here an attendee has
to sign up for -- `CLAUDE.md` is blunt that anything needing a key does not
belong in the attendee path. "Sends itself" means the clock fires and the
letter is written with nobody remembering. A person still signs it and a person
still sends it.

**It does not print a street address.** The appraisal district publishes one and
this repo is public. The letter needs the parcel and the owner, because those
are what the screening flagged. A specimen carrying a real mailing address
invites being mailed.

**It does not know about weekends.** The interval is counted in calendar days,
and whole weeks means the second letter always falls on the same weekday as the
first. On the committed SH16 run both fall on a Sunday. The clock writes the
letter anyway, and the person sends it on Monday. Saying that is cheaper than a
holiday calendar the tool would have to keep right.

**An RPLS signs it and remains accountable for it.** 22 Tex. Admin. Code
§ 131.2(38): responsible charge is the same standard as direct supervision. A
letter a machine wrote is a letter a licensed human sends.
"""

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

from . import beats, lead_times, parcel_table
from .cache import long_path

# The committed SH16 run. The demo is built from it rather than from anything
# typed here, so the letter's parcel, owner and flags are all values a reader
# can go and find in a public file.
SCREENING = Path(__file__).resolve().parent.parent.parent / "project-sh16" / "screening.json"
SOURCE_FILE = "screening.json"

# Where the recorded demo lives. `beats.capture_dir` rather than a path spelled
# out again, because it is the same folder rule the failure beats use.
CAPTURE_DIR = beats.capture_dir("the-letter-that-sends-itself")

# Not `the-beat.txt`. This is not a failure beat -- nothing in it is wrong, and
# `tests/test_beats.py` finds beats by looking for a callable named `beat`,
# which this module deliberately does not export. What it borrows from a beat
# is the plain-ASCII rule, because it prints to the same podium console.
DEMO_NAME = "the-demo.txt"

# Which days the derived interval counts. Only rows counted in these days are
# eligible, and the number is never converted from anything else. See the
# module docstring.
CALENDAR_DAYS = "calendar days"

# A letter moves in weeks, so the interval is rounded to them. Rounding down,
# never up: the tool may spend its own slack and never the schedule's.
DAYS_IN_A_WEEK = 7

# TxDOT's own templates, from the Surveyors' Toolkit. Named on the letters so a
# reader can see this tool is standing in for a department form rather than
# inventing correspondence.
TEMPLATES = {1: "020-10-tem", 2: "020-11-tem"}
TOOLKIT_URL = "https://www.txdot.gov/business/resources/surveyor-toolkit.html"
ROE_MANUAL_URL = "https://www.txdot.gov/manuals/row/ess/surveying_procedures/right_of_entry.html"

# The day the clock starts on the committed demo: the day the SH16 screening
# run finished and flagged the tract. Read from the run rather than typed, so
# the demo cannot drift from the data it claims to come from.
DEMO_PARCEL = "15664-003-0040"


class NoFollowUpInterval(Exception):
    """The lead-time table cannot produce a follow-up interval, and says why."""


class NotAFlaggedParcel(Exception):
    """Asked for a letter about a tract the screening did not flag."""


class FollowUpInterval:
    """How long the first letter waits, and the arithmetic that got there.

    Every field here is either read from one row of the lead-time table or
    computed from it in front of the reader. There is nothing to take on trust,
    which is the point of the segment.
    """

    def __init__(self, row, days, half_days):
        self.driver = row.key
        self.label = row.label
        self.lead_time_days = row.days
        self.basis = row.basis
        self.source = row.source
        self.url = row.url
        self.half_days = half_days
        self.days = days

    def arithmetic(self):
        """The three steps, as plain lines a console or a letter can print.

        **The citation is given as its URL and not as its title**, and that is
        not a style choice. One of the two callers is the podium console, which
        is held to plain ASCII by `beats.render` -- and Union Pacific's own
        page title carries an em dash, so printing `source` here fails the
        guard. A URL is ASCII by construction. The full title goes on the
        letter, which is read in an editor and may carry anything.

        This was caught by the guard rather than by review, which is the whole
        argument for having it.
        """
        weeks = self.days // DAYS_IN_A_WEEK
        return [
            f"longest confirmed wait, counted in {self.basis}   "
            f"{self.lead_time_days} days",
            f"  set by the {self.driver} row, cited to {self.url}",
            f"half of it, so letter two has the window letter one had   "
            f"{self.half_days} days",
            f"rounded down to whole weeks, because a letter moves in weeks   "
            f"{self.days} days ({weeks} weeks)",
        ]


def follow_up_interval(table=None):
    """Derive the follow-up interval from the lead-time table.

    Raises `NoFollowUpInterval` rather than guessing. A tool that answers zero
    here has told a firm to send both letters on the same morning.
    """
    table = table if table is not None else lead_times.load()
    eligible = [
        row for row in table.values()
        if row.confirmed and row.basis == CALENDAR_DAYS
        and isinstance(row.days, (int, float))
    ]
    if not eligible:
        # Name what was rejected and why. "No eligible rows" sends somebody to
        # read this function; naming the working-day rows sends them to the
        # table, which is where the answer is.
        working = sorted(
            row.key for row in table.values()
            if row.confirmed and row.basis != CALENDAR_DAYS
        )
        raise NoFollowUpInterval(
            "no confirmed lead time in the table is counted in calendar days, "
            "so there is no number to halve."
            + (
                f" Rows counted in working days are not eligible and were not "
                f"converted: {', '.join(working)}. Two working days and two "
                f"calendar days are different promises."
                if working else
                " Every row with a number is unconfirmed, and an unconfirmed "
                "row has no figure to derive from."
            )
        )

    row = max(eligible, key=lambda r: r.days)
    half_days = math.floor(row.days / 2)
    days = (half_days // DAYS_IN_A_WEEK) * DAYS_IN_A_WEEK
    if days < DAYS_IN_A_WEEK:
        raise NoFollowUpInterval(
            f"the longest confirmed wait counted in calendar days is "
            f"{row.days} days ({row.key}). Half of that is {half_days} days, "
            f"which is not a whole week, so no follow-up interval can be "
            f"derived. Zero days would read as sending both letters at once, "
            f"and that is not a plan."
        )
    return FollowUpInterval(row, days, half_days)


class Letter:
    """One right-of-entry request, and the day it falls on."""

    def __init__(self, number, day, date, parcel, document, interval):
        self.number = number
        self.day = day
        self.date = date
        self.parcel_id = parcel["id"]
        self.owner = parcel.get("owner") or "Owner not published by the appraisal district"
        self.parcel = parcel
        self.document = document
        self.interval = interval
        self.source_file = SOURCE_FILE

    @property
    def template(self):
        return TEMPLATES[self.number]

    def filename(self):
        return f"roe-letter-{self.number}.md"

    def markdown(self):
        return "\n".join(_letter_lines(self)) + "\n"


def schedule(document, parcel, sent_on, interval=None):
    """The two letters this tract gets, and the dates they fall on.

    Two, because TxDOT ships two templates. A third would be this tool's own
    invention, and there is nothing to cite for it.
    """
    if not parcel.get("flags"):
        raise NotAFlaggedParcel(
            f"parcel {parcel.get('id')} carries no flags in this run, so there "
            f"is nothing the screening found to ask about. A letter written "
            f"for every tract in a corridor is a mail merge, not a finding."
        )
    interval = interval if interval is not None else follow_up_interval()
    return [
        Letter(1, 0, sent_on, parcel, document, interval),
        Letter(2, interval.days, sent_on + dt.timedelta(days=interval.days),
               parcel, document, interval),
    ]


def due_on(letters, as_of):
    """The letters whose day has come or gone, as of a date.

    **Gone counts.** A clock nobody read on the day is still a clock, and a
    follow-up that silently expires because the check did not run on the right
    morning is the failure this whole segment is about.
    """
    return [letter for letter in letters if letter.date <= as_of]


# ---------------------------------------------------------------------------
# The letters themselves
# ---------------------------------------------------------------------------

def _wait_sentence(parcel):
    """What the screening says this tract costs, in one readable line."""
    return parcel_table.wait_cell(parcel)


def _flag_sentence(parcel):
    return parcel_table.flag_cell(parcel)


def _citations(parcel):
    """Source and link for every flag on this tract, deduplicated.

    A letter quoting a statutory notice period has to carry the statute. The
    reader of the letter is the person who would be relying on it.
    """
    seen = {}
    for flag in parcel.get("flags") or []:
        source = flag.get("lead_time_source")
        if source and source not in seen:
            seen[source] = flag.get("lead_time_url")
    return list(seen.items())


def _not_found_accounts(parcel):
    seen = []
    for flag in parcel.get("flags") or []:
        account = flag.get("lead_time_not_found")
        if account and account not in seen:
            seen.append(account)
    return seen


def _letter_lines(letter):
    parcel = letter.parcel
    run = letter.document.get("run") or {}
    interval = letter.interval
    ordinal = "first" if letter.number == 1 else "second"

    lines = [
        f"# Right of entry — {ordinal} request",
        "",
        f"**Parcel `{letter.parcel_id}`** · {letter.owner}",
        "",
        f"**Written {letter.date.isoformat()}** — day {letter.day} of the "
        f"follow-up clock.",
        "",
        "> **Specimen. Not mailed, not signed, not sent.** This letter was "
        "written by the corridor-screening tool from public records, for the "
        "TSPS 2026 session. It carries no address and it went nowhere. An "
        "**RPLS** signs a real one and remains accountable for it — 22 Tex. "
        "Admin. Code § 131.2(38).",
        "",
        "---",
        "",
        "## Why you are getting this",
        "",
        "Right of entry is **not a statutory right** in Texas. A surveyor asks "
        "permission, and a landowner may say no. A Registered Professional "
        "Land Surveyor who is refused *may seek* a court order — Tex. Occ. "
        "Code § 1071.3585 — and a Licensed State Land Surveyor acting in an "
        "official capacity *is entitled to* one, § 1071.358. Neither is a "
        "right to walk on your land today.",
        "",
        "So this is a request, and it is the only thing it is.",
        "",
    ]

    if letter.number == 2:
        lines += [
            "## This is the second request",
            "",
            f"A first request was written on "
            f"{(letter.date - dt.timedelta(days=letter.day)).isoformat()} and "
            f"**{letter.day} calendar days** have passed with no reply on "
            f"file. TxDOT ships a second request letter template "
            f"(`{TEMPLATES[2]}`) in its [Surveyors' Toolkit]"
            f"({TOOLKIT_URL}) precisely because non-response is the ordinary "
            f"case rather than the exception. This stands in for that form.",
            "",
            "### Where day "
            f"{letter.day} came from",
            "",
            "**No published TxDOT right-of-entry turn-around was found.** Every "
            "manual this repo read was searched and none states one — the "
            "account of where we looked is in "
            "[`docs/txdot-research.md`](../../docs/txdot-research.md), Part 3. "
            "The 30-day windows in the acquisition process are offer-stage and "
            "are a different thing. So this interval is **not** quoted from a "
            "source. It is derived from the checked-in "
            "[lead-time table](../../docs/corridor-screen/lead-times.md):",
            "",
            "```",
        ]
        lines += ["  " + step for step in interval.arithmetic()]
        lines += [
            "```",
            "",
            f"The row that set it: {interval.source} — <{interval.url}>",
            "",
            f"Change the table and this day changes. `{interval.days}` is not "
            f"written anywhere in the tool.",
            "",
        ]

    lines += [
        "## What the screening found on this tract",
        "",
        f"- **On it:** {_flag_sentence(parcel)}",
        f"- **Longest wait before entry:** {_wait_sentence(parcel)}",
        "",
        "That wait is a notice period, not the length of the work. It is how "
        "long a crew must wait before it can start.",
        "",
    ]

    citations = _citations(parcel)
    if citations:
        lines += ["### Where that comes from", ""]
        for source, url in citations:
            lines.append(f"- {source}" + (f" — <{url}>" if url else ""))
        lines.append("")

    accounts = _not_found_accounts(parcel)
    if accounts:
        lines += ["### What we looked for and could not confirm", ""]
        for account in accounts:
            lines.append(f"- {account}")
        lines += [
            "",
            "A wait recorded as **not found** is unmeasured, not zero. Somebody "
            "has to make the call that turns it into a date.",
            "",
        ]

    lines += [
        "## What is being asked for",
        "",
        "Permission for a survey crew to enter the tract above on foot, to "
        "locate and recover existing monuments and to take measurements. No "
        "excavation beyond hand-driven monuments, no vehicles off existing "
        "surface, and every gate left as it was found.",
        "",
        "TxDOT's own procedure requires every request to be documented by "
        f"written letter — [Survey Manual, Ch. 2 §3]({ROE_MANUAL_URL}). Oral "
        "permission is valid for **one day and for the one person who received "
        "it**, and is recorded in the field notes and initialed.",
        "",
        "## How this letter was produced",
        "",
        f"- Read from `{letter.source_file}`, screening run "
        f"`{run.get('run_id', 'not recorded')}`, finished "
        f"{run.get('finished_at', 'not recorded')}",
        f"- Stands in for TxDOT template `{letter.template}`",
        "- Every value above is public record. **No client data was used.**",
        "",
        "Not mailed. Not signed. A licensed surveyor does both.",
    ]
    return lines


# ---------------------------------------------------------------------------
# The demo
# ---------------------------------------------------------------------------

def read_screening(path=None):
    with open(long_path(Path(path or SCREENING)), "r", encoding="utf-8") as handle:
        return json.load(handle)


def find(document, parcel_id):
    for record in document.get("parcels") or []:
        if record.get("id") == parcel_id:
            return record
    raise NotAFlaggedParcel(f"{parcel_id} is not in this screening run")


def _found_in_run(document, flag_type):
    """Did this run actually find that kind of flag, on a parcel or corridor-wide?

    Asked so the demo can answer the obvious objection only when there is one.
    """
    for parcel in document.get("parcels") or []:
        for flag in parcel.get("flags") or []:
            if flag.get("type") == flag_type:
                return True
    for flag in document.get("corridor_flags") or []:
        if flag.get("type") == flag_type:
            return True
    return False


def demo(document=None, parcel_id=DEMO_PARCEL):
    """The six minutes, as a console can print it.

    Built from the committed run and the committed table, so it needs no
    network and reads the same on the day as it does now.
    """
    document = document if document is not None else read_screening()
    parcel = find(document, parcel_id)
    interval = follow_up_interval()
    run = document.get("run") or {}

    # Day 0 is the day the screening flagged the tract. Read from the run
    # rather than typed here, so the demo cannot claim a date the data does
    # not have.
    sent_on = dt.date.fromisoformat((run.get("finished_at") or "")[:10])
    letters = schedule(document, parcel, sent_on, interval)
    second = letters[1]
    day_before = second.date - dt.timedelta(days=1)

    # No leading or trailing blank line, so the committed recording is the
    # rendered text plus exactly one newline -- the same shape the three
    # failure beats commit, checked the same way.
    lines = [
        "  The letter that sends itself",
        "  ===========================",
        "",
        "  Right of entry is not a statutory right in Texas. You have to ask,",
        "  and when nobody answers you have to ask again. TxDOT ships a second",
        "  request letter template because non-response is the ordinary case.",
        "",
        f"  The tract, read out of project-sh16/{SOURCE_FILE}",
        f"    parcel        {parcel['id']}",
        f"    owner         {parcel.get('owner')}",
        f"    on it         {_flag_sentence(parcel)}",
        f"    longest wait  {_wait_sentence(parcel)}",
        "",
        f"  Where day {interval.days} comes from",
        "    No published right-of-entry turn-around was found in any TxDOT",
        "    manual this repo read, so there is no number to quote. The",
        "    interval is derived from the checked-in lead-time table instead:",
        "",
    ]
    lines += ["      " + step for step in interval.arithmetic()]
    lines += [
        "",
        f"    Change the table and this day changes. There is no {interval.days} "
        f"written anywhere in the tool.",
    ]
    # The obvious objection from the room, answered before it is asked. On
    # SH16 the railroad row sets the interval and the run found no railroad,
    # which reads as a bug until somebody says what the interval is actually
    # measuring. Printed only when it is true of the run in hand -- a corridor
    # that does have a railroad on it should not be told this.
    if not _found_in_run(document, interval.driver):
        lines += [
            "",
            f"    The {interval.driver} row sets it, and no {interval.driver} "
            f"was found on this corridor.",
            "    That is deliberate. The interval is how long a letter may sit",
            "    before you ask again, not what is on this one tract -- so it",
            "    comes from the longest wait the firm plans against anywhere.",
            "",
        ]
    lines += [
        "  The clock, with nobody watching it",
        f"    {letters[0].date.isoformat()}   day {letters[0].day:<2}  "
        f"request 1 of 2 written",
        f"    {day_before.isoformat()}   day {second.day - 1:<2}  nothing due",
        f"    {second.date.isoformat()}   day {second.day:<2}  "
        f"request 2 of 2 written -- no human action",
        "",
        f"  {interval.days} days is {interval.days // DAYS_IN_A_WEEK} whole weeks, "
        f"so letter two falls on the same weekday as letter one. Both",
        f"  land on a {second.date.strftime('%A')}. The clock counts calendar days "
        f"and knows nothing about weekends or",
        "  holidays. It writes the letter; a person still sends it.",
        "",
        "  What this does not do",
        "    It does not mail anything. It has no address and no authority.",
        "    An RPLS signs the letter and remains accountable for it --",
        "    22 Tex. Admin. Code 131.2(38).",
    ]
    return beats.render(lines)


def write_recording(folder=None, text=None):
    """Write the rendered demo beside its README, and say where it went.

    Not `beats.write_fallback`, which writes a file called `the-beat.txt`.
    This is not a failure beat and should not be filed as one. What the two
    share -- the ASCII guard, UTF-8, `\\n` endings and `long_path` -- is
    shared; the file name is not.
    """
    folder = Path(folder or CAPTURE_DIR)
    path = folder / DEMO_NAME
    with open(long_path(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write((text if text is not None else demo()) + "\n")
    return path


def write_letters(out_dir, as_of=None, parcel_id=DEMO_PARCEL, document=None):
    """Write every letter that is due as of a date. This is what the clock runs.

    Only the letters that are due. A run before day 21 writes one file; a run
    on or after it writes two, and nobody had to remember.
    """
    document = document if document is not None else read_screening()
    parcel = find(document, parcel_id)
    interval = follow_up_interval()
    run = document.get("run") or {}
    sent_on = dt.date.fromisoformat((run.get("finished_at") or "")[:10])
    as_of = as_of or dt.date.today()

    folder = Path(out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for letter in due_on(schedule(document, parcel, sent_on, interval), as_of):
        path = folder / letter.filename()
        with open(long_path(path), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(letter.markdown())
        written.append((letter, path))
    return written


def main(argv=None):
    """``python -m corridor_screen.roe --show``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen roe",
        description=(
            "The two right-of-entry letters for a flagged tract, and the clock "
            "that writes the second one without being asked."
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show", action="store_true",
                       help="print the demo (the default)")
    group.add_argument("--write-fallback", action="store_true",
                       help=f"re-render the committed {DEMO_NAME} beside its README")
    group.add_argument("--write", metavar="DIR",
                       help="write every letter that is due into DIR")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD",
                        help="the date the clock is read on. Default today.")
    args = parser.parse_args(argv)

    if args.write_fallback:
        print(f"  written  {write_recording()}")
        return 0

    if args.write:
        try:
            as_of = dt.date.fromisoformat(args.as_of) if args.as_of else None
        except ValueError:
            parser.error("--as-of must be a date written YYYY-MM-DD")
        written = write_letters(args.write, as_of=as_of)
        for letter, path in written:
            print(f"  written  {path}  (request {letter.number} of 2, "
                  f"day {letter.day})")
        if len(written) < 2:
            interval = follow_up_interval()
            print(f"  waiting  request 2 of 2 is not due until day "
                  f"{interval.days}")
        return 0

    print(demo())
    return 0


if __name__ == "__main__":
    sys.exit(main())
