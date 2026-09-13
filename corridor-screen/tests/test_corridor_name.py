"""The corridor is named in one place, and the name that was wrong stays gone.

Issue #99. Until 2026-09-13 thirteen files in this repo called the north end of
the worked example **Gibeaut Rd**. No such road exists in Bexar County. The name
was invented during the grilling on 12 September, copied everywhere, and never
checked against a map until Rick read it off a slide.

**This file cannot check that a place name is real.** Doing that needs a map
service, and the suite runs with no network -- deliberately, because it is the
one thing in this repo that proves the rest of it works. So it checks the two
things that can be checked offline, and they are the two that would actually
catch a repeat.

**The old name does not come back.** A find-and-replace across thirteen files is
easy to do once and easy to half-undo later, and the half that survives is on a
projector in front of people who know Bexar County.

**The corridor is defined once.** `CONTEXT.md` carries the DFO pair, and the DFO
pair is what the corridor *is* -- two road names are a label for it. A page that
restates the limits rather than pointing at that row is a page that can drift.

The two files that still carry the old name are a verbatim transcript and a
verbatim quotation from a Texas RPLS. Both are records of what somebody typed
or said, and a record that gets quietly corrected is not a record. Each carries
a note beside it saying the name is wrong, and this file checks the note is
there rather than checking the name is gone.
"""

import re
import unittest
from pathlib import Path

from corridor_screen.cache import long_path

REPO = Path(__file__).resolve().parent.parent.parent

# The name that was never real. Searched for case-insensitively, because the
# way it comes back is somebody retyping it from memory.
GONE = "gibeaut"

# **Using the old name, not mentioning it.** The first draft of this check
# forbade the bare word and immediately failed four files -- `CONTEXT.md`, the
# grilling README, this file, and the deck -- three of which exist to *explain*
# that the name is wrong. A rule that cannot tell a correction from a mistake
# gets switched off.
#
# So what is forbidden is the name used as the corridor's limit: "Loop 410 to
# Gibeaut", "Loop 410 → Gibeaut". That is the shape it had in all thirteen
# files, and it is the shape somebody retyping from memory would produce.
IN_USE = re.compile(r"Loop\s*410\s*(?:to|→|-+>)\s*Gibeaut", re.I)

# The two places the old name is allowed to survive, and why. Both are verbatim
# records -- a transcript of what was typed, and a quotation of what a Texas
# RPLS said. The value is the file that must carry the correction beside it, so
# a reader of the record learns the name is wrong without leaving the page.
KEPT = {
    Path("corridor-screen/captures/the-grilling/the-grilling.md"):
        Path("corridor-screen/captures/the-grilling/README.md"),
    Path("docs/plan-of-record.md"): Path("docs/plan-of-record.md"),
}

# Files that may carry the used form without being a record of it, because
# their subject *is* the mistake. Listed one by one rather than matched by a
# pattern: an exemption that can be earned by accident is not an exemption.
EXPLAINING_IT = {
    # Quotes the transcript's own line in order to say it is wrong.
    Path("corridor-screen/captures/the-grilling/README.md"),
    # This file. The examples below prove the check can still fire.
    Path("corridor-screen/tests/test_corridor_name.py"),
}

# Where the corridor is defined. Everything else agrees with this rather than
# restating it.
CONTEXT = REPO / "CONTEXT.md"

# The limits themselves. These are the corridor; the road names are a label.
BEGIN_DFO, END_DFO, MILES = "347.7", "356.367", "8.691"

# Folders that are not this repo's prose.
SKIP = {".git", "site", "node_modules", "__pycache__", ".claude", "_slides"}

READABLE = (".md", ".py", ".toml", ".yml", ".yaml")


def text_of(path):
    with open(long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def repo_files():
    for path in REPO.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in READABLE:
            continue
        if any(part in SKIP for part in path.relative_to(REPO).parts):
            continue
        yield path


class TestTheNameThatWasNeverRealStaysGone(unittest.TestCase):

    def test_no_file_outside_the_two_records_uses_it_as_the_corridor(self):
        allowed = {(REPO / p).resolve() for p in (*KEPT, *EXPLAINING_IT)}
        offenders = []
        for path in repo_files():
            if path.resolve() in allowed:
                continue
            if IN_USE.search(text_of(path)):
                offenders.append(str(path.relative_to(REPO)))
        self.assertEqual(
            offenders, [],
            "these files name a road that does not exist in Bexar County. The "
            "corridor's north end is Old Bandera Rd, in Old Town Helotes -- see "
            "CONTEXT.md. Only a verbatim record may keep the old name, and then "
            "only with a note beside it:\n  " + "\n  ".join(offenders),
        )

    def test_the_check_would_notice_the_name_coming_back(self):
        """A rule that can never fire is a comment, not a check."""
        for shape in ("Loop 410 to Gibeaut Rd",
                      "Loop 410 → Gibeaut Rd",
                      "loop 410 to gibeaut road"):
            with self.subTest(shape=shape):
                self.assertTrue(IN_USE.search(shape))

    def test_the_check_lets_a_correction_through(self):
        """Three files in this repo exist to say the name was wrong. A check
        that cannot tell a correction from a mistake gets switched off."""
        for shape in ("There is no Gibeaut Rd in Bexar County",
                      "Until 2026-09-13 every page called it Gibeaut Rd",
                      "Loop 410 to Old Bandera Rd"):
            with self.subTest(shape=shape):
                self.assertIsNone(IN_USE.search(shape))

    def test_each_record_that_keeps_it_says_beside_it_that_it_is_wrong(self):
        """A record left uncorrected and unannotated just reads as a mistake."""
        for record, annotation in KEPT.items():
            with self.subTest(record=str(record)):
                said = text_of(REPO / annotation).lower()
                self.assertIn(
                    "old bandera rd", said,
                    f"{record} keeps the old name and {annotation} does not say "
                    f"what the corridor is actually called",
                )
                self.assertIn(
                    "no such road", said.replace("there is no gibeaut rd", "no such road"),
                    f"{annotation} does not say plainly that the old name names "
                    f"nothing",
                )

    def test_the_two_records_really_do_still_carry_it(self):
        """Otherwise this file is guarding something that is not there any more,
        and the exemptions above quietly become dead weight."""
        for record in KEPT:
            with self.subTest(record=str(record)):
                self.assertIn(GONE, text_of(REPO / record).lower())


class TestTheCorridorIsDefinedInOnePlace(unittest.TestCase):
    """`CONTEXT.md` is the row every other page agrees with."""

    def test_context_carries_the_limits_rather_than_only_the_road_names(self):
        said = text_of(CONTEXT)
        for number in (BEGIN_DFO, END_DFO, MILES):
            with self.subTest(number=number):
                self.assertIn(number, said)

    def test_context_names_the_new_end_point(self):
        self.assertIn("Old Bandera Rd", text_of(CONTEXT))

    def test_context_says_where_the_new_name_was_checked(self):
        """A place name is a claim like any other. This one rests on
        OpenStreetMap rather than on TxDOT's own roadway inventory, which the
        SH16 run does not call -- and that is worth a reader knowing."""
        said = text_of(CONTEXT).lower()
        self.assertIn("nominatim", said)
        self.assertIn("overpass", said)

    def test_context_says_the_corridor_did_not_move(self):
        """The whole risk of a rename is somebody later assuming the figures
        moved with it. They did not, and the page says so."""
        said = text_of(CONTEXT).lower()
        self.assertTrue(
            "never moved" in said or "did not move" in said,
            "CONTEXT.md renames the end point without saying the limits are "
            "unchanged. Somebody will assume Act II's figures moved too.",
        )


class TestNoPageRestatesTheLimitsWithoutThem(unittest.TestCase):
    """A page may name the corridor. A page that states its *limits* has to
    state them correctly, because a second copy of a number is a number that
    drifts."""

    A_DFO_PAIR = re.compile(r"347\.7\D{1,12}356\.\d+")

    def test_every_page_stating_the_dfo_pair_states_the_committed_one(self):
        for path in repo_files():
            said = text_of(path)
            for found in self.A_DFO_PAIR.finditer(said):
                with self.subTest(path=str(path.relative_to(REPO))):
                    self.assertIn(
                        END_DFO, found.group(0),
                        f"{path.relative_to(REPO)} states a DFO pair that is not "
                        f"the committed run's {BEGIN_DFO} to {END_DFO}",
                    )


if __name__ == "__main__":
    unittest.main()
