"""The pages in `docs/` held to the plain-language standard, issue #134.

`CLAUDE.md` has always said "prefer short sentences and concrete examples over
abstraction." That was a wish. Nothing counted it, so nothing stopped it being
ignored, and measuring the 38 reader-facing pages in issue #133 found what you
would expect: sentences running past forty words, sentences with two and three
em dashes in them, and one sentence of 219 words holding ten semicolons.

Issue #49 fixed the US English spelling in this repo by hand and left no test
behind. Nothing stops that coming back either. This file is the answer to both:
the standard is written down in `toolkit/.claude/skills/plain-language/`, and
what can be counted is counted here, on every pull request.

**What it counts.** Three rules, on every sentence of prose:

* over 40 words
* 2 or more em dashes
* any of the 55 words in `banned-words.md`

**Why an allowlist.** The pages are not swept yet. That work is the six child
work orders of #133, one per folder, one pull request each. Without a list of
the files not yet done this test would land red and stay red, and a red check
everyone has learned to ignore is worse than no check. So every unswept file is
named in `plain_language_allowlist.txt` and skipped, each child deletes its own
lines in the same pull request that fixes those files, and when the list is
empty the file and the code that reads it go too. The length of that list is how
much of #133 is left.

**How the allowlist is kept honest.** Two tests do it between them.
`test_every_page_not_on_the_list_is_clean` holds every other file to the three
rules. `test_every_file_on_the_list_really_is_dirty` fails on an entry that has
nothing wrong with it. Take a line out without fixing the file and the first
test picks it up; fix a file and forget to take its line out and the second one
does.

**Where the word list lives.** In the skill, not here. The skill is the document
a person and an agent both read, and a second copy of fifty-five words would
drift the first time somebody edited one of them. This file parses the table.

**What is permanently exempt, which is not the same as allowlisted.** An
allowlist entry is a debt that gets paid. An exemption is a decision that
stands. `docs/corridor-screen/spec.md` and `docs/txdot-research.md` are the
agent's own dated output and the evidence the demo happened; rewriting them to
read better would make the stage demo a lie. `docs/agents/` is read by software.
`docs/slides/beyond-the-prompt.md` is slide bullets and is already short.
`docs/adr/0003-produced-artifacts-stay-as-produced.md` writes that down.

**On reproducing #133's counts.** They do not reproduce here, and the difference
is in the reader rather than in the pages. Measured on 2026-09-15:

|  | #133, at triage | `markdown_docs.sentences` |
|---|---|---|
| Pages in `docs/` | 38 | 40 |
| Sentences | 2,031 | 2,391 |
| Over 40 words | 94 | 44 |
| 2 or more em dashes | 55 | 52 |

The em dash counts nearly agree. The sentence counts do not, and the gap runs
the way it would if the earlier splitter merged sentences that this one
separates -- most likely across the `**` that ends a bold run, which
`unemphasized` takes off before the split. The two page counts differ because
this test scans everything under `docs/` that is not exempt, where #133 also
held out `docs/vocabulary/index.md` as too short to bother with. It passes.

Both agree on the worst sentence in the repo, at 219 words in
`docs/slides/index.md`.

**#133's per-child table is therefore stale.** It tells #135 that
`docs/data-sources/` holds 31 sentences over forty words. Read the allowlist
header for the figures this test actually produces, and read
`markdown_docs.prose` before arguing with any of them.
"""

import re
import unittest
from pathlib import Path

from tests.markdown_docs import sentences, table_rows, text_of

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "toolkit" / ".claude" / "skills" / "plain-language"
WORD_LIST = SKILL / "banned-words.md"
ALLOWLIST = Path(__file__).resolve().parent / "plain_language_allowlist.txt"

# The numbers. They are the same three the skill states, and a test below holds
# the skill to them.
WORD_LIMIT = 40
EM_DASH_LIMIT = 2
EM_DASH = "—"
WORD_LIST_LENGTH = 55

# The folders this test reads. `docs/` is the reader-facing prose. The skill is
# in here because a standard that does not meet its own standard is not one --
# that is an acceptance criterion of #134 and it is checked by being in this
# tuple, not by a test of its own.
SCANNED = (
    REPO / "docs",
    SKILL,
)

# Settled in #133 and recorded in ADR 0003. These never go on the allowlist and
# they never come off this tuple. A folder is written with a trailing slash.
EXEMPT = (
    "docs/agents/",
    "docs/corridor-screen/spec.md",
    "docs/txdot-research.md",
    "docs/slides/beyond-the-prompt.md",
)

# Not scanned at all, which is the strongest form of exempt there is: they are
# not under any path in SCANNED, so no allowlist entry could ever reach them.
# `CONTEXT.md` is a glossary and stays dense, `CLAUDE.md` is rules for an agent.
# #133, decision 2. Checked, because "outside the tree" is the kind of fact that
# quietly stops being true when somebody widens a search path.
OUTSIDE_THE_TREE = ("CONTEXT.md", "CLAUDE.md", "README.md", "HANDOVER.md")


def relative(path):
    return path.relative_to(REPO).as_posix()


def is_exempt(name):
    return any(
        name == entry or name.startswith(entry)
        for entry in EXEMPT
    )


def scanned_files():
    """Every markdown file this standard applies to, as repo-relative paths."""
    found = []
    for root in SCANNED:
        for path in root.rglob("*.md"):
            name = relative(path)
            if not is_exempt(name):
                found.append(name)
    return sorted(found)


def banned_words():
    """The first column of the table in the skill's `banned-words.md`.

    Header and divider rows are dropped by shape rather than by position, so
    the table can gain a row above the list without this reading it as a word.
    """
    found = []
    for row in table_rows(text_of(WORD_LIST)):
        if len(row) != 2:
            continue
        word = row[0]
        if not word or word.startswith("-") or word == "Word or phrase":
            continue
        found.append(word)
    return found


def banned_pattern(word):
    """One banned word or phrase, as something to search a sentence with.

    `(?<![\\w-])` and `(?![\\w-])` rather than `\\b`, so `cutting-edge` is not
    matched inside a longer hyphenated word and `delve` is not matched inside
    `delved`. The apostrophe is matched either way it gets typed.
    """
    body = re.escape(word).replace("'", "['’]")
    return re.compile(r"(?<![\w-])" + body + r"(?![\w-])", flags=re.IGNORECASE)


BANNED = [(word, banned_pattern(word)) for word in banned_words()]


def faults(markdown):
    """Every place a piece of markdown breaks one of the three counted rules.

    Returns one string per fault, already written the way a failure message
    wants to read, because a check that says only "this file is wrong" leaves
    the next person to go and find out where.
    """
    found = []
    for sentence in sentences(markdown):
        words = len(sentence.split())
        if words > WORD_LIMIT:
            found.append(f"{words} words: {sentence[:90]}")
        if sentence.count(EM_DASH) >= EM_DASH_LIMIT:
            found.append(f"{sentence.count(EM_DASH)} em dashes: {sentence[:90]}")
        for word, pattern in BANNED:
            if pattern.search(sentence):
                found.append(f"the word {word!r}: {sentence[:90]}")
    return found


def allowlisted():
    """The files not swept yet. An empty or absent list means #133 is finished.

    Blank lines and `#` comments are skipped, so the list can explain itself to
    the person deleting lines out of it.
    """
    if not ALLOWLIST.is_file():
        return []
    found = []
    for line in text_of(ALLOWLIST).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            found.append(line)
    return found


class TestTheRulesCatchWhatTheyClaim(unittest.TestCase):
    """The three rules, each shown failing on a sentence written to break it.

    Without these the suite could go green because the checks never fire, which
    looks exactly like every page being clean.
    """

    def test_a_sentence_over_forty_words_fails(self):
        long_one = "The " + "word " * WORD_LIMIT + "ends here."
        self.assertEqual(len(long_one.split()), WORD_LIMIT + 3)
        self.assertTrue(
            any("words:" in fault for fault in faults(long_one)),
            "a sentence past the word limit was not caught",
        )

    def test_a_sentence_of_exactly_forty_words_passes(self):
        """The limit is where it says it is. Off by one here would move it."""
        exact = " ".join(["word"] * (WORD_LIMIT - 1)) + " ends."
        self.assertEqual(len(exact.split()), WORD_LIMIT)
        self.assertEqual(faults(exact), [])

    def test_a_sentence_with_two_em_dashes_fails(self):
        two = f"The zone {EM_DASH} which covers more than one county {EM_DASH} reports in feet."
        self.assertTrue(
            any("em dashes:" in fault for fault in faults(two)),
            "a sentence with two em dashes was not caught",
        )

    def test_a_sentence_with_one_em_dash_passes(self):
        one = f"The zone covers more than one county {EM_DASH} rather a lot more."
        self.assertEqual(faults(one), [])

    def test_a_banned_word_fails(self):
        for word, _ in BANNED:
            with self.subTest(word=word):
                sentence = f"The crew had to {word} before the survey could start."
                self.assertTrue(
                    any(repr(word) in fault for fault in faults(sentence)),
                    f"{word!r} is on the list and was not caught",
                )

    def test_a_banned_word_inside_a_longer_word_passes(self):
        """`delve` is banned. `delved` is a different word and is not."""
        self.assertEqual(faults("The crew delved through the old field notes."), [])

    def test_code_and_tables_are_not_prose(self):
        """The rules apply to writing. A command line is not writing.

        Without this a page would fail for quoting a long command correctly,
        which would teach the next person to stop quoting commands.
        """
        page = (
            "```bash\n"
            + "python -m tool " + "--flag value " * 30 + "\n"
            + "```\n\n"
            + "| a | b |\n|---|---|\n| " + "long " * 50 + " | x |\n"
        )
        self.assertEqual(faults(page), [])

    def test_a_blockquote_is_not_prose(self):
        """A quotation is somebody else's sentence, so it is not counted.

        `docs/governance/` quotes statute and board rules at length. Four of
        those sentences run past forty words because the Texas Legislature and
        the board wrote them that way, and `CLAUDE.md` does not allow a citation
        to be altered. #136 settled it: the counter stopped reading blockquotes.

        Without this test the skip is one line in `prose` that a refactor could
        drop, and the page it protects would start failing for quoting the law
        correctly.
        """
        page = "> " + "word " * 60 + "\n> and it ends here.\n"
        self.assertEqual(faults(page), [])

    def test_a_paragraph_under_a_blockquote_is_still_prose(self):
        """The skip takes the quotation and nothing else.

        A blockquote becomes a blank line rather than disappearing, so the
        paragraph after it is still its own paragraph. If the two ran together
        the page would be measured as sentences nobody wrote.
        """
        page = (
            "> " + "quoted " * 60 + "\n"
            "\n"
            + "The " + "word " * WORD_LIMIT + "ends here.\n"
        )
        self.assertTrue(
            any("words:" in fault for fault in faults(page)),
            "prose after a blockquote stopped being counted",
        )


class TestTheWordList(unittest.TestCase):
    """The skill's table, which is where the word list is actually kept."""

    def test_the_list_is_where_the_skill_says_it_is(self):
        self.assertTrue(WORD_LIST.is_file(), f"{relative(WORD_LIST)} is missing")

    def test_the_list_holds_fifty_five_words(self):
        self.assertEqual(
            len(BANNED),
            WORD_LIST_LENGTH,
            "the count in the skill's own prose and the rows in its table disagree",
        )

    def test_the_words_are_unique(self):
        words = [word.lower() for word, _ in BANNED]
        self.assertEqual(sorted(words), sorted(set(words)))


class TestTheSkillStatesTheSameRules(unittest.TestCase):
    """The standard and the check, held to each other.

    A skill that said 50 words while the test failed at 40 would send a writer
    to fix the wrong thing, and they would believe the skill.
    """

    def setUp(self):
        self.skill = text_of(SKILL / "SKILL.md")

    def test_there_is_a_skill(self):
        self.assertTrue((SKILL / "SKILL.md").is_file())

    def test_it_states_the_word_limit(self):
        self.assertIn(f"{WORD_LIMIT} words", self.skill)

    def test_it_states_the_length_of_the_word_list(self):
        self.assertIn("Fifty-five", text_of(WORD_LIST))

    def test_it_names_the_four_faults_no_test_counts(self):
        for fault in ("The flip", "Self-reference", "The stack", "The setup"):
            with self.subTest(fault=fault):
                self.assertIn(fault, self.skill)

    def test_it_credits_its_sources(self):
        for credit in ("plainlanguage.gov", "humanize-writing-skill", "MIT"):
            with self.subTest(credit=credit):
                self.assertIn(credit, self.skill)

    def test_it_needs_nothing_installed(self):
        """`CLAUDE.md`: git, a GitHub account and the Claude desktop app.

        The whole reason the other nine skills in the kit are vendored as
        markdown is that `npx` needs Node, which needs a Windows administrator
        in a lot of firms. A tenth skill that quietly reintroduced that would
        undo the point of the other nine.
        """
        for installer in ("npx ", "npm install", "pip install", "API key"):
            with self.subTest(installer=installer):
                self.assertNotIn(installer, self.skill)

    def test_the_kit_readme_explains_it(self):
        """`toolkit/.claude/skills/README.md` says why each skill is in there."""
        readme = text_of(SKILL.parent / "README.md")
        self.assertIn("plain-language", readme)


class TestThePagesThemselves(unittest.TestCase):
    """The standard, applied. The allowlist is what keeps this green today."""

    def test_something_is_being_scanned(self):
        """First, so a wrong path reports as one failure rather than as success.

        A glob that matched nothing would make every test below pass.
        """
        self.assertGreater(len(scanned_files()), 30)

    def test_every_page_not_on_the_list_is_clean(self):
        skip = set(allowlisted())
        for name in scanned_files():
            if name in skip:
                continue
            with self.subTest(page=name):
                self.assertEqual(
                    faults(text_of(REPO / name)),
                    [],
                    f"{name} breaks the plain-language standard",
                )

    def test_every_file_on_the_list_really_is_dirty(self):
        """An entry with nothing wrong with it is a line somebody forgot to cut.

        This is the other half of the allowlist being honest. Together with the
        test above it means the list cannot be padded and cannot go stale.
        """
        for name in allowlisted():
            with self.subTest(page=name):
                self.assertNotEqual(
                    faults(text_of(REPO / name)),
                    [],
                    f"{name} is clean now and its line in "
                    f"{ALLOWLIST.name} should be deleted",
                )

    def test_every_file_on_the_list_exists_and_is_scanned(self):
        scanned = set(scanned_files())
        for name in allowlisted():
            with self.subTest(page=name):
                self.assertIn(
                    name,
                    scanned,
                    "an allowlist entry that is not scanned does nothing",
                )

    def test_nothing_permanently_exempt_is_on_the_list(self):
        """The two are different promises and must not be confused.

        The allowlist empties out and gets deleted. The exemptions do not. An
        exempt file on the allowlist would be deleted from it by whichever child
        work order owns that folder, and then the exemption would be gone.
        """
        for name in allowlisted():
            with self.subTest(page=name):
                self.assertFalse(is_exempt(name), f"{name} is exempt, not owed")

    def test_the_adr_names_every_exempt_path(self):
        """`EXEMPT` is the list that bites. ADR 0003 is the list people read.

        Five places in this repo describe what is exempt: this tuple, the header
        of the allowlist, the ADR, the skill, and the row in `CONTEXT.md`. Four
        of those are prose about a decision and only this one is enforced, which
        is exactly the arrangement that drifts -- and it already had, on first
        review, with `CONTEXT.md` naming two paths where this tuple has four.

        The word list solved the same problem by moving the single source of
        truth into the skill. That does not work here, because the tuple has to
        be readable before any file is opened. So the ADR is held to the tuple
        instead, and a path added to one without the other fails loudly.
        """
        adr = text_of(REPO / "docs" / "adr"
                      / "0003-produced-artifacts-stay-as-produced.md")
        for entry in EXEMPT:
            with self.subTest(path=entry):
                self.assertIn(
                    entry.rstrip("/"),
                    adr,
                    f"{entry} is exempt in the code and unexplained in the ADR",
                )

    def test_the_files_outside_the_tree_stay_outside_it(self):
        scanned = set(scanned_files())
        for name in OUTSIDE_THE_TREE:
            with self.subTest(page=name):
                self.assertNotIn(name, scanned)


if __name__ == "__main__":
    unittest.main()
