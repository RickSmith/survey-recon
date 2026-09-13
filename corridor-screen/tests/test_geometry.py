"""Tests for the plane and sphere arithmetic."""

import unittest

from corridor_screen import geometry as g


class TestDistance(unittest.TestCase):
    def test_one_degree_of_latitude_is_about_sixty_nine_miles(self):
        d = g.haversine_miles([-98.6, 29.0], [-98.6, 30.0])
        self.assertAlmostEqual(d, 69.09, places=1)

    def test_the_same_point_is_no_distance_away(self):
        self.assertEqual(g.haversine_miles([-98.6, 29.5], [-98.6, 29.5]), 0.0)

    def test_a_path_adds_its_legs_up(self):
        path = [[-98.6, 29.0], [-98.6, 29.5], [-98.6, 30.0]]
        self.assertAlmostEqual(g.path_length_miles(path), 69.09, places=1)

    def test_a_gap_between_runs_is_not_measured(self):
        """A corridor with a break in it is legitimate. The break is not length."""
        near = [[-98.6, 29.0], [-98.6, 29.1]]
        far = [[-98.6, 35.0], [-98.6, 35.1]]
        both = g.paths_length_miles([near, far])
        self.assertAlmostEqual(both, 2 * g.path_length_miles(near), places=2)


class TestBoundingBox(unittest.TestCase):
    def test_corners_come_back_in_arcgis_order(self):
        paths = [[[-98.7, 29.4], [-98.5, 29.6]], [[-98.9, 29.2], [-98.6, 29.5]]]
        self.assertEqual(g.bbox_of(paths), [-98.9, 29.2, -98.5, 29.6])

    def test_no_vertices_is_an_error_rather_than_a_guess(self):
        with self.assertRaises(ValueError):
            g.bbox_of([])


SQUARE = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]


class TestPointInPolygon(unittest.TestCase):
    def test_a_point_in_the_middle_is_inside(self):
        self.assertTrue(g.point_in_ring([0.5, 0.5], SQUARE))

    def test_a_point_outside_is_outside(self):
        self.assertFalse(g.point_in_ring([1.5, 0.5], SQUARE))

    def test_a_hole_counts_as_outside(self):
        hole = [[0.4, 0.4], [0.4, 0.6], [0.6, 0.6], [0.6, 0.4]]
        self.assertFalse(g.point_in_rings([0.5, 0.5], [SQUARE, hole]))
        self.assertTrue(g.point_in_rings([0.1, 0.1], [SQUARE, hole]))


class TestArea(unittest.TestCase):
    def test_a_ring_smaller_than_three_vertices_has_no_area(self):
        self.assertEqual(g.ring_area_sq_miles([[0.0, 0.0], [1.0, 1.0]]), 0.0)

    def test_a_tenth_degree_square_near_bexar_is_about_forty_eight_square_miles(self):
        ring = [[-98.7, 29.5], [-98.7, 29.6], [-98.6, 29.6], [-98.6, 29.5]]
        self.assertAlmostEqual(g.ring_area_sq_miles(ring), 41.5, delta=1.5)

    def test_a_hole_comes_off_the_area(self):
        outer = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]
        hole = [[0.25, 0.25], [0.25, 0.75], [0.75, 0.75], [0.75, 0.25]]
        whole = g.ring_area_sq_miles(outer)
        self.assertAlmostEqual(g.polygon_area_sq_miles([outer, hole]), whole * 0.75, delta=whole * 0.01)

    def test_two_separate_rings_add_up_rather_than_cancel(self):
        """A buffer can come back in two pieces when the corridor has a break.

        Treating the second piece as a hole would report less area than the
        first piece alone, which is the kind of quiet wrong answer this repo
        exists to talk about.
        """
        left = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]
        right = [[5.0, 0.0], [5.0, 1.0], [6.0, 1.0], [6.0, 0.0]]
        expected = g.ring_area_sq_miles(left) + g.ring_area_sq_miles(right)
        self.assertAlmostEqual(g.polygon_area_sq_miles([left, right]), expected, delta=expected * 0.01)


if __name__ == "__main__":
    unittest.main()
