"""Tests for saved responses and their provenance records."""

import tempfile
import tomllib
import unittest
from pathlib import Path

from corridor_screen.cache import Cache, render_toml, write_text

URL = "https://example.invalid/arcgis/rest/services/Thing/FeatureServer/0/query"
PARAMS = {"where": "1=1", "outFields": "*", "f": "json"}


class TestCacheKey(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Cache(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_same_request_lands_on_the_same_file(self):
        a = self.cache.entry("BCAD_Parcels", "parcels page 1", URL, PARAMS)
        b = self.cache.entry("BCAD_Parcels", "parcels page 1", URL, dict(reversed(list(PARAMS.items()))))
        self.assertEqual(a.body_path, b.body_path)

    def test_a_different_request_lands_on_a_different_file(self):
        a = self.cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
        b = self.cache.entry("BCAD_Parcels", "parcels", URL, dict(PARAMS, resultOffset="2000"))
        self.assertNotEqual(a.body_path, b.body_path)

    def test_the_file_name_stays_readable(self):
        entry = self.cache.entry("BCAD_Parcels", "parcels page 1", URL, PARAMS)
        self.assertTrue(entry.body_path.name.startswith("parcels-page-1__"))
        self.assertTrue(entry.body_path.name.endswith(".json"))


class TestProvenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Cache(Path(self.tmp.name))
        self.entry = self.cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
        self.cache.write(self.entry, b'{"features": []}', 200, layer_id=0, record_count=17)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_response_is_saved_exactly_as_sent(self):
        self.assertEqual(self.entry.body_path.read_bytes(), b'{"features": []}')

    def test_the_record_reads_back_as_valid_toml(self):
        data = tomllib.loads(self.entry.meta_path.read_text(encoding="utf-8"))
        self.assertEqual(data["service"], "BCAD_Parcels")
        self.assertEqual(data["http_status"], 200)
        self.assertEqual(data["record_count"], 17)
        self.assertEqual(data["layer_id"], 0)

    def test_every_request_parameter_is_recorded(self):
        data = tomllib.loads(self.entry.meta_path.read_text(encoding="utf-8"))
        self.assertEqual(data["request_params"], PARAMS)
        self.assertEqual(data["request_url"], URL)

    def test_the_capture_time_carries_a_time_zone(self):
        data = tomllib.loads(self.entry.meta_path.read_text(encoding="utf-8"))
        self.assertIsNotNone(data["captured_at"].tzinfo if hasattr(data["captured_at"], "tzinfo") else None)

    def test_nothing_of_the_record_is_written_into_the_response(self):
        """The sentence 'this is real data the server really sent' is load-bearing."""
        self.assertNotIn(b"captured_at", self.entry.body_path.read_bytes())


class TestIndex(unittest.TestCase):
    def test_the_index_lists_one_line_per_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Cache(Path(tmp))
            for offset in ("0", "2000"):
                entry = cache.entry("BCAD_Parcels", "parcels", URL, dict(PARAMS, resultOffset=offset))
                cache.write(entry, b"{}", 200, layer_id=0, record_count=2000)
            index = cache.write_index("SH16")
            text = index.read_text(encoding="utf-8")
            self.assertIn("SH16", text)
            self.assertEqual(text.count("| BCAD_Parcels |"), 2)


class TestWarningsRecordedLater(unittest.TestCase):
    """Section 14 asks the record to carry any sanity check that tripped, and
    checks only run once a response is in hand."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Cache(Path(self.tmp.name))
        self.entry = self.cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
        self.cache.write(self.entry, b'{"features": []}', 200, layer_id=0, record_count=2000)

    def tearDown(self):
        self.tmp.cleanup()

    def read_back(self):
        return tomllib.loads(self.entry.meta_path.read_text(encoding="utf-8"))

    def test_a_check_that_tripped_lands_in_the_record(self):
        self.cache.add_warnings(self.entry, [{"check": "record count equals a paging cap"}])
        self.assertEqual(self.read_back()["warnings"], ["record count equals a paging cap"])

    def test_the_response_itself_is_still_not_touched(self):
        before = self.entry.body_path.read_bytes()
        self.cache.add_warnings(self.entry, [{"check": "something"}])
        self.assertEqual(self.entry.body_path.read_bytes(), before)

    def test_the_rest_of_the_record_survives_the_second_visit(self):
        self.cache.add_warnings(self.entry, [{"check": "something"}])
        data = self.read_back()
        self.assertEqual(data["record_count"], 2000)
        self.assertEqual(data["request_params"], PARAMS)
        self.assertEqual(data["http_status"], 200)

    def test_no_warnings_leaves_the_record_alone(self):
        self.cache.add_warnings(self.entry, [])
        self.assertEqual(self.read_back()["warnings"], [])


class TestReplayedFromCache(unittest.TestCase):
    def test_a_cached_response_can_still_say_how_old_it_is(self):
        """A run served from the cache that cannot say when its data was
        captured is a run nobody can judge."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = Cache(Path(tmp))
            first = cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
            cache.write(first, b"{}", 200, layer_id=0, record_count=5)
            again = cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
            captured = cache.captured_at_of(again)
            self.assertIsNotNone(captured)
            self.assertIn("T", captured)

    def test_a_check_tripping_on_replayed_data_is_still_written_down(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Cache(Path(tmp))
            first = cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
            cache.write(first, b"{}", 200, layer_id=0, record_count=5)
            again = cache.entry("BCAD_Parcels", "parcels", URL, PARAMS)
            cache.captured_at_of(again)
            cache.add_warnings(again, [{"check": "impossible acreage"}])
            data = tomllib.loads(again.meta_path.read_text(encoding="utf-8"))
            self.assertEqual(data["warnings"], ["impossible acreage"])
            self.assertEqual(data["request_params"], PARAMS)


class TestTomlWriter(unittest.TestCase):
    def test_quotes_and_backslashes_survive_the_round_trip(self):
        awkward = {"where": 'Situs LIKE \'%"quoted"%\' AND path = "C:\temp"'}
        data = tomllib.loads(render_toml(awkward))
        self.assertEqual(data["where"], awkward["where"])

    def test_a_newline_in_a_value_survives_the_round_trip(self):
        """A raw newline inside a quoted TOML string is a parse error, so a
        request parameter containing one would make its record unreadable."""
        awkward = {"where": "Situs LIKE '%A%'\nAND 1=1\tpadded"}
        data = tomllib.loads(render_toml(awkward))
        self.assertEqual(data["where"], awkward["where"])

    def test_lists_and_numbers_survive_the_round_trip(self):
        data = tomllib.loads(render_toml({"warnings": ["a", "b"], "count": 3, "ratio": 0.5, "ok": True}))
        self.assertEqual(data["warnings"], ["a", "b"])
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["ratio"], 0.5)
        self.assertTrue(data["ok"])



class TestTheIndexHeadingSurvivesACallerWithNothingToSay(unittest.TestCase):
    """A caller with no label, and a cache with no corridor, are not the same.

    ``INDEX.md`` carries the corridor in its heading, and specification section
    14 calls it "the file you point at when you say the captures are from a
    particular date." Two commands write it. The screening run knows the
    corridor; the live NGS check does not, and passed nothing.

    Nothing distinguished passing nothing from saying there is no corridor, so
    the live check blanked the heading. That really happened: the label went
    missing on 2026-09-13 and main carried a plain heading until 2026-09-19,
    six days and several reviews later, and it only came back because a
    screening run happened to rewrite it.

    **This is the same defect this repo has found three times.** A county road
    with no published right-of-way width is not a road with no right of way. A
    sheet with no drawing is not a sheet nobody can reach. Absent and unstated
    are different, and a default argument that conflates them is that bug in
    the cache writer. Fixed under
    [#186](https://github.com/RickSmith/survey-recon/issues/186).
    """

    CORRIDOR = "SH0016-KG DFO 347.7 to 356.367"

    def heading_of(self, index):
        return index.read_text(encoding="utf-8").splitlines()[0]

    def with_one_response(self, tmp):
        cache = Cache(Path(tmp))
        entry = cache.entry("NGS_Data_Explorer", "live-check-radial", URL, PARAMS)
        cache.write(entry, b"[]", 200, record_count=0)
        return cache

    def test_a_caller_with_no_label_keeps_the_heading_that_is_there(self):
        """The live check. It knows nothing about the corridor and asserts nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index(self.CORRIDOR)
            self.assertEqual(self.heading_of(cache.write_index()), f"# Cached responses -- {self.CORRIDOR}")

    def test_a_label_still_sets_the_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            index = cache.write_index(self.CORRIDOR)
            self.assertEqual(self.heading_of(index), f"# Cached responses -- {self.CORRIDOR}")

    def test_a_label_overwrites_a_different_one(self):
        """A cache folder rerun on another corridor is renamed, not appended to."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index("US0281-KG DFO 1 to 2")
            self.assertEqual(self.heading_of(cache.write_index(self.CORRIDOR)), f"# Cached responses -- {self.CORRIDOR}")

    def test_an_empty_label_means_there_is_no_corridor(self):
        """Said deliberately, which is a different thing from saying nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index(self.CORRIDOR)
            self.assertEqual(self.heading_of(cache.write_index("")), "# Cached responses")

    def test_a_cache_with_no_index_yet_gets_a_plain_heading(self):
        """Nothing to preserve, and this must not fail."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            self.assertEqual(self.heading_of(cache.write_index()), "# Cached responses")

    def test_an_index_whose_first_line_is_not_a_heading_is_not_carried_forward(self):
        """Junk in the file is not a corridor, and copying it on would spread it."""
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index(self.CORRIDOR)
            write_text(cache.root / "INDEX.md", "something else entirely\n\nrows\n")
            self.assertEqual(self.heading_of(cache.write_index()), "# Cached responses")

    def test_an_empty_index_file_is_not_carried_forward(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index(self.CORRIDOR)
            write_text(cache.root / "INDEX.md", "")
            self.assertEqual(self.heading_of(cache.write_index()), "# Cached responses")

    def test_preserving_a_heading_still_rewrites_the_rows(self):
        """Keeping the heading must not mean keeping a stale file.

        The whole reason the live check regenerates this at all is that writing
        a response without regenerating leaves the index wrong about it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            cache = self.with_one_response(tmp)
            cache.write_index(self.CORRIDOR)
            second = cache.entry("BCAD_Parcels", "parcels", URL, dict(PARAMS, resultOffset="2000"))
            cache.write(second, b"{}", 200, layer_id=0, record_count=2000)
            text = cache.write_index().read_text(encoding="utf-8")
            self.assertIn(self.CORRIDOR, text.splitlines()[0])
            self.assertIn("| BCAD_Parcels |", text)


if __name__ == "__main__":
    unittest.main()
