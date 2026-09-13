"""The whole tool, end to end, with the network actually gone.

Issue #19 exists because the conference network is untrusted, TxDOT's ROW
server blocks intermittently, and this repo's own research recorded USGS
elevation timing out three times out of four. The demo runs from cache.

**`--mode cache-only` is not by itself proof of that.** It is the tool
*choosing* not to call out. What a presenter needs to know is what happens when
the choice is taken away -- when the venue Wi-Fi is a captive portal, or is
simply not there. Those are different failures and only one of them is tested
by asking the tool nicely.

So these tests take the network away at the socket, which is below every
library that could reach for it, and then run the real pipeline against the
real committed capture. Nothing is stubbed except the network itself.

This is the slowest test file in the repo, and deliberately so: it copies the
2 MB demo cache and runs all nine steps. It is the one that would have caught a
stray live call on the morning of the session.
"""

import io
import json
import os
import socket
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from corridor_screen import cli, replay
from corridor_screen.arcgis import ServiceDown
from corridor_screen.cache import long_path

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "project-sh16"

# The SH16 scope, exactly as the README tells a presenter to run it.
SH16 = ["--route", "SH0016-KG", "--begin-dfo", "347.7", "--end-dfo", "356.367"]


class NetworkWasUsed(AssertionError):
    """Something reached for the network during a run that must not have."""


@contextmanager
def no_network():
    """Take the network away, below anything that could reach for it.

    Patched at ``socket`` rather than at ``urllib`` on purpose. Patching the
    fetcher would only prove the fetcher behaves, which is the part already
    under test. Patching the socket proves that **nothing at all** in nine
    steps opened a connection -- including any library that might one day be
    reached for without going through ``arcgis.Fetcher``.
    """
    real_socket = socket.socket
    real_create = socket.create_connection
    real_getaddrinfo = socket.getaddrinfo

    def refuse(*args, **kwargs):
        raise NetworkWasUsed(
            "a run that must work offline tried to open a network connection"
        )

    socket.socket = refuse
    socket.create_connection = refuse
    socket.getaddrinfo = refuse
    try:
        yield
    finally:
        socket.socket = real_socket
        socket.create_connection = real_create
        socket.getaddrinfo = real_getaddrinfo


@contextmanager
def quiet():
    """Run without printing the whole screening report into the test output."""
    said = io.StringIO()
    original = cli._say

    def capture(message=""):
        said.write(str(message) + "\n")

    cli._say = capture
    try:
        yield said
    finally:
        cli._say = original


def _copy_tree(source, destination):
    """Copy a directory through ``cache.long_path``.

    ``shutil.copytree`` cannot do this job here, and finding out why is worth
    the four lines. A surveyor's checkout sits under a path like "OneDrive -
    Some Long Firm Name\\Documents\\Projects\\...", and this repo's own worktree
    already pushes a cached response past the 260 characters Windows will open
    without being asked in the extended form. ``shutil`` asks in the plain form
    and fails with a file-not-found error on a file that is plainly there.

    ``cache.long_path`` is the whole reason the tool itself survives that, and
    the first run of this test failed exactly the way its docstring says. So
    the copy goes through the same door the tool uses.
    """
    for item in sorted(Path(source).rglob("*")):
        target = Path(destination) / item.relative_to(source)
        if item.is_dir():
            os.makedirs(long_path(target), exist_ok=True)
            continue
        os.makedirs(long_path(target.parent), exist_ok=True)
        with open(long_path(item), "rb") as reading, open(long_path(target), "wb") as writing:
            writing.write(reading.read())


@contextmanager
def a_copy_of_the_demo_cache():
    """The committed SH16 capture, in a temp directory this test may write to.

    Copied rather than used in place, so a test run never rewrites the demo
    artifact that a session depends on.
    """
    if not (DEMO / "cache").is_dir():
        raise AssertionError(
            f"the committed demo cache is missing from {DEMO / 'cache'} -- "
            "it is what this test replays, and it is checked into the repo"
        )
    with tempfile.TemporaryDirectory() as temporary:
        out = Path(temporary) / "project"
        out.mkdir()
        _copy_tree(DEMO / "cache", out / "cache")
        yield out


def run_offline(out, extra=()):
    """One cache-only run with the network taken away. Returns (exit code, output)."""
    args = cli.parse_args(SH16 + ["--out", str(out), "--mode", "cache-only", "--yes", *extra])
    with no_network(), quiet() as said:
        code = cli.run(args)
    return code, said.getvalue()


class TestTheWholeToolWithNoNetwork(unittest.TestCase):
    """Nine steps, one corridor, no network at all."""

    def test_the_full_run_completes_with_every_socket_refused(self):
        with a_copy_of_the_demo_cache() as out:
            code, _ = run_offline(out)
        self.assertEqual(code, 0, "a cache-only run of the demo corridor must complete")

    def test_it_writes_a_complete_run_not_an_incomplete_one(self):
        """`screening.incomplete.json` would mean a step was missed."""
        with a_copy_of_the_demo_cache() as out:
            run_offline(out)
            document = json.loads((out / "screening.json").read_text(encoding="utf-8"))
        self.assertEqual(document["run"]["status"], "complete")
        self.assertEqual(document["run"]["mode"], "cache-only")

    def test_every_service_answered_from_the_cache(self):
        with a_copy_of_the_demo_cache() as out:
            run_offline(out)
            document = json.loads((out / "screening.json").read_text(encoding="utf-8"))
        skipped = [s["name"] for s in document["services"] if s["status"] != "ok"]
        self.assertEqual(skipped, [], "every service should have replayed from cache")

    def test_it_finds_the_same_things_the_committed_run_found(self):
        """The acceptance criterion: output from cache matches output from live.

        Compared against ``project-sh16/screening.json``, which is committed and
        was produced by a live run. If this fails, either the tool changed what
        it reports -- in which case re-run it live and commit the new file -- or
        the replay is not faithful, which is the thing this repo cannot ship.
        """
        committed = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
        with a_copy_of_the_demo_cache() as out:
            run_offline(out)
            replayed = json.loads((out / "screening.json").read_text(encoding="utf-8"))
        self.assertTrue(
            replay.same_findings(committed, replayed),
            "\n" + replay.report(committed, replayed),
        )

    def test_the_parcel_count_a_presenter_would_read_off_the_screen_is_there(self):
        """A blunt check on the number that goes on the projector."""
        committed = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
        with a_copy_of_the_demo_cache() as out:
            _, said = run_offline(out)
        self.assertIn(f"parcels     {len(committed['parcels'])}", said)


class TestAMissingCaptureFailsLoudly(unittest.TestCase):
    """Never silently. A quiet gap is the one thing worse than a stopped run."""

    def test_a_request_that_was_never_captured_stops_the_run_and_names_itself(self):
        with a_copy_of_the_demo_cache() as out:
            # A corridor nobody ever captured. Every other input is the same.
            args = cli.parse_args(
                ["--route", "SH0016-KG", "--begin-dfo", "100.0", "--end-dfo", "110.0",
                 "--out", str(out), "--mode", "cache-only", "--yes"]
            )
            with no_network(), quiet() as said:
                code = cli.run(args)
        self.assertEqual(code, 1, "a run with no capture for it must not report success")
        printed = said.getvalue()
        self.assertIn("no cached response", printed)
        self.assertIn("cache-first", printed, "it should say how to capture the missing one")

    def test_the_fetcher_names_the_exact_request_it_could_not_find(self):
        """So the missing capture can be taken, rather than guessed at."""
        from corridor_screen.arcgis import Fetcher
        from corridor_screen.cache import Cache

        with tempfile.TemporaryDirectory() as temporary:
            fetcher = Fetcher(Cache(Path(temporary) / "cache"), mode="cache-only")
            with no_network(), self.assertRaises(ServiceDown) as caught:
                fetcher.get_json(
                    "Some_Service", "a-request-nobody-captured",
                    "https://example.invalid/query", {"f": "json"},
                )
        message = str(caught.exception)
        self.assertIn("some-service/a-request-nobody-captured", message)
        self.assertIn("cache-first", message)

    def test_a_cache_only_run_never_pings_and_says_so(self):
        """The ping is a network call too, and it is the first thing a run does."""
        with a_copy_of_the_demo_cache() as out:
            run_offline(out)
            document = json.loads((out / "screening.json").read_text(encoding="utf-8"))
        for service in document["services"]:
            self.assertEqual(service["ping"], "skipped")
            self.assertIn("no network calls", service["ping_detail"])


class TestTheNetworkGuardItself(unittest.TestCase):
    """A test harness that cannot fail is not a test harness.

    If ``no_network`` quietly stopped blocking -- a Python release renaming
    something, a refactor -- every test above would keep passing while proving
    nothing at all. So the guard is tested too.
    """

    def test_the_guard_refuses_a_connection(self):
        with no_network():
            with self.assertRaises(NetworkWasUsed):
                socket.create_connection(("example.invalid", 443))

    def test_the_guard_refuses_a_name_lookup(self):
        with no_network():
            with self.assertRaises(NetworkWasUsed):
                socket.getaddrinfo("example.invalid", 443)

    def test_the_guard_puts_the_network_back_afterwards(self):
        before = socket.socket
        with no_network():
            pass
        self.assertIs(socket.socket, before)


if __name__ == "__main__":
    unittest.main()
