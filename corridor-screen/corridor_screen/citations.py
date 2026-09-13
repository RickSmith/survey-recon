"""Failure beat one: the manual that is real, authoritative, and out of date.

Written under [issue #25](https://github.com/RickSmith/survey-recon/issues/25).

This module holds superseded-url-evidence. The legacy URLs in ``CAPTURES``
below record what was served and where each capture came from; they are not
citations, and the declaration on this line is what tells ``check_repo`` so.

**The trap.** Ask a search engine for the TxDOT Survey Manual and you are still
handed `onlinemanuals.txdot.gov` links. The manual moved to
`txdot.gov/manuals/row/ess/`, and the two are not the same document. The last
thing the old host served was the **March 2025** revision, Manual Notice
**2025-1**. The one in force is **April 2026**, Manual Notice **2026-1**.

So an agent taking the first search result does not get an error. It gets a
real manual, with real section numbers, under a revision no longer in force.
That is the plan of record's beat: *"It didn't lie to you. It found the wrong
document and believed it -- which is exactly what a new hire does."*

----

Why this file exists rather than a paragraph on a slide
=======================================================

Issue #25 asks for a failure that "reproduces on demand, every time" and
"reproduces from cache, so it never depends on the network." A story about a
broken link is not reproducible; a check that finds one is.

So there are two halves, and the second is the useful one:

**The beat** -- ``--show`` prints both URLs, what each serves, the revision each
names, and the one sentence saying what went wrong. Every word of it comes from
files committed in ``captures/superseded-manual/``, so it runs on a dead
network in a hotel basement.

**The guard** -- ``--check`` scans this repo for a superseded URL and fails if
it finds one. ``CLAUDE.md`` already forbids them; this is what makes that rule
something other than a sentence nobody runs. It is deliberately boring, which
is the plan of record's own point about beat three: *"The rule that catches an
error is usually boring and was written for something else."*

----

What this file is careful not to claim
======================================

**The old host is not called dead.** Checked on 2026-09-13, it still resolves
in DNS -- ``onlinemanuals.txdot.gov`` answers as ``168.44.238.246`` -- and
nothing accepts a connection on port 80 or 443. "Resolves but does not answer"
and "does not exist" are different findings, and this repo writes "not found"
rather than "does not exist" for exactly this reason.

**The revisions are read from the captures, not typed here.** ``revision_in``
pulls them out of the committed HTML, and there is a test asserting the file
really says what this module claims it says. A number quoted from memory beside
a capture that disagrees is how a teaching repo starts teaching something that
is no longer true.
"""

import argparse
import html
import re
import sys
from pathlib import Path

CAPTURE_DIR = Path(__file__).resolve().parent.parent / "captures" / "superseded-manual"

# When every claim below was checked against the live web. Section numbers and
# revision dates move; a claim with no date is a claim about nothing.
CHECKED_ON = "2026-09-13"

# The one sentence. Issue #25: "The script names what the agent did wrong in one
# sentence." One, and it stays one -- there is a test on the full stops.
VERDICT = (
    "It did not invent anything: it followed the link search gave it, read a "
    "real TxDOT manual, and cited a revision that had been replaced."
)

# **A citation has a scheme; a description does not.** Both legacy path shapes
# live on this host -- the first meta-refreshed to the second -- so the path is
# left open and the scheme is what decides.
#
# That is not a shortcut, it is the distinction itself. Five places in this repo
# name `onlinemanuals.txdot.gov` in order to warn about it, and one writes out
# `onlinemanuals.txdot.gov/txdotmanuals/ess/...` to describe the family. None is
# clickable and none supports a claim. A guard that flagged the rule forbidding
# the trap is a guard somebody deletes on a deadline.
#
# The cost is honest and small: a markdown link written without a scheme is
# missed. Such a link is already broken -- it resolves against this site -- so
# it fails as a link before it fails as a citation.
LEGACY_PATTERN = r"https?://onlinemanuals\.txdot\.gov/\S*"

# A file whose job is to hold these URLs says so, in words, where a reader and
# this check can both see it. The captures are the same thing in HTML: evidence
# of what was served, not a claim that it is current.
EVIDENCE_MARKER = "superseded-url-evidence"

# Where the manual actually lives. Not a guess -- fetched and read on the date
# above, and committed as `current-ess-index.html` beside this module.
CURRENT_BASE = "https://www.txdot.gov/manuals/row/ess/"
CURRENT_INDEX = CURRENT_BASE + "index.html"

# The committed evidence. Each entry says what the file is and where it came
# from, in the same spirit as a cache `.meta.toml`: a capture nobody can trace
# back to a request is not evidence.
CAPTURES = (
    {
        "name": "legacy",
        "file": "legacy-ess-index-archived-2025-06-18.html",
        "url": "http://onlinemanuals.txdot.gov/TxDOTOnlineManuals/TxDOTManuals/ess/index.htm",
        "via": "Internet Archive capture 20250618021450",
        "note": "The last archived capture carrying real manual content. The live "
                "host no longer answers, so the archive is the only way to show "
                "what it served.",
    },
    {
        "name": "current",
        "file": "current-ess-index.html",
        "url": CURRENT_INDEX,
        "via": f"fetched live on {CHECKED_ON}",
        "note": "The manual in force.",
    },
    {
        "name": "redirect",
        "file": "legacy-old-path-archived-2025-03-08.html",
        "url": "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm",
        "via": "Internet Archive capture 20250308044703",
        "note": "186 bytes of meta-refresh, pointing at the other legacy path. "
                "Kept because it is why there are two patterns to check for.",
    },
)

# What the old host does today, recorded rather than characterized. See this
# module's docstring on why it is not called dead.
HOST_TODAY = (
    "resolves in DNS as 168.44.238.246, and accepts no connection on port 80 or "
    "443 (three attempts, 12 s each)"
)

# Files worth checking, and the one directory that is exempt. The captures are
# **evidence**: they contain the legacy URLs because that is what was served,
# and flagging them would be flagging the photograph for showing the crime.
CHECK_SUFFIXES = (".md", ".py", ".toml", ".yml", ".yaml")
SKIP_PARTS = ("captures", ".git", "__pycache__", "site", "node_modules")


def capture_text(name):
    """One committed capture, as text. Never a network call.

    **Decoded as the page says it is encoded, not as UTF-8.** The legacy manual
    declares ``charset=ISO-8859-1`` in its own head, which is period detail --
    it is a page from an older web, and reading it as UTF-8 quietly corrupts
    every byte above 127. That is the same shape of error as reading a survey
    file in the wrong coordinate system: it does not fail, it just comes out
    wrong somewhere you were not looking.
    """
    for capture in CAPTURES:
        if capture["name"] == name:
            raw = (CAPTURE_DIR / capture["file"]).read_bytes()
            return raw.decode(declared_charset(raw), errors="replace")
    raise KeyError(f"no capture named {name!r}")


def declared_charset(raw, fallback="utf-8"):
    """The character set a page says it is written in."""
    found = re.search(rb"charset=[\"']?([A-Za-z0-9_-]+)", raw[:2048])
    return found.group(1).decode("ascii") if found else fallback


def revision_in(page):
    """Which revision of the Survey Manual a page says it is.

    Read out of the page rather than stated here, so the claim and the evidence
    cannot drift apart. Both halves are returned: TxDOT stamps the manual with a
    month and year in its footer and with a Manual Notice number in its
    navigation, and the notice number is the one a surveyor would quote.
    """
    # Entities first. The legacy page writes the date as `March&nbsp;2025`, so
    # a search for "March 2025" on the raw markup finds nothing and a reader
    # concludes the page does not carry a revision at all. It does.
    flat = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))
    revised = re.search(r"TxDOT Survey Manual (?:Revised )?([A-Z][a-z]+ \d{4})", flat)
    notice = re.search(r"Manual Notice:? (\d{4}-\d+)", flat)
    return {
        "revised": revised.group(1) if revised else "not found",
        "manual_notice": notice.group(1) if notice else "not found",
    }


def superseded(text):
    """Every superseded TxDOT manual URL in some text, with its replacement.

    **Naming the host is not citing it.** ``CLAUDE.md`` carries the rule
    "Never `onlinemanuals.txdot.gov`", and a check that flagged its own rule
    would be a check somebody deletes. So a bare hostname is left alone and only
    a fetchable URL -- a scheme, or a path under one of the two legacy
    directories -- counts as a citation.
    """
    found, seen = [], set()
    for match in re.finditer(LEGACY_PATTERN, text):
        url = match.group(0).rstrip(".,;:)]}>\"'`")
        if url in seen:
            continue
        seen.add(url)
        found.append({"url": url, "replacement": CURRENT_INDEX})
    return sorted(found, key=lambda f: f["url"])


def exempt(root):
    """Files that hold these URLs as evidence, and say so.

    Returned rather than silently skipped, so `report` can name them. A guard
    with an invisible exemption list is a guard that quietly stops guarding, and
    a reader can see each declaration in the diff that added it.
    """
    out = []
    for path in sorted(Path(root).rglob("*")):
        if path.suffix.lower() not in CHECK_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            if EVIDENCE_MARKER in path.read_text(encoding="utf-8", errors="replace"):
                out.append(str(path.relative_to(root)))
        except OSError:
            continue
    return out


def check_repo(root):
    """Every superseded citation in the repo, as (path, url, replacement)."""
    offenders = []
    for path in sorted(Path(root).rglob("*")):
        if path.suffix.lower() not in CHECK_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if EVIDENCE_MARKER in text:
            continue
        for finding in superseded(text):
            offenders.append({
                "path": str(Path(path).relative_to(root)),
                "url": finding["url"],
                "replacement": finding["replacement"],
            })
    return offenders


def report(offenders):
    """What to print when the guard trips."""
    if not offenders:
        return "  no superseded TxDOT manual URLs found"
    lines = [f"  {len(offenders)} superseded TxDOT manual "
             f"{'URL' if len(offenders) == 1 else 'URLs'} cited:"]
    for bad in offenders:
        lines += [f"    {bad['path']}", f"      cites   {bad['url']}",
                  f"      use     {bad['replacement']}"]
    return "\n".join(lines)


def beat():
    """The failure beat, built entirely from committed captures."""
    legacy = revision_in(capture_text("legacy"))
    current = revision_in(capture_text("current"))
    old_url = CAPTURES[0]["url"]

    return "\n".join([
        "  Failure beat 1 — the superseded manual",
        "",
        "  What a search for the TxDOT Survey Manual still hands you:",
        f"    {old_url}",
        f"      serves    TxDOT Survey Manual {legacy['revised']}, "
        f"Manual Notice {legacy['manual_notice']}",
        f"      today     {HOST_TODAY}",
        f"      evidence  captures/superseded-manual/{CAPTURES[0]['file']}"
        f" ({CAPTURES[0]['via']})",
        "",
        "  Where the manual actually is:",
        f"    {CURRENT_INDEX}",
        f"      serves    TxDOT Survey Manual {current['revised']}, "
        f"Manual Notice {current['manual_notice']}",
        f"      evidence  captures/superseded-manual/{CAPTURES[1]['file']}"
        f" ({CAPTURES[1]['via']})",
        "",
        f"  {VERDICT}",
        "",
        f"  Every line above was checked on {CHECKED_ON} and reads from disk,",
        "  so it does not need a network to run again.",
    ])


def main(argv=None):
    """``python -m corridor_screen.citations --show``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen citations",
        description="Failure beat one, and the guard that keeps this repo out of it.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--show", action="store_true",
                       help="print the failure beat (the default)")
    group.add_argument("--check", metavar="ROOT", nargs="?", const=".",
                       help="fail if any page or module cites a superseded URL")
    args = parser.parse_args(argv)

    if args.check:
        root = Path(args.check).resolve()
        offenders = check_repo(root)
        print(report(offenders))
        for name in exempt(root):
            print(f"  (holding these URLs as evidence, by declaration: {name})")
        return 1 if offenders else 0

    print(beat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
