"""The shared seam behind the failure beats, and the rule it makes structural.

Issue #67. Two beat modules grew the same shape, and the shape carries a rule
that was being remembered rather than enforced:

> **Plain ASCII.** An em dash is a `UnicodeEncodeError` and a traceback on a
> Windows console that has not been told otherwise, which is every borrowed
> podium laptop.

Beat one shipped with an em dash in its output and was caught by review on
[PR #65](https://github.com/RickSmith/survey-recon/pull/65), not by anything
running. Beat two avoided it because whoever wrote it had just read about it.
That is not a safeguard.

So there are two halves here, and they fail at different times:

* **`beats.render` refuses a non-ASCII character outright.** It fails the
  moment anybody runs the beat, on the machine they ran it on, naming the
  character -- rather than in CI, or at 1:36 on a projector
* **The check finds beat modules rather than listing them.** A third beat is
  covered the day it lands, by nobody remembering anything. That is the whole
  point of the issue, and a test that named `manual_links` and
  `elevation_trap` would have missed it

**What this file is careful not to assume.** The issue says plainly there may
never be a third beat module, and that "two copies is fine, leave it" would be
a reasonable ruling. So nothing here is built for a caller that does not exist:
every function under test has two callers today, and the discovery check costs
nothing if it only ever finds two.
"""

import importlib
import pkgutil
import unittest
from pathlib import Path

import corridor_screen
from corridor_screen import beats
from corridor_screen.cache import long_path

REPO = Path(__file__).resolve().parents[2]

# A console that has not been told to speak UTF-8. `cp437` is what a borrowed
# Windows laptop gives you; `ascii` is the floor.
CONSOLES = ("cp437", "cp1252", "ascii")

# Importing this one runs it, because that is what `__main__` is for.
NOT_IMPORTABLE = ("__main__",)


def beat_modules():
    """Every module of the tool that renders a failure beat.

    Found rather than listed. A third beat inherits every check in this file by
    existing, which is what issue #67 asks for -- the alternative is a list
    somebody has to remember to add to, and remembering is the thing that
    already failed once.
    """
    found = {}
    for info in pkgutil.iter_modules(corridor_screen.__path__):
        if info.name in NOT_IMPORTABLE:
            continue
        module = importlib.import_module(f"corridor_screen.{info.name}")
        if callable(getattr(module, "beat", None)):
            found[info.name] = module
    return found


class RenderRefusesWhatAPodiumCannotPrint(unittest.TestCase):
    def test_it_joins_lines_with_a_newline(self):
        self.assertEqual(beats.render(["one", "two"]), "one\ntwo")

    def test_it_refuses_a_character_a_cp437_console_cannot_print(self):
        with self.assertRaises(ValueError) as caught:
            beats.render(["  Failure beat 1 — the superseded manual"])
        said = str(caught.exception)
        self.assertIn("—", said, "the message does not show the character")
        self.assertIn("EM DASH", said.upper(), "the message does not name it")

    def test_the_message_says_which_line(self):
        """A beat is thirty lines long. "There is an em dash somewhere in it"
        is a worse message than the line it is on."""
        with self.assertRaises(ValueError) as caught:
            beats.render(["fine", "also fine", "not é fine"])
        self.assertIn("3", str(caught.exception))

    def test_plain_ascii_passes_through_untouched(self):
        lines = ["  Failure beat 2 - the answer that is wrong", "", "  ok"]
        self.assertEqual(beats.render(lines), "\n".join(lines))


class EveryBeatSurvivesAConsoleThatOnlySpeaksAscii(unittest.TestCase):
    def test_the_modules_are_found_rather_than_listed(self):
        """The check itself, checked. If discovery silently found nothing, every
        test below would pass on an empty set."""
        found = beat_modules()
        self.assertGreaterEqual(
            len(found), 2, f"expected at least the two beats, found {sorted(found)}"
        )

    def test_every_beat_prints_on_such_a_console(self):
        for name, module in beat_modules().items():
            said = module.beat()
            for console in CONSOLES:
                with self.subTest(beat=name, console=console):
                    said.encode(console)

    def test_every_beat_goes_through_the_guard(self):
        """Encoding cleanly is not the same as being guarded.

        A beat that built its own string with `"\\n".join(...)` would pass the
        check above today and stop passing it the first time somebody typed a
        nicer dash. So the seam is checked for use, not only for effect.
        """
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                source = (REPO / "corridor-screen" / "corridor_screen" / f"{name}.py")
                with open(long_path(source), encoding="utf-8") as handle:
                    text = handle.read()
                self.assertIn(
                    "render(",
                    text,
                    f"{name}.beat() does not go through beats.render, so the "
                    f"plain-ASCII rule is a comment in it again",
                )


class TheFallbackIsWrittenTheSameWayEveryTime(unittest.TestCase):
    def test_every_beat_has_its_rendered_fallback_committed(self):
        """`--write-fallback`'s output, pinned to what `beat()` says now.

        The per-module tests already pin their own; this one is the same check
        arriving free for a beat nobody has written yet.
        """
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                path = module.CAPTURE_DIR / beats.BEAT_NAME
                # `newline=""` and the replace, rather than universal newlines,
                # because git may check this file out with CRLF and the check is
                # about the beat's content rather than about line endings.
                #
                # Through `long_path`, which the copy of this check inside
                # `test_elevation_trap` was not -- the same miss issue #76 found
                # in `manual_links.capture_text`. One copy cannot drift from
                # itself.
                with open(long_path(path), encoding="utf-8", newline="") as handle:
                    committed = handle.read()
                self.assertEqual(
                    committed.replace("\r\n", "\n"), module.beat() + "\n"
                )

    def test_the_capture_directory_is_inside_the_committed_captures(self):
        captures = REPO / "corridor-screen" / "captures"
        for name, module in beat_modules().items():
            with self.subTest(beat=name):
                self.assertEqual(module.CAPTURE_DIR.parent, captures)
                self.assertTrue(module.CAPTURE_DIR.is_dir())


if __name__ == "__main__":
    unittest.main()
