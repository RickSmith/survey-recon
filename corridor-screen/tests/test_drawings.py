"""The drawings of the SH16 run, held to the run they are drawn from. Issue #154.

A drawing is the easiest place in this repo for a number to rot, because
nobody diffs a picture. So every number a drawing shows is read back out of
the SVG here and compared with the run that is supposed to have produced it:
the count of tracts, the count of flagged tracts, every PID on the control map,
every distance on the safety map, and the totals on the crew-day sheet.

Two other things this file settles:

* **The copies under ``docs/`` are the sources.** The site shows a copy of each
  drawing, and a copy that has drifted from its source is the site showing an
  older run than the one it describes. Byte-for-byte, no exceptions.
* **The module needs nothing installed.** ``CLAUDE.md``: git, a GitHub account
  and the Claude desktop app. A drawing module that quietly imported a plotting
  library would put a dependency in front of the one page a surveyor opens to
  see whether any of this is real.
"""

import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from corridor_screen import crew_day, drawings
from corridor_screen.cache import long_path

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "project-sh16"
SOURCES = DEMO / "drawings"
COPIES = REPO / "docs" / "scenarios" / "sh16" / "img"
MODULE = REPO / "corridor-screen" / "corridor_screen" / "drawings.py"

SVG = "{http://www.w3.org/2000/svg}"

# What the standard library is allowed to look like at the top of the module.
# Anything else imported at module level is a dependency, and the test says so
# by name rather than by failing to import.
STANDARD_LIBRARY = {
    "argparse", "json", "math", "os", "re", "sys", "pathlib", "xml.sax.saxutils",
}


def demo():
    return drawings.load(DEMO)


def parsed(text):
    return ElementTree.fromstring(text)


def with_class(root, name):
    return [e for e in root.iter() if e.get("class") == name]


def texts(root):
    return [(e.text or "") for e in root.iter(f"{SVG}text")]


class TestTheDrawingsAreDrawings(unittest.TestCase):
    """Each one parses, has a viewBox, and says which run it came from."""

    @classmethod
    def setUpClass(cls):
        cls.document, cls.capture = demo()
        cls.drawn = drawings.draw_all(cls.document, cls.capture)

    def test_every_drawing_is_named_and_every_name_is_drawn(self):
        """The count is not in the name, because the count has changed twice.

        This read `five` from #154 until #177 made it eight and #201 made it
        seven, and it was wrong for both of those. The assertion was always
        right -- it reads `NAMES` -- so only the label lied. A name that states
        a number has to be edited every time the number moves, and nothing
        fails when somebody forgets.
        """
        self.assertEqual(set(self.drawn), set(drawings.NAMES.values()))

    def test_every_drawing_is_well_formed_svg_with_a_viewbox(self):
        for name, content in self.drawn.items():
            with self.subTest(drawing=name):
                root = parsed(content)
                self.assertEqual(root.tag, f"{SVG}svg")
                self.assertEqual(root.get("viewBox"), f"0 0 {drawings.WIDTH} {drawings.HEIGHT}")

    def test_every_drawing_names_its_run(self):
        run_id = self.document["run"]["run_id"]
        for name, content in self.drawn.items():
            with self.subTest(drawing=name):
                self.assertIn(run_id, " ".join(texts(parsed(content))))

    def test_no_text_runs_off_the_page(self):
        """Estimated from the type size, which is close enough to catch a
        panel that has grown past the bottom or a line past the right edge --
        both of which the first draft of every one of these drawings did."""
        for name, content in self.drawn.items():
            root = parsed(content)
            for element in root.iter(f"{SVG}text"):
                x = float(element.get("x"))
                y = float(element.get("y"))
                size = float(element.get("font-size"))
                width = 0.52 * size * len(element.text or "")
                anchor = element.get("text-anchor", "start")
                left = x if anchor == "start" else x - width if anchor == "end" else x - width / 2
                with self.subTest(drawing=name, text=(element.text or "")[:40]):
                    self.assertLessEqual(left + width, drawings.WIDTH - 20)
                    self.assertGreaterEqual(left, 20)
                    self.assertLessEqual(y, drawings.HEIGHT - 8)


class TestTheCorridorMapShowsTheRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document, cls.capture = demo()
        cls.root = parsed(drawings.corridor_map(cls.document, cls.capture))

    def test_every_tract_the_run_counted_is_drawn_and_no_other(self):
        self.assertEqual(len(with_class(self.root, "parcel")), len(self.document["parcels"]))

    def test_the_flagged_tracts_are_picked_out(self):
        flagged = [p for p in self.document["parcels"] if p.get("flags")]
        self.assertEqual(len(with_class(self.root, "flagged")), len(flagged))
        self.assertEqual(len(with_class(self.root, "flag-number")), len(flagged))

    def test_the_flagged_list_names_every_flagged_tract(self):
        said = " ".join(texts(self.root))
        for parcel in self.document["parcels"]:
            if parcel.get("flags"):
                with self.subTest(parcel=parcel["id"]):
                    self.assertIn(parcel["id"], said)

    def test_the_places_that_raised_the_flags_are_drawn_once_each(self):
        places = {
            (f["source_service"], f["source_feature_id"])
            for p in self.document["parcels"] for f in p.get("flags", [])
        }
        self.assertEqual(len(with_class(self.root, "place")), len(places))

    def test_an_unmeasured_wait_says_not_found_rather_than_showing_a_number(self):
        """The parcel table's rule, on the map: seven of eight flagged tracts
        have no published wait, and a blank or a zero would read as clear."""
        said = texts(self.root)
        unmeasured = [p for p in self.document["parcels"]
                      if p.get("flags") and p.get("max_lead_time_days") is None]
        self.assertEqual(
            len([t for t in said if t.startswith("wait not found")]), len(unmeasured),
        )

    def test_both_ends_are_labeled_with_their_dfo(self):
        labels = [e.text for e in with_class(self.root, "end-label")]
        self.assertEqual(len(labels), 2)
        self.assertTrue(any("347.7" in label for label in labels))
        self.assertTrue(any("356.367" in label for label in labels))

    def test_the_scale_bar_is_a_measured_mile(self):
        """One mile on the frame is measured with the same haversine the run
        uses, not assumed to be 69 miles a degree."""
        frame = drawings.Frame(self.document["corridor"]["bbox"], (60, 150, 1000, 870))
        per_mile = frame.pixels_per_mile()
        self.assertGreater(per_mile, 50)
        self.assertLess(per_mile, 200)


class TestTheControlMapShowsTheRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document, cls.capture = demo()
        cls.root = parsed(drawings.control_map(cls.document, cls.capture))

    def test_every_ngs_mark_is_drawn_and_named(self):
        marks = self.document["control"]["ngs_marks"]
        self.assertEqual(len(with_class(self.root, "mark")), len(marks))
        said = " ".join(texts(self.root))
        for mark in marks:
            with self.subTest(pid=mark["pid"]):
                self.assertIn(mark["pid"], said)

    def test_every_mark_condition_is_written_out(self):
        """MARK NOT FOUND is the finding of the whole run. It is on the map
        once per mark and once in the subtitle, never summarized to a count."""
        marks = self.document["control"]["ngs_marks"]
        conditions = [t for t in texts(self.root) if t == "MARK NOT FOUND"]
        expected = len([m for m in marks if m.get("condition") == "MARK NOT FOUND"])
        self.assertEqual(len(conditions), expected)

    def test_distinct_txdot_monuments_are_drawn_once_each(self):
        points = self.document["control"]["txdot_points"]
        distinct = {p["station"] for p in points}
        self.assertEqual(len(with_class(self.root, "monument")), len(distinct))
        self.assertEqual(len(drawings.distinct_monuments(points)), len(distinct))


class TestTheSafetyMapShowsTheRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document, cls.capture = demo()
        cls.root = parsed(drawings.crew_safety_map(cls.document, cls.capture))

    def test_one_line_per_kind_of_place_found(self):
        found = drawings.nearest_places(self.document)
        self.assertEqual(len(with_class(self.root, "help-line")), len(found))
        self.assertEqual(len(with_class(self.root, "help-place")), len(found))

    def test_every_distance_on_a_line_is_the_run_s_own(self):
        """The distance written on each line is the shorter of the two end
        distances the run recorded, to the same two decimals."""
        found = drawings.nearest_places(self.document)
        on_lines = sorted(e.text for e in with_class(self.root, "help-distance"))
        expected = sorted(f"{p['end_miles']:.2f} mi" for p in found)
        self.assertEqual(on_lines, expected)

    def test_the_hospital_is_two_miles_from_one_end_and_eight_from_the_other(self):
        """The reason this map exists. A crew at the north end reading only the
        first number would be wrong by nearly six miles."""
        said = " ".join(texts(self.root))
        hospital = self.document["crew_safety"]["by_type"]["hospital"]["nearest"]
        self.assertIn(f"{hospital['distance_from_end_mi']:.2f} mi", said)
        self.assertIn(f"{hospital['distance_from_start_mi']:.2f} mi", said)

    def test_it_says_the_lines_are_straight(self):
        said = " ".join(texts(self.root)).lower()
        self.assertIn("straight line", said)


class TestTheDiagramCountsTheRun(unittest.TestCase):
    def test_every_service_is_listed_with_what_it_returned(self):
        document, capture = demo()
        root = parsed(drawings.how_it_works(document, capture))
        listed = [e.text for e in with_class(root, "service")]
        self.assertEqual(len(listed), len(document["services"]))
        for service in document["services"]:
            with self.subTest(service=service["name"]):
                self.assertTrue(any(
                    line.startswith(service["name"]) and str(service["record_count"]) in line
                    for line in listed
                ))


class TestTheSheetIsTheBuildUp(unittest.TestCase):
    """Every figure on the sheet is `crew_day`'s own. Nothing is retyped."""

    @classmethod
    def setUpClass(cls):
        cls.document, cls.capture = demo()
        cls.root = parsed(drawings.crew_day_sheet(cls.document, cls.capture))
        cls.rates = crew_day.load_rates()
        cls.lines = crew_day.lines(cls.document, cls.rates)

    def test_every_line_of_the_build_up_is_on_the_sheet(self):
        on_sheet = [e.text for e in with_class(self.root, "line")]
        self.assertEqual(on_sheet, [line["label"] for line in self.lines])

    def test_a_line_with_no_total_is_shown_as_having_no_total(self):
        blocked = [line for line in self.lines if line["hours"] is None]
        self.assertEqual(len(with_class(self.root, "blocked-line")), len(blocked))
        for element in with_class(self.root, "blocked-line"):
            self.assertIn(drawings.UNMEASURED, element.text)
            self.assertNotIn("0.00", element.text)

    def test_every_unmeasured_input_is_marked(self):
        inputs = crew_day.counts(self.document)
        unmeasured = [c for c in inputs if not c.get("measured")]
        self.assertEqual(len(with_class(self.root, "input")), len(inputs))
        self.assertEqual(len(with_class(self.root, "unmeasured-input")), len(unmeasured))

    def test_the_totals_are_the_build_up_s_totals(self):
        field_hours, _ = crew_day.hours_for("field", self.lines)
        office_hours, _ = crew_day.hours_for("office", self.lines)
        field_days = crew_day.days(field_hours, self.rates["field_hours_per_crew_day"].value)
        office_days = crew_day.days(office_hours, self.rates["office_hours_per_day"].value)
        field = with_class(self.root, "field-total")[0].text
        office = with_class(self.root, "office-total")[0].text
        self.assertIn(f"{field_hours:.2f} hours", field)
        self.assertIn(f"{field_days} crew-days", field)
        self.assertIn(f"{office_hours:.2f} hours", office)
        self.assertIn(f"{office_days} days", office)

    def test_the_floor_is_said_when_a_line_has_no_total(self):
        _, blocked = crew_day.hours_for("field", self.lines)
        if blocked:
            self.assertTrue(with_class(self.root, "floor"))


class TestTheCopiesAreTheSources(unittest.TestCase):
    """The site shows `docs/scenarios/sh16/img/`. It must be the run's drawing."""

    def test_every_drawing_has_a_committed_source_and_a_committed_copy(self):
        for name in drawings.NAMES.values():
            with self.subTest(drawing=name):
                self.assertTrue((SOURCES / name).is_file(), f"{SOURCES / name} is missing")
                self.assertTrue((COPIES / name).is_file(), f"{COPIES / name} is missing")

    def test_every_copy_is_byte_for_byte_its_source(self):
        for name in drawings.NAMES.values():
            with self.subTest(drawing=name):
                self.assertEqual(
                    (COPIES / name).read_bytes(), (SOURCES / name).read_bytes(),
                    f"{name}: the copy under docs/ is not the drawing in {SOURCES.name}/. "
                    "Re-run the drawings command with --copy-to.",
                )

    def test_the_committed_drawings_are_what_the_run_draws_today(self):
        """Re-drawing the committed run must reproduce the committed files.
        A drawing that changes without the run changing is a drawing that was
        edited by hand, or code that changed under it, and either way the copy
        in the repo no longer says what it claims."""
        document, capture = demo()
        for name, content in drawings.draw_all(document, capture).items():
            with self.subTest(drawing=name):
                self.assertEqual(
                    (SOURCES / name).read_text(encoding="utf-8"), content,
                    f"{name}: re-run the drawings command and commit the result",
                )


def a_copy_of_the_demo(folder):
    """The demo project's run and the cache entries the run names, in ``folder``.

    Only the named entries, and copied through ``long_path``: this repo's folder
    name is long enough that ``shutil.copytree`` cannot open half the cache on
    Windows, and the layer-metadata files it trips over are ones no drawing
    reads anyway.
    """
    out = Path(folder) / "project"
    out.mkdir()
    document = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
    (out / "screening.json").write_text(json.dumps(document), encoding="utf-8")
    named = [document["corridor"]["polygon_cache_key"]]
    for service in document["services"]:
        named += service.get("cache_files") or []
    for key in named:
        source = DEMO / "cache" / f"{key}.json"
        target = out / "cache" / f"{key}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(long_path(source), "rb") as reading:
            with open(long_path(target), "wb") as writing:
                writing.write(reading.read())
    return out


class TestTheCommand(unittest.TestCase):
    def test_it_writes_every_drawing_and_the_copies(self):
        with tempfile.TemporaryDirectory() as folder:
            out = a_copy_of_the_demo(folder)
            copies = Path(folder) / "site"
            self.assertEqual(drawings.main(["--out", str(out), "--copy-to", str(copies)]), 0)
            for name in drawings.NAMES.values():
                with self.subTest(drawing=name):
                    self.assertTrue((out / "drawings" / name).is_file())
                    self.assertTrue((copies / name).is_file())

    def test_a_run_without_its_cache_says_so_rather_than_drawing_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / "screening.json").write_text(
                (DEMO / "screening.json").read_text(encoding="utf-8"), encoding="utf-8",
            )
            self.assertEqual(drawings.main(["--out", str(out)]), 1)


class TestNothingIsInstalled(unittest.TestCase):
    def test_the_module_imports_only_the_standard_library_and_itself(self):
        source = MODULE.read_text(encoding="utf-8")
        for found in re.finditer(r"^(?:import|from)\s+([\w.]+)", source, flags=re.MULTILINE):
            name = found.group(1)
            with self.subTest(module=name):
                self.assertTrue(
                    name.startswith(".") or name in STANDARD_LIBRARY,
                    f"{name} is not the standard library, and CLAUDE.md says attendees "
                    "install nothing",
                )


if __name__ == "__main__":
    unittest.main()


class TestTheCenterlineIsReadFromTheNamedSource(unittest.TestCase):
    """The drawing asks the capture for the service ``sources`` names.

    This file used to spell `TxDOT_Roadways` itself. TxDOT withdrew that
    service on 2026-09-19 and the run moved to a differently named layer under
    [#180](https://github.com/RickSmith/survey-recon/issues/180). The run then
    worked and the drawings did not, because a second copy of a service name is
    a second place to forget.

    It forgets quietly, too. Nothing is drawn wrong: the command stops with
    "the run has no cached response", long after the run that could have said
    so and in a different command than the one anybody was watching.
    """

    class AskedCapture:
        """A capture that records which service it was asked for."""

        def __init__(self):
            self.asked = []

        def features(self, name):
            self.asked.append(name)
            return []

    def test_it_asks_for_the_service_the_sources_module_names(self):
        from corridor_screen.sources import ROADWAYS

        capture = self.AskedCapture()
        document = {"alignment": {"source_path": "SH0016-KG DFO 347.7 to 356.367"}}
        with self.assertRaises(drawings.DrawingError):
            drawings.centerline(document, capture)
        self.assertEqual(capture.asked, [ROADWAYS.name])

    def test_the_error_names_the_service_it_actually_looked_for(self):
        """A message naming a service the run never called sends the reader nowhere."""
        from corridor_screen.sources import ROADWAYS

        document = {"alignment": {"source_path": "SH0016-KG DFO 347.7 to 356.367"}}
        with self.assertRaises(drawings.DrawingError) as caught:
            drawings.centerline(document, self.AskedCapture())
        self.assertIn(ROADWAYS.name, str(caught.exception))
