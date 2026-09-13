"""The shared module behind the failure beats, and the rules it makes structural.

Issue #67. Two beat modules grew the same shape, and the shape carried three
rules that were being restated in prose rather than enforced. The issue names
all three:

1. **Plain ASCII.** An em dash is a `UnicodeEncodeError` and a traceback on a
   Windows console that has not been told otherwise, which is every borrowed
   podium laptop
2. **A capture carries the exact request it came from.** A capture nobody can
   repeat is not evidence
3. **The rendered beat is committed and pinned to the code by a test**

Beat one shipped with an em dash and was caught by review on
[PR #65](https://github.com/RickSmith/survey-recon/pull/65), not by anything
running. Beat two avoided it because whoever wrote it had just read about it.
That is not a safeguard.

So all three are checked here, and **the modules are found rather than listed**.
A third beat inherits every check in this file by existing. A file naming
`manual_links` and `elevation_trap` would have missed it, and remembering is
the thing that already failed once.

`beats.render` carries the first rule further still: it refuses a non-ASCII
character outright, so it fails when somebody *runs* the beat rather than when
somebody runs this suite.

**What a beat module has to provide** is written down in `beats.py`, under *The
shape a beat module has*. These checks read exactly that, and say so when a
module is missing a piece rather than dying on an `AttributeError`.

**What this file is careful not to assume.** The issue says plainly there may
never be a third beat module, and that "two copies is fine, leave it" would be
a reasonable ruling. Every function under test has two callers today. The
discovery costs nothing if it only ever finds two.
"""

import importlib
import pkgutil
import unittest
from pathlib import Path

import corridor_screen
from corridor_screen import beats
from corridor_screen.cache import long_path

from tests.test_offline import no_network

# A console that has not been told to speak UTF-8. `cp437` is what a borrowed
# Windows laptop gives you; `ascii` is the floor.
CONSOLES = ("cp437", "cp1252", "ascii")


def beat_modules():
    """Every module of the tool that renders a failure beat.

    Found rather than listed, which is the whole of issue #67 -- the
    alternative is a list somebody has to remember to add to.

    Modules whose name starts with an underscore are skipped, because importing
    `__main__` runs it: that is what `__main__` is for. A rule rather than a
    list, for the same reason as everything else in this file.
    """
    found = {}
    for info in pkgutil.iter_modules(corridor_screen.__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"corridor_screen.{info.name}")
        if callable(getattr(module, "beat", None)):
            found[info.name] = module
    return found


def captures_of(module):
    """A beat's captures as a list of records, whichever shape it keeps them in.

    `manual_links` holds a tuple of dicts, because its entries have a `name`
    field and their order is the order the beat reads them in. `elevation_trap`
    holds a dict keyed by name, because its beat reaches for them individually.
    Both are right for their own module, and neither should be bent to suit a
    check that only wants to iterate.
    """
    captures = getattr(module, "CAPTURES", None)
    if isinstance(captures, dict):
        return list(captures.values())
    return list(captures or [])


class RenderRefusesWhatAPodiumCannotPrint(unittest.TestCase):
    def test_it_joins_lines_with_a_newline(self):
        self.assertEqual(beats.render(["one", "two"]), "one\ntwo")

    def test_it_refuses_a_character_a_cp437_console_cannot_print(self):
        with self.assertRaises(ValueError) as caught:
            beats.render(["  Failure beat 1 — the superseded manual"])
        self.assertIn("EM DASH", str(caught.exception).upper())

    def test_the_message_says_which_line(self):
        """A beat is thirty lines long. "There is an em dash somewhere in it"
        is a worse message than the line it is on."""
        with self.assertRaises(ValueError) as caught:
            beats.render(["fine", "also fine", "not é fine"])
        self.assertIn("3", str(caught.exception))

    def test_the_message_itself_prints_on_that_console(self):
        """The guard is read on the machine it fires on, which is the machine
        that cannot print the character it is complaining about."""
        try:
            beats.render(["  Failure beat 1 — the superseded manual"])
        except ValueError as refused:
            str(refused).encode("cp437", errors="backslashreplace")
        else:
            self.fail("render accepted an em dash")

    def test_plain_ascii_passes_through_untouched(self):
        lines = ["  Failure beat 2 - the answer that is wrong", "", "  ok"]
        self.assertEqual(beats.render(lines), "\n".join(lines))


class EveryBeatIsShaped(unittest.TestCase):
    """The contract in `beats.py`, checked rather than assumed.

    Without this, a third beat with a `beat()` and nothing else fails the rest
    of this file on a bare `AttributeError`, which reads like a broken test
    rather than an unfinished module.
    """

    def test_the_modules_are_found_rather_than_listed(self):
        """The discovery itself, checked. If it silently found nothing, every
        test in this file would pass over an empty set."""
        found = beat_modules()
        self.assertGreaterEqual(
            len(found), 2, f"expected at least the two beats, found {sorted(found)}"
        )

    def test_every_beat_declares_where_its_evidence_lives(self):
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                folder = getattr(module, "CAPTURE_DIR", None)
                self.assertIsNotNone(
                    folder,
                    f"{name} renders a beat and declares no CAPTURE_DIR. See "
                    f"'The shape a beat module has' in beats.py",
                )
                self.assertTrue(folder.is_dir(), f"{folder} is not a folder")

    def test_every_capture_directory_is_one_beats_would_build(self):
        """Read back through `beats.capture_dir`, not re-derived from the repo
        root -- a second expression for the same path is the duplication this
        issue is about, arriving in the test that removed it."""
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                leaf = module.CAPTURE_DIR.name
                self.assertEqual(module.CAPTURE_DIR, beats.capture_dir(leaf))

    def test_every_beat_says_when_its_evidence_was_checked(self):
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                self.assertRegex(
                    getattr(module, "CHECKED_ON", ""),
                    r"^\d{4}-\d{2}-\d{2}$",
                    f"{name} has no CHECKED_ON date. A claim with no date is a "
                    f"claim about nothing",
                )


class EveryBeatSurvivesAConsoleThatOnlySpeaksAscii(unittest.TestCase):
    def test_every_beat_prints_on_such_a_console(self):
        """Built with the network taken away, at the socket.

        The per-module tests each proved their own beat builds offline. Doing
        it here as well is what makes a third beat inherit it -- the offline
        rule is as much a part of a beat as the ASCII one, and the first draft
        of this file left it behind in the two modules.
        """
        for name, module in beat_modules().items():
            with no_network():
                said = module.beat()
            for console in CONSOLES:
                with self.subTest(beat=name, console=console):
                    said.encode(console)

    def test_every_beat_goes_through_the_guard(self):
        """Encoding cleanly is not the same as being guarded.

        A beat that built its own string with `"\\n".join(...)` would pass the
        check above today and stop passing it the first time somebody typed a
        nicer dash.

        **Checked by taking `beats.render` away**, not by searching the module
        for the word. The first draft grepped the source for `render(`, which
        passes for a module that mentions it in a docstring, defines its own,
        or calls it somewhere other than `beat()` -- three ways to be green
        while the rule is unenforced.
        """
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                called = []
                original = beats.render
                beats.render = lambda lines: called.append(lines) or original(lines)
                try:
                    module.beat()
                finally:
                    beats.render = original
                self.assertTrue(
                    called,
                    f"{name}.beat() does not go through beats.render, so the "
                    f"plain-ASCII rule is a comment in it again",
                )


class EveryCaptureCarriesTheRequestItCameFrom(unittest.TestCase):
    """The issue's second rule, which both modules restated in prose.

    > A capture nobody can repeat is not evidence.

    `CLAUDE.md`'s data rules lean on this harder than on anything else here:
    every cached response is stamped with the exact request URL. A beat's
    captures are the same kind of thing, and until now the only check on it was
    a copy inside one beat's own test file.
    """

    def test_every_beat_has_captures_at_all(self):
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                self.assertTrue(
                    captures_of(module),
                    f"{name} renders a beat from no committed captures",
                )

    def test_every_capture_names_the_request_that_produced_it(self):
        for name, module in beat_modules().items():
            for capture in captures_of(module):
                with self.subTest(beat=name, capture=capture.get("file")):
                    url = capture.get("url", "")
                    self.assertTrue(
                        url.startswith("http"),
                        f"a capture of {name} carries no request URL, so "
                        f"nobody can repeat it",
                    )

    def test_every_capture_the_record_names_is_committed(self):
        """Asked through `cache.long_path`, and the first draft was not.

        It reported two of `manual_links`' captures missing on a checkout where
        they are plainly there -- the paths run past the 260 characters Windows
        answers without being asked in the extended form. Which is the same
        failure issue #76 found, found again, by a check written to replace two
        copies of itself.
        """
        for name, module in beat_modules().items():
            for capture in captures_of(module):
                with self.subTest(beat=name, capture=capture.get("file")):
                    path = module.CAPTURE_DIR / capture["file"]
                    self.assertTrue(
                        Path(long_path(path)).is_file(), f"{path} is not on disk"
                    )


class TheFallbackIsWrittenTheSameWayEveryTime(unittest.TestCase):
    def test_every_beat_has_its_rendered_fallback_committed(self):
        """`--write-fallback`'s output, pinned to what `beat()` says now.

        This arrives free for a beat nobody has written yet. The two copies it
        replaced were per-module, and the one inside `test_elevation_trap`
        opened its file **without** `cache.long_path` -- the same miss issue
        #76 found in `manual_links.capture_text`, which would have failed on a
        checkout whose paths run past 260 characters.
        """
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                path = module.CAPTURE_DIR / beats.BEAT_NAME
                # `newline=""` and the replace rather than universal newlines:
                # git may check this file out with CRLF, and the check is about
                # the beat's content rather than about line endings.
                with open(long_path(path), encoding="utf-8", newline="") as handle:
                    committed = handle.read()
                self.assertEqual(
                    committed.replace("\r\n", "\n"), module.beat() + "\n"
                )


if __name__ == "__main__":
    unittest.main()
