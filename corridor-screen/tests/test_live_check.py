"""Tests for the one call that is genuinely live.

The plan of record asks for this in one line: *"Keep one genuinely live call --
NGS `/radial` was the most reliable endpoint tested. One live moment proves it
isn't a movie."*

So this is the moment. Everything in a screening run is replayed from a
committed capture, said out loud, and this one call goes out to NGS while the
room watches. It asks a **different NGS endpoint** than the screening run uses,
so when the two agree that is a real cross-check rather than a recording
agreeing with itself.

The tests here are about the three ways that moment could mislead a room.

Reporting agreement the tool did not actually establish. The live call asks
about a circle around the corridor's midpoint; the screening run asks about a
300-foot ribbon. They overlap and they are not the same question, so a mark in
one and not the other is ordinary and must never be counted as a disagreement.

Reporting a disagreement as a failure. If NGS has changed a record since the
capture, that is the most interesting thing to happen all session -- it is the
tool being right about how old its data is. It is news, not an error.

And dying on stage. A venue with no network must cost the live moment and
nothing else. The screening run is already on disk.
"""

import unittest

from corridor_screen import live_check


def a_live_record(pid, condition="MARK NOT FOUND", **extra):
    """One mark, in the shape the NGS Data Explorer answers with.

    Note the spelling. This API answers in camel case -- ``lastRecovered`` --
    where the datasheets feature service the screening run uses answers
    ``LAST_RECV``. Two NGS endpoints, two spellings, one mark.
    """
    record = {
        "pid": pid,
        "condition": condition,
        "name": "J 13",
        "lastRecovered": "20020308",
        "lat": 29.5285,
        "lon": -98.6446,
    }
    record.update(extra)
    return record


def a_captured_mark(pid, condition="MARK NOT FOUND"):
    """One mark, as the screening run wrote it into ``screening.json``."""
    return {"pid": pid, "condition": condition, "designation": "J 13"}


class TestReadingWhatNgsSent(unittest.TestCase):
    """The API answers with a list, not the object an ArcGIS service returns."""

    def test_a_mark_carries_the_field_the_whole_session_is_about(self):
        mark = live_check.to_mark(a_live_record("AY1102"))
        self.assertEqual(mark["pid"], "AY1102")
        self.assertEqual(mark["condition"], "MARK NOT FOUND")

    def test_the_recovery_date_is_written_out_for_a_person(self):
        mark = live_check.to_mark(a_live_record("AY1102", lastRecovered="20020308"))
        self.assertEqual(mark["last_recovered"], "2002-03-08")

    def test_a_record_with_no_condition_says_so_rather_than_guessing(self):
        mark = live_check.to_mark(a_live_record("AY1102", condition=None))
        self.assertIsNone(mark["condition"])


class TestComparingTheLiveCallAgainstTheCapture(unittest.TestCase):
    """The cross-check, and the line between agreement and coincidence."""

    def compare(self, live, captured):
        return live_check.compare(
            [live_check.to_mark(r) for r in live], captured
        )

    def test_marks_in_both_with_the_same_condition_are_the_agreement(self):
        found = self.compare(
            [a_live_record("AY1102"), a_live_record("AY1100")],
            [a_captured_mark("AY1102"), a_captured_mark("AY1100")],
        )
        self.assertEqual(found["in_both"], 2)
        self.assertEqual(found["agree"], 2)
        self.assertEqual(found["disagree"], [])

    def test_a_mark_only_the_live_call_saw_is_not_a_disagreement(self):
        """The two ask different questions. A wider circle sees more marks."""
        found = self.compare(
            [a_live_record("AY1102"), a_live_record("AY9999")],
            [a_captured_mark("AY1102")],
        )
        self.assertEqual(found["in_both"], 1)
        self.assertEqual(found["disagree"], [])
        self.assertEqual(found["only_live"], 1)

    def test_a_mark_only_the_capture_saw_is_not_a_disagreement_either(self):
        found = self.compare(
            [a_live_record("AY1102")],
            [a_captured_mark("AY1102"), a_captured_mark("AY0958")],
        )
        self.assertEqual(found["only_captured"], 1)
        self.assertEqual(found["disagree"], [])

    def test_a_changed_condition_is_reported_and_names_both_values(self):
        """NGS changing a record since the capture is news, not an error."""
        found = self.compare(
            [a_live_record("AY1102", condition="GOOD")],
            [a_captured_mark("AY1102", condition="MARK NOT FOUND")],
        )
        self.assertEqual(found["agree"], 0)
        self.assertEqual(len(found["disagree"]), 1)
        changed = found["disagree"][0]
        self.assertEqual(changed["pid"], "AY1102")
        self.assertEqual(changed["captured"], "MARK NOT FOUND")
        self.assertEqual(changed["live"], "GOOD")

    def test_conditions_are_compared_without_tripping_over_case(self):
        found = self.compare(
            [a_live_record("AY1102", condition="mark not found")],
            [a_captured_mark("AY1102", condition="MARK NOT FOUND")],
        )
        self.assertEqual(found["agree"], 1)
        self.assertEqual(found["disagree"], [])

    def test_nothing_in_common_is_said_plainly_rather_than_read_as_agreement(self):
        """Zero of zero agreeing is not a cross-check. It is no cross-check."""
        found = self.compare([a_live_record("AY9999")], [a_captured_mark("AY0958")])
        self.assertEqual(found["in_both"], 0)
        self.assertFalse(found["cross_checked"])

    def test_any_overlap_at_all_counts_as_a_cross_check(self):
        found = self.compare([a_live_record("AY1102")], [a_captured_mark("AY1102")])
        self.assertTrue(found["cross_checked"])


class TestWhatTheRoomIsTold(unittest.TestCase):
    """The report, which is read aloud while it is on the screen."""

    def report(self, live, captured, captured_at="2026-09-13T06:51:13-05:00"):
        marks = [live_check.to_mark(r) for r in live]
        return live_check.report(marks, captured, captured_at, radius_mi=2.0)

    def test_it_says_the_call_just_happened(self):
        printed = self.report([a_live_record("AY1102")], [a_captured_mark("AY1102")])
        self.assertIn("live", printed.lower())

    def test_it_says_when_the_screening_run_was_captured(self):
        printed = self.report([a_live_record("AY1102")], [a_captured_mark("AY1102")])
        self.assertIn("2026-09-13", printed)

    def test_it_says_the_two_endpoints_are_different(self):
        """Otherwise the cross-check looks like a recording agreeing with itself."""
        printed = self.report([a_live_record("AY1102")], [a_captured_mark("AY1102")])
        self.assertIn("different", printed.lower())

    def test_a_disagreement_is_the_loudest_thing_on_the_page(self):
        printed = self.report(
            [a_live_record("AY1102", condition="GOOD")],
            [a_captured_mark("AY1102", condition="MARK NOT FOUND")],
        )
        self.assertIn("CHANGED", printed)
        self.assertIn("AY1102", printed)

    def test_no_overlap_does_not_claim_a_cross_check(self):
        printed = self.report([a_live_record("AY9999")], [a_captured_mark("AY0958")])
        self.assertNotIn("agree", printed.lower().split("no cross-check")[0])


class TestWhenTheFieldHasBeenRenamed(unittest.TestCase):
    """The failure that would put a false alarm on a projector.

    ``sources.py`` records this trap for the *other* NGS endpoint: the
    condition field is ``LAST_COND`` on the feature service and ``condition``
    here, and reading the wrong name returns nothing and raises nothing. If NGS
    renames it on this API, every mark comes back with no condition, every one
    of them then "differs" from the capture, and the report announces
    ``CHANGED SINCE THE CAPTURE -- 5 marks`` to a room. All of it wrong.

    Thirteen marks do not lose their condition on the same afternoon. A field
    does.
    """

    def test_no_mark_carrying_a_condition_is_not_five_disagreements(self):
        found = live_check.compare(
            [live_check.to_mark({"pid": "AY1102"}), live_check.to_mark({"pid": "AY1100"})],
            [a_captured_mark("AY1102"), a_captured_mark("AY1100")],
        )
        self.assertTrue(found["no_conditions"])
        self.assertFalse(found["cross_checked"])

    def test_the_report_says_the_field_may_have_been_renamed(self):
        printed = live_check.report(
            [live_check.to_mark({"pid": "AY1102"})],
            [a_captured_mark("AY1102")],
            "2026-09-13T06:51:13-05:00",
        )
        self.assertIn("different", printed.lower())
        self.assertNotIn("CHANGED", printed)

    def test_one_mark_missing_a_condition_is_still_an_ordinary_disagreement(self):
        """Only *every* mark missing one points at the field rather than the data."""
        found = live_check.compare(
            [
                live_check.to_mark({"pid": "AY1102"}),
                live_check.to_mark({"pid": "AY1100", "condition": "GOOD"}),
            ],
            [a_captured_mark("AY1102"), a_captured_mark("AY1100")],
        )
        self.assertFalse(found["no_conditions"])
        self.assertEqual(len(found["disagree"]), 2)


class TestTheCommandLine(unittest.TestCase):
    """``argparse``, the same as the screening run.

    The first version parsed by hand, and ``--out`` with no value after it put
    an ``IndexError`` traceback on screen -- on the one command that runs live
    in front of a room.
    """

    def test_the_project_directory_is_required(self):
        with self.assertRaises(SystemExit):
            live_check.parse_args([])

    def test_a_missing_value_is_an_error_rather_than_a_traceback(self):
        with self.assertRaises(SystemExit):
            live_check.parse_args(["--out"])

    def test_a_radius_that_is_not_a_number_is_an_error(self):
        with self.assertRaises(SystemExit):
            live_check.parse_args(["--out", "somewhere", "--radius-miles", "wide"])

    def test_a_radius_of_zero_would_find_nothing_and_is_refused(self):
        with self.assertRaises(SystemExit):
            live_check.parse_args(["--out", "somewhere", "--radius-miles", "0"])

    def test_the_defaults_are_the_stated_ones(self):
        args = live_check.parse_args(["--out", "../project-sh16"])
        self.assertEqual(args.out, "../project-sh16")
        self.assertEqual(args.radius_miles, live_check.DEFAULT_RADIUS_MI)


class TestWhenThereIsNoNetwork(unittest.TestCase):
    """A venue with no network costs the live moment and nothing else."""

    def test_the_message_says_the_screening_run_is_unaffected(self):
        printed = live_check.unreachable("Errno 11001 getaddrinfo failed")
        self.assertIn("screening run", printed.lower())
        self.assertIn("unaffected", printed.lower())

    def test_the_message_carries_what_actually_went_wrong(self):
        printed = live_check.unreachable("Errno 11001 getaddrinfo failed")
        self.assertIn("11001", printed)


if __name__ == "__main__":
    unittest.main()
