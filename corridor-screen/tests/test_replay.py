"""Tests for comparing a replayed run against the live one it replays.

Issue #19 asks for one thing that cannot be taken on trust: "output from cache
matches output from live." A tool that replays a capture and quietly answers
differently is worse than no replay at all, because the whole point is to be
able to stand in front of a room and say the numbers are the same ones.

So the comparison has to be exact about what "matches" means. Two runs of the
same corridor are never byte-identical -- they start at different times, and one
of them pinged hosts the other did not. Those differences are the run's account
of **itself**, and none of them is a finding.

The tests here are about keeping that line in the right place. Too loose and a
real change slips through; too tight and the check cries wolf every run and
somebody stops reading it.
"""

import unittest

from corridor_screen import replay


def a_document(**overrides):
    """A screening document, cut down to the parts these tests care about."""
    document = {
        "run": {
            "run_id": "texas-bexar-sh0016-kg-20260913T064752",
            "started_at": "2026-09-13T06:47:52-05:00",
            "finished_at": "2026-09-13T06:48:26-05:00",
            "mode": "live",
            "half_width_ft": 300,
        },
        "services": [
            {
                "name": "BCAD_Parcels",
                "ping": "ok",
                "ping_ms": 235,
                "ping_detail": "",
                "attempts": 1,
                "status": "ok",
                "record_count": 530,
                "captured_at": "2026-09-13T06:47:55-05:00",
            }
        ],
        "parcels": [{"id": "15664-003-0040", "owner": "SOMEBODY", "max_lead_time_days": 14}],
        "crew_safety": {"by_type": {"hospital": {"nearest": {"name": "Audie L Murphy"}}}},
    }
    document.update(overrides)
    return document


def replayed(document):
    """The same corridor, replayed from cache rather than fetched."""
    import copy

    other = copy.deepcopy(document)
    other["run"]["run_id"] = "texas-bexar-sh0016-kg-20260913T064826"
    other["run"]["started_at"] = "2026-09-13T06:48:26-05:00"
    other["run"]["finished_at"] = "2026-09-13T06:48:28-05:00"
    other["run"]["mode"] = "cache-only"
    for service in other["services"]:
        service["ping"] = "skipped"
        service["ping_ms"] = 0
        service["ping_detail"] = "cache-only run makes no network calls"
        service["attempts"] = 0
    return other


class TestWhatCountsAsTheSameAnswer(unittest.TestCase):
    """A replay differs from the live run in how it ran, never in what it found."""

    def test_a_replay_of_the_same_run_has_no_differences(self):
        live = a_document()
        self.assertEqual(replay.differences(live, replayed(live)), [])

    def test_a_replay_of_the_same_run_is_reported_as_matching(self):
        live = a_document()
        self.assertTrue(replay.same_findings(live, replayed(live)))

    def test_a_changed_finding_is_caught(self):
        live = a_document()
        cached = replayed(live)
        cached["parcels"][0]["max_lead_time_days"] = 30
        found = replay.differences(live, cached)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["path"], "parcels[0].max_lead_time_days")

    def test_a_changed_finding_means_the_two_do_not_match(self):
        live = a_document()
        cached = replayed(live)
        cached["crew_safety"]["by_type"]["hospital"]["nearest"]["name"] = "Somewhere Else"
        self.assertFalse(replay.same_findings(live, cached))

    def test_a_dropped_record_is_caught_rather_than_read_as_a_shorter_list(self):
        live = a_document()
        cached = replayed(live)
        cached["parcels"] = []
        found = replay.differences(live, cached)
        self.assertEqual(len(found), 1)
        self.assertIn("parcels", found[0]["path"])

    def test_a_block_that_vanished_is_caught(self):
        live = a_document()
        cached = replayed(live)
        del cached["crew_safety"]
        found = replay.differences(live, cached)
        self.assertTrue(any("crew_safety" in d["path"] for d in found))

    def test_the_record_count_a_service_reported_is_a_finding_not_an_account(self):
        """How many records came back is an answer, not a fact about the run."""
        live = a_document()
        cached = replayed(live)
        cached["services"][0]["record_count"] = 1
        found = replay.differences(live, cached)
        self.assertEqual(found[0]["path"], "services[0].record_count")

    def test_when_the_answer_was_captured_is_a_finding_too(self):
        """It is how old the data is. A replay reports the capture, not today.

        This is the field that makes a replayed run honest, so it is compared
        rather than excused: if a replay claimed a fresh capture time, the
        honesty block would be lying about the age of its own data.
        """
        live = a_document()
        cached = replayed(live)
        cached["services"][0]["captured_at"] = "2020-01-01T00:00:00-05:00"
        found = replay.differences(live, cached)
        self.assertEqual(found[0]["path"], "services[0].captured_at")


class TestWhatIsAllowedToDiffer(unittest.TestCase):
    """The run's account of itself. Named, with a reason, and never hidden."""

    def test_every_excluded_path_carries_a_reason(self):
        """A path excluded without a reason is a path nobody can argue with."""
        for path, reason in replay.RUN_ACCOUNT.items():
            self.assertTrue(reason, f"{path} is excluded with no reason given")

    def test_the_differences_that_were_allowed_are_reported_rather_than_dropped(self):
        """What the check ignored is shown, so the reader can disagree with it."""
        live = a_document()
        allowed = replay.run_account_differences(live, replayed(live))
        paths = {d["path"] for d in allowed}
        self.assertIn("run.mode", paths)
        self.assertIn("services[0].ping", paths)

    def test_the_mode_differing_is_the_whole_point_and_not_a_failure(self):
        live = a_document()
        cached = replayed(live)
        self.assertEqual(live["run"]["mode"], "live")
        self.assertEqual(cached["run"]["mode"], "cache-only")
        self.assertTrue(replay.same_findings(live, cached))

    def test_a_stated_distance_is_not_part_of_the_run_account(self):
        """`half_width_ft` lives in `run` and is an input, not a timestamp.

        Excluding the whole `run` block would have been the easy way to write
        this and would have hidden a corridor screened at a different width.
        """
        live = a_document()
        cached = replayed(live)
        cached["run"]["half_width_ft"] = 600
        found = replay.differences(live, cached)
        self.assertEqual(found[0]["path"], "run.half_width_ft")


class TestReadingTheReport(unittest.TestCase):
    """What a person sees when the two do not match."""

    def test_a_difference_names_the_path_and_both_values(self):
        live = a_document()
        cached = replayed(live)
        cached["parcels"][0]["owner"] = "SOMEBODY ELSE"
        found = replay.differences(live, cached)[0]
        self.assertEqual(found["path"], "parcels[0].owner")
        self.assertEqual(found["live"], "SOMEBODY")
        self.assertEqual(found["replayed"], "SOMEBODY ELSE")

    def test_the_report_says_so_plainly_when_they_match(self):
        live = a_document()
        self.assertIn("match", replay.report(live, replayed(live)).lower())

    def test_the_report_names_what_differs_when_they_do_not(self):
        live = a_document()
        cached = replayed(live)
        cached["parcels"][0]["owner"] = "SOMEBODY ELSE"
        printed = replay.report(live, cached)
        self.assertIn("parcels[0].owner", printed)
        self.assertIn("SOMEBODY ELSE", printed)

    def test_the_report_always_says_how_many_differences_it_allowed(self):
        """Even on a clean match. A check that hides its own slack is not a check."""
        live = a_document()
        printed = replay.report(live, replayed(live))
        self.assertIn("run.mode", printed)


if __name__ == "__main__":
    unittest.main()
