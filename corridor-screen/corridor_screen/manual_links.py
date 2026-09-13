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

**The old host is not called dead.** Checked on 2026-09-13, the name is still
published in DNS and nothing accepted a connection on port 80 or 443. "Listed
but not answering" and "does not exist" are different findings, and this repo
writes "not found" rather than "does not exist" for exactly this reason. The
address it resolved to that day is in the capture README, with its date, which
is where a fact with a shelf life belongs.

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

from . import beats
from .cache import long_path

CAPTURE_DIR = beats.capture_dir("superseded-manual")

# When every claim below was checked against the live web. Section numbers and
# revision dates move; a claim with no date is a claim about nothing.
CHECKED_ON = "2026-09-13"

# The rendered beat is committed as `beats.BEAT_NAME` beside the captures.
# Issue #27 asks for "a capture that can stand in if the live thing breaks on
# the day" -- the page captures are this beat's *inputs*, and the rendered beat
# is its *output*. If Python will not start on the podium, a presenter opens a
# text file instead. `tests/test_beats.py` pins it to what `beat()` produces,
# the way the committed `screening.json` is pinned by the replay check.

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
# That is not a shortcut, it is the distinction itself. Several pages here name
# `onlinemanuals.txdot.gov` in order to warn about it -- including the rule in
# CLAUDE.md forbidding it -- and one writes the family out as
# `onlinemanuals.txdot.gov/txdotmanuals/ess/...`. None is clickable and none
# supports a claim. A guard that flagged the rule forbidding the trap is a guard
# somebody deletes on a deadline.
#
# **The count is deliberately not written here.** An earlier draft of this
# comment said "five", which was wrong the moment this module and its docs page
# were added, and a number nobody re-counts is the exact failure this file
# exists to catch. `--check` prints what it actually found.
#
# The cost is honest and small: a markdown link written without a scheme is
# missed. Such a link is already broken -- it resolves against this site -- so
# it fails as a link before it fails as a citation.
#
# No trailing slash is required. `https://onlinemanuals.txdot.gov` is clickable
# and supports a claim just as well as a deep link, and the first version of
# this pattern let it straight through.
#
# **Case-insensitive, and an optional `www.`.** Host names are case-insensitive
# by definition, so `HTTP://OnlineManuals.txdot.gov/...` is the same address and
# the same mistake. The first version matched none of those three shapes.
LEGACY_PATTERN = re.compile(r"https?://(?:www\.)?onlinemanuals\.txdot\.gov\S*",
                            re.IGNORECASE)

# A file whose job is to hold these URLs says so, in words, where a reader and
# this check can both see it. The captures are the same thing in HTML: evidence
# of what was served, not a claim that it is current.
#
# **The declaration has to be at the top.** Anywhere in the file, and an HTML
# comment on the last line -- invisible in rendered MkDocs -- silences a real
# citation a hundred lines above it. A reader who opens the file meets the
# declaration before the URLs or the exemption is not honest.
EVIDENCE_MARKER = "superseded-url-evidence"
DECLARATION_LINES = 40

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
#
# **The IP address is deliberately not here.** An address has a shelf life, so
# the one seen on the day is in the capture README beside its date, which is
# where a fact that rots belongs. This module holds the
# part that does not: the name is still published, and nothing answers on it.
# Two paragraphs up this file says revisions are read from the captures rather
# than typed; a typed IP would have been the one claim held to a lower standard
# than the rest.
HOST_TODAY = (
    "the name is still published, and nothing accepted a connection on port 80 "
    "or 443 (three attempts, 12 s each)"
)

# Files worth checking, and the one directory that is exempt. The captures are
# **evidence**: they contain the legacy URLs because that is what was served,
# and flagging them would be flagging the photograph for showing the crime.
#
# `.json` is on the list because a generated output can carry a URL too --
# `screening.json` already carries `txdot.gov` ones -- and a superseded address
# reaching a file somebody sends out is worse than one in a page.
CHECK_SUFFIXES = (".md", ".py", ".toml", ".yml", ".yaml", ".json", ".html")

# `.claude` holds this repo's own git worktrees, each a full copy of everything.
# Without it, a check run from the main checkout walks every branch in progress,
# reports other people's files, and breaks the test that pins the exempt list.
SKIP_PARTS = ("captures", ".git", ".claude", "__pycache__", "site", "node_modules")


def capture_text(name):
    """One committed capture, as text. Never a network call.

    **Decoded as the page says it is encoded, not as UTF-8.** The legacy manual
    declares ``charset=ISO-8859-1`` in its own head, which is period detail --
    it is a page from an older web, and reading it as UTF-8 quietly corrupts
    every byte above 127. That is the same shape of error as reading a survey
    file in the wrong coordinate system: it does not fail, it just comes out
    wrong somewhere you were not looking.

    **Opened through ``cache.long_path``**, like every other read in this
    module. Issue #76: this one was missed, and the beat it renders would not
    open its own evidence on a checkout whose paths run past the 260 characters
    Windows takes without being asked in the extended form. A firm's checkout
    under "OneDrive - Some Long Firm Name" gets there easily, and this repo's
    own worktrees already do. The presenter would be typing ``--show`` at a
    podium with no network -- the one moment the fallback exists for -- and
    getting a not-found error naming a file they can see in their editor.
    """
    for capture in CAPTURES:
        if capture["name"] == name:
            with open(long_path(CAPTURE_DIR / capture["file"]), "rb") as handle:
                raw = handle.read()
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
    would be a check somebody deletes. So a hostname in a sentence is left
    alone, and a URL counts as a citation when it is **clickable** -- when it
    carries ``http://`` or ``https://`` in front of it.
    """
    found, seen = [], set()
    for match in LEGACY_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:)]}>\"'`")
        if url in seen:
            continue
        seen.add(url)
        found.append({"url": url, "replacement": CURRENT_INDEX})
    return sorted(found, key=lambda f: f["url"])


def _pages(root):
    """Every file worth checking, walked once, through the door that opens them.

    **``Path.read_text`` is not that door on Windows.** A surveyor's checkout
    sits under something like "OneDrive - Some Long Firm Name\\Documents\\...",
    and this repo's own worktree already pushes files past the 260 characters
    Windows will open without being asked in the extended form.

    The first version of this guard used ``read_text`` behind a bare
    ``except OSError: continue`` and silently skipped **21 files here** -- a
    fifth of everything it was asked to check -- while printing a clean result.
    A guard that quietly does not read a file is worse than no guard, because
    it is trusted.

    So the read goes through ``cache.long_path``, which is the same door
    ``test_offline._copy_tree`` needed for ``shutil``, and anything still
    unreadable is yielded as the exception so a caller can say so out loud.
    """
    for path in sorted(Path(root).rglob("*")):
        if path.suffix.lower() not in CHECK_SUFFIXES:
            continue
        inside = Path(path).relative_to(root)
        # **Relative parts, not absolute ones.** Skipping on the full path
        # means the root's own folders count: this very repo is checked out
        # under a `.claude/worktrees/...` directory, so an absolute test for
        # `.claude` skipped every file in it and reported a clean, empty run.
        if any(part in SKIP_PARTS for part in inside.parts):
            continue
        name = inside.as_posix()
        try:
            with open(long_path(path), encoding="utf-8", errors="replace") as handle:
                yield name, handle.read()
        except OSError as exc:
            yield name, exc


def declares_evidence(body):
    """Whether a file declares, up front, that it holds these URLs as evidence.

    Only the opening lines count. See ``DECLARATION_LINES``: an exemption a
    reader does not meet before the URLs is not a declaration, it is a hiding
    place.
    """
    return EVIDENCE_MARKER in "\n".join(body.splitlines()[:DECLARATION_LINES])


def unreadable(root):
    """Files the guard could not open at all.

    Must be empty for a clean result to mean anything: "nothing found" across a
    file nobody read is not a finding.
    """
    return [name for name, body in _pages(root) if isinstance(body, Exception)]


def exempt(root):
    """Files that hold these URLs as evidence, and say so.

    Returned rather than silently skipped, so ``main`` can name them. A guard
    with an invisible exemption list is a guard that quietly stops guarding, and
    a reader can see each declaration in the diff that added it.
    """
    return [name for name, body in _pages(root)
            if not isinstance(body, Exception) and declares_evidence(body)]


def check_repo(root):
    """Every superseded citation in the repo, as (path, url, replacement)."""
    offenders = []
    for name, body in _pages(root):
        if isinstance(body, Exception) or declares_evidence(body):
            continue
        for finding in superseded(body):
            offenders.append({
                "path": name,
                "url": finding["url"],
                "replacement": finding["replacement"],
            })
    return offenders


def report(offenders, unreadable=()):
    """What to print when the guard runs.

    Anything unreadable is named. "No superseded URLs found" across a file
    nobody managed to open is not a finding, and printing it as one is how a
    guard starts lying quietly.
    """
    if offenders:
        lines = [f"  {len(offenders)} superseded TxDOT manual "
                 f"{'URL' if len(offenders) == 1 else 'URLs'} cited:"]
        for bad in offenders:
            lines += [f"    {bad['path']}", f"      cites   {bad['url']}",
                      f"      use     {bad['replacement']}"]
    else:
        lines = ["  no superseded TxDOT manual URLs found"]
    for name in unreadable:
        lines.append(f"  could not read, so it was not checked: {name}")
    return "\n".join(lines)


def beat():
    """The failure beat, built entirely from committed captures."""
    legacy = revision_in(capture_text("legacy"))
    current = revision_in(capture_text("current"))
    old_url = CAPTURES[0]["url"]

    # **Plain ASCII, and `beats.render` refuses anything else.** An em dash here
    # is a `UnicodeEncodeError` and a traceback on a Windows console that has
    # not been told otherwise -- which is every borrowed podium laptop.
    # Verified: the first version of this function died under
    # `PYTHONIOENCODING=cp437`, at 1:36, instead of printing the beat. It was
    # caught by review rather than by anything running, which is what issue #67
    # moved into the seam below.
    return beats.render([
        "  Failure beat 1 - the superseded manual",
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
    """``python -m corridor_screen.manual_links --show``"""
    parser = argparse.ArgumentParser(
        prog="corridor-screen manual-links",
        description="Failure beat one, and the guard that keeps this repo out of it.",
    )
    group = beats.beat_arguments(parser)
    # This beat's own option, in the same mutually exclusive group -- which is
    # why `beat_arguments` hands the group back rather than keeping it.
    group.add_argument("--check", metavar="ROOT", nargs="?", const=".",
                       help="fail if any page or module cites a superseded URL")
    args = parser.parse_args(argv)

    if args.write_fallback:
        print(f"  written  {beats.write_fallback(CAPTURE_DIR, beat())}")
        return 0

    if args.check:
        root = Path(args.check).resolve()
        offenders, cannot = check_repo(root), unreadable(root)
        print(report(offenders, cannot))
        for name in exempt(root):
            print(f"  (holding these URLs as evidence, by declaration: {name})")
        # A file nobody could open fails this too. The alternative is a green
        # check over unread files, which is the failure this whole module is
        # about.
        return 1 if (offenders or cannot) else 0

    print(beat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
