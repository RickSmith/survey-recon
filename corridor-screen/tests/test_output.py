"""Tests for the one file a screening run produces."""

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from corridor_screen import output
from corridor_screen.alignment import from_route_features
from corridor_screen.corridor import Corridor
from corridor_screen.sources import PARCELS

STRAIGHT = [[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]
RING = [[-98.7, 29.0], [-98.7, 29.2], [-98.5, 29.2], [-98.5, 29.0]]


def a_document(status="complete", parcels=()):
    alignment = from_route_features(
        [{"attributes": {}, "geometry": {"paths": [STRAIGHT]}}], "SH0016-KG", 100.0, 102.0
    )
    corridor = Corridor([RING], 300, "arcgis-geometry/buffer__abc123")
    return output.build(
        run_id="texas-bexar-test",
        started_at=datetime.now(timezone.utc).astimezone(),
        mode="cache-first",
        half_width_ft=300,
        adjacent_distance_ft=100,
        tool_version="0.1.0",
        alignment=alignment,
        corridor=corridor,
        services=[],
        parcel_rows=list(parcels),
        warnings=[],
        status=status,
        stopped_at_service=None if status == "complete" else "BCAD_Parcels",
    )


class TestShape(unittest.TestCase):
    def test_every_block_the_specification_names_is_present(self):
        document = a_document()
        for block in (
            "schema_version", "run", "alignment", "corridor", "roadway",
            "services", "control", "row_maps", "parcels", "corridor_flags", "warnings",
        ):
            self.assertIn(block, document)

    def test_blocks_this_pass_does_not_fill_say_so_rather_than_being_absent(self):
        document = a_document()
        for block in ("roadway", "control", "row_maps"):
            self.assertEqual(document[block]["status"], "not-screened")
            self.assertTrue(document[block]["detail"])

    def test_the_two_things_no_public_source_publishes_are_always_named(self):
        types = {item["type"] for item in a_document()["run"]["not_screenable"]}
        self.assertEqual(types, {"gated access", "livestock"})

    def test_the_run_block_carries_the_two_stated_distances(self):
        run = a_document()["run"]
        self.assertEqual(run["half_width_ft"], 300)
        self.assertEqual(run["adjacent_distance_ft"], 100)

    def test_the_map_link_points_at_the_middle_of_the_corridor(self):
        link = a_document()["run"]["map_link"]
        self.assertIn("29.1", link)
        self.assertIn("-98.6", link)


class TestHonestyBlock(unittest.TestCase):
    def test_a_service_entry_records_what_was_asked_and_of_what(self):
        entry = output.service_entry(
            PARCELS,
            {"ping": "ok", "ms": 210, "detail": ""},
            "ok",
            [{"cache_key": "bcad/parcels__abc", "attempts": 1}],
            530,
        )
        self.assertEqual(entry["layer_id"], 0)
        self.assertEqual(entry["record_count"], 530)
        self.assertEqual(entry["cache_files"], ["bcad/parcels__abc"])
        self.assertIn("BCAD_Parcels", entry["url"])

    def test_a_skipped_service_says_why_rather_than_being_left_out(self):
        entry = output.skipped_service(PARCELS, "the run stopped first")
        self.assertEqual(entry["status"], "skipped")
        self.assertEqual(entry["warnings"], ["the run stopped first"])


class TestWriting(unittest.TestCase):
    def test_a_complete_run_writes_the_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = output.write(a_document(), tmp)
            self.assertEqual(path.name, "screening.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["run"]["status"], "complete")

    def test_a_stopped_run_does_not_overwrite_the_last_good_output(self):
        """A blocked host on the morning of a session must not destroy a capture
        that already worked."""
        with tempfile.TemporaryDirectory() as tmp:
            good = output.write(a_document(parcels=[{"id": "A"}]), tmp)
            bad = output.write(a_document(status="incomplete"), tmp)
            self.assertNotEqual(good, bad)
            self.assertEqual(bad.name, "screening.incomplete.json")
            still_there = json.loads(Path(good).read_text(encoding="utf-8"))
            self.assertEqual(len(still_there["parcels"]), 1)

    def test_a_stopped_run_names_what_stopped_it(self):
        document = a_document(status="incomplete")
        self.assertEqual(document["run"]["stopped_at_service"], "BCAD_Parcels")


if __name__ == "__main__":
    unittest.main()
