"""Tests for the field list check and the sanity checks."""

import unittest

from corridor_screen import checks
from corridor_screen.geometry import LocalPlane
from corridor_screen.sources import Source

LAYER = Source(
    name="Made_Up_Service",
    base_url="https://example.invalid/FeatureServer",
    layer_id=0,
    purpose="parcels",
    required_fields=("Geo_id", "Situs"),
)


def metadata(*names):
    return {"fields": [{"name": n} for n in names]}


class TestFieldList(unittest.TestCase):
    def test_the_right_layer_passes(self):
        published = checks.confirm_fields(LAYER, metadata("Geo_id", "Situs", "Owner_Name"))
        self.assertIn("Geo_id", published)

    def test_a_missing_field_stops_the_run(self):
        with self.assertRaises(checks.FieldListError):
            checks.confirm_fields(LAYER, metadata("Geo_id"))

    def test_the_message_names_what_is_missing_and_what_is_there(self):
        with self.assertRaises(checks.FieldListError) as caught:
            checks.confirm_fields(LAYER, metadata("OBJECTID", "SomethingElse"))
        message = str(caught.exception)
        self.assertIn("Geo_id", message)
        self.assertIn("Situs", message)
        self.assertIn("SomethingElse", message)

    def test_the_message_teaches_the_layer_number_trap(self):
        """The wrong layer is the trap this whole check exists for."""
        with self.assertRaises(checks.FieldListError) as caught:
            checks.confirm_fields(LAYER, metadata("OBJECTID"))
        self.assertIn("67", str(caught.exception))
        self.assertIn("328", str(caught.exception))


class TestPagingCap(unittest.TestCase):
    def test_a_count_on_a_cap_is_doubted(self):
        self.assertIsNotNone(checks.check_paging_cap("BCAD_Parcels", 2000))

    def test_an_ordinary_count_is_not_doubted(self):
        self.assertIsNone(checks.check_paging_cap("BCAD_Parcels", 1873))

    def test_a_warning_never_claims_to_be_an_error(self):
        found = checks.check_paging_cap("BCAD_Parcels", 500)
        self.assertEqual(found["severity"], "warning")


class TestParcelDensity(unittest.TestCase):
    def test_a_plausible_corridor_passes(self):
        self.assertIsNone(checks.check_parcel_density("BCAD_Parcels", 900, 1.0))

    def test_a_county_worth_of_parcels_is_caught(self):
        """55,000 parcels in a one square mile ribbon is the bbox mistake."""
        found = checks.check_parcel_density("BCAD_Parcels", 55000, 1.0)
        self.assertIsNotNone(found)
        self.assertIn("55000", found["detail"])

    def test_no_corridor_area_means_no_opinion(self):
        self.assertIsNone(checks.check_parcel_density("BCAD_Parcels", 55000, 0.0))


# A north-south centerline through Bexar County.
CENTERLINE = [[[-98.64, 29.48], [-98.64, 29.58]]]
PLANE = LocalPlane(29.53)


def box(west, south, east, north):
    return [[[west, south], [west, north], [east, north], [east, south]]]


def near(service, shapes, margin_ft=500.0):
    return checks.check_shapes_near_corridor(service, shapes, CENTERLINE, 300.0, margin_ft, PLANE)


class TestNearTheCorridor(unittest.TestCase):
    def test_parcels_on_the_route_raise_nothing(self):
        shapes = [
            ("A", box(-98.641, 29.50, -98.639, 29.51)),
            ("B", box(-98.645, 29.55, -98.635, 29.56)),
        ]
        self.assertIsNone(near("x", shapes))

    def test_a_big_tract_clipped_by_the_ribbon_is_not_doubted(self):
        """Its center point is a quarter mile away; its frontage is on the road.
        This is the parcel that matters most to an estimate."""
        ranch = [("RANCH", box(-98.6402, 29.50, -98.6000, 29.54))]
        self.assertIsNone(near("x", ranch))

    def test_parcels_from_across_the_county_are_counted_and_named(self):
        shapes = [
            ("NEAR", box(-98.641, 29.50, -98.639, 29.51)),
            ("FAR1", box(-98.30, 29.20, -98.29, 29.21)),
            ("FAR2", box(-98.20, 29.90, -98.19, 29.91)),
        ]
        found = near("x", shapes)
        self.assertIn("2 of 3", found["detail"])
        self.assertIn("FAR1", found["detail"])

    def test_the_margin_is_what_decides_a_borderline_parcel(self):
        borderline = [("EDGE", box(-98.6430, 29.52, -98.6428, 29.53))]
        self.assertIsNotNone(near("x", borderline, margin_ft=100.0))
        self.assertIsNone(near("x", borderline, margin_ft=1500.0))

    def test_the_default_margin_is_five_hundred_feet(self):
        self.assertEqual(checks.DEFAULT_SANITY_MARGIN_FT, 500.0)

    def test_nothing_to_check_means_no_opinion(self):
        self.assertIsNone(near("x", []))
        self.assertIsNone(
            checks.check_shapes_near_corridor("x", [("A", box(0, 0, 1, 1))], [], 300.0, 500.0, PLANE)
        )


class TestAcreage(unittest.TestCase):
    def test_negative_acreage_is_caught(self):
        parcels = [{"id": "A", "legal_acres": 1.0}, {"id": "B", "legal_acres": -3.0}]
        found = checks.check_impossible_acres("BCAD_Parcels", parcels)
        self.assertIn("B", found["detail"])

    def test_a_missing_acreage_is_not_an_impossible_one(self):
        parcels = [{"id": "A", "legal_acres": None}]
        self.assertIsNone(checks.check_impossible_acres("BCAD_Parcels", parcels))


class TestCollect(unittest.TestCase):
    def test_checks_that_did_not_trip_are_dropped(self):
        found = checks.collect(None, checks.check_paging_cap("x", 500), None)
        self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
