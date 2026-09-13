"""The one call that is genuinely live, and what it proves.

The plan of record asks for this in one line: **"Keep one genuinely live call --
NGS `/radial` was the most reliable endpoint tested. One live moment proves it
isn't a movie."**

This is that moment. A screening run replays a committed capture and says so;
this command goes out to NGS while the room watches, and compares what comes
back against what the capture found.

----

Why it is a separate command and not a mode
===========================================

It would have been easy to make one service in the screening run go live while
the rest replayed. That would have been a worse demo and a worse tool.

``--mode cache-only`` promises no network calls at all, and that promise is the
safety net a presenter is standing on. A blended mode would have put a live
call inside the run that must not fail, so a captive portal at the venue would
take down the screening as well as the live moment. Here, the worst a dead
network can do is cost the live moment. The screening is already on disk.

Two acts, in the order a presenter wants them: run the screening from cache,
then prove the wires are real.

**Running this rewrites one cache entry**, and that is worth knowing before it
surprises somebody. Section 14 says every response is saved, and it also says
`--mode live` is the only thing that refreshes the cache. A call that must be
live every time cannot honor both, so it saves its answer over the same key
each run and `git status` shows one modified file afterwards. Expected, not a
surprise. Raised on [PR #59](https://github.com/RickSmith/survey-recon/pull/59)
together with the question of whether this command should exist at all; neither
is the agent's to settle.

----

Why this call is worth making
=============================

**It asks a different NGS endpoint than the screening run uses**, and that is
the whole value. The run queries the NGS datasheets *feature service* with a
corridor; this queries the NGS Data Explorer *API* with a point and a radius.
Different service, different query, different field spellings -- ``condition``
here, ``LAST_COND`` there; ``lastRecovered`` here, ``LAST_RECV`` there. See
``sources.py`` for the full account of the two.

So when the two agree on a mark, that is a cross-check rather than a recording
agreeing with itself.

Read live on 2026-09-13 against the committed SH16 capture: the API returned 13
marks within two miles of the corridor midpoint, 5 of them also in the capture's
11, and **all 5 conditions agreed** -- ``MARK NOT FOUND`` on every one.

----

What it does not mean
=====================

**A mark in one and not the other is ordinary.** The live call asks about a
circle around the midpoint; the run asks about a 300-foot ribbon along eight
and a half miles. They overlap and they are not the same question, so neither
"only live" nor "only captured" is ever reported as a disagreement.

**A disagreement is news, not a failure.** If NGS has changed a record since the
capture, that is the most interesting thing to happen all session: it is the
tool being right about how old its data is. It is printed loudly and it is not
an error.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .arcgis import USER_AGENT, from_compact_date
from .cache import Cache, long_path
from .sources import NGS_RADIAL

# How far around the corridor's midpoint to ask. Stated, never derived -- the
# same rule as every other distance in this tool. Two miles is enough to catch
# marks the corridor run found without being a different job: on SH16 it returns
# 13 marks, 5 of which the run also found.
DEFAULT_RADIUS_MI = 2.0

# The same three tries and the same growing wait `arcgis.Fetcher` uses, for the
# same reason: this repo watched a host fail and then succeed minutes later.
RETRIES = 3
TIMEOUT_S = 30


class Unreachable(Exception):
    """NGS could not be reached, or did not answer in a shape we can read."""

# What the tool is willing to say the cross-check proved.
NO_OVERLAP = (
    "no cross-check -- the live call and the capture have no mark in common, "
    "so there was nothing to compare"
)

NO_CONDITIONS = (
    "no cross-check -- NGS answered, but not one mark came back carrying a "
    "condition. That is far more likely to be the field having a different "
    "name than every mark losing its condition at once, so nothing is reported "
    "as changed. Check what this API calls `condition` now"
)


def to_mark(record):
    """One mark from the Data Explorer, in the shape this command compares.

    The API answers in camel case where the feature service answers in capitals
    with underscores. Two NGS endpoints, two spellings, one mark -- which is
    exactly why asking both is worth doing.
    """
    condition = record.get("condition")
    if isinstance(condition, str):
        condition = condition.strip() or None
    return {
        "pid": record.get("pid"),
        "condition": condition,
        "designation": record.get("name"),
        "last_recovered": from_compact_date(record.get("lastRecovered")),
        "latitude": record.get("lat"),
        "longitude": record.get("lon"),
    }


def _same(a, b):
    """Do two conditions say the same thing, ignoring case and padding."""
    return (a or "").strip().upper() == (b or "").strip().upper()


def compare(live_marks, captured_marks):
    """What the live call and the committed capture agree and disagree about.

    Only marks in **both** are compared. A mark in one and not the other is the
    two asking different questions, which they are, and is counted separately
    rather than folded into a disagreement.
    """
    live = {m["pid"]: m for m in live_marks if m.get("pid")}
    captured = {m["pid"]: m for m in captured_marks if m.get("pid")}
    both = sorted(set(live) & set(captured))
    # Every mark came back with no condition at all. That is not thirteen marks
    # losing their condition at once; it is the field having a different name
    # than this code asks for -- the exact `LAST_COND` trap ``sources.py``
    # records for the other NGS endpoint, pointed at a projector. Without this,
    # a rename would print "CHANGED SINCE THE CAPTURE -- 5 marks" and somebody
    # would read that false alarm out to a room.
    no_conditions = bool(live) and not any(m.get("condition") for m in live.values())
    disagree = [
        {
            "pid": pid,
            "captured": captured[pid].get("condition"),
            "live": live[pid].get("condition"),
        }
        for pid in both
        if not _same(captured[pid].get("condition"), live[pid].get("condition"))
    ]
    return {
        "live_marks": len(live),
        "captured_marks": len(captured),
        "in_both": len(both),
        "agree": len(both) - len(disagree),
        "disagree": disagree,
        "only_live": len(set(live) - set(captured)),
        "only_captured": len(set(captured) - set(live)),
        # Zero of zero agreeing is not a cross-check, and must never be read as
        # one. The two questions can legitimately share no mark at all.
        "cross_checked": bool(both) and not no_conditions,
        # The live call answered, and carried no condition on any mark.
        "no_conditions": no_conditions,
    }


def report(live_marks, captured_marks, captured_at, radius_mi=DEFAULT_RADIUS_MI):
    """What the room is told, while it is on the screen."""
    found = compare(live_marks, captured_marks)
    lines = [
        "  This call was live, just now.",
        "",
        f"    NGS Data Explorer returned {found['live_marks']} marks within "
        f"{radius_mi:g} miles of the corridor midpoint.",
        f"    The screening run beside it was captured {captured_at} and "
        f"found {found['captured_marks']} marks in the 300 ft corridor.",
        "",
        "    These are two different NGS endpoints asking two different",
        "    questions -- an API with a point and a radius, against a feature",
        "    service with a corridor. So a mark in one and not the other is",
        "    ordinary, and only the marks in both are compared.",
        "",
    ]
    if found["no_conditions"]:
        lines.append(f"    {NO_CONDITIONS}.")
        return "\n".join(lines)
    if not found["cross_checked"]:
        lines.append(f"    {NO_OVERLAP}.")
        return "\n".join(lines)

    lines.append(f"    marks in both        {found['in_both']}")
    lines.append(f"    conditions agreeing  {found['agree']}")
    lines.append(f"    only the live call   {found['only_live']}")
    lines.append(f"    only the capture     {found['only_captured']}")
    lines.append("")
    if found["disagree"]:
        lines.append(
            f"    CHANGED SINCE THE CAPTURE -- {len(found['disagree'])} mark(s). "
            "This is news, not an error:"
        )
        for changed in found["disagree"]:
            lines.append(
                f"      {changed['pid']}  captured {changed['captured']!r}  "
                f"now {changed['live']!r}"
            )
        lines.append("")
        lines.append(
            "    NGS has updated a record since this capture was taken. The "
            "capture is not wrong about what it saw; it is old, and it says so."
        )
    else:
        lines.append(
            f"    Every one of the {found['agree']} marks in both says the same "
            "thing live as it did in the capture."
        )
    return "\n".join(lines)


def unreachable(detail):
    """What to say when the call cannot be made. The demo carries on."""
    return (
        "  The live call could not be made.\n"
        "\n"
        f"    {detail}\n"
        "\n"
        "    The screening run is unaffected. It replays a committed capture\n"
        "    and makes no network calls, which is the whole reason it is\n"
        "    captured. This step is the proof that the wires are real, and\n"
        "    proving that needs wires."
    )


def fetch(cache, lat, lon, radius_mi=DEFAULT_RADIUS_MI, timeout=TIMEOUT_S, retries=RETRIES):
    """Ask NGS, now. Always live, never from the cache.

    **Three tries with a growing wait**, the same as ``arcgis.Fetcher``, and
    for the reason that fetcher's own ping docstring records: this repo watched
    a host fail and then succeed minutes later. One attempt is thin cover for
    the single call a session is standing on, and the whole point of this
    command is that it goes out.

    The answer is saved with its provenance, because specification section 14
    asks that every response this tool receives is written down -- but it is
    never read back. A cached live call would defeat the only thing this
    command is for. That does mean running it rewrites one cache entry; see the
    note in this file's docstring.
    """
    params = {"lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "radius": radius_mi, "units": "MILE"}
    url = f"{NGS_RADIAL.base_url}?{urllib.parse.urlencode(params)}"
    wait = 1.0
    last = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url)
            request.add_header("User-Agent", USER_AGENT)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                status = response.status
            records = json.loads(body)
            break
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            if attempt == retries:
                raise Unreachable(f"{last} (after {retries} attempts)") from exc
            time.sleep(wait)
            wait *= 2
    if not isinstance(records, list):
        # The API answers with a list. Anything else is an error body or a
        # changed contract, and reading it as marks would walk its keys.
        raise Unreachable(
            f"NGS answered with {type(records).__name__}, not the list of marks "
            f"this command expects: {str(records)[:200]}"
        )
    entry = cache.entry(NGS_RADIAL.name, "live-check-radial", NGS_RADIAL.base_url, params)
    cache.write(entry, body, status, record_count=len(records))
    # Section 14 calls INDEX.md "the file you point at" when you say the
    # captures are from a particular date. Writing a response without
    # regenerating it leaves that file quietly wrong about this one.
    cache.write_index()
    return [to_mark(r) for r in records], entry.cache_key


def _read_screening(out_dir):
    """The committed screening run: its marks, and when it was captured."""
    path = Path(out_dir) / "screening.json"
    with open(long_path(path), "r", encoding="utf-8") as handle:
        document = json.load(handle)
    marks = document.get("control", {}).get("ngs_marks")
    if not isinstance(marks, list):
        raise SystemExit(
            f"{path} has no list of NGS marks in it -- the run that wrote it "
            "never reached the control step, so there is nothing to check against."
        )
    captured_at = next(
        (s.get("captured_at") for s in document.get("services", []) if s.get("captured_at")),
        "an unrecorded date",
    )
    return marks, captured_at, document


def parse_args(argv=None):
    """The command line. ``argparse``, the same as the screening run uses.

    Hand-rolled parsing was the first version of this, and ``--out`` with no
    value after it put an ``IndexError`` traceback on the screen -- on the one
    command in this repo that runs live in front of a room. Caught by the
    review on issue #20.
    """
    parser = argparse.ArgumentParser(
        prog="corridor-screen live-check",
        description=(
            "Make the one call that is genuinely live, and compare what NGS says "
            "now against what the committed screening run captured."
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        help="The project directory holding screening.json and its cache",
    )
    parser.add_argument(
        "--radius-miles",
        type=float,
        default=DEFAULT_RADIUS_MI,
        help=(
            "How far around the corridor midpoint to ask, in miles. Stated, "
            f"never derived. Default {DEFAULT_RADIUS_MI:g}."
        ),
    )
    args = parser.parse_args(argv)
    if args.radius_miles <= 0:
        parser.error("--radius-miles must be greater than zero; nothing would be found otherwise")
    return args


def main(argv=None):
    """``python -m corridor_screen.live_check --out ../project-sh16``"""
    args = parse_args(argv)
    out_dir, radius = args.out, args.radius_miles

    marks, captured_at, document = _read_screening(out_dir)
    bbox = document["alignment"]["bbox"]
    lat, lon = (bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2

    print()
    print(f"  Live check -- NGS Data Explorer, {lat:.6f}, {lon:.6f}")
    print()
    try:
        live, cache_key = fetch(Cache(Path(out_dir) / "cache"), lat, lon, radius)
    except Unreachable as exc:
        print(unreachable(str(exc)))
        print()
        return 1
    print(report(live, marks, captured_at, radius))
    print()
    print(f"    saved as  {cache_key}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
