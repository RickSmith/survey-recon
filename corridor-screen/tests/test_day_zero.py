"""The Day 0 setup guide, held to the parts of #28 a machine can settle.

`docs/day-0/index.md` is the only page in this repo a reader opens before they
own anything. Every other page assumes the three prerequisites are installed.
This one is the reason they are.

That makes it the page whose failure is hardest to see from the inside. A
maintainer with git, a GitHub account and the desktop app already working cannot
tell by reading whether the page gets somebody there, because the page cannot
fail for them. So:

* **It is reachable in one click**, from the landing page and from the top level
  of the menu -- an acceptance criterion that is one edit to `mkdocs.yml` away
  from quietly stopping being true
* **It needs nothing beyond the three.** No Node, no npx, no Docker, and an API
  key only ever mentioned to deny it. The commands are checked inside the fenced
  blocks, because a code block is where a fourth prerequisite actually gets in
* **The addresses are the toolkit's addresses.** Every download link on the page
  is one `toolkit/README.md` already hands out. Two documents sending a reader to
  two different installers is how one of them ends up wrong
* **It covers all three, fills the kit in, and then checks that it worked** --
  sections, rather than mentions
* **The screenshot slots are honest.** Numbered without gaps, each saying what it
  must show, and each either carrying its image or saying on the page that it
  does not

**Why this file can check screenshots at all.** It cannot check that a
screenshot is good, or that it is of the right thing. It checks the two failures
that have no other alarm: a slot nobody ever filled reaching the projector
looking like a finished page, and an image landing in the folder that no slot
points at. `mkdocs build --strict` catches a broken image reference; nothing
catches an image that is simply never referenced.

**What this file deliberately does not do.** It does not check that the guide
works. Only somebody who has never done it can settle that, which is
[#9](https://github.com/RickSmith/survey-recon/issues/9), and no test replaces
it. Two of #28's six criteria are that person's, not this file's.
"""

import re
import unittest
from pathlib import Path

from tests.markdown_docs import flat, headings, local_link_targets, text_of

REPO = Path(__file__).resolve().parents[2]

GUIDE = REPO / "docs" / "day-0" / "index.md"
IMAGES = REPO / "docs" / "day-0" / "img"
LANDING = REPO / "docs" / "index.md"
NAV = REPO / "mkdocs.yml"
TOOLKIT_README = REPO / "toolkit" / "README.md"

# The three prerequisites, plus the step that turns a copied folder into *your
# firm's* agent rather than a stranger's. Their addresses are not written here --
# they are read back out of `toolkit/README.md` below, which is the document that
# already promises them. Written twice, they would drift the first time one of
# them moved.
#
# Each entry is a word the guide has to have a section about.
THE_THREE = ["GitHub account", "git", "Claude desktop app"]

# `toolkit/README.md` puts "Filling it in" before "Checking that it worked", and
# it is right to. A reader who copies the kit and stops has an agent holding a
# handbook that still says «FIRM NAME», which is the one outcome this guide's own
# opening sentence promises against.
FILLING_IN = "claude.md"  # lowercased, because `headings` lowercases what it returns

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
#   !!! info "Screenshot 4 — the installer page about your PATH"
#
# The number is what makes the set checkable: a slot inserted in the middle
# without renumbering, and a slot deleted, both show up as a gap.
SLOT = re.compile(r'^!!!\s+\w+\s+"Screenshot (\d+)\s*[-—]\s*(.+)"\s*$', re.MULTILINE)

# An image inside a slot, as the page references it. Every capture lands in
# `docs/day-0/img/`, so a slot carrying one of these is a slot that has been
# filled.
IMAGE_IN_A_SLOT = re.compile(r"\]\(img/([^)\s]+)\)")

# What every slot has to say about its picture. Two spellings, because the
# sentence outlives the capture:
#
#   **Not captured yet.** Must show: the sign-up form as it first loads
#   **Shows:** the sign-up form as it first loads
#
# Before the shot it stops whoever holds the camera having to guess, and a slot
# saying only "screenshot here" is one that gets taken wrong and re-taken on the
# morning of the session. After the shot the same sentence is the caption, and
# it is the only way anybody re-taking the picture in a year knows what it was
# supposed to contain. Screens change; the requirement does not.
WHAT_IT_SHOWS = ("Must show:", "**Shows:**")

# The sentence an empty slot carries. It is what makes the gap visible to a
# reader rather than only to a maintainer.
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


def slots():
    """Every screenshot slot as (number, title, the text under it), in order."""
    parts = re.split(SLOT, guide())[1:]
    return [tuple(parts[at:at + 3]) for at in range(0, len(parts), 3)]


def code_blocks(markdown):
    """Everything inside triple-backtick fences, as a list of blocks.

    The fence line comes back too -- a fence naming powershell names a language,
    not a command, and no check here cares about the difference.
    """
    return re.findall(r"^```.*?^```", markdown, flags=re.MULTILINE | re.DOTALL)


def sentences(markdown):
    """The page as sentences, flattened, for checks that need one at a time."""
    return re.split(r"(?<=[.!?])\s+", flat(markdown))


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
    """#28: reachable within one click of the site's landing page."""

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
    """#28: starts from zero and assumes no terminal experience."""

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

    def test_it_has_the_reader_fill_the_kit_in(self):
        """Installing three things and copying a folder is not a working agent.
        It is a working agent belonging to nobody, reading a handbook with the
        firm name still in guillemets."""
        self.assertTrue(
            any(FILLING_IN in heading for heading in headings(guide())),
            "no section of the guide has the reader fill in CLAUDE.md, so they "
            "finish with a handbook that names no firm and no signer. "
            "toolkit/README.md puts this before the check that it worked.",
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
    """#28: never requires Node, npx, or an API key."""

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
        the three turns three prerequisites into four.

        Skipped rather than passed when the guide does not mention it at all. A
        conditional check that returns early reports success while testing
        nothing, which is worse than reporting that it did not run.
        """
        markdown = guide()
        if "cli.github.com" not in markdown:
            self.skipTest("the guide does not mention GitHub CLI")
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
    """#28: screenshots at every step where a reader could get lost.

    The slots are the specification for the captures. They are checked; the
    photographs are not, and cannot be.
    """

    def test_there_are_slots_at_all(self):
        self.assertTrue(
            slots(),
            "no screenshot slots on a guide whose issue calls for screenshots "
            "at every step where a reader could get lost",
        )

    def test_they_are_numbered_from_one_without_gaps(self):
        numbers = [int(number) for number, _, _ in slots()]
        self.assertEqual(
            list(range(1, len(numbers) + 1)),
            numbers,
            "the screenshot numbers skip, repeat, or start somewhere other than "
            "1. They are how whoever holds the camera keeps their place.",
        )

    def test_every_slot_says_what_it_shows(self):
        """A slot without this is a slot that gets captured twice, and a picture
        nobody can re-take correctly once the screen behind it changes."""
        for number, _, body in slots():
            self.assertTrue(
                any(wording in body for wording in WHAT_IT_SHOWS),
                f"screenshot {number} does not say what it shows, in either the "
                f"wording an empty slot uses or the wording a filled one does",
            )

    def test_every_slot_either_carries_its_image_or_says_it_does_not(self):
        """Checked one slot at a time, deliberately.

        The first version of this checked the folder instead: if any image had
        been captured, it stopped checking every slot. The day the first
        screenshot landed, the other eleven would have gone unwatched -- which is
        exactly the silent failure this class exists to catch, rebuilt inside the
        check meant to catch it.
        """
        for number, _, body in slots():
            if IMAGE_IN_A_SLOT.search(body):
                continue
            self.assertIn(
                NOT_CAPTURED,
                body,
                f"screenshot {number} has no image and does not say so, so it "
                f"reads on the page as though it were finished",
            )

    def test_every_image_a_slot_claims_is_really_there(self):
        for number, _, body in slots():
            for name in IMAGE_IN_A_SLOT.findall(body):
                self.assertTrue(
                    (IMAGES / name).is_file(),
                    f"screenshot {number} points at img/{name}, which is not in "
                    f"docs/day-0/img/",
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
        for target in local_link_targets(guide()):
            page = (GUIDE.parent / target).resolve()
            self.assertTrue(page.exists(), f"{target} is not a file in docs/")


if __name__ == "__main__":
    unittest.main()
