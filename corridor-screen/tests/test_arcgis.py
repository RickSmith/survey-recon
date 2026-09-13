"""Tests for the fetcher, and for the ping that goes first.

The ping's whole job is one question: **is this host answering today?** It runs
before any real work precisely so that a bad answer costs seconds rather than
ninety of them.

Issue #62 is what happens when it gets that question wrong. On 2026-09-13 the
Railroad Commission's pipeline service began returning ``HTTP 200`` carrying a
``503`` error in the body. The transport succeeded, so the ping said ``ok`` — of a
host that was serving nothing — and then saved that error body straight over a
good cached response, which broke the offline replay as well.

Two failures in one, and the tests here separate them:

**A 200 that carries an error is not a host answering.** The ping has to read
the body, not just the status line. Everything downstream depends on it: a
blocked flag service costs its own flag type, while a service the ping waves
through costs the entire run at the field-list check.

**A failed call must never destroy a good capture.** The demo runs from that
cache. Specification section 14 also says every response is saved, so the error
is kept — under its own name, beside the good one rather than on top of it.
"""

import json
import tempfile
import tomllib
import unittest
from contextlib import contextmanager
from pathlib import Path

from corridor_screen import arcgis
from corridor_screen.cache import Cache
from corridor_screen.sources import PARCELS

# What an ArcGIS service sends when it is unwell but the transport is fine.
# Copied from what `gis.rrc.texas.gov` actually returned on 2026-09-13.
AN_ERROR_BODY = json.dumps({
    "error": {
        "code": 503,
        "message": "User couldn't access this resource 'rrc_public/tpms.mapserver'.",
        "details": [],
    }
}).encode("utf-8")

A_GOOD_BODY = json.dumps({
    "name": "BCAD Parcels",
    "fields": [{"name": "Geo_id"}, {"name": "PropID"}],
}).encode("utf-8")


@contextmanager
def answering(body, status=200):
    """The network, replaced by one fixed answer, and put back afterwards.

    A context manager for the same reason ``test_offline`` uses one for the
    socket: a test that leaves a stand-in in place poisons every test that runs
    after it, and the one that fails is never the one at fault.
    """
    def reply(url, params, method, timeout):
        return body, status

    before = arcgis._open
    arcgis._open = reply
    try:
        yield
    finally:
        arcgis._open = before


def a_fetcher(root, mode="cache-first"):
    """A fetcher reading and writing a cache under `root`."""
    return arcgis.Fetcher(Cache(Path(root) / "cache"), mode=mode)


class TestReadingAnErrorInTheBody(unittest.TestCase):
    """The body, not the status line, says whether a service answered."""

    def test_an_error_in_the_body_is_recognized(self):
        found = arcgis.error_of(json.loads(AN_ERROR_BODY))
        self.assertIn("rrc_public", found)
        self.assertIn("503", found)

    def test_a_real_answer_is_not_mistaken_for_one(self):
        self.assertIsNone(arcgis.error_of(json.loads(A_GOOD_BODY)))

    def test_a_list_is_not_an_error(self):
        """Some services answer with a list. It has no keys to misread."""
        self.assertIsNone(arcgis.error_of([{"pid": "AY0713"}]))

    def test_an_error_with_nothing_readable_in_it_is_still_an_error(self):
        """It must never come back falsy. Every caller writes `if reported:`,
        so an empty string would wave through the thing it was asked about."""
        for empty in ({"error": {}}, {"error": {"message": "", "details": []}},
                      {"error": None}):
            with self.subTest(body=empty):
                self.assertTrue(arcgis.error_of(empty), empty)

    def test_details_are_carried_when_the_service_gives_them(self):
        found = arcgis.error_of(
            {"error": {"message": "Invalid URL", "details": ["layer not found"]}}
        )
        self.assertIn("Invalid URL", found)
        self.assertIn("layer not found", found)

    def test_a_body_that_is_not_json_at_all_reports_no_error(self):
        """`live_check` has seen plain text come back inside a 200."""
        self.assertIsNone(arcgis.error_of("Call failed."))


class TestThePingReadsTheBody(unittest.TestCase):
    """A host serving errors is not a host that is answering."""

    def test_a_200_carrying_an_error_is_reported_as_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            with answering(AN_ERROR_BODY):
                result = a_fetcher(temporary).ping(PARCELS)
        self.assertEqual(result["ping"], "blocked")

    def test_the_service_own_words_are_the_reason_given(self):
        """Not a summary of them. The reader has to be able to act on it."""
        with tempfile.TemporaryDirectory() as temporary:
            with answering(AN_ERROR_BODY):
                result = a_fetcher(temporary).ping(PARCELS)
        self.assertIn("rrc_public", result["detail"])

    def test_the_reason_names_the_status_that_really_came_back(self):
        """The trap is that the status said 200. Naming a status nobody
        checked would be the same mistake in the other direction."""
        with tempfile.TemporaryDirectory() as temporary:
            with answering(AN_ERROR_BODY, status=207):
                result = a_fetcher(temporary).ping(PARCELS)
        self.assertIn("HTTP 207", result["detail"])

    def test_a_body_that_is_not_json_at_all_is_also_blocked(self):
        """A gateway error page is a 200 too, and is not an answer either."""
        with tempfile.TemporaryDirectory() as temporary:
            with answering(b"<html><body>503 Service Unavailable</body></html>"):
                result = a_fetcher(temporary).ping(PARCELS)
        self.assertEqual(result["ping"], "blocked")
        self.assertIn("not JSON", result["detail"])

    def test_a_non_json_body_cannot_destroy_a_good_capture_either(self):
        with tempfile.TemporaryDirectory() as temporary:
            with answering(A_GOOD_BODY):
                a_fetcher(temporary).ping(PARCELS)
            cache = Cache(Path(temporary) / "cache")
            url, readable, params = arcgis._describe_url(PARCELS)
            good = cache.entry(PARCELS.name, readable, url, params)
            captured = cache.read(good)

            with answering(b"<html>503</html>"):
                a_fetcher(temporary).ping(PARCELS)
            self.assertEqual(captured, cache.read(good))

    def test_a_host_that_really_is_answering_is_still_ok(self):
        with tempfile.TemporaryDirectory() as temporary:
            with answering(A_GOOD_BODY):
                result = a_fetcher(temporary).ping(PARCELS)
        self.assertIn(result["ping"], ("ok", "slow"))


class TestAFailedPingCannotDestroyAGoodCapture(unittest.TestCase):
    """The demo runs from this cache. Issue #62 broke it for real."""

    def _ping_with(self, root, body):
        with answering(body):
            return a_fetcher(root).ping(PARCELS)

    def test_the_good_response_survives_a_later_failed_ping(self):
        with tempfile.TemporaryDirectory() as temporary:
            self._ping_with(temporary, A_GOOD_BODY)
            cache = Cache(Path(temporary) / "cache")
            url, readable, params = arcgis._describe_url(PARCELS)
            good = cache.entry(PARCELS.name, readable, url, params)
            captured = cache.read(good)
            self.assertIn(b"BCAD Parcels", captured)

            self._ping_with(temporary, AN_ERROR_BODY)
            still_there = cache.read(good)
        self.assertEqual(captured, still_there, "a failed ping overwrote a good capture")

    def test_the_failure_is_still_saved_somewhere(self):
        """Section 14: every response is saved. Fixing #62 must not weaken it."""
        with tempfile.TemporaryDirectory() as temporary:
            self._ping_with(temporary, AN_ERROR_BODY)
            bodies = sorted((Path(temporary) / "cache").rglob("*.json"))
            saved = [p for p in bodies if b"rrc_public" in p.read_bytes()]
        self.assertTrue(saved, "the error body was discarded rather than recorded")

    def test_the_failure_carries_its_date_and_its_exact_request(self):
        """A record nobody can repeat is not a provenance record."""
        with tempfile.TemporaryDirectory() as temporary:
            result = self._ping_with(temporary, AN_ERROR_BODY)
            meta = (Path(temporary) / "cache" / f"{result['cache_key']}.meta.toml")
            written = tomllib.loads(meta.read_text(encoding="utf-8"))
        self.assertEqual(written["request_url"], PARCELS.layer_url)
        self.assertIsNotNone(written["captured_at"])
        # `http_status = 200` is true and is the whole trap, so the record has
        # to say in words that the service reported a failure inside it.
        self.assertEqual(written["http_status"], 200)
        self.assertTrue(any("rrc_public" in w for w in written["warnings"]), written)

    def test_the_failure_is_saved_under_its_own_name(self):
        """Beside the good capture, never on top of it."""
        with tempfile.TemporaryDirectory() as temporary:
            self._ping_with(temporary, AN_ERROR_BODY)
            names = [p.name for p in sorted((Path(temporary) / "cache").rglob("*.json"))]
        self.assertTrue(any("error" in name for name in names), names)

    def test_a_failed_ping_leaves_no_cached_response_to_replay(self):
        """A first run that fails must not leave something that looks captured."""
        with tempfile.TemporaryDirectory() as temporary:
            self._ping_with(temporary, AN_ERROR_BODY)
            cache = Cache(Path(temporary) / "cache")
            url, readable, params = arcgis._describe_url(PARCELS)
            self.assertIsNone(cache.read(cache.entry(PARCELS.name, readable, url, params)))


class TestGetJsonStillRefusesAnErrorBody(unittest.TestCase):
    """The half that was already right, kept under test."""

    def test_an_error_body_raises_rather_than_being_returned(self):
        with tempfile.TemporaryDirectory() as temporary:
            with answering(AN_ERROR_BODY), self.assertRaises(arcgis.ServiceError):
                a_fetcher(temporary, mode="live").get_json(PARCELS.name, "parcels", PARCELS.query_url, {"f": "json"})

    def test_it_does_not_cache_the_error_as_if_it_were_an_answer(self):
        with tempfile.TemporaryDirectory() as temporary:
            with answering(AN_ERROR_BODY), self.assertRaises(arcgis.ServiceError):
                a_fetcher(temporary, mode="live").get_json(PARCELS.name, "parcels", PARCELS.query_url, {"f": "json"})
            bodies = list((Path(temporary) / "cache").rglob("*.json"))
        self.assertEqual(bodies, [])


if __name__ == "__main__":
    unittest.main()
