"""Tests for measuring how far a flag is from a parcel.

Everything a flag does rests on four distances, and each of them answers the
same question in a different shape: how far is this feature from this parcel?
Zero means the feature is on the parcel. A small number means adjacent. A big
number means it belongs to neither.

The shapes are in a plain square near Bexar County so the numbers can be
checked by hand. At that latitude a degree of longitude is about 60.2 miles and
a degree of latitude about 69.1, which is where the expected figures come from.
"""

import unittest

from corridor_screen import geometry as g

# A square about a tenth of a degree on a side, sitting on Bandera Road.
PARCEL = [[-98.66, 29.54], [-98.66, 29.55], [-98.65, 29.55], [-98.65, 29.54]]
PLANE = g.LocalPlane(29.545)

MILES_PER_DEG_LON = 60.2  # near enough at this latitude to check by hand


class TestPointToRings(unittest.TestCase):
    def test_a_point_inside_the_parcel_is_no_distance_away(self):
        self.assertEqual(g.point_to_rings_miles([-98.655, 29.545], [PARCEL], PLANE), 0.0)

    def test_a_point_on_the_edge_is_no_distance_away(self):
        self.assertAlmostEqual(g.point_to_rings_miles([-98.66, 29.545], [PARCEL], PLANE), 0.0, places=6)

    def test_a_point_outside_is_measured_to_the_nearest_edge(self):
        # A hundredth of a degree of longitude west of the western edge.
        got = g.point_to_rings_miles([-98.67, 29.545], [PARCEL], PLANE)
        self.assertAlmostEqual(got, 0.01 * MILES_PER_DEG_LON, delta=0.01)

    def test_a_point_in_a_hole_is_outside_the_parcel(self):
        """A hole is not the parcel. A well inside a doughnut is not on it."""
        hole = [[-98.657, 29.544], [-98.657, 29.546], [-98.653, 29.546], [-98.653, 29.544]]
        self.assertGreater(g.point_to_rings_miles([-98.655, 29.545], [PARCEL, hole], PLANE), 0.0)

    def test_a_parcel_with_no_shape_cannot_be_measured(self):
        self.assertIsNone(g.point_to_rings_miles([-98.655, 29.545], [], PLANE))


class TestPathsToRings(unittest.TestCase):
    def test_a_line_crossing_the_parcel_is_no_distance_away(self):
        crossing = [[[-98.67, 29.545], [-98.64, 29.545]]]
        self.assertEqual(g.paths_to_rings_miles(crossing, [PARCEL], PLANE), 0.0)

    def test_a_line_ending_inside_the_parcel_is_no_distance_away(self):
        stops_inside = [[[-98.67, 29.545], [-98.655, 29.545]]]
        self.assertEqual(g.paths_to_rings_miles(stops_inside, [PARCEL], PLANE), 0.0)

    def test_a_line_running_past_the_parcel_is_measured_to_it(self):
        alongside = [[[-98.67, 29.53], [-98.67, 29.56]]]
        got = g.paths_to_rings_miles(alongside, [PARCEL], PLANE)
        self.assertAlmostEqual(got, 0.01 * MILES_PER_DEG_LON, delta=0.01)

    def test_a_line_that_passes_over_the_parcel_without_a_vertex_inside_still_counts(self):
        """The trap this replaces: testing vertices only.

        A railroad drawn with a vertex either side of a city lot has no vertex
        inside it, and a check that only looked at vertices would call the lot
        clear while the track ran straight through the back yard.
        """
        over = [[[-98.70, 29.545], [-98.60, 29.545]]]
        self.assertEqual(g.paths_to_rings_miles(over, [PARCEL], PLANE), 0.0)


class TestPointToPaths(unittest.TestCase):
    def test_a_point_on_the_line_is_no_distance_away(self):
        line = [[[-98.67, 29.545], [-98.64, 29.545]]]
        self.assertAlmostEqual(g.point_to_paths_miles([-98.655, 29.545], line, PLANE), 0.0, places=6)

    def test_a_point_beside_the_line_is_measured_square_to_it(self):
        line = [[[-98.67, 29.545], [-98.64, 29.545]]]
        got = g.point_to_paths_miles([-98.655, 29.555], line, PLANE)
        self.assertAlmostEqual(got, 0.01 * g.LocalPlane.MILES_PER_DEGREE_LAT, delta=0.01)

    def test_a_point_past_the_end_is_measured_to_the_end(self):
        """Clamped to the segment. Otherwise a short line measures as if infinite."""
        line = [[[-98.67, 29.545], [-98.66, 29.545]]]
        got = g.point_to_paths_miles([-98.65, 29.545], line, PLANE)
        self.assertAlmostEqual(got, 0.01 * MILES_PER_DEG_LON, delta=0.01)


class TestPathsToPaths(unittest.TestCase):
    def test_two_lines_that_cross_are_no_distance_apart(self):
        a = [[[-98.67, 29.545], [-98.64, 29.545]]]
        b = [[[-98.655, 29.53], [-98.655, 29.56]]]
        self.assertEqual(g.paths_to_paths_miles(a, b, PLANE), 0.0)

    def test_two_parallel_lines_are_measured_apart(self):
        a = [[[-98.67, 29.545], [-98.64, 29.545]]]
        b = [[[-98.67, 29.555], [-98.64, 29.555]]]
        got = g.paths_to_paths_miles(a, b, PLANE)
        self.assertAlmostEqual(got, 0.01 * g.LocalPlane.MILES_PER_DEGREE_LAT, delta=0.01)

    def test_nothing_to_measure_gives_nothing_rather_than_zero(self):
        """Zero would read as "touching", which is the opposite of the truth."""
        self.assertIsNone(g.paths_to_paths_miles([], [[[-98.6, 29.5], [-98.6, 29.6]]], PLANE))


class TestFeatureShape(unittest.TestCase):
    """ArcGIS draws a point, a line and a polygon three different ways."""

    def test_a_point_feature(self):
        self.assertEqual(g.shape_of({"x": -98.66, "y": 29.54}), ("point", [-98.66, 29.54]))

    def test_a_line_feature(self):
        paths = [[[-98.66, 29.54], [-98.65, 29.55]]]
        self.assertEqual(g.shape_of({"paths": paths}), ("paths", paths))

    def test_a_polygon_feature(self):
        self.assertEqual(g.shape_of({"rings": [PARCEL]}), ("rings", [PARCEL]))

    def test_no_geometry_at_all(self):
        self.assertEqual(g.shape_of({}), (None, None))
        self.assertEqual(g.shape_of(None), (None, None))


class TestDistanceBetweenShapes(unittest.TestCase):
    """One door, so a flag does not have to know what shape it is."""

    def test_a_point_against_a_parcel(self):
        got = g.shape_to_rings_miles(("point", [-98.655, 29.545]), [PARCEL], PLANE)
        self.assertEqual(got, 0.0)

    def test_a_line_against_a_parcel(self):
        got = g.shape_to_rings_miles(("paths", [[[-98.67, 29.545], [-98.64, 29.545]]]), [PARCEL], PLANE)
        self.assertEqual(got, 0.0)

    def test_a_polygon_against_a_parcel_uses_its_outline(self):
        overlapping = [[-98.655, 29.545], [-98.655, 29.56], [-98.64, 29.56], [-98.64, 29.545]]
        got = g.shape_to_rings_miles(("rings", [overlapping]), [PARCEL], PLANE)
        self.assertEqual(got, 0.0)

    def test_a_shape_that_is_not_there_cannot_be_measured(self):
        self.assertIsNone(g.shape_to_rings_miles((None, None), [PARCEL], PLANE))


if __name__ == "__main__":
    unittest.main()
