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

from corridor_screen import arcgis, cli, replay
from corridor_screen.arcgis import ServiceDown
from corridor_screen.cache import Cache, long_path
from corridor_screen.sources import PIPELINES

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "project-sh16"

# The real network opener, kept so the one test that replaces it can put it back.
REAL_OPEN = arcgis._open

# What the Railroad Commission served on 2026-09-13: a 503 inside a 200.
AN_ERROR_BODY = json.dumps({
    "error": {
        "code": 503,
        "message": "User couldn't access this resource 'rrc_public/tpms.mapserver'.",
        "details": [],
    }
}).encode("utf-8")

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
    def refuse(*args, **kwargs):
        raise NetworkWasUsed(
            "a run that must work offline tried to reach the network"
        )

    # Every door out, and the ways to walk through each one. `connect` is
    # patched on the socket class rather than replacing the class itself: a
    # replacement would make `socket.socket` a function, so any `isinstance`
    # check against it would raise TypeError somewhere unrelated and look like
    # a different bug entirely. Patching the method leaves the class a class.
    doors = [
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (socket, "gethostbyname"),
        (socket, "gethostbyname_ex"),
    ]
    originals = [(holder, name, getattr(holder, name)) for holder, name in doors]
    for holder, name in doors:
        setattr(holder, name, refuse)
    try:
        yield
    finally:
        for holder, name, original in originals:
            setattr(holder, name, original)


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
    """Nine steps, one corridor, no network at all.

    The run happens **once**, in ``setUpClass``, and every test here reads the
    same result. Copying two megabytes of cache and replaying 524 parcels five
    times over to assert five different fields about one run is the same run
    five times, and the clock is the only thing that notices.
    """

    @classmethod
    def setUpClass(cls):
        cls.committed = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
        with a_copy_of_the_demo_cache() as out:
            cls.code, cls.said = run_offline(out)
            cls.document = json.loads((out / "screening.json").read_text(encoding="utf-8"))

    def test_the_full_run_completes_with_every_network_door_refused(self):
        self.assertEqual(self.code, 0, "a cache-only run of the demo corridor must complete")

    def test_it_writes_a_complete_run_not_an_incomplete_one(self):
        """`screening.incomplete.json` would mean a step was missed."""
        self.assertEqual(self.document["run"]["status"], "complete")
        self.assertEqual(self.document["run"]["mode"], "cache-only")

    def test_every_service_says_in_the_output_that_it_came_from_the_cache(self):
        """`from-cache`, not `ok`. The honesty block has to say where it looked.

        The first version of this test asserted ``status == "ok"`` on all
        fourteen, under a name claiming the opposite, and passed -- because the
        emitter hard-coded that word at all eight call sites while the responses
        underneath carried the truth. The word ``from-cache`` appeared nowhere
        in any output file this tool had ever written. The review on issue #19
        caught it.
        """
        came_from = {s["name"]: s["status"] for s in self.document["services"]}
        wrong = {name: status for name, status in came_from.items() if status != "from-cache"}
        self.assertEqual(wrong, {}, "a replayed run must say so on every service")

    def test_it_finds_the_same_things_the_committed_run_found(self):
        """The acceptance criterion: output from cache matches output from live.

        Compared against ``project-sh16/screening.json``, which is committed and
        was produced by a live run. If this fails, either the tool changed what
        it reports -- in which case re-run it live and commit the new file -- or
        the replay is not faithful, which is the thing this repo cannot ship.
        """
        self.assertTrue(
            replay.same_findings(self.committed, self.document),
            "\n" + replay.report(self.committed, self.document),
        )

    def test_the_parcel_count_a_presenter_would_read_off_the_screen_is_there(self):
        """A blunt check on the number that goes on the projector."""
        self.assertIn(f"parcels     {len(self.committed['parcels'])}", self.said)


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


class TestAFailedLiveRunLeavesTheDemoIntact(unittest.TestCase):
    """Issue #62, end to end, on the capture the session actually presents.

    The incident was not that a host went down. Hosts go down -- the whole of
    issue #19 is built on the assumption that they will. The incident was that
    going down **took the offline demo with it**: the failed ping saved a 503
    error body over 44 real fields, and `--mode cache-only` then failed too.

    So this replays the sequence in order. A live run fails the way it really
    failed, against a copy of the real committed cache, and then the cache-only
    run that a presenter would fall back on has to still work.
    """

    def test_a_failed_live_ping_does_not_break_the_cache_only_fallback(self):
        with a_copy_of_the_demo_cache() as out:
            # The live run, failing exactly as it did on 2026-09-13.
            fetcher = arcgis.Fetcher(Cache(out / "cache"), mode="live")
            arcgis._open = lambda url, params, method, timeout: (AN_ERROR_BODY, 200)
            try:
                ping = fetcher.ping(PIPELINES)
            finally:
                arcgis._open = REAL_OPEN
            self.assertEqual(ping["ping"], "blocked", "the 503 inside the 200 was missed")

            # The fallback a presenter reaches for, with the network gone.
            code, said = run_offline(out)
            document = json.loads((out / "screening.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0, said)
        committed = json.loads((DEMO / "screening.json").read_text(encoding="utf-8"))
        self.assertTrue(
            replay.same_findings(committed, document),
            "\n" + replay.report(committed, document),
        )


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

    def test_the_guard_refuses_a_direct_connect(self):
        with no_network(), socket.socket() as probe:
            with self.assertRaises(NetworkWasUsed):
                probe.connect(("example.invalid", 443))

    def test_the_guard_leaves_the_socket_class_a_class(self):
        """Replacing it outright would break `isinstance` in unrelated code."""
        with no_network():
            with socket.socket() as probe:
                self.assertIsInstance(probe, socket.socket)

    def test_the_guard_puts_every_door_back_afterwards(self):
        before = (socket.socket.connect, socket.create_connection, socket.getaddrinfo)
        with no_network():
            pass
        self.assertEqual(
            (socket.socket.connect, socket.create_connection, socket.getaddrinfo), before
        )

    def test_the_guard_puts_them_back_even_when_a_test_raises(self):
        before = socket.create_connection
        with self.assertRaises(ValueError):
            with no_network():
                raise ValueError("something went wrong inside the guard")
        self.assertIs(socket.create_connection, before)


if __name__ == "__main__":
    unittest.main()
