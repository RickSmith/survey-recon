"""Tests for cutting a TxDOT route down to two DFO limits.

The vertices here are shaped like the ones the service really returns:
``[longitude, latitude, measure]``, where the measure is DFO in miles.
"""

import unittest

from corridor_screen.alignment import (
    AlignmentError,
    clip_path_by_measure,
    from_route_features,
)

# A straight north-south run, one mile of DFO per tenth of a degree.
STRAIGHT = [
    [-98.6, 29.0, 100.0],
    [-98.6, 29.1, 101.0],
    [-98.6, 29.2, 102.0],
    [-98.6, 29.3, 103.0],
    [-98.6, 29.4, 104.0],
]


class TestClipping(unittest.TestCase):
    def test_a_window_inside_the_route_is_cut_at_both_ends(self):
        runs = clip_path_by_measure(STRAIGHT, 101.5, 102.5)
        self.assertEqual(len(runs), 1)
        self.assertAlmostEqual(runs[0][0][2], 101.5)
        self.assertAlmostEqual(runs[0][-1][2], 102.5)

    def test_the_cut_lands_between_the_vertices_it_falls_between(self):
        runs = clip_path_by_measure(STRAIGHT, 101.5, 102.0)
        self.assertAlmostEqual(runs[0][0][1], 29.15, places=6)

    def test_a_window_wider_than_the_route_returns_the_whole_route(self):
        runs = clip_path_by_measure(STRAIGHT, 0.0, 999.0)
        self.assertEqual(len(runs), 1)
        self.assertAlmostEqual(runs[0][0][2], 100.0)
        self.assertAlmostEqual(runs[0][-1][2], 104.0)

    def test_a_window_off_the_end_of_the_route_returns_nothing(self):
        self.assertEqual(clip_path_by_measure(STRAIGHT, 200.0, 300.0), [])

    def test_the_limits_may_be_given_in_either_order(self):
        forward = clip_path_by_measure(STRAIGHT, 101.0, 103.0)
        backward = clip_path_by_measure(STRAIGHT, 103.0, 101.0)
        self.assertEqual(forward, backward)

    def test_a_route_that_leaves_the_window_and_returns_gives_two_runs(self):
        """DFO can run backwards on a route that doubles back.

        Two runs must stay two runs. Joining them would invent centerline
        TxDOT never published, and the gap between them is real.
        """
        doubling = [
            [-98.6, 29.0, 100.0],
            [-98.6, 29.1, 101.0],
            [-98.6, 29.2, 105.0],
            [-98.6, 29.3, 106.0],
            [-98.6, 29.4, 101.0],
            [-98.6, 29.5, 100.0],
        ]
        runs = clip_path_by_measure(doubling, 100.0, 101.0)
        self.assertEqual(len(runs), 2)


def route_feature(path):
    return {"attributes": {"RTE_NM": "SH0016-KG"}, "geometry": {"paths": [path]}}


class TestBuildingAnAlignment(unittest.TestCase):
    def test_the_alignment_starts_at_the_lower_dfo(self):
        alignment = from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 103.0, 101.0)
        self.assertAlmostEqual(alignment.paths[0][0][2], 101.0)
        self.assertAlmostEqual(alignment.paths[-1][-1][2], 103.0)

    def test_a_route_returned_in_reverse_still_starts_at_the_lower_dfo(self):
        alignment = from_route_features(
            [route_feature(list(reversed(STRAIGHT)))], "SH0016-KG", 101.0, 103.0
        )
        self.assertAlmostEqual(alignment.paths[0][0][2], 101.0)
        self.assertAlmostEqual(alignment.paths[-1][-1][2], 103.0)

    def test_two_features_are_merged_and_counted(self):
        north = [[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]
        south = [[-98.6, 29.2, 102.0], [-98.6, 29.3, 103.0]]
        alignment = from_route_features(
            [route_feature(south), route_feature(north)], "SH0016-KG", 100.0, 103.0
        )
        self.assertEqual(alignment.feature_count, 2)
        self.assertEqual(len(alignment.paths), 2)
        self.assertAlmostEqual(alignment.paths[0][0][2], 100.0)

    def test_the_measure_is_dropped_before_the_geometry_is_sent_on(self):
        alignment = from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 101.0, 103.0)
        self.assertTrue(alignment.dropped_m)
        self.assertTrue(all(len(pt) == 2 for run in alignment.flat_paths for pt in run))

    def test_the_length_is_reported_for_the_wrong_file_check(self):
        alignment = from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 100.0, 104.0)
        self.assertAlmostEqual(alignment.length_mi, 27.6, delta=0.2)

    def test_limits_that_match_nothing_say_so_rather_than_returning_an_empty_corridor(self):
        with self.assertRaises(AlignmentError):
            from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 500.0, 501.0)

    def test_two_identical_limits_are_rejected(self):
        with self.assertRaises(AlignmentError):
            from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 101.0, 101.0)

    def test_geometry_without_measures_is_rejected_rather_than_guessed_at(self):
        flat = [[-98.6, 29.0], [-98.6, 29.1]]
        with self.assertRaises(AlignmentError):
            from_route_features([route_feature(flat)], "SH0016-KG", 100.0, 101.0)

    def test_the_description_carries_what_the_wrong_file_check_needs(self):
        alignment = from_route_features([route_feature(STRAIGHT)], "SH0016-KG", 101.0, 103.0)
        described = alignment.describe()
        for field in ("length_mi", "start", "end", "bbox", "source_kind", "crs_in"):
            self.assertIn(field, described)
        self.assertEqual(described["source_kind"], "route-dfo")


if __name__ == "__main__":
    unittest.main()
