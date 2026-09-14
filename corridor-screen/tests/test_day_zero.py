"""The Day 0 setup guide, held to the five things #28 asks of it.

`docs/day-0/index.md` is the only page in this repo a reader opens before they
own anything. Every other page assumes the three prerequisites are installed.
This one is the reason they are.

That makes it the page whose failure is hardest to see from the inside. A
maintainer with git, a GitHub account and the desktop app already working cannot
tell by reading whether the page gets somebody there, because the page cannot
fail for them. So the parts of #28 a machine can settle are settled here:

* **It is reachable in one click**, from the landing page and from the top level
  of the menu -- an acceptance criterion that is one edit to `mkdocs.yml` away
  from quietly stopping being true
* **It needs nothing beyond the three.** No Node, no npx, no Docker, and an API
  key only ever mentioned to deny it. The commands are checked inside the fenced
  blocks, because a code block is where a fourth prerequisite actually gets in
* **The addresses are the toolkit's addresses.** Every download link on the page
  is one `toolkit/README.md` already hands out. Two documents sending a reader to
  two different installers is how one of them ends up wrong
* **It covers all three, and then checks that it worked.** Three sections and a
  verification, rather than three mentions
* **The screenshot slots are honest.** Numbered without gaps, each saying what it
  must show, and none left behind once the image beside it exists

**Why this file can check screenshots at all.** It cannot check that a
screenshot is good, or that it is of the right thing. It checks the two failures
that have no other alarm: a slot nobody ever filled going to the projector
looking like a finished page, and an image landing in the folder that no slot on
the page points at. Both are silent. `mkdocs build --strict` catches a broken
image reference; nothing catches an image that is simply never referenced.

**What this file deliberately does not do.** It does not check that the guide
works. Only a person who has never done it can settle that, which is
[#9](https://github.com/RickSmith/survey-recon/issues/9), and no test replaces
it.
"""

import re
import unittest
from pathlib import Path

from tests.markdown_docs import flat, text_of

REPO = Path(__file__).resolve().parents[2]

GUIDE = REPO / "docs" / "day-0" / "index.md"
IMAGES = REPO / "docs" / "day-0" / "img"
LANDING = REPO / "docs" / "index.md"
NAV = REPO / "mkdocs.yml"
TOOLKIT_README = REPO / "toolkit" / "README.md"

# The three prerequisites. Their addresses are not written here -- they are read
# back out of `toolkit/README.md` below, which is the document that already
# promises them. Written twice, they would drift the first time one of them
# moved.
#
# Each entry is a word the guide has to have a section about.
THE_THREE = ["GitHub account", "git", "Claude desktop app"]

# What a fourth prerequisite looks like sneaking in through a code block. These
# are the exact tools `CLAUDE.md` rules out of the attendee path:
#
#   "Do not add a Node dependency to anything attendees run."
#
# Matched inside fenced blocks only. The page is allowed -- and expected -- to
# say the words in prose, because "you do not need Node" is the promise being
# kept rather than broken. A command is the promise being broken.
FORBIDDEN_IN_A_CODE_BLOCK = ["npx", "npm", "node", "docker", "pip", "yarn"]

# An API key on the page, and the words that make a mention of one a denial
# rather than an instruction.
#
# The first draft of this banned the phrase outright, reasoning that a setup
# guide never needs it. That was wrong, and `docs/toolkit/index.md` is why: it
# says "no Node, npm, npx, Docker, or an API key" as reassurance, and heading off
# that fear is worth more than avoiding the words. What #28's criterion is
# actually about is the guide never sending somebody to go and get one.
#
# Checked one sentence at a time, on the flattened page, so a sentence the
# eighty-column wrapping split across two lines is still read as one sentence.
API_KEY = re.compile(r"\bAPI key\b", re.IGNORECASE)
DENIAL = re.compile(
    r"\b(no|not|never|nothing|none|without|neither|nor)\b", re.IGNORECASE
)

# A screenshot slot. One admonition, one number, one short title.
#
#   !!! info "Screenshot 4 - the installer page about your PATH"
#
# The number is what makes the set checkable: a slot inserted in the middle
# without renumbering, and a slot deleted, both show up as a gap.
SLOT = re.compile(r'^!!!\s+\w+\s+"Screenshot (\d+)\s*[-—]\s*(.+)"\s*$', re.MULTILINE)

# What every slot has to promise, so whoever holds the camera does not have to
# guess. A slot that says only "screenshot here" is a slot that gets captured
# wrong once and re-captured on the morning of the session.
WHAT_IT_MUST_SHOW = "Must show:"

# The sentence a slot carries while it is still empty. It is what makes an
# unfilled slot visible to a reader rather than only to a maintainer, and it is
# how this file tells an empty slot from a filled one.
NOT_CAPTURED = "Not captured yet"


def guide():
    return text_of(GUIDE)


def captured_images():
    """The screenshots that have actually been taken.

    A dotfile is not a screenshot. `docs/day-0/img/.gitkeep` is what keeps the
    empty folder in git, and counting it would tell this file the captures were
    finished on the day the folder was created.
    """
    if not IMAGES.is_dir():
        return []
    return sorted(
        image
        for image in IMAGES.iterdir()
        if image.is_file() and not image.name.startswith(".")
    )


def code_blocks(markdown):
    """Everything inside triple-backtick fences, as a list of blocks.

    The fence line comes back too -- a fence naming powershell names a language,
    not a command, and no check here cares about the difference.
    """
    return re.findall(r"^```.*?^```", markdown, flags=re.MULTILINE | re.DOTALL)


def sentences(markdown):
    """The page as sentences, flattened, for checks that need one at a time."""
    return re.split(r"(?<=[.!?])\s+", flat(markdown))


def headings(markdown):
    """Every heading on the page, lowercased, with the typesetting taken off."""
    found = re.findall(r"^#{1,6}\s+(.*)$", markdown, flags=re.MULTILINE)
    return [line.replace("*", "").replace("`", "").strip().lower() for line in found]


def addresses(markdown):
    """Every http address in a document, without its surrounding markdown.

    Both the bracketed link form and the bare angle-bracket form, which
    `toolkit/README.md` uses for its three prerequisites.
    """
    found = re.findall(r"\]\((https?://[^)\s]+)\)", markdown)
    found += re.findall(r"<(https?://[^>\s]+)>", markdown)
    return {address.rstrip("/.,") for address in found}


def prerequisite_addresses():
    """The install addresses `toolkit/README.md` hands out, as a set.

    The toolkit README is the source. It is the file a reader who never opens the
    website still gets, because it travels inside the folder they copy.
    """
    return addresses(text_of(TOOLKIT_README))


class TheGuideIsReachableInOneClick(unittest.TestCase):
    """#28, last criterion: reachable within one click of the landing page."""

    def test_the_landing_page_links_to_it(self):
        self.assertIn(
            "day-0/index.md",
            text_of(LANDING),
            "the site's front page does not link to the setup guide, so a "
            "reader who has installed nothing has nowhere to start",
        )

    def test_the_menu_has_it_at_the_top_level(self):
        """A top-level entry is one click. A page nested under a section heading
        is two, and the criterion says one."""
        top_level = [
            line
            for line in text_of(NAV).splitlines()
            if line.startswith("  - ") and "day-0/index.md" in line
        ]
        self.assertEqual(
            1,
            len(top_level),
            "day-0/index.md is not a top-level entry in the mkdocs.yml menu",
        )


class TheGuideStartsFromZero(unittest.TestCase):
    """#28, first criterion: starts from zero, assumes no terminal experience."""

    def test_it_is_no_longer_a_stub(self):
        markdown = guide().lower()
        for leftover in ("placeholder", "to be written", "this page is a stub"):
            self.assertNotIn(leftover, markdown)

    def test_it_has_a_section_for_each_of_the_three(self):
        found = headings(guide())
        for prerequisite in THE_THREE:
            self.assertTrue(
                any(prerequisite.lower() in heading for heading in found),
                f"no section of the guide is about installing {prerequisite!r}. "
                f"The words being somewhere in the prose is the page mentioning "
                f"a prerequisite, which is what the stub already did.",
            )

    def test_it_ends_by_checking_that_it_worked(self):
        """A setup guide that stops at the last install leaves the reader
        guessing whether they are done. `toolkit/README.md` already settles what
        the check is -- typing one command and seeing the agent answer -- and the
        guide has to arrive at the same one."""
        self.assertIn(
            "/grill-with-docs",
            guide(),
            "the guide never has the reader prove the setup works. That is the "
            "check toolkit/README.md uses, and it is the difference between "
            "finished and probably finished.",
        )

    def test_it_says_where_to_go_next(self):
        self.assertIn("toolkit/index.md", guide())


class TheGuideNeedsNothingBeyondTheThree(unittest.TestCase):
    """#28, fifth criterion: never requires Node, npx, or an API key."""

    def test_no_code_block_installs_a_fourth_thing(self):
        for block in code_blocks(guide()):
            for tool in FORBIDDEN_IN_A_CODE_BLOCK:
                found = re.search(rf"(?<![\w-]){re.escape(tool)}(?![\w-])", block)
                self.assertIsNone(
                    found,
                    f"{tool!r} is being run in a code block on the one page "
                    f"whose promise is git, a GitHub account and the desktop "
                    f"app. CLAUDE.md: do not add a Node dependency to anything "
                    f"attendees run.",
                )

    def test_an_api_key_is_only_ever_mentioned_to_deny_it(self):
        for sentence in sentences(guide()):
            if not API_KEY.search(sentence):
                continue
            self.assertTrue(
                DENIAL.search(sentence),
                f"an API key is mentioned without being denied: {sentence!r}. "
                f"CLAUDE.md: anything that needs an API key does not belong in "
                f"the attendee path.",
            )

    def test_the_optional_fourth_thing_is_marked_optional(self):
        """GitHub CLI is the one honest asterisk, and both the toolkit README and
        the toolkit page mark it as skippable. A setup guide that lists it beside
        the three turns three prerequisites into four."""
        markdown = guide()
        if "cli.github.com" not in markdown:
            return
        self.assertIn(
            "optional",
            flat(markdown).lower(),
            "GitHub CLI is on the page but nothing says it is optional",
        )


class TheAddressesAreTheToolkitsAddresses(unittest.TestCase):
    """Two documents, one set of download links."""

    # The hosts a reader downloads something from. A link to the repo itself, or
    # to a file inside it, is not an installer and is not checked here.
    INSTALLER_HOSTS = (
        "git-scm.com",
        "github.com/signup",
        "claude.ai",
        "cli.github.com",
    )

    def test_every_install_address_is_one_the_toolkit_hands_out(self):
        """The guide may link to fewer than the toolkit does. It may not invent
        one."""
        from_toolkit = prerequisite_addresses()
        self.assertTrue(from_toolkit, "no addresses found in toolkit/README.md")
        installers = {
            address
            for address in addresses(guide())
            if any(host in address for host in self.INSTALLER_HOSTS)
        }
        self.assertTrue(
            installers,
            "the guide links to none of the three downloads it is about",
        )
        for address in installers:
            self.assertIn(
                address,
                from_toolkit,
                f"{address} is not the address toolkit/README.md sends people "
                f"to. One of the two documents is now wrong, and a reader only "
                f"ever sees one of them.",
            )


class TheScreenshotSlotsAreHonest(unittest.TestCase):
    """#28, second criterion: screenshots at every step a reader could get lost.

    The slots are the specification for the captures. They are checked; the
    photographs are not, and cannot be.
    """

    def slots(self):
        return SLOT.findall(guide())

    def bodies(self):
        """Each slot as (number, title, everything under it), in page order."""
        parts = re.split(SLOT, guide())[1:]
        return [tuple(parts[at:at + 3]) for at in range(0, len(parts), 3)]

    def test_there_are_slots_at_all(self):
        self.assertTrue(
            self.slots(),
            "no screenshot slots on a guide whose issue calls for screenshots "
            "at every step where a reader could get lost",
        )

    def test_they_are_numbered_from_one_without_gaps(self):
        numbers = [int(number) for number, _ in self.slots()]
        self.assertEqual(
            list(range(1, len(numbers) + 1)),
            numbers,
            "the screenshot numbers skip, repeat, or start somewhere other than "
            "1. They are how whoever holds the camera keeps their place.",
        )

    def test_every_slot_says_what_it_must_show(self):
        """A slot without this is a slot that gets captured twice."""
        for number, _, body in self.bodies():
            self.assertIn(
                WHAT_IT_MUST_SHOW,
                body,
                f"screenshot {number} does not say what it has to show, so it "
                f"cannot be captured without asking",
            )

    def test_an_uncaptured_slot_says_so_on_the_page(self):
        """While the folder is empty, every slot is empty, and a reader is told
        rather than left wondering whether their browser failed to load an
        image."""
        if captured_images():
            return
        for number, _, body in self.bodies():
            self.assertIn(
                NOT_CAPTURED,
                body,
                f"screenshot {number} has no image and does not say so",
            )

    def test_every_captured_image_is_on_the_page(self):
        """The failure with no other alarm. A broken image reference stops
        `mkdocs build --strict`; an image that landed in the folder and was never
        referenced stops nothing, and looks exactly like a finished capture
        list."""
        markdown = guide()
        for image in captured_images():
            self.assertIn(
                image.name,
                markdown,
                f"{image.name} is in docs/day-0/img/ and no slot on the guide "
                f"points at it",
            )


class TheGuidesLinksGoSomewhere(unittest.TestCase):
    def test_every_page_it_links_to_is_committed(self):
        """`mkdocs build --strict` catches this too, but only once somebody
        builds the site. The suite runs on every pull request."""
        for target in re.findall(r"\]\(([^)]+)\)", guide()):
            if target.startswith("http") or target.startswith("#"):
                continue
            page = (GUIDE.parent / target.split("#")[0]).resolve()
            self.assertTrue(page.exists(), f"{target} is not a file in docs/")


if __name__ == "__main__":
    unittest.main()
