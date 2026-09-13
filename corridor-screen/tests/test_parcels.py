"""Tests for turning service records into parcel rows.

The attribute names here are the ones the CoSA BCAD service really publishes,
not the ones the specification lists. The difference is recorded at the top of
``corridor_screen/sources.py``.
"""

import unittest

from corridor_screen import parcels


def feature(**attributes):
    geometry = attributes.pop("geometry", {"rings": [[[0, 0], [0, 1], [1, 1], [1, 0]]]})
    return {"attributes": attributes, "geometry": geometry}


FULL = feature(
    Geo_id="05678-000-0010",
    PropID=112233,
    Owner_Name="SMITH RICK A",
    Situs="5309 BANDERA RD, LEON VALLEY, TX 78238",
    legal_desc="NCB 1234 BLK 2 LOT 5",
    legal_acre=2.5,
    state_cd="A1",
)


class TestOneRow(unittest.TestCase):
    def test_the_published_fields_come_through(self):
        row = parcels.to_row(FULL)
        self.assertEqual(row["id"], "05678-000-0010")
        self.assertEqual(row["owner"], "SMITH RICK A")
        self.assertEqual(row["legal_acres"], 2.5)
        self.assertEqual(row["property_use"], "A1")

    def test_the_identifier_says_which_field_it_came_from(self):
        self.assertEqual(parcels.to_row(FULL)["id_source"], "Geo_id")

    def test_a_missing_identifier_falls_back_before_it_invents_one(self):
        row = parcels.to_row(feature(Geo_id=None, PropID=112233))
        self.assertEqual(row["id"], "112233")
        self.assertEqual(row["id_source"], "PropID")

    def test_a_parcel_with_no_key_gets_one_made_from_its_shape_and_says_so(self):
        row = parcels.to_row(feature(Geo_id=None, PropID=None))
        self.assertEqual(row["id_source"], "synthetic")
        self.assertTrue(row["id"].startswith("synthetic-"))

    def test_the_same_shape_always_makes_the_same_synthetic_identifier(self):
        a = parcels.to_row(feature(Geo_id=None, PropID=None))
        b = parcels.to_row(feature(Geo_id=None, PropID=None))
        self.assertEqual(a["id"], b["id"])

    def test_a_blank_string_is_an_absent_value_not_an_empty_answer(self):
        row = parcels.to_row(feature(Geo_id="05678-000-0010", Situs="   ", Owner_Name=""))
        self.assertIsNone(row["situs"])
        self.assertIsNone(row["owner"])

    def test_right_of_entry_defaults_to_unknown_and_never_to_no(self):
        """One of those two words sends a crew to a locked gate."""
        self.assertEqual(parcels.to_row(FULL)["roe_required"], "unknown")

    def test_nothing_has_been_screened_for_yet_so_the_list_is_empty(self):
        self.assertEqual(parcels.to_row(FULL)["screened_for"], [])

    def test_the_lead_time_column_is_present_and_empty(self):
        row = parcels.to_row(FULL)
        self.assertIn("max_lead_time_days", row)
        self.assertIsNone(row["max_lead_time_days"])
        self.assertIsNone(row["lead_time_driver"])
        self.assertEqual(row["flags"], [])

    def test_the_columns_this_pass_cannot_fill_are_present_and_empty(self):
        row = parcels.to_row(FULL)
        for field in ("acres_in_corridor", "fraction_in_corridor", "txdot_owned"):
            self.assertIn(field, row)
            self.assertIsNone(row[field])

    def test_each_row_carries_its_own_warning_list(self):
        a = parcels.to_row(FULL)
        b = parcels.to_row(FULL)
        a["warnings"].append("something")
        self.assertEqual(b["warnings"], [])


class TestManyRows(unittest.TestCase):
    def test_a_parcel_crossed_twice_is_still_one_row(self):
        rows = parcels.to_rows([FULL, FULL])
        self.assertEqual(len(rows), 1)

    def test_different_parcels_stay_separate(self):
        other = feature(Geo_id="05678-000-0011")
        self.assertEqual(len(parcels.to_rows([FULL, other])), 2)


class TestCentroid(unittest.TestCase):
    def test_a_center_point_comes_back_in_longitude_latitude_order(self):
        with_centroid = dict(FULL, centroid={"x": -98.6, "y": 29.5})
        self.assertEqual(parcels.centroid_of(with_centroid), [-98.6, 29.5])

    def test_a_missing_center_point_is_nothing_to_check_rather_than_a_failure(self):
        self.assertIsNone(parcels.centroid_of(FULL))
        self.assertIsNone(parcels.centroid_of(dict(FULL, centroid={"x": None, "y": None})))


if __name__ == "__main__":
    unittest.main()
