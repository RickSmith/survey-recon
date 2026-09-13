"""Tests for the right-of-entry letters, and for the clock that sends the second one.

Issue #34. The demo is six minutes long and first on the cut line, so most of
what is checked here is not about the letters at all. It is about the four ways
this could be wrong in front of a room of licensed surveyors.

**Day 21 could be a number somebody typed.** That is the whole point of the
segment -- an agent that writes ``21`` into a source file has invented a
requirement, which is the thing this repo says never to do. So the tests below
change the lead-time table and check the day moves. A derivation that only ever
answers 21 is indistinguishable from a constant.

**The second letter could need somebody to remember it.** A follow-up that
fires because a person ran a command is the exact failure the segment is about.
So the clock is tested on its own, against dates, with nothing else running.

**It could quietly promise more than it does.** The tool writes a letter. It
does not mail one, it has no address, and it has no authority. Every one of
those limits is checked as text on the letter rather than trusted to be
remembered.

**It could stop working at the podium.** The rendered demo is committed and
pinned to the code, and it is built with the network taken away at the socket
-- the same rule the three failure beats are held to.

Everything here reads the committed SH16 run and the committed lead-time table.
Nothing here reaches a network, and nothing here is a client's.
"""

import datetime as dt
import io
import json
import socket
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from corridor_screen import beats, lead_times, roe

REPO = Path(__file__).resolve().parent.parent.parent
SCREENING = REPO / "project-sh16" / "screening.json"

# The one parcel on SH16 with a confirmed wait behind it. Named rather than
# searched for, so a test that breaks says which tract it was looking at.
CEMETERY_PARCEL = "15664-003-0040"

# A school parcel -- flagged, and with no published number of days. It is here
# to prove a letter can still be written for a parcel whose wait is unmeasured,
# because "we could not find a number" is not "there is nothing to ask for."
SCHOOL_PARCEL = "04524-401-0020"


def document():
    with open(SCREENING, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parcel(document, parcel_id):
    for record in document["parcels"]:
        if record["id"] == parcel_id:
            return record
    raise AssertionError(f"{parcel_id} is not in the committed SH16 run")


def table(**overrides):
    """The committed lead-time table, with rows swapped for a test.

    Each override replaces one row's fields. Passing ``None`` drops the row
    entirely, which is how a table with no confirmed calendar-day figure at all
    is built.
    """
    rows = lead_times.load()
    for key, changes in overrides.items():
        if changes is None:
            rows.pop(key, None)
            continue
        for name, value in changes.items():
            setattr(rows[key], name, value)
    return rows


class TestWhereDayTwentyOneComesFrom(unittest.TestCase):
    """Acceptance criterion 3: derived from the lead-time data, not hard-coded.

    The derivation is three steps and every one of them is arguable, which is
    the point -- an estimator can disagree with it out loud. What they cannot
    do is find a 21 typed into a file.
    """

    def test_the_committed_table_gives_twenty_one_days(self):
        """The number on the slide, the run of show and the work order."""
        self.assertEqual(roe.follow_up_interval(table()).days, 21)

    def test_the_railroad_row_is_what_sets_it(self):
        interval = roe.follow_up_interval(table())
        self.assertEqual(interval.driver, "railroad")
        self.assertEqual(interval.lead_time_days, 45)

    def test_it_carries_the_citation_of_the_row_that_set_it(self):
        """A derived number is worth what the number it was derived from is worth."""
        interval = roe.follow_up_interval(table())
        self.assertIn("Union Pacific", interval.source)
        self.assertTrue(interval.url.startswith("https://"))

    def test_a_longer_lead_time_moves_the_day(self):
        """The check that tells a derivation from a constant."""
        interval = roe.follow_up_interval(table(railroad={"days": 60}))
        self.assertEqual(interval.days, 28)

    def test_a_shorter_lead_time_moves_it_the_other_way(self):
        interval = roe.follow_up_interval(table(railroad={"days": 30}))
        self.assertEqual(interval.days, 14)

    def test_dropping_the_longest_row_falls_back_to_the_next_one(self):
        """With the railroad gone, the cemetery's 14 calendar days is the outer clock."""
        interval = roe.follow_up_interval(table(railroad=None))
        self.assertEqual(interval.driver, "cemetery")
        self.assertEqual(interval.days, 7)

    def test_a_working_day_row_is_never_used(self):
        """Two working days and two calendar days are different promises.

        The pipeline row is counted in working days, and converting it would
        mean inventing a calendar of weekends and Texas legal holidays this
        tool does not have. So it is left out of the arithmetic rather than
        guessed at -- even when it is the biggest number in the table.
        """
        rows = table(railroad=None, cemetery=None, pipeline={"days": 90})
        with self.assertRaises(roe.NoFollowUpInterval) as raised:
            roe.follow_up_interval(rows)
        self.assertIn("working days", str(raised.exception))

    def test_an_unconfirmed_row_is_never_used(self):
        """A row with no published figure has no number to halve."""
        rows = table(railroad=None, cemetery=None)
        with self.assertRaises(roe.NoFollowUpInterval):
            roe.follow_up_interval(rows)

    def test_a_table_too_short_to_halve_says_so_rather_than_answering_zero(self):
        """Zero days would read as "send both letters at once", which is not a plan.

        Thirteen calendar days halves to six, which is not a whole week, so
        there is no interval to derive. The honest answer is to say that, name
        the row, and stop -- the same shape as "not found" everywhere else
        here.
        """
        rows = table(railroad=None, cemetery={"days": 13})
        with self.assertRaises(roe.NoFollowUpInterval) as raised:
            roe.follow_up_interval(rows)
        self.assertIn("13", str(raised.exception))

    def test_the_arithmetic_is_printable_rather_than_hidden(self):
        """An estimator argues with the steps, not with the answer."""
        lines = roe.follow_up_interval(table()).arithmetic()
        shown = "\n".join(lines)
        self.assertIn("45", shown)
        self.assertIn("22", shown)
        self.assertIn("21", shown)

    def test_the_interval_is_counted_in_calendar_days_and_says_so(self):
        interval = roe.follow_up_interval(table())
        self.assertEqual(interval.basis, "calendar days")


class TestTheFirstLetter(unittest.TestCase):
    """Acceptance criterion 1: generated from a flagged parcel."""

    def setUp(self):
        self.document = document()
        self.parcel = parcel(self.document, CEMETERY_PARCEL)
        self.interval = roe.follow_up_interval(table())
        self.sent_on = dt.date(2026, 9, 13)

    def letter(self):
        return roe.schedule(self.document, self.parcel, self.sent_on, self.interval)[0]

    def test_it_is_the_first_request_and_goes_out_on_day_zero(self):
        letter = self.letter()
        self.assertEqual(letter.number, 1)
        self.assertEqual(letter.day, 0)
        self.assertEqual(letter.date, self.sent_on)

    def test_it_names_the_parcel_the_screening_flagged(self):
        body = self.letter().markdown()
        self.assertIn(CEMETERY_PARCEL, body)
        self.assertIn(self.parcel["owner"], body)

    def test_it_names_what_is_on_the_tract_and_what_that_costs(self):
        body = self.letter().markdown()
        self.assertIn("cemetery", body.lower())
        self.assertIn("14", body)

    def test_it_cites_the_statute_behind_the_wait(self):
        self.assertIn("711.041", self.letter().markdown())

    def test_it_says_right_of_entry_is_not_a_right(self):
        """The one sentence the segment exists to say out loud."""
        body = self.letter().markdown().lower()
        self.assertIn("permission", body)
        self.assertIn("not a statutory right", body)

    def test_a_parcel_with_no_published_wait_still_gets_a_letter(self):
        """Unmeasured is not clear, and it is not nothing to ask about either."""
        letter = roe.schedule(
            self.document, parcel(self.document, SCHOOL_PARCEL),
            self.sent_on, self.interval,
        )[0]
        body = letter.markdown()
        self.assertIn(SCHOOL_PARCEL, body)
        self.assertIn("not found", body.lower())

    def test_an_unflagged_parcel_is_refused(self):
        """The work order says *from a flagged parcel*. Anything else is a form letter."""
        clear = next(p for p in self.document["parcels"] if not p.get("flags"))
        with self.assertRaises(roe.NotAFlaggedParcel):
            roe.schedule(self.document, clear, self.sent_on, self.interval)


class TestTheSecondLetterFiresOnItsOwn(unittest.TestCase):
    """Acceptance criterion 2: it fires on day 21 with no human action.

    "No human action" is a claim about a clock, so it is tested as one. The
    only input that changes between these tests is the date.
    """

    def setUp(self):
        self.document = document()
        self.parcel = parcel(self.document, CEMETERY_PARCEL)
        self.interval = roe.follow_up_interval(table())
        self.sent_on = dt.date(2026, 9, 13)
        self.schedule = roe.schedule(
            self.document, self.parcel, self.sent_on, self.interval)

    def test_there_are_exactly_two_letters(self):
        """TxDOT ships two templates. A third would be this tool's invention."""
        self.assertEqual([l.number for l in self.schedule], [1, 2])

    def test_the_second_falls_on_day_twenty_one(self):
        second = self.schedule[1]
        self.assertEqual(second.day, 21)
        self.assertEqual(second.date, dt.date(2026, 10, 4))

    def test_nothing_is_due_on_day_twenty(self):
        due = roe.due_on(self.schedule, dt.date(2026, 10, 3))
        self.assertEqual([l.number for l in due], [1])

    def test_the_second_is_due_on_day_twenty_one(self):
        due = roe.due_on(self.schedule, dt.date(2026, 10, 4))
        self.assertEqual([l.number for l in due], [1, 2])

    def test_it_stays_due_after_the_day_rather_than_being_missed(self):
        """A clock nobody read on the day is still a clock. Missing the run
        must not mean missing the letter."""
        due = roe.due_on(self.schedule, dt.date(2026, 11, 1))
        self.assertEqual([l.number for l in due], [1, 2])

    def test_the_day_moves_when_the_table_moves(self):
        """The clock is downstream of the lead-time table, not of a constant."""
        longer = roe.schedule(
            self.document, self.parcel, self.sent_on,
            roe.follow_up_interval(table(railroad={"days": 60})),
        )
        self.assertEqual(longer[1].date, dt.date(2026, 10, 11))

    def test_the_second_letter_says_it_is_the_second(self):
        body = self.schedule[1].markdown()
        self.assertIn("second", body.lower())

    def test_it_names_the_txdot_template_it_stands_in_for(self):
        """TxDOT ships a second request letter. Non-response is the baseline
        the department already designed for, and saying so is what stops this
        looking like the tool's own idea."""
        self.assertIn("020-11-tem", self.schedule[1].markdown())

    def test_it_shows_the_reader_where_day_twenty_one_came_from(self):
        body = self.schedule[1].markdown()
        self.assertIn("45", body)
        self.assertIn("21", body)

    def test_it_says_no_published_turnaround_was_found(self):
        """The honest half of the derivation. There is no right-of-entry clock
        to quote, and the letter says so rather than implying 21 is a rule.

        Pinned to the sentence rather than to a looser phrase, because this is
        the one claim on the letter a reader could be misled by. *Was found* is
        this repo's rule everywhere -- never *does not exist*.
        """
        self.assertIn(
            "no published txdot right-of-entry turn-around was found",
            self.schedule[1].markdown().lower(),
        )


class TestItNeverPretendsToHaveSentAnything(unittest.TestCase):
    """The tool writes a letter. A person signs it and a person mails it."""

    def setUp(self):
        self.document = document()
        self.schedule = roe.schedule(
            self.document, parcel(self.document, CEMETERY_PARCEL),
            dt.date(2026, 9, 13), roe.follow_up_interval(table()),
        )

    def test_every_letter_says_it_was_not_mailed(self):
        for letter in self.schedule:
            with self.subTest(letter=letter.number):
                self.assertIn("not mailed", letter.markdown().lower())

    def test_every_letter_says_a_licensed_surveyor_signs_it(self):
        for letter in self.schedule:
            with self.subTest(letter=letter.number):
                body = letter.markdown()
                self.assertIn("RPLS", body)

    def test_no_letter_prints_a_street_address(self):
        """The appraisal district publishes one, and this repo is public.

        A specimen letter needs the parcel and the owner, because those are
        what the screening flagged. It does not need the street address, and a
        letter that carries one invites being mailed.
        """
        situs = parcel(self.document, CEMETERY_PARCEL).get("situs")
        self.assertTrue(situs, "the committed run no longer records a situs to check against")
        for letter in self.schedule:
            with self.subTest(letter=letter.number):
                self.assertNotIn(situs, letter.markdown())

    def test_every_field_in_a_letter_came_from_the_screening_run(self):
        """Acceptance criterion 5: nothing in it touches client data.

        The check is not that the letters look clean. It is that every value
        they carry can be pointed at in a committed public file.
        """
        record = parcel(self.document, CEMETERY_PARCEL)
        for letter in self.schedule:
            with self.subTest(letter=letter.number):
                self.assertEqual(letter.parcel_id, record["id"])
                self.assertEqual(letter.owner, record["owner"])
                self.assertEqual(letter.source_file, "screening.json")


class TestTheDemoSurvivesBeingRecorded(unittest.TestCase):
    """Acceptance criterion 4: it can be shown as a recording if the segment is cut.

    Same three rules the failure beats are held to, and for the same reason --
    this is the block most likely to be played from a file rather than run.
    """

    def test_it_prints_on_a_console_that_only_speaks_plain_ascii(self):
        beats.render(roe.demo().splitlines())

    def test_it_builds_with_the_network_taken_away(self):
        saved = socket.socket
        socket.socket = _NoNetwork
        try:
            said = roe.demo()
        finally:
            socket.socket = saved
        self.assertIn("day 21", said)

    def test_the_committed_recording_is_what_the_code_prints(self):
        """A fallback file that has drifted from the code is worse than none,
        because it is the one that gets played.

        Read the way `test_beats.py` reads a committed beat: `newline=""` and
        the replace rather than universal newlines, because git may check the
        file out with CRLF and this check is about content.
        """
        path = roe.CAPTURE_DIR / roe.DEMO_NAME
        self.assertTrue(path.exists(), f"{path} is not committed")
        with open(path, "r", encoding="utf-8", newline="") as handle:
            committed = handle.read()
        self.assertEqual(committed.replace("\r\n", "\n"), roe.demo() + "\n")

    def test_it_shows_the_day_before_as_well_as_the_day(self):
        """One frame showing nothing due is what makes the next frame mean
        something. A recording of only the letter appearing proves nothing."""
        said = roe.demo()
        self.assertIn("day 20", said)
        self.assertIn("day 21", said)

    def test_it_shows_the_arithmetic_behind_the_day(self):
        said = roe.demo()
        self.assertIn("45", said)
        self.assertIn("21", said)


class TestWhatIsCommittedAndWhatIsNot(unittest.TestCase):
    """The first letter is in the repo. The second one is not, and that is the demo.

    A folder holding both letters would say the tool can write two letters. A
    folder holding one, beside a clock that has not reached day 21 yet, says
    the thing the segment is actually about.
    """

    FOLDER = REPO / "project-sh16" / "roe"

    def setUp(self):
        self.document = document()
        self.schedule = roe.schedule(
            self.document, parcel(self.document, roe.DEMO_PARCEL),
            dt.date.fromisoformat(self.document["run"]["finished_at"][:10]),
            roe.follow_up_interval(table()),
        )

    def test_the_first_letter_is_committed(self):
        path = self.FOLDER / self.schedule[0].filename()
        self.assertTrue(path.exists(), f"{path} is not committed")

    def test_the_committed_first_letter_is_what_the_code_writes(self):
        path = self.FOLDER / self.schedule[0].filename()
        with open(path, "r", encoding="utf-8", newline="") as handle:
            committed = handle.read()
        self.assertEqual(committed.replace("\r\n", "\n"), self.schedule[0].markdown())

    def test_the_second_letter_is_not_committed_yet(self):
        """It is not due. A file sitting there would undo the whole point."""
        path = self.FOLDER / self.schedule[1].filename()
        self.assertFalse(
            path.exists(),
            f"{path} is committed, and day {self.schedule[1].day} has not arrived. "
            f"A follow-up that is already in the repo is not a follow-up.",
        )

    def test_the_folder_explains_the_letter_that_is_missing(self):
        """An empty-looking folder reads as unfinished work rather than as a clock."""
        readme = self.FOLDER / "README.md"
        self.assertTrue(readme.exists(), f"{readme} is not committed")
        with open(readme, "r", encoding="utf-8") as handle:
            said = handle.read()
        self.assertIn(self.schedule[1].filename(), said)
        self.assertIn(str(self.schedule[1].day), said)


class TestTheCommandLine(unittest.TestCase):
    """What a presenter types, and what happens if they type it wrong."""

    def test_show_prints_the_demo_and_succeeds(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = roe.main(["--show"])
        self.assertEqual(code, 0)
        self.assertIn("day 21", out.getvalue())

    def test_it_is_what_show_prints_that_is_committed(self):
        out = io.StringIO()
        with redirect_stdout(out):
            roe.main(["--show"])
        self.assertIn(roe.demo(), out.getvalue())


class _NoNetwork:
    """Every door to a network, closed. Same stand-in the beats use."""

    def __init__(self, *args, **kwargs):
        raise OSError("the network is not available to this test")


if __name__ == "__main__":
    unittest.main()
