"""The fallback card, held against the run of show it claims to cover.

Issue #27 asks a question rather than asking for a build: **is there something
to fall back on at every point in the two hours, and does it work?** The answer
is written down for a presenter in `docs/presenting/fallbacks.md` -- one page,
in clock order, because the moment it gets read is the moment something has
already gone wrong in front of three hundred people.

A page like that is worth exactly what its last edit is worth. So this file
checks it rather than trusting it:

* every row of the run of show in `docs/plan-of-record.md` §5 has a row on the
  card, and the card invents no step the plan does not have
* every file the card names is committed, and is not empty
* every command the card names **runs with the network taken away**, not
  politely asked to stay home -- removed, at the socket
* every gap says it is a gap and names the work order that would close it

The last one is the point of an audit. A card that quietly omits the four
blocks with nothing recorded yet would pass the first three checks and lie to
the presenter, which is worse than having no card at all.

**Why the card, and not a Python table.** The presenter reads a page. A list
held anywhere else would be a second copy of the same facts, and the first
correction would go into only one of them.
"""

import contextlib
import importlib
import io
import re
import shlex
import unittest
from contextlib import contextmanager
from pathlib import Path

from corridor_screen import cli
from corridor_screen.cache import long_path

# Borrowed rather than copied. `no_network` takes the network away below every
# library that could reach for it, and `a_copy_of_the_demo_cache` puts a run
# somewhere that is not the committed demo artifact. Two copies of either would
# drift the first time somebody fixed one of them.
from tests.test_offline import a_copy_of_the_demo_cache, no_network

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
PLAN = REPO / "docs" / "plan-of-record.md"

# `0:57–1:18`, with the en dash the plan of record actually uses.
A_TIME = re.compile(r"^\d:\d\d\u2013\d:\d\d$")

# The three things a "reach for" cell is allowed to start with. Anything else
# is a sentence somebody wrote in a hurry, and a presenter cannot act on it.
READY, GAP, NOTHING_LIVE = "`", "not recorded", "nothing live"


def text_of(path):
    """Read a committed file, through the door that survives a long path.

    A surveyor's checkout sits under something like "OneDrive - Some Long Firm
    Name\\Documents\\Projects", and this repo's own worktrees already push a
    capture past the 260 characters Windows opens without being asked in the
    extended form. `cache.long_path` is how every other read here gets in.
    """
    with open(long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def table_rows(markdown):
    """Every table row in a markdown file, as a list of stripped cells.

    Header and divider rows come back too. The callers filter on the first
    cell rather than on position, so a table growing a column above it does not
    quietly change which row is which.
    """
    rows = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def run_of_show():
    """The blocks of the session, in order, read from the plan of record.

    Read rather than restated. The plan of record is the spec, and a fallback
    list that had its own private copy of the run of show would go on passing
    its own tests after the run of show changed.
    """
    section = markdown_section(text_of(PLAN), "## 5. Run of show")
    return [row[0] for row in table_rows(section) if A_TIME.match(row[0])]


def markdown_section(markdown, heading):
    """Everything under one heading, up to the next heading of any depth.

    Matched on how the heading starts rather than the whole of it. The plan of
    record writes its running time into this one -- "## 5. Run of show (2:00)" --
    and a heading that gains or loses a parenthesis should not fail a check
    about fallbacks.
    """
    lines = markdown.splitlines()
    for start, line in enumerate(lines):
        if line.strip().startswith(heading):
            break
    else:
        raise AssertionError(f"{heading!r} is not in that file")
    for end in range(start + 1, len(lines)):
        if lines[end].startswith("#"):
            return "\n".join(lines[start + 1:end])
    return "\n".join(lines[start + 1:])


def card_rows():
    """The fallback card, as (time, block, reach for, covers) tuples."""
    rows = [row for row in table_rows(text_of(CARD)) if A_TIME.match(row[0])]
    if not rows:
        raise AssertionError(f"no run-of-show rows found in {CARD}")
    return rows


def named_in(cell):
    """The backticked files and commands in one "reach for" cell."""
    return re.findall(r"`([^`]+)`", cell)


def is_a_command(named):
    return named.startswith("python ")


@contextmanager
def silenced():
    """Run a command without printing the whole screening report into the test.

    Both doors have to be shut. The screening run says everything through
    `cli._say`; the two failure beats use plain `print`.
    """
    said = io.StringIO()
    original = cli._say

    def capture(message=""):
        said.write(str(message) + "\n")

    cli._say = capture
    try:
        with contextlib.redirect_stdout(said):
            yield said
    finally:
        cli._say = original


@contextmanager
def somewhere_to_write(argv):
    """Point a command that writes at a copy of the demo, not at the demo.

    The card gives the presenter the real line, `--out ../project-sh16`, which
    is where the committed bid memo and crew-day build-up live. Running that
    line here would rewrite the artifacts the session depends on, so the run
    goes to a temporary copy instead. The rest of the command is untouched:
    what is being checked is the command a presenter would actually type.
    """
    if "--out" not in argv:
        yield argv
        return
    with a_copy_of_the_demo_cache() as out:
        swapped = list(argv)
        swapped[swapped.index("--out") + 1] = str(out)
        yield swapped


def run_offline(command):
    """Run one command off the card with every network door refused."""
    parts = shlex.split(command)
    if parts[:2] != ["python", "-m"]:
        raise AssertionError(
            f"the card should give a presenter a `python -m ...` line, not {command!r}"
        )
    target, argv = parts[2], parts[3:]
    # `python -m corridor_screen` runs `__main__`, and importing that module
    # would run it a second time. Its one job is to call `cli.main`, so call it.
    entry = cli.main if target == "corridor_screen" else importlib.import_module(target).main
    with somewhere_to_write(argv) as prepared, no_network(), silenced() as said:
        code = entry(prepared)
    return code, said.getvalue()


class TestTheCardCoversTheWholeSession(unittest.TestCase):
    """Eleven blocks in the run of show, eleven rows on the card."""

    def test_every_block_in_the_run_of_show_has_a_row(self):
        missing = [time for time in run_of_show() if time not in {row[0] for row in card_rows()}]
        self.assertEqual(
            missing, [],
            "these blocks of the session have no line on the fallback card",
        )

    def test_the_card_invents_no_block_the_plan_of_record_does_not_have(self):
        """A row for a step that was cut is a presenter reading the wrong page."""
        extra = [row[0] for row in card_rows() if row[0] not in set(run_of_show())]
        self.assertEqual(extra, [], "these are on the card and not in the run of show")

    def test_the_rows_are_in_clock_order(self):
        """The ten-second rule. A presenter knows the time, so time is the index.

        A block may take more than one line -- the failure beat is three
        separate things and a presenter needs to reach for one of them, not for
        a paragraph. So times may repeat, as long as they never go backwards
        and the blocks arrive in the order the session runs them.
        """
        times = [row[0] for row in card_rows()]
        self.assertEqual(times, sorted(times, key=run_of_show().index))
        self.assertEqual(list(dict.fromkeys(times)), run_of_show())

    def test_every_row_says_plainly_which_of_the_three_things_it_is(self):
        """Ready, not recorded, or nothing to lose. No fourth kind of sentence."""
        for time, block, reach_for, _covers in card_rows():
            with self.subTest(block=block):
                self.assertTrue(
                    reach_for.startswith((READY, GAP, NOTHING_LIVE)),
                    f"{time} reads {reach_for!r}, which is none of "
                    f"{READY!r}, {GAP!r} or {NOTHING_LIVE!r}",
                )


class TestEveryFileTheCardNamesIsCommitted(unittest.TestCase):
    """The card is a set of directions. Directions to a missing file are worse
    than no directions, because they are followed."""

    def test_every_file_named_is_on_disk_and_not_empty(self):
        for time, _block, reach_for, _covers in card_rows():
            for named in named_in(reach_for):
                if is_a_command(named):
                    continue
                with self.subTest(time=time, file=named):
                    path = REPO / named
                    self.assertTrue(
                        Path(long_path(path)).is_file(),
                        f"{named} is on the card and not in the repo",
                    )
                    self.assertGreater(
                        Path(long_path(path)).stat().st_size, 0,
                        f"{named} is on the card and is empty",
                    )

    def test_a_ready_row_actually_names_something(self):
        """`ready` and an empty cell is the failure this whole file is about."""
        for time, block, reach_for, _covers in card_rows():
            if not reach_for.startswith(READY):
                continue
            with self.subTest(block=block):
                self.assertTrue(named_in(reach_for), f"{time} claims a fallback and names none")


class TestEveryFallbackPlaysWithNoNetwork(unittest.TestCase):
    """The acceptance criterion, taken literally.

    `--mode cache-only` is the tool *choosing* not to call out, and a venue
    does not offer that choice. So the network is removed at the socket, which
    is below every library that could reach for it, and then the exact line
    off the card is run.
    """

    def test_each_command_on_the_card_runs_with_every_network_door_refused(self):
        commands = [
            (row[0], named)
            for row in card_rows()
            for named in named_in(row[2])
            if is_a_command(named)
        ]
        self.assertTrue(commands, "the card gives a presenter no command at all")
        for time, command in commands:
            with self.subTest(time=time, command=command):
                code, said = run_offline(command)
                self.assertEqual(code, 0, f"{command}\n{said}")

    def test_each_command_prints_something_a_room_can_read(self):
        """A silent success on a projector looks exactly like a hang."""
        for row in card_rows():
            for named in named_in(row[2]):
                if not is_a_command(named):
                    continue
                with self.subTest(command=named):
                    _code, said = run_offline(named)
                    self.assertGreater(len(said.strip()), 0, f"{named} printed nothing")


class TestAGapSaysSoAndNamesTheWorkThatWouldCloseIt(unittest.TestCase):
    """Four blocks of this session have nothing recorded yet, because the thing
    they would record does not exist yet. That is a finding, and the card's job
    is to say it out loud rather than leave a presenter to discover it."""

    def test_every_gap_names_a_work_order(self):
        for time, block, reach_for, _covers in card_rows():
            if not reach_for.startswith(GAP):
                continue
            with self.subTest(block=block):
                self.assertRegex(
                    reach_for, r"#\d+",
                    f"{time} has no fallback and does not say which work order would give it one",
                )

    def test_a_gap_never_also_names_a_file(self):
        """Half a fallback reads as a whole one at four minutes past the hour."""
        for time, block, reach_for, _covers in card_rows():
            if not reach_for.startswith(GAP):
                continue
            with self.subTest(block=block):
                self.assertEqual(
                    named_in(reach_for), [],
                    f"{time} says it has nothing recorded and then names something",
                )


class TestTheWorkOrderCaptureHoldsBeatThree(unittest.TestCase):
    """Beat three is the one the plan of record says not to cut for time, and
    until this capture existed it was the only beat that needed GitHub to be
    reachable from the podium.

    Both halves have to be in the file. The beat is the two of them in order:
    the instruction, then the refusal.
    """

    CAPTURE = REPO / "corridor-screen" / "captures" / "the-work-order" / "issue-7.txt"

    def setUp(self):
        self.captured = text_of(self.CAPTURE)

    def test_it_holds_the_acceptance_criterion_that_was_wrong(self):
        self.assertIn(
            "It states plainly that TBPELS has not spoken directly to AI",
            self.captured,
        )

    def test_it_holds_the_answer_that_refused_to_write_it(self):
        self.assertIn("acceptance criterion 4 is factually wrong", self.captured)
        self.assertIn("Policy Advisory Opinion 71", self.captured)

    def test_it_carries_the_date_that_makes_the_point(self):
        """PAO 71 was public for nearly two years when the work order was written."""
        self.assertIn("14 November 2024", self.captured)


if __name__ == "__main__":
    unittest.main()
