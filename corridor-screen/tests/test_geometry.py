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


# A north-south centerline through Bexar County, and a plane fitted to it.
CENTERLINE = [[[-98.64, 29.50], [-98.64, 29.56]]]
PLANE = g.LocalPlane(29.53)
FOOT_MI = 1.0 / 5280.0


def box(west, south, east, north):
    return [[[west, south], [west, north], [east, north], [east, south]]]


class TestShapeNearALine(unittest.TestCase):
    def test_a_shape_the_line_runs_through_is_near_it(self):
        here = box(-98.65, 29.52, -98.63, 29.53)
        self.assertTrue(g.shape_is_within_miles(here, CENTERLINE, 10 * FOOT_MI, PLANE))

    def test_a_shape_across_the_county_is_not(self):
        away = box(-98.30, 29.20, -98.28, 29.22)
        self.assertFalse(g.shape_is_within_miles(away, CENTERLINE, 800 * FOOT_MI, PLANE))

    def test_a_long_edge_running_past_the_line_counts_with_no_corner_near_it(self):
        """A big tract can have a long fence line along the road with both of
        its corners a mile away. Testing corners alone would call that parcel
        far from the corridor."""
        long_tract = box(-98.6405, 29.40, -98.5000, 29.70)
        self.assertTrue(g.shape_is_within_miles(long_tract, CENTERLINE, 200 * FOOT_MI, PLANE))

    def test_a_shape_just_outside_the_limit_is_outside_it(self):
        far = box(-98.6430, 29.52, -98.6428, 29.53)
        self.assertFalse(g.shape_is_within_miles(far, CENTERLINE, 500 * FOOT_MI, PLANE))

    def test_the_same_shape_is_inside_a_wider_limit(self):
        far = box(-98.6430, 29.52, -98.6428, 29.53)
        self.assertTrue(g.shape_is_within_miles(far, CENTERLINE, 1200 * FOOT_MI, PLANE))

    def test_nothing_to_measure_is_not_a_failure(self):
        self.assertTrue(g.shape_is_within_miles([], CENTERLINE, FOOT_MI, PLANE))
        self.assertTrue(g.shape_is_within_miles(box(-98.64, 29.5, -98.63, 29.51), [], FOOT_MI, PLANE))


class TestLocalPlane(unittest.TestCase):
    def test_a_degree_of_latitude_is_about_sixty_nine_miles(self):
        plane = g.LocalPlane(29.5)
        _, y0 = plane.xy([-98.6, 29.0])
        _, y1 = plane.xy([-98.6, 30.0])
        self.assertAlmostEqual(y1 - y0, 69.06, places=1)

    def test_longitude_is_squeezed_by_latitude(self):
        plane = g.LocalPlane(29.5)
        x0, _ = plane.xy([-98.6, 29.5])
        x1, _ = plane.xy([-97.6, 29.5])
        self.assertAlmostEqual(x1 - x0, 60.2, places=0)


if __name__ == "__main__":
    unittest.main()
