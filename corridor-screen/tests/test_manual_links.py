"""Tests for failure beat one -- the superseded manual.

This file holds superseded-url-evidence: the legacy URLs below are fixtures for
the guard, not citations, and `manual_links.EVIDENCE_MARKER` is how the guard is
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

from corridor_screen import manual_links

# The socket guard `test_offline` built under #19. Borrowed rather than rebuilt:
# there should be one answer in this repo to "take the network away," and it
# should be the one that patches below every library that could reach for it.
from tests.test_offline import no_network

REPO = Path(__file__).resolve().parents[2]


class TestFindingASupersededCitation(unittest.TestCase):
    """The check that makes this reproduce every time rather than on the day."""

    def test_a_legacy_url_is_found(self):
        found = manual_links.superseded(
            "See http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm for ROE."
        )
        self.assertEqual(len(found), 1)

    def test_a_url_with_no_scheme_is_a_description_rather_than_a_citation(self):
        """`docs/txdot-research.md` writes the family out as
        `onlinemanuals.txdot.gov/txdotmanuals/ess/...` to describe the trap. It
        is not clickable and it supports no claim."""
        self.assertEqual(
            manual_links.superseded("legacy onlinemanuals.txdot.gov/txdotmanuals/ess/... URLs"),
            [],
        )

    def test_a_clickable_host_with_no_path_is_still_a_citation(self):
        """`https://onlinemanuals.txdot.gov` is clickable and supports a claim.
        The first pattern required a trailing slash and let it through."""
        self.assertEqual(
            len(manual_links.superseded("see https://onlinemanuals.txdot.gov today")), 1)

    def test_the_host_is_matched_whatever_its_capitalization(self):
        """Host names are case-insensitive by definition, so these are the same
        address and the same mistake. The first pattern matched none of them."""
        for url in ("HTTP://onlinemanuals.txdot.gov/x.htm",
                    "http://OnlineManuals.txdot.gov/TxDOTOnlineManuals/ess/index.htm",
                    "https://www.onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm"):
            with self.subTest(url=url):
                self.assertEqual(len(manual_links.superseded(url)), 1)

    def test_one_citation_is_reported_once(self):
        self.assertEqual(
            len(manual_links.superseded(
                "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm")),
            1,
        )

    def test_the_other_legacy_path_shape_is_found_too(self):
        """There are two, and the first one redirected to the second."""
        found = manual_links.superseded(
            "https://onlinemanuals.txdot.gov/TxDOTOnlineManuals/TxDOTManuals/ess/index.htm"
        )
        self.assertEqual(len(found), 1)

    def test_the_current_url_is_not_flagged(self):
        self.assertEqual(
            manual_links.superseded("https://www.txdot.gov/manuals/row/ess/index.html"), []
        )

    def test_naming_the_host_as_forbidden_is_not_citing_it(self):
        """`CLAUDE.md` says "Never `onlinemanuals.txdot.gov`". The rule against
        the trap must not itself trip the check -- a guard that cannot be
        written about is a guard nobody documents."""
        self.assertEqual(
            manual_links.superseded(
                "Use `txdot.gov/manuals/row/ess/...`. Never `onlinemanuals.txdot.gov`."
            ),
            [],
        )

    def test_each_finding_carries_the_url_that_replaces_it(self):
        """Acceptance criterion: "The correct `txdot.gov` URL is shown
        alongside, as the fix." A check that only says no is half a check."""
        found = manual_links.superseded(
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm"
        )
        self.assertTrue(found[0]["replacement"].startswith("https://www.txdot.gov/manuals/"))

    def test_a_file_with_several_is_reported_once_per_citation(self):
        found = manual_links.superseded(
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm and "
            "http://onlinemanuals.txdot.gov/txdotmanuals/ess/right_of_entry.htm"
        )
        self.assertEqual(len(found), 2)


class TestTheGuardActuallyReadsEverythingItClaimsTo(unittest.TestCase):
    """A guard that silently skips a file is worse than no guard.

    The first version used `Path.read_text`, which cannot open a path past the
    260 characters Windows will take without being asked in the extended form.
    On this repo's own worktree that was **21 files** -- a fifth of what it was
    asked to check -- skipped by an `except OSError: continue` that said nothing.

    `cache.long_path` is the door the rest of the tool already uses, and
    `test_offline._copy_tree` carries the same lesson for `shutil`.
    """

    def test_no_file_is_skipped_because_of_its_path_length(self):
        self.assertEqual(manual_links.unreadable(REPO), [])

    def test_a_file_that_cannot_be_read_is_reported_rather_than_ignored(self):
        """If one ever does become unreadable, the guard has to say so out loud
        rather than quietly returning a clean result."""
        self.assertIn("could not read", manual_links.report([], unreadable=["some/file.md"]))


class TestTheEvidenceIsOnDiskRatherThanOnTheNetwork(unittest.TestCase):
    """Criterion two: it reproduces from cache, so the venue cannot take it."""

    def test_every_captured_file_the_record_names_is_committed(self):
        for capture in manual_links.CAPTURES:
            with self.subTest(capture=capture["file"]):
                self.assertTrue((manual_links.CAPTURE_DIR / capture["file"]).is_file())

    def test_the_legacy_capture_really_says_the_revision_we_claim(self):
        """The claim and the evidence are checked against each other, so this
        repo cannot drift into quoting a revision its own capture does not
        show."""
        said = manual_links.revision_in(manual_links.capture_text("legacy"))
        self.assertEqual(said["manual_notice"], "2025-1")
        self.assertIn("March 2025", said["revised"])

    def test_the_current_capture_really_says_the_revision_we_claim(self):
        said = manual_links.revision_in(manual_links.capture_text("current"))
        self.assertEqual(said["manual_notice"], "2026-1")
        self.assertIn("April 2026", said["revised"])

    def test_the_legacy_page_is_read_in_the_encoding_it_declares(self):
        """It says `charset=ISO-8859-1` in its own head -- period detail from an
        older web. Read as UTF-8 it does not fail; it just comes out wrong
        above byte 127, which is the same shape of error as reading a survey
        file in the wrong coordinate system."""
        raw = (manual_links.CAPTURE_DIR / manual_links.CAPTURES[0]["file"]).read_bytes()
        self.assertEqual(manual_links.declared_charset(raw).lower(), "iso-8859-1")

    def test_an_html_entity_does_not_hide_the_revision(self):
        """The legacy page writes it as `March&nbsp;2025`. Searching the raw
        markup for "March 2025" finds nothing and concludes, wrongly, that the
        page carries no revision at all."""
        self.assertEqual(
            manual_links.revision_in("<p>TxDOT Survey Manual</p><p>March&nbsp;2025</p>")["revised"],
            "March 2025",
        )

    def test_the_two_revisions_are_actually_different(self):
        """If they ever converge, the beat is over and this should say so
        rather than keep teaching a thing that stopped being true."""
        legacy = manual_links.revision_in(manual_links.capture_text("legacy"))
        current = manual_links.revision_in(manual_links.capture_text("current"))
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
            said = manual_links.beat()
        self.assertIn("2025-1", said)
        self.assertIn("2026-1", said)

    def test_the_guard_runs_with_every_network_door_refused(self):
        with no_network():
            self.assertEqual(manual_links.check_repo(REPO), [])


class TestItSurvivesTheLaptopItWillActuallyRunOn(unittest.TestCase):
    """At 1:36, on a machine somebody else set up.

    The first version of `beat()` printed an em dash. On a Windows console that
    has not been told to use UTF-8 -- which is the default, and every borrowed
    podium laptop -- that is a `UnicodeEncodeError` and a traceback where the
    beat should be. Nothing else in this package prints a non-ASCII character.
    """

    def test_the_beat_prints_on_a_console_that_only_speaks_ascii(self):
        for console in ("cp437", "cp1252", "ascii"):
            with self.subTest(console=console):
                manual_links.beat().encode(console)

    def test_the_guard_report_prints_there_too(self):
        said = manual_links.report(
            [{"path": "a.md", "url": "http://x", "replacement": "http://y"}],
            unreadable=["b.md"],
        )
        said.encode("cp437")


class TestTheFallbackARunCanBeReadFrom(unittest.TestCase):
    """Issue #27 wants a capture "that can stand in if the live thing breaks."

    The page captures are the beat's *inputs*. This is its *output*, written
    out and committed, so a presenter whose Python will not start can open a
    text file instead. Pinned to `beat()` by this test, the same way the
    committed `screening.json` is pinned by the replay check -- otherwise it is
    a file that silently stops matching the code that made it.
    """

    def test_the_committed_rendering_is_what_the_code_produces_today(self):
        path = manual_links.CAPTURE_DIR / manual_links.BEAT_NAME
        with open(path, encoding="utf-8", newline="") as handle:
            written = handle.read()
        self.assertEqual(written.replace("\r\n", "\n"), manual_links.beat() + "\n")


class TestTheBeatItself(unittest.TestCase):
    """What goes on the projector at 1:36."""

    def setUp(self):
        self.said = manual_links.beat()

    def test_it_shows_both_urls(self):
        self.assertIn("onlinemanuals.txdot.gov", self.said)
        self.assertIn("txdot.gov/manuals/row/ess/", self.said)

    def test_it_shows_both_revisions(self):
        self.assertIn("2025-1", self.said)
        self.assertIn("2026-1", self.said)

    def test_it_names_what_the_agent_did_wrong_in_one_sentence(self):
        """Acceptance criterion, quoted. The sentence is the beat; everything
        else on screen is the evidence for it."""
        self.assertIn(manual_links.VERDICT, self.said)
        self.assertEqual(manual_links.VERDICT.count("."), 1)

    def test_it_says_when_each_claim_was_checked(self):
        """A capture with no date is a claim about nothing in particular."""
        self.assertIn(manual_links.CHECKED_ON, self.said)

    def test_it_does_not_say_the_old_host_is_dead(self):
        """It resolves. Nothing answers on it. Those are not the same finding,
        and this repo says "not found" rather than "does not exist"."""
        self.assertNotIn("dead", self.said.lower())


class TestThisRepoDoesNotMakeTheMistakeItTeaches(unittest.TestCase):
    """CLAUDE.md: "Use `txdot.gov/manuals/row/ess/...` URLs. Never
    `onlinemanuals.txdot.gov`." A rule with nothing enforcing it is a rule that
    is true until somebody is in a hurry."""

    def test_no_page_or_module_cites_a_superseded_url(self):
        offenders = manual_links.check_repo(REPO)
        self.assertEqual(offenders, [], manual_links.report(offenders))

    def test_a_declaration_buried_at_the_bottom_does_not_exempt_anything(self):
        """An HTML comment on the last line renders as nothing in MkDocs. If
        that silenced a citation a hundred lines above it, the exemption would
        be a hiding place rather than a declaration."""
        buried = ("See https://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm\n"
                  + "\n" * 60 + f"<!-- {manual_links.EVIDENCE_MARKER} -->\n")
        self.assertFalse(manual_links.declares_evidence(buried))
        self.assertEqual(len(manual_links.superseded(buried)), 1)

    def test_a_declaration_at_the_top_does_exempt(self):
        declared = (f"<!-- {manual_links.EVIDENCE_MARKER} -->\n"
                    "https://onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm\n")
        self.assertTrue(manual_links.declares_evidence(declared))

    def test_the_repos_own_worktrees_are_not_walked(self):
        """`.claude/worktrees/` holds a full copy of the repo per branch. A
        check run from the main checkout would otherwise report other people's
        work in progress, and break the exempt list this class pins."""
        self.assertIn(".claude", manual_links.SKIP_PARTS)

    def test_no_address_with_a_shelf_life_is_typed_into_the_module(self):
        """The IP was right the day it was checked. It belongs in the capture
        README with its date, beside the rest of the evidence."""
        source = Path(manual_links.__file__).read_text(encoding="utf-8")
        self.assertNotIn("168.44.238.246", source)

    def test_exactly_two_files_are_exempt_and_both_declare_why(self):
        """An exemption list nobody looks at is how a guard stops guarding.

        Two files hold these URLs on purpose: this one, whose fixtures are the
        guard's own test data, and `manual_links.py`, whose `CAPTURES` record what
        each committed capture was fetched from. Both say so in a line a reader
        meets before the URLs.
        """
        exempt = sorted(Path(p).as_posix() for p in manual_links.exempt(REPO))
        self.assertEqual(exempt, [
            "corridor-screen/corridor_screen/manual_links.py",
            "corridor-screen/tests/test_manual_links.py",
        ])


if __name__ == "__main__":
    unittest.main()
