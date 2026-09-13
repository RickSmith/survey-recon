"""Tests for saved responses and their provenance records."""

import tempfile
import tomllib
import unittest
from pathlib import Path

from corridor_screen.cache import Cache, render_toml

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


class TestTomlWriter(unittest.TestCase):
    def test_quotes_and_backslashes_survive_the_round_trip(self):
        awkward = {"where": 'Situs LIKE \'%"quoted"%\' AND path = "C:\temp"'}
        data = tomllib.loads(render_toml(awkward))
        self.assertEqual(data["where"], awkward["where"])

    def test_lists_and_numbers_survive_the_round_trip(self):
        data = tomllib.loads(render_toml({"warnings": ["a", "b"], "count": 3, "ratio": 0.5, "ok": True}))
        self.assertEqual(data["warnings"], ["a", "b"])
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["ratio"], 0.5)
        self.assertTrue(data["ok"])


if __name__ == "__main__":
    unittest.main()
