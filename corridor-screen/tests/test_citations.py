"""Tests for failure beat one -- the superseded manual.

This file holds superseded-url-evidence: the legacy URLs below are fixtures for
the guard, not citations, and `citations.EVIDENCE_MARKER` is how the guard is
told so in a way a reader can see in the diff.

Issue #25 asks for a failure that "reproduces on demand, every time" and
"reproduces from cache, so it never depends on the network." Those two
sentences are the whole design. A beat that needs the internet is a beat that
can be taken away from you by the venue Wi-Fi, in front of the room, at 1:36.

So the evidence is captured into `corridor-screen/captures/superseded-manual/`
and committed, and everything here reads those files rather than a host.

**What the beat actually is.** Search still hands out
`onlinemanuals.txdot.gov` links for the TxDOT Survey Manual. That host still
resolves in DNS today and answers nothing at all. The manual moved to
`txdot.gov/manuals/row/ess/`, and the two are not the same document: the last
thing the old host served was **March 2025, Manual Notice 2025-1**, and the
current one is **April 2026, Manual Notice 2026-1**.

So an agent that takes the first search result does not get an error. It gets
a real manual, with real section numbers, under a revision that is no longer in
force -- which is the failure the plan of record describes as "It didn't lie to
you. It found the wrong document and believed it."
"""

import unittest
from pathlib import Path

from corridor_screen import citations

# The socket guard `test_offline` built under #19. Borrowed rather than rebuilt:
# there should be one answer in this repo to "take the network away," and it
# should be the one that patches below every library that could reach for it.
from tests.test_offline import no_network

REPO = Path(__file__).resolve().parents[2]


class TestFindingASupersededCitation(unittest.TestCase):
    """The check that makes this reproduce every time rather than on the day."""

    def test_a_legacy_url_is_found(self):
        found = citations.superseded(
            "See http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm for ROE."
        )
        self.assertEqual(len(found), 1)

    def test_a_url_with_no_scheme_is_a_description_rather_than_a_citation(self):
        """`docs/txdot-research.md` writes the family out as
        `onlinemanuals.txdot.gov/txdotmanuals/ess/...` to describe the trap. It
        is not clickable and it supports no claim."""
        self.assertEqual(
            citations.superseded("legacy onlinemanuals.txdot.gov/txdotmanuals/ess/... URLs"),
            [],
        )

    def test_one_citation_is_reported_once(self):
        self.assertEqual(
            len(citations.superseded(
                "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm")),
            1,
        )

    def test_the_other_legacy_path_shape_is_found_too(self):
        """There are two, and the first one redirected to the second."""
        found = citations.superseded(
            "https://onlinemanuals.txdot.gov/TxDOTOnlineManuals/TxDOTManuals/ess/index.htm"
        )
        self.assertEqual(len(found), 1)

    def test_the_current_url_is_not_flagged(self):
        self.assertEqual(
            citations.superseded("https://www.txdot.gov/manuals/row/ess/index.html"), []
        )

    def test_naming_the_host_as_forbidden_is_not_citing_it(self):
        """`CLAUDE.md` says "Never `onlinemanuals.txdot.gov`". The rule against
        the trap must not itself trip the check -- a guard that cannot be
        written about is a guard nobody documents."""
        self.assertEqual(
            citations.superseded(
                "Use `txdot.gov/manuals/row/ess/...`. Never `onlinemanuals.txdot.gov`."
            ),
            [],
        )

    def test_each_finding_carries_the_url_that_replaces_it(self):
        """Acceptance criterion: "The correct `txdot.gov` URL is shown
        alongside, as the fix." A check that only says no is half a check."""
        found = citations.superseded(
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm"
        )
        self.assertTrue(found[0]["replacement"].startswith("https://www.txdot.gov/manuals/"))

    def test_a_file_with_several_is_reported_once_per_citation(self):
        found = citations.superseded(
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm and "
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/right_of_entry.htm"
        )
        self.assertEqual(len(found), 2)


class TestTheEvidenceIsOnDiskRatherThanOnTheNetwork(unittest.TestCase):
    """Criterion two: it reproduces from cache, so the venue cannot take it."""

    def test_every_captured_file_the_record_names_is_committed(self):
        for capture in citations.CAPTURES:
            with self.subTest(capture=capture["file"]):
                self.assertTrue((citations.CAPTURE_DIR / capture["file"]).is_file())

    def test_the_legacy_capture_really_says_the_revision_we_claim(self):
        """The claim and the evidence are checked against each other, so this
        repo cannot drift into quoting a revision its own capture does not
        show."""
        said = citations.revision_in(citations.capture_text("legacy"))
        self.assertEqual(said["manual_notice"], "2025-1")
        self.assertIn("March 2025", said["revised"])

    def test_the_current_capture_really_says_the_revision_we_claim(self):
        said = citations.revision_in(citations.capture_text("current"))
        self.assertEqual(said["manual_notice"], "2026-1")
        self.assertIn("April 2026", said["revised"])

    def test_the_legacy_page_is_read_in_the_encoding_it_declares(self):
        """It says `charset=ISO-8859-1` in its own head -- period detail from an
        older web. Read as UTF-8 it does not fail; it just comes out wrong
        above byte 127, which is the same shape of error as reading a survey
        file in the wrong coordinate system."""
        raw = (citations.CAPTURE_DIR / citations.CAPTURES[0]["file"]).read_bytes()
        self.assertEqual(citations.declared_charset(raw).lower(), "iso-8859-1")

    def test_an_html_entity_does_not_hide_the_revision(self):
        """The legacy page writes it as `March&nbsp;2025`. Searching the raw
        markup for "March 2025" finds nothing and concludes, wrongly, that the
        page carries no revision at all."""
        self.assertEqual(
            citations.revision_in("<p>TxDOT Survey Manual</p><p>March&nbsp;2025</p>")["revised"],
            "March 2025",
        )

    def test_the_two_revisions_are_actually_different(self):
        """If they ever converge, the beat is over and this should say so
        rather than keep teaching a thing that stopped being true."""
        legacy = citations.revision_in(citations.capture_text("legacy"))
        current = citations.revision_in(citations.capture_text("current"))
        self.assertNotEqual(legacy["manual_notice"], current["manual_notice"])


class TestItRunsWithTheNetworkActuallyGone(unittest.TestCase):
    """Criterion two, proven rather than asserted.

    `--mode cache-only` was not accepted as proof of offline replay under #19
    either -- that is the tool *choosing* not to call out. What a presenter
    needs to know is what happens when the choice is taken away, at 1:36, in a
    hotel basement. So the network is removed at the socket and the beat is run
    against it.
    """

    def test_the_whole_beat_builds_with_every_network_door_refused(self):
        with no_network():
            said = citations.beat()
        self.assertIn("2025-1", said)
        self.assertIn("2026-1", said)

    def test_the_guard_runs_with_every_network_door_refused(self):
        with no_network():
            self.assertEqual(citations.check_repo(REPO), [])


class TestTheBeatItself(unittest.TestCase):
    """What goes on the projector at 1:36."""

    def setUp(self):
        self.said = citations.beat()

    def test_it_shows_both_urls(self):
        self.assertIn("onlinemanuals.txdot.gov", self.said)
        self.assertIn("txdot.gov/manuals/row/ess/", self.said)

    def test_it_shows_both_revisions(self):
        self.assertIn("2025-1", self.said)
        self.assertIn("2026-1", self.said)

    def test_it_names_what_the_agent_did_wrong_in_one_sentence(self):
        """Acceptance criterion, quoted. The sentence is the beat; everything
        else on screen is the evidence for it."""
        self.assertIn(citations.VERDICT, self.said)
        self.assertEqual(citations.VERDICT.count("."), 1)

    def test_it_says_when_each_claim_was_checked(self):
        """A capture with no date is a claim about nothing in particular."""
        self.assertIn(citations.CHECKED_ON, self.said)

    def test_it_does_not_say_the_old_host_is_dead(self):
        """It resolves. Nothing answers on it. Those are not the same finding,
        and this repo says "not found" rather than "does not exist"."""
        self.assertNotIn("dead", self.said.lower())


class TestThisRepoDoesNotMakeTheMistakeItTeaches(unittest.TestCase):
    """CLAUDE.md: "Use `txdot.gov/manuals/row/ess/...` URLs. Never
    `onlinemanuals.txdot.gov`." A rule with nothing enforcing it is a rule that
    is true until somebody is in a hurry."""

    def test_no_page_or_module_cites_a_superseded_url(self):
        offenders = citations.check_repo(REPO)
        self.assertEqual(offenders, [], citations.report(offenders))

    def test_exactly_two_files_are_exempt_and_both_declare_why(self):
        """An exemption list nobody looks at is how a guard stops guarding.

        Two files hold these URLs on purpose: this one, whose fixtures are the
        guard's own test data, and `citations.py`, whose `CAPTURES` record what
        each committed capture was fetched from. Both say so in a line a reader
        meets before the URLs.
        """
        exempt = sorted(Path(p).as_posix() for p in citations.exempt(REPO))
        self.assertEqual(exempt, [
            "corridor-screen/corridor_screen/citations.py",
            "corridor-screen/tests/test_citations.py",
        ])


if __name__ == "__main__":
    unittest.main()
