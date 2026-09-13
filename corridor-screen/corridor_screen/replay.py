"""Proving that a replayed run answers the same as the live one it replays.

The conference network is untrusted, TxDOT's ROW server blocks intermittently,
and this repo's own research recorded USGS elevation timing out three times out
of four. So the demo runs from cache. That is only safe if the cached run gives
the **same answers** as the live one -- and "same" is a claim somebody has to be
able to check, not one the tool gets to assert about itself.

This file is that check. Point it at two screening files and it says whether
they found the same things.

----

What "the same" has to mean, and why it is not "identical"
==========================================================

Two runs of the same corridor are never byte-identical. They start at different
times, they take different lengths of time, and one of them pinged hosts the
other deliberately did not. **None of those is a finding.** They are the run's
account of itself.

Compared on the SH16 corridor on 2026-09-13, a live run and a cache-only run
differed in exactly 60 places, and every one of them was in that account: four
fields on ``run``, and four on each of the fourteen services. Every parcel,
every flag, every lead time, every mark, every sheet and the whole crew safety
sheet were identical.

``RUN_ACCOUNT`` below is that list, named once, with a reason beside each entry.

**The whole ``run`` block is not excluded, and that is deliberate.** It would
have been the easy way to write this. It would also have hidden a replay that
screened a different corridor width, because ``half_width_ft`` lives there too.
Only the four fields that must differ are named.

``captured_at`` is **not** excluded either, though a careless reading would put
it there. It is not when this run happened -- it is when the answer was
obtained, which is how old the data is. That field is the thing that makes a
replayed run honest rather than a recording pretending to be live, so it is
compared like any other finding. A replay that claimed a fresh capture time
would be the one lie this whole design exists to prevent.

----

What it does not prove
======================

That the cache is *right*. Only that replaying it is faithful. If a service
answered wrongly on the day it was captured, this check will happily confirm
that both runs report the same wrong thing. The provenance record beside each
response, and the honesty block in the output, are what carry that question.
"""

import copy
import json
import sys
from pathlib import Path

from .cache import long_path

# Every place a faithful replay is allowed to differ from the run it replays,
# and why. Data rather than code, so the list can be argued with -- and so that
# adding to it is a visible decision rather than a quiet loosening.
RUN_ACCOUNT = {
    "run.run_id": "built from the time the run started, so it is different every run",
    "run.started_at": "when this run began, which is not a fact about the corridor",
    "run.finished_at": "when this run ended, likewise",
    "run.mode": "the difference this check exists to allow: live against cache-only",
    "services[].ping": (
        "a cache-only run makes no network calls at all, so it has nothing to "
        "report here and says `skipped` rather than inventing a result"
    ),
    "services[].ping_ms": "how long that ping took, when there was one",
    "services[].ping_detail": "what the ping said, when there was one",
    "services[].attempts": (
        "how many times the network had to be asked. A replay asks zero times, "
        "which is the point of it"
    ),
}


def _shape(path):
    """A path with its list indexes removed, so one entry covers every service."""
    out = []
    for part in path.split("."):
        if "[" in part:
            out.append(part[: part.index("[")] + "[]")
        else:
            out.append(part)
    return ".".join(out)


def _walk(live, replayed, path=""):
    """Every leaf where two documents disagree, with the path that reaches it.

    Missing keys and different list lengths are reported rather than skipped.
    A replay that dropped a block or returned a shorter list is exactly the
    failure this is looking for, and both of those read as "nothing to compare"
    to a comparison that only walks what the two have in common.
    """
    if type(live) is not type(replayed):
        yield path, live, replayed
        return
    if isinstance(live, dict):
        for key in sorted(set(live) | set(replayed)):
            here = f"{path}.{key}" if path else key
            if key not in live or key not in replayed:
                yield here, live.get(key, "(absent)"), replayed.get(key, "(absent)")
            else:
                yield from _walk(live[key], replayed[key], here)
    elif isinstance(live, list):
        if len(live) != len(replayed):
            yield path, f"{len(live)} items", f"{len(replayed)} items"
            return
        for index, (a, b) in enumerate(zip(live, replayed)):
            yield from _walk(a, b, f"{path}[{index}]")
    elif live != replayed:
        yield path, live, replayed


def _found(path, live, replayed):
    return {"path": path, "live": live, "replayed": replayed}


def differences(live, replayed):
    """Every place the two runs found something different.

    The run's own account of itself is left out -- see ``RUN_ACCOUNT``. What
    comes back is the list that matters: if it is empty, the replay is faithful.
    """
    return [
        _found(path, a, b)
        for path, a, b in _walk(live, replayed)
        if _shape(path) not in RUN_ACCOUNT
    ]


def run_account_differences(live, replayed):
    """The differences this check allowed, so a reader can disagree with it.

    Reported rather than dropped. A check that hides its own slack teaches a
    reader to trust it further than it has earned, and the slack here is the
    whole design decision.
    """
    return [
        _found(path, a, b)
        for path, a, b in _walk(live, replayed)
        if _shape(path) in RUN_ACCOUNT
    ]


def same_findings(live, replayed):
    """Did the replay find the same things. One question, one answer."""
    return not differences(live, replayed)


def findings_of(document):
    """The document with the run's account of itself taken out.

    Not used by the comparison, which walks both documents at once. It is here
    because "what did this run find, as opposed to how did it go" is a useful
    thing to be able to hold, and naming it is half of what this file is for.
    """
    stripped = copy.deepcopy(document)
    for key in ("run_id", "started_at", "finished_at", "mode"):
        stripped.get("run", {}).pop(key, None)
    for service in stripped.get("services", []) or []:
        for key in ("ping", "ping_ms", "ping_detail", "attempts"):
            service.pop(key, None)
    return stripped


def report(live, replayed):
    """What the comparison says, for a person to read.

    Always says how much slack it allowed, even on a clean match, because a
    reader who cannot see the slack cannot judge the result.
    """
    found = differences(live, replayed)
    allowed = run_account_differences(live, replayed)
    lines = []
    if found:
        lines.append(f"The two runs found DIFFERENT things -- {len(found)} of them.")
        lines.append("")
        for difference in found:
            lines.append(f"  {difference['path']}")
            lines.append(f"      live      {difference['live']!r}")
            lines.append(f"      replayed  {difference['replayed']!r}")
    else:
        lines.append("The two runs found the same things. Every finding is a match.")
    lines.append("")
    lines.append(
        f"  {len(allowed)} differences were allowed, all of them the run's own "
        "account of itself:"
    )
    for shape in sorted({_shape(d["path"]) for d in allowed}):
        lines.append(f"      {shape:<26} {RUN_ACCOUNT[shape]}")
    return "\n".join(lines)


def _read(path):
    with open(long_path(Path(path)), "r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None):
    """``python -m corridor_screen.replay <live.json> <replayed.json>``"""
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2:
        print(
            "Compare two screening files and say whether they found the same things.\n"
            "\n"
            "  python -m corridor_screen.replay <live.json> <replayed.json>\n"
            "\n"
            "Exit code 0 when every finding matches, 1 when any does not.",
            file=sys.stderr,
        )
        return 2
    live, replayed = _read(argv[0]), _read(argv[1])
    print(report(live, replayed))
    return 0 if same_findings(live, replayed) else 1


if __name__ == "__main__":
    sys.exit(main())
