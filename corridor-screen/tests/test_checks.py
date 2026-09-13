"""Tests for the field list check and the sanity checks."""

import unittest

from corridor_screen import checks
from corridor_screen.geometry import grow_bbox, point_in_bbox
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


# A ribbon through Bexar County, roughly the extent of the SH16 corridor.
CORRIDOR_BBOX = [-98.69, 29.48, -98.60, 29.58]


def near(service, points):
    return checks.check_centroids_near_corridor(service, points, CORRIDOR_BBOX, grow_bbox, point_in_bbox)


class TestNearTheCorridor(unittest.TestCase):
    def test_points_inside_raise_nothing(self):
        self.assertIsNone(near("x", [[-98.64, 29.52], [-98.62, 29.55]]))

    def test_a_large_tract_whose_center_sits_just_outside_is_not_doubted(self):
        """A 189-acre tract clipped by a 600-foot ribbon is genuinely in the
        corridor while its center point is a quarter mile outside it."""
        self.assertIsNone(near("x", [[-98.695, 29.47]]))

    def test_records_from_across_the_county_are_counted(self):
        mixed = [[-98.64, 29.52], [-98.30, 29.30], [-98.25, 29.90]]
        found = near("x", mixed)
        self.assertIn("2 of 3", found["detail"])

    def test_nothing_to_check_means_no_opinion(self):
        self.assertIsNone(near("x", []))
        self.assertIsNone(checks.check_centroids_near_corridor("x", [[0.0, 0.0]], None, grow_bbox, point_in_bbox))


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
