"""The workflow that runs this suite, held to the suite it claims to run.

Issue #78: until this landed, GitHub Actions ran no tests at all. `docs.yml`
built the site and `slides.yml` built the deck, and a pull request that broke
every test in the repo went green.

That was a gap under any circumstances and a sharper one here, because a good
half of these tests exist to stop a demo artifact drifting away from the code
that made it — the tool replaying with the network removed, the fallback card
held to the run of show, the deck held to the same table, each failure beat
pinned to its committed transcript. Every one of those protects something that
goes on a projector on October 8, 2026. A check nobody runs protects nothing.

**Why a test about a workflow, rather than trusting the workflow.** The
workflow is the only file in this repo that cannot fail loudly in the place it
is wrong. A workflow quietly running a narrower command than the one the docs
hand a presenter looks exactly like success: a green tick, and a different
suite behind it.

**What this can and cannot see.** `tests.yml` is read as text, not parsed —
PyYAML is not a dependency of this repo and `CLAUDE.md` sets a hard line on
adding one for a single file. Text matching cannot tell a setting from a
sentence about a setting, so the `on:` block is read with the comments stripped
off. The rest is matched against a file whose comments were written knowing
that, and the real proof is the run itself: a deliberately broken test was
confirmed to exit non-zero before this went up.
"""

import re
import unittest
from pathlib import Path

from corridor_screen.cache import long_path

from tests.markdown_docs import text_of

REPO = Path(__file__).resolve().parents[2]
TESTS_WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"
DOCS_WORKFLOW = REPO / ".github" / "workflows" / "docs.yml"
CARD = REPO / "docs" / "presenting" / "fallbacks.md"
TOOL_README = REPO / "corridor-screen" / "README.md"

# The one command, and the folder it only works from. Written here once because
# this file is what holds the workflow's copy and the tool README's to each
# other.
THE_COMMAND = "python -m unittest discover -s tests -t ."
THE_FOLDER = "corridor-screen"

# `corridor-screen/README.md`: "Python 3.11 or newer ... the floor because it
# is the first version that reads TOML on its own". CI may run a later one; it
# may not run an earlier one.
THE_PYTHON_FLOOR = (3, 11)


def workflow_text():
    return text_of(TESTS_WORKFLOW)


def without_comments(yaml_text):
    """The workflow with whole-line comments removed.

    This file matches text rather than parsing YAML, so without this a
    commented-out `# pull_request:` would satisfy a check about triggers. It
    only removes whole-line comments, which is all this workflow has.
    """
    return "\n".join(
        line for line in yaml_text.splitlines() if not line.lstrip().startswith("#")
    )


class TestTheWorkflowRunsThisSuite(unittest.TestCase):
    """The acceptance criteria of #78, one test each."""

    def test_there_is_a_workflow_that_runs_the_tests(self):
        """First, so that a missing file reports as one failure with a sentence
        rather than as seven identical `FileNotFoundError`s."""
        self.assertTrue(
            Path(long_path(TESTS_WORKFLOW)).is_file(),
            "nothing in .github/workflows runs the test suite",
        )

    def test_it_runs_the_same_command_the_tool_readme_hands_a_person(self):
        """A narrower command in CI is a green tick about a different suite.

        `discover -s tests -t .` is load-bearing in both halves: `-s` is where
        the tests are and `-t` is the folder imports resolve against. Get
        either wrong and most of the suite is not collected, which reports as
        success.
        """
        self.assertIn(THE_COMMAND, workflow_text())
        self.assertIn(THE_COMMAND, text_of(TOOL_README))

    def test_it_runs_the_command_from_the_folder_the_command_needs(self):
        """`-t .` means "imports resolve against here", and here has to be
        `corridor-screen` or nothing imports `corridor_screen` at all."""
        self.assertRegex(
            without_comments(workflow_text()),
            rf"(working-directory:\s*{re.escape(THE_FOLDER)}|cd {re.escape(THE_FOLDER)})",
            f"the workflow never says to run in {THE_FOLDER}",
        )

    def test_it_runs_on_a_push_to_main_and_on_every_pull_request(self):
        """The triggers #78 asked for, in the shape `docs.yml` already uses.

        The brief on #78 is explicit about the second half: *"A reader who
        understands one workflow in this repo should understand the next one
        without learning a second style."* An earlier draft of this workflow
        triggered on every push to every branch, which is a defensible choice
        and not the one that was asked for.
        """
        triggers = without_comments(workflow_text())
        triggers = triggers[: triggers.index("jobs:")]
        self.assertRegex(triggers, r"push:\s*\n\s*branches:\s*\[\s*main\s*\]")
        self.assertIn("pull_request:", triggers)

    def test_it_triggers_the_way_the_site_workflow_does(self):
        """The same claim, made against `docs.yml` rather than against a
        string here, so the two cannot drift apart quietly."""
        mine = without_comments(workflow_text())
        theirs = without_comments(text_of(DOCS_WORKFLOW))
        wanted = re.compile(r"push:\s*\n\s*branches:\s*\[\s*main\s*\]")
        self.assertRegex(theirs, wanted, "docs.yml no longer triggers the way this copies")
        self.assertRegex(mine, wanted)

    def test_it_installs_nothing(self):
        """`CLAUDE.md`: the tool has no dependencies and the workflow must not
        invent any. A `pip install` here is also the first step toward a lock
        file nobody updates.

        Read with the comments left in on purpose. The workflow explains at
        length why it installs nothing, and a comment that said `pip install`
        while arguing against it would be exactly the sentence to catch.
        """
        for forbidden in ("pip install", "pip3 install", "poetry install", "-r requirements"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, workflow_text())

    def test_it_asks_for_a_python_at_or_above_the_floor_the_tool_states(self):
        asked = re.search(r"python-version:\s*['\"]?(\d+)\.(\d+)", without_comments(workflow_text()))
        self.assertIsNotNone(asked, "the workflow does not pin a Python version")
        self.assertGreaterEqual(
            (int(asked.group(1)), int(asked.group(2))), THE_PYTHON_FLOOR,
            f"the tool states Python {'.'.join(map(str, THE_PYTHON_FLOOR))} or newer",
        )

    def test_the_floor_it_asks_for_is_the_floor_the_tool_states(self):
        """Read out of the tool's own README rather than trusted from up there."""
        stated = re.search(r"Python (\d+)\.(\d+) or newer", text_of(TOOL_README))
        self.assertIsNotNone(stated, "the tool README no longer states a Python floor")
        self.assertEqual((int(stated.group(1)), int(stated.group(2))), THE_PYTHON_FLOOR)

    def test_a_run_on_main_is_never_canceled(self):
        """"A push to `main` runs the full suite" is the point of the push
        trigger, and two merges landing close together would otherwise leave
        the first commit on main with no answer at all.

        Superseded pull request runs may still be canceled. Nothing is
        published by this workflow, so there is nothing to leave half-done.
        """
        concurrency = without_comments(workflow_text())
        if "concurrency:" not in concurrency:
            self.skipTest("the workflow sets no concurrency group, so nothing is canceled")
        setting = re.search(r"cancel-in-progress:\s*(.+)", concurrency)
        self.assertIsNotNone(setting, "there is a concurrency group and no cancel setting")
        self.assertNotEqual(
            setting.group(1).strip(), "true",
            "this cancels a run on main, which is the one run that has to finish",
        )


class TestTheFallbackCardNoLongerSaysNobodyRunsIt(unittest.TestCase):
    """The last acceptance criterion of #78, and the one most likely to be
    forgotten: the page that documented the gap has to stop documenting it.

    A page that says a check is not running, when it is, teaches a presenter to
    do work by hand that is already being done — and quietly suggests the green
    tick on the pull request means less than it does.

    **Scoped to the two pages that said it.** An earlier draft of this banned
    the sentences from every page under `docs/`, which is a trap in a repo that
    deliberately keeps wrong things verbatim: `the-force-push.md` and
    `the-claim-we-got-wrong.md` exist to preserve a claim that was wrong, and
    `the-superseded-manual.md` now quotes its own bad draft on purpose.
    """

    # The opening of the paragraph #78 asked to have removed, named exactly:
    # "It is under *How this page is kept honest* and it begins 'Somebody still
    # has to run that suite.'"
    THE_PARAGRAPH = "Somebody still has to run that suite"

    def test_the_paragraph_the_work_order_named_is_gone(self):
        self.assertFalse(
            self.THE_PARAGRAPH in text_of(CARD),
            f"the fallback card still opens a paragraph {self.THE_PARAGRAPH!r}",
        )

    def test_the_sentence_above_it_is_left_reading_correctly(self):
        """#78 asked for that too, by name, and it is the sentence the whole
        paragraph used to qualify."""
        self.assertIn("This one fails the test suite instead.", text_of(CARD))

    def test_the_card_no_longer_claims_actions_runs_no_tests(self):
        self.assertFalse("does not run a single test" in text_of(CARD))

    def test_the_managing_page_no_longer_claims_it_either(self):
        """`the-superseded-manual.md` carried the same claim in its own words,
        on the one page in this repo whose subject is a sentence that reads as
        a guarantee and is not one. Searching the card's wording alone left it
        standing."""
        page = REPO / "docs" / "managing-your-agent" / "the-superseded-manual.md"
        body = text_of(page)
        self.assertFalse(
            "neither runs the Python tests" in body,
            "the-superseded-manual.md still says neither workflow runs the tests",
        )
        self.assertFalse("It does not yet fail CI" in body)


class TestDiscoveryReachesEveryTestInTheFolder(unittest.TestCase):
    """The failure #78 is really about, in its purest form.

    A file of tests that discovery never reaches does not fail. It does not
    run, and the suite reports OK without it. CI would then be green about a
    file nobody has executed since it was written, which is worse than having
    no CI at all, because now there is a tick arguing otherwise.

    `unittest discover` opens `test*.py` and nothing else, so the check is on
    the name against the contents rather than on the name alone. An earlier
    draft asserted that two helper filenames did not start with "test" — which,
    given the filenames were literals in the test, could not fail.
    """

    def test_every_file_holding_a_test_case_is_named_so_discovery_finds_it(self):
        folder = REPO / "corridor-screen" / "tests"
        missed = []
        for path in sorted(Path(long_path(folder)).glob("*.py")):
            if path.name.startswith("test"):
                continue
            if "unittest.TestCase" in text_of(path):
                missed.append(path.name)
        self.assertEqual(
            missed, [],
            "these hold test cases and `discover` will never open them",
        )

    def test_the_folder_holds_the_helpers_the_tests_import(self):
        """The other direction, and not a tautology: these are read off disk.

        `markdown_docs` and `slide_canvas` are imported by tests rather than
        being tests. If either were renamed to start with `test`, discovery
        would import it looking for cases — and the check above would stop
        being able to see it at all.
        """
        folder = Path(long_path(REPO / "corridor-screen" / "tests"))
        helpers = sorted(
            path.name for path in folder.glob("*.py")
            if not path.name.startswith(("test", "__"))
        )
        self.assertEqual(helpers, ["markdown_docs.py", "slide_canvas.py"])


if __name__ == "__main__":
    unittest.main()
