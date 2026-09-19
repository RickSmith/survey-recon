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



class TestTheQueryAsksForWhatTheSourceDeclares(unittest.TestCase):
    """The alignment query and the source's field list must not drift apart.

    Written under [#180](https://github.com/RickSmith/survey-recon/issues/180),
    where TxDOT withdrew ``TxDOT_Roadways`` without notice and the replacement
    publishes the same three things under different names. The failure that
    would follow a half-finished swap is not a crash. ``confirm_fields`` passes,
    because it reads the source's own list, and then the query asks for columns
    the layer does not have and the service answers with nothing -- which reads
    as a route that does not reach the corridor.

    So the query is built from the same mapping the field check reads, and this
    is the test that says the two are the same mapping.
    """

    def test_the_query_names_every_field_the_source_requires(self):
        """Every required field is asked for. More than that is allowed.

        It used to be an exact match, because the query asked for exactly the
        three the alignment needs. Under
        [#183](https://github.com/RickSmith/survey-recon/issues/183) it also
        asks for the four the ``roadway`` block reports, which cost nothing on
        a query already being made. Those four are deliberately not required:
        a layer that stopped publishing them should cost that block and never
        stop a run.
        """
        from corridor_screen.cli import route_query
        from corridor_screen.sources import ROADWAYS

        asked = route_query("SH0016-KG", 347.7, 356.367)
        wanted = set(ROADWAYS.required_fields)
        self.assertLessEqual(wanted, set(asked["outFields"].split(",")))
        for field in wanted:
            self.assertIn(field, asked["where"])

    def test_the_window_is_the_two_limits_whichever_way_round_they_come(self):
        """``BEGIN_DFO <= the larger`` and ``END_DFO >= the smaller``.

        Swap those two and the query asks for the segments that miss the
        corridor rather than the ones that reach it.
        """
        from corridor_screen.cli import route_query
        from corridor_screen.sources import ROADWAY_FIELDS

        where = route_query("SH0016-KG", 347.7, 356.367)["where"]
        self.assertIn(f"{ROADWAY_FIELDS['begin_dfo']}<=356.367", where)
        self.assertIn(f"{ROADWAY_FIELDS['end_dfo']}>=347.7", where)

    def test_the_route_name_goes_in_as_given(self):
        from corridor_screen.cli import route_query
        from corridor_screen.sources import ROADWAY_FIELDS

        where = route_query("SH0016-KG", 347.7, 356.367)["where"]
        self.assertIn(f"{ROADWAY_FIELDS['route']}='SH0016-KG'", where)

    def test_the_measures_are_asked_for_because_the_cut_needs_them(self):
        """Without M there is no DFO on the vertices and nothing can be cut."""
        from corridor_screen.cli import route_query

        self.assertEqual(route_query("SH0016-KG", 347.7, 356.367)["returnM"], "true")


class TestASegmentedRouteIsStillOneAlignment(unittest.TestCase):
    """The replacement layer returns the corridor in pieces, not in one record.

    ``TxDOT_Roadways`` answered SH0016-KG with a single 1,800-vertex record.
    ``TxDOT_Roadway_Inventory`` answers the same corridor with forty, each a
    short inventory segment. Both describe the same centerline -- measured on
    2026-09-19, the largest gap between the two was 0.00 ft.

    So a run that treats many records as many corridors, or that keeps them in
    the order the service happened to send, would be wrong on the replacement
    and right on the original.
    """

    def test_segments_returned_out_of_order_come_back_in_dfo_order(self):
        later = route_feature([[-98.6, 29.2, 102.0], [-98.6, 29.3, 103.0]])
        earlier = route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]])
        middle = route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]])
        alignment = from_route_features([later, earlier, middle], "SH0016-KG", 100.0, 103.0)
        starts = [run[0][2] for run in alignment.paths]
        self.assertEqual(starts, sorted(starts))
        self.assertAlmostEqual(starts[0], 100.0)

    def test_every_segment_that_reaches_the_window_is_counted(self):
        features = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]),
            route_feature([[-98.6, 29.2, 102.0], [-98.6, 29.3, 103.0]]),
        ]
        alignment = from_route_features(features, "SH0016-KG", 100.0, 103.0)
        self.assertEqual(alignment.feature_count, 3)

    def test_a_segment_outside_the_window_is_left_out_rather_than_counted(self):
        inside = route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]])
        outside = route_feature([[-98.6, 29.8, 200.0], [-98.6, 29.9, 201.0]])
        alignment = from_route_features([inside, outside], "SH0016-KG", 100.0, 101.0)
        self.assertEqual(alignment.feature_count, 1)


class TestRunCountMeansBreaksInTheRoad(unittest.TestCase):
    """``run_count`` counts breaks in the centerline, not records in a response.

    This is the trap [#180](https://github.com/RickSmith/survey-recon/issues/180)
    left behind. ``TxDOT_Roadways`` answered a corridor with one record, so
    counting records and counting continuous stretches gave the same number and
    nobody had to choose. The layer that replaced it cuts the same road into
    forty inventory segments that touch end to end.

    Counted as records, the SH16 corridor reads as forty separate runs of road.
    It is one. The wrong-file check prints that number on the first screen a
    presenter reads aloud, and a corridor in forty pieces is a different claim
    about the ground from a corridor in one.

    A real gap is still a real gap. TxDOT publishes `SH0016-KG` with seven
    stretches that do not join, because a route can leave the state highway
    system and come back, and closing one would invent centerline TxDOT never
    published.
    """

    def test_segments_that_touch_end_to_end_are_one_run(self):
        features = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]),
            route_feature([[-98.6, 29.2, 102.0], [-98.6, 29.3, 103.0]]),
        ]
        alignment = from_route_features(features, "SH0016-KG", 100.0, 103.0)
        self.assertEqual(len(alignment.paths), 1)

    def test_every_segment_is_still_counted_as_a_feature(self):
        """``feature_count`` is how many records answered. That is a different number."""
        features = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]),
        ]
        alignment = from_route_features(features, "SH0016-KG", 100.0, 102.0)
        self.assertEqual(alignment.feature_count, 2)
        self.assertEqual(len(alignment.paths), 1)

    def test_a_real_gap_is_never_closed(self):
        """Joining across this one would invent centerline TxDOT never published."""
        features = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.4, 105.0], [-98.6, 29.5, 106.0]]),
        ]
        alignment = from_route_features(features, "SH0016-KG", 100.0, 106.0)
        self.assertEqual(len(alignment.paths), 2)

    def test_joining_does_not_repeat_the_shared_vertex(self):
        """The end of one segment and the start of the next are the same point."""
        features = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]),
        ]
        run = from_route_features(features, "SH0016-KG", 100.0, 102.0).paths[0]
        self.assertEqual([round(p[2], 3) for p in run], [100.0, 101.0, 102.0])

    def test_the_length_is_the_same_however_the_road_was_cut_up(self):
        """Forty segments of one road are as long as one record of it."""
        whole = [route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]])]
        pieces = [
            route_feature([[-98.6, 29.0, 100.0], [-98.6, 29.1, 101.0]]),
            route_feature([[-98.6, 29.1, 101.0], [-98.6, 29.2, 102.0]]),
        ]
        one = from_route_features(whole, "SH0016-KG", 100.0, 102.0)
        many = from_route_features(pieces, "SH0016-KG", 100.0, 102.0)
        self.assertAlmostEqual(one.length_mi, many.length_mi, places=9)
        self.assertEqual(len(one.paths), len(many.paths))


class TestTheTwoLimitsMayArriveEitherWayRound(unittest.TestCase):
    """``--begin-dfo`` and ``--end-dfo`` in either order, as the README promises.

    ``from_route_features`` has always sorted them. The query did not, so a
    reversed pair asked for segments starting before the lower limit and ending
    after the higher one. Nothing matches that, and no service errors on it: the
    run reports a route that does not reach the corridor.
    """

    def test_reversed_limits_ask_the_same_question_as_ordered_ones(self):
        from corridor_screen.cli import route_query

        self.assertEqual(
            route_query("SH0016-KG", 356.367, 347.7)["where"],
            route_query("SH0016-KG", 347.7, 356.367)["where"],
        )

    def test_the_window_opens_at_the_lower_limit_and_closes_at_the_higher(self):
        from corridor_screen.cli import route_query
        from corridor_screen.sources import ROADWAY_FIELDS

        where = route_query("SH0016-KG", 356.367, 347.7)["where"]
        self.assertIn(f"{ROADWAY_FIELDS['begin_dfo']}<=356.367", where)
        self.assertIn(f"{ROADWAY_FIELDS['end_dfo']}>=347.7", where)


class TestTheRoadwayFactsRideAlongOnTheSameQuery(unittest.TestCase):
    """Step 5 costs no request, and that is the whole design of it.

    Specification section 5 names "Roadway facts -- ROW_MIN, lanes, traffic" as
    a step of its own, and it used to name a service of its own too. The layer
    the run already asks for the alignment publishes all three, so the facts
    ride along on a query that was being made anyway.

    Under [#183](https://github.com/RickSmith/survey-recon/issues/183).
    """

    def test_the_fact_fields_are_asked_for(self):
        from corridor_screen.cli import route_query
        from corridor_screen.sources import ROADWAY_FACT_FIELDS

        asked = set(route_query("SH0016-KG", 347.7, 356.367)["outFields"].split(","))
        self.assertLessEqual(set(ROADWAY_FACT_FIELDS.values()), asked)

    def test_the_fact_fields_are_not_required(self):
        """A layer that stopped publishing them costs the block, not the run.

        The three alignment fields are the corridor: without them there is
        nothing to screen and the field list check must stop the run. A lane
        count is a fact about the road, and nothing else depends on it.
        """
        from corridor_screen.sources import ROADWAY_FACT_FIELDS, ROADWAYS

        required = set(ROADWAYS.required_fields)
        for field in ROADWAY_FACT_FIELDS.values():
            self.assertNotIn(field, required)

    def test_the_two_mappings_do_not_overlap(self):
        """One field in both lists would be required by accident."""
        from corridor_screen.sources import ROADWAY_FACT_FIELDS, ROADWAY_FIELDS

        self.assertEqual(
            set(ROADWAY_FIELDS.values()) & set(ROADWAY_FACT_FIELDS.values()), set()
        )

if __name__ == "__main__":
    unittest.main()
