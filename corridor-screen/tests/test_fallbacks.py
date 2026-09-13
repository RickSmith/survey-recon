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
* every file the card names is committed, is not empty, and opens
* every command the card names **runs with the network taken away**, not
  politely asked to stay home -- removed, at the socket
* every gap says it is a gap and names the work order that would close it
* the number of gaps the card states in prose is the number of gaps it has

The last two are the point of an audit. A card that quietly dropped the blocks
with nothing recorded yet would pass every other check here and lie to the
presenter, which is worse than having no card at all. How many there are is a
number on the card, so it is not restated here -- the count in this file would
be the next thing to rot.

**Why the card, and not a Python table.** The presenter reads a page. A list
held anywhere else would be a second copy of the same facts, and the first
correction would go into only one of them.
"""

import contextlib
import importlib
import json
import re
import shlex
import unittest
from contextlib import contextmanager
from pathlib import Path

from corridor_screen import cli
from corridor_screen.cache import long_path

# Borrowed rather than copied. `no_network` takes the network away below every
# library that could reach for it, `a_copy_of_the_demo_cache` puts a run
# somewhere that is not the committed demo artifact, and `quiet` keeps a whole
# screening report out of the test output. Two copies of any of them would
# drift the first time somebody fixed one of them.
from tests.test_offline import a_copy_of_the_demo_cache, no_network, quiet

REPO = Path(__file__).resolve().parents[2]
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
PLAN = REPO / "docs" / "plan-of-record.md"

# `0:57–1:18`, with the en dash the plan of record actually uses.
A_TIME = re.compile(r"^\d:\d\d\u2013\d:\d\d$")

# The three ways a "reach for" cell is allowed to start. Anything else is a
# sentence somebody wrote in a hurry, and a presenter cannot act on one of
# those at four minutes past the hour. A cell that is ready opens with a code
# span -- a backtick -- because what it holds is a path or a command.
A_CODE_SPAN, GAP, NOTHING_LIVE = "`", "not recorded", "nothing live"


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

    `quiet` shuts the door the screening run talks through, which is `cli._say`.
    The two failure beats use plain `print`, so stdout goes into the same
    buffer -- both halves of what a presenter would see, in one string.
    """
    with quiet() as said, contextlib.redirect_stdout(said):
        yield said


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


def play(command):
    """Run one command off the card with every network door refused.

    Named for what the ticket asks -- "each one plays with no network
    connection" -- and deliberately not `run_offline`, which already means
    something else one file over: there it is one whole screening run of the
    demo corridor, and here it is any one line off the card.
    """
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
    """Every block of the session reaches the card, and nothing else does.

    Rows outnumber blocks: the failure beat is three separate things plus the
    review, and a presenter needs to reach for one of them rather than for a
    paragraph. What has to match is the set of blocks and their order.
    """

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
                    reach_for.startswith((A_CODE_SPAN, GAP, NOTHING_LIVE)),
                    f"{time} reads {reach_for!r}, which is none of "
                    f"{A_CODE_SPAN!r}, {GAP!r} or {NOTHING_LIVE!r}",
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

    def test_every_file_named_opens_and_has_something_in_it(self):
        """Existing is not the same as opening.

        A file can be on disk, the right size, and still be unreadable from
        where the tool stands -- which is exactly the finding that came out of
        this audit on #76. So each one is opened, through the same door.
        """
        for time, _block, reach_for, _covers in card_rows():
            for named in named_in(reach_for):
                if is_a_command(named):
                    continue
                with self.subTest(time=time, file=named):
                    self.assertGreater(len(text_of(REPO / named).strip()), 0)

    def test_the_drawing_carries_nothing_it_would_have_to_fetch(self):
        """An `.svg` is the one fallback that could still need a network.

        A drawing that reaches out for a font or an image renders as a blank
        rectangle on a laptop with no network, which is the moment it is being
        put on the projector. A namespace declaration is not a fetch, so the
        check is on the attributes that actually go and get something.
        """
        fetches = re.compile(r'(?:href|src|xlink:href)="http|url\(\s*["\']?http')
        for _time, _block, reach_for, _covers in card_rows():
            for named in named_in(reach_for):
                if is_a_command(named) or not named.endswith(".svg"):
                    continue
                with self.subTest(file=named):
                    self.assertIsNone(
                        fetches.search(text_of(REPO / named)),
                        f"{named} reaches out for something it will not get offline",
                    )

    def test_a_ready_row_actually_names_something(self):
        """`ready` and an empty cell is the failure this whole file is about."""
        for time, block, reach_for, _covers in card_rows():
            if not reach_for.startswith(A_CODE_SPAN):
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
                code, said = play(command)
                self.assertEqual(code, 0, f"{command}\n{said}")

    def test_each_command_prints_something_a_room_can_read(self):
        """A silent success on a projector looks exactly like a hang."""
        for row in card_rows():
            for named in named_in(row[2]):
                if not is_a_command(named):
                    continue
                with self.subTest(command=named):
                    _code, said = play(named)
                    self.assertGreater(len(said.strip()), 0, f"{named} printed nothing")


class TestAGapSaysSoAndNamesTheWorkThatWouldCloseIt(unittest.TestCase):
    """Blocks of this session with nothing recorded yet are mostly waiting on
    something that does not exist yet -- the deck, the money slide, Hermes. That
    is a finding, and the card's job is to say it out loud rather than leave a
    presenter to discover it at the podium."""

    def test_every_gap_names_a_work_order(self):
        for time, block, reach_for, _covers in card_rows():
            if not reach_for.startswith(GAP):
                continue
            with self.subTest(block=block):
                self.assertRegex(
                    reach_for, r"#\d+",
                    f"{time} has no fallback and does not say which work order would give it one",
                )

    def test_the_number_of_gaps_the_card_states_is_the_number_it_has(self):
        """A number written in prose beside a table is a number that rots.

        The first draft of this page said four, having counted the pieces of
        work that were missing rather than the blocks left without anything to
        reach for. The deck is one piece of work and two blocks of the session,
        so a presenter counting rows would have found five and stopped trusting
        the page. Both numbers are now on the page, and this holds the one a
        reader can check.
        """
        stated = re.search(r"\*\*(\d+) blocks have nothing to reach for\*\*", text_of(CARD))
        self.assertIsNotNone(stated, "the card no longer says how many gaps it has")
        gaps = [row for row in card_rows() if row[2].startswith(GAP)]
        self.assertEqual(int(stated.group(1)), len(gaps))

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


class TestTheGrillingCaptureHoldsActI(unittest.TestCase):
    """The fallback for the hinge of the session, from the run that really happened.

    Two of these are about the honesty of the thing rather than its content.
    A transcript put on a projector as if it were a recording, or a set of work
    orders shown as if the session had written them, would be the kind of
    overclaim this repo keeps apologizing for in `docs/managing-your-agent/`.
    """

    FOLDER = REPO / "corridor-screen" / "captures" / "the-grilling"

    def test_the_run_it_came_from_is_named_rather_than_implied(self):
        """Evidence with no provenance is an anecdote."""
        readme = text_of(self.FOLDER / "README.md")
        self.assertIn("issues/5", readme, "the work order the grilling ran on")
        self.assertIn("12 September 2026", readme)

    def test_it_says_out_loud_that_it_is_a_transcript_and_not_a_recording(self):
        self.assertIn(
            "transcript, not a recording", text_of(self.FOLDER / "README.md")
        )

    def test_the_machine_it_ran_on_is_nowhere_in_it(self):
        """The one that matters. This repo is public and the source was a
        session store on somebody's laptop, full of paths and one address.

        The raw JSON is checked too, and it is the file most likely to carry
        something in one day: it is the only one here that gets regenerated by
        re-running a command rather than rewritten by a person.
        """
        for name in ("README.md", "the-grilling.md", "the-tickets.md", "the-tickets.json"):
            with self.subTest(file=name):
                body = text_of(self.FOLDER / name)
                for leak in ("yodas", "@gmail", "C:\\Users", "OneDrive"):
                    self.assertNotIn(leak, body, f"{leak} survived into {name}")

    def test_the_one_screen_summary_covers_every_question_that_was_asked(self):
        """The README's table is what goes on the projector, and it is the one
        authored thing here -- a reading of the transcript rather than a copy
        of it.

        Testing a paraphrase against its source is not something a test can do.
        What it can do is make sure no question quietly went missing between
        the two, which is the failure that would actually mislead a room: a
        summary that is accurate about eighteen questions and silent about the
        nineteenth.
        """
        readme = text_of(self.FOLDER / "README.md")
        transcript = text_of(self.FOLDER / "the-grilling.md")
        for number in range(1, 20):
            asked = f"**Q{number}**"
            with self.subTest(question=asked):
                self.assertIn(asked, transcript, f"{asked} is not in the transcript")
                self.assertIn(asked, readme, f"{asked} was asked and the summary skips it")

    def test_every_row_of_the_ticket_table_is_what_github_returned(self):
        """The readable table beside the raw capture, held to the raw capture.

        This is not hypothetical. The first draft of that table had `#39`
        labeled `ready-for-agent` when GitHub says `ready-for-human`, and this
        check is what found it. One wrong label is exactly the size of error
        that survives a proofread and then gets read out to a room.
        """
        issues = {
            issue["number"]: issue
            for issue in json.loads(text_of(self.FOLDER / "the-tickets.json"))
        }
        rows = [
            row for row in table_rows(text_of(self.FOLDER / "the-tickets.md"))
            if row[0].isdigit()
        ]
        self.assertTrue(rows, "the ticket table has no rows")
        for number, created, state, label, title in rows:
            issue = issues.get(int(number))
            with self.subTest(issue=number):
                self.assertIsNotNone(issue, f"#{number} is not in the capture")
                self.assertEqual(created, issue["createdAt"][11:19])
                self.assertEqual(state, issue["state"].lower())
                self.assertEqual([label], [l["name"] for l in issue["labels"]])
                self.assertEqual(title, issue["title"])


if __name__ == "__main__":
    unittest.main()
