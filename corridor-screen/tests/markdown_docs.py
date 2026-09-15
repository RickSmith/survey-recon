"""Reading a committed markdown document, for the tests that check one.

Six test files hold a page in `docs/` to what it claims:

* `test_fallbacks.py` — the fallback card, against the run of show
* `test_deck.py` — the slide deck, against the same table
* `test_plan_of_record.py` — the run of show's own Act II figures, against the
  SH16 run in `project-sh16/screening.json`
* `test_principals_brief.py` — the one-page handout, against the crew-day
  build-up its cost figures are read out of
* `test_day_zero.py` — the setup guide, against the toolkit README it has to
  hand out the same three download addresses as
* `test_plain_language.py` — every page, against the plain-language standard.
  The one that reads prose rather than tables. See the second half of this file

The first five have to open a file, find a heading, and read a table out from under
it. Those three functions were written twice before they were written here, and
the second copy is what this module exists to delete. The reason is
`test_fallbacks.py`'s own, about the helpers it borrows rather than copies:

> Two copies of any of them would drift the first time somebody fixed one of
> them.

**What is deliberately not here.** Each test file keeps its own idea of what a
time looks like, and its own reader for the run of show. Those two files check
different documents and should be able to disagree about the shape of a row
without one of them being edited to suit the other — `test_fallbacks` anchors
its time pattern to a whole cell, `test_deck` searches for one inside a line of
prose. Sharing those would be sharing a coincidence.
"""

import json
import re

from corridor_screen.cache import long_path


def text_of(path):
    """Read a committed file, through the door that survives a long path.

    A surveyor's checkout sits under something like "OneDrive - Some Long Firm
    Name\\Documents\\Projects", and this repo's own worktrees already push a
    capture past the 260 characters Windows opens without being asked in the
    extended form. `cache.long_path` is how every other read here gets in.
    """
    with open(long_path(path), "r", encoding="utf-8") as handle:
        return handle.read()


def flat(markdown):
    """The document as one long line, for checking that a phrase is in it.

    Every page in `docs/` is hard-wrapped at about eighty characters, so half
    the phrases worth checking have a line break somewhere in the middle of
    them. A break is where the wrapping fell, not something the page says, and a
    check that fails when a sentence is re-wrapped is a check that punishes
    editing.

    `test_plan_of_record.py` was already doing this inline before it had a name.
    It lives here for the module's own reason: two copies would drift the first
    time somebody fixed one of them.
    """
    return " ".join(markdown.split())


def unemphasized(markdown):
    """The document with its bold, its italic and its backticks taken off.

    Two documents saying the same thing rarely emphasize it the same way. The
    bid memo writes `**may seek**` and a slide quoting it writes `*may seek*` --
    one phrase to a reader, two strings to a test, and a check that failed on
    that would punish editing exactly the way `flat` exists to stop.

    **Line breaks are left alone**, because dropping them is a separate
    decision with a real cost: a phrase that ran across two bullets would start
    matching, and a check that cannot tell one bullet from two is weaker than
    the one it replaced. `plain` below is the version that does both, for
    callers that want both.

    `deck_reader.visible` is the slide-side caller. It kept the second copy of
    these replacements until #84's review found the fourth being written.
    """
    return markdown.replace("**", "").replace("*", "").replace("`", "")


def plain(markdown):
    """One long line, with the emphasis off too. `flat` and `unemphasized`.

    What a test wants when it is comparing a sentence in a hard-wrapped page
    with the same sentence on a slide, which is a comparison that has to
    survive both a line break and a change of emphasis.
    """
    return unemphasized(flat(markdown))


def markdown_section(markdown, heading):
    """Everything under one heading, up to the next heading of any depth.

    Matched on how the heading starts rather than the whole of it. The plan of
    record writes its running time into one of them -- "## 5. Run of show
    (2:00)" -- and a heading that gains or loses a parenthesis should not fail
    a check about fallbacks or about slides.
    """
    lines = markdown.splitlines()
    for start, line in enumerate(lines):
        if line.strip().startswith(heading):
            break
    else:
        raise AssertionError(f"{heading!r} is not in that file")
    for end in range(start + 1, len(lines)):
        if lines[end].startswith("#"):
            return "\n".join(lines[start + 1:end])
    return "\n".join(lines[start + 1:])


def table_rows(markdown):
    """Every table row in a markdown file, as a list of stripped cells.

    Header and divider rows come back too. The callers filter on the first
    cell rather than on position, so a table growing a column above it does not
    quietly change which row is which.
    """
    rows = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def json_of(path):
    """A committed JSON file, read through the same door as a markdown one.

    Three test files were spelling this out, each with its own `SCREENING`
    constant and its own `open(long_path(...))`. The SH16 run is the thing
    they all load and it is read the same way every time.
    """
    return json.loads(text_of(path))


def headings(markdown):
    """Every section heading in a document, lowercased, with the typesetting off.

    The hashes, the bold and the backticks come off, because what a caller is
    asking is what the section is *about* rather than how it is set.

    This was written in `test_principals_brief.py` first, to tell a page that
    answers a question in a section from one that mentions it in a sentence.
    `test_day_zero.py` needed the same distinction for the same reason -- a stub
    can mention three prerequisites, only a real page has a section for each --
    and a second copy is what this module exists to delete.
    """
    found = re.findall(r"^#{1,6}\s+(.*)$", markdown, flags=re.MULTILINE)
    return [line.replace("*", "").replace("`", "").strip().lower() for line in found]


def local_link_targets(markdown):
    """Every link on a page that points at another file in this repo.

    Addresses and same-page anchors are dropped; what comes back is the part
    before any `#`, ready to be resolved against the page's own folder.

    Two test files check that these resolve, and they check it for the same
    reason: `mkdocs build --strict` already catches a link to a page that does
    not exist, but only once somebody builds the site, and by then the page may
    be on a projector. The suite runs on every pull request.
    """
    targets = []
    for target in re.findall(r"\]\(([^)]+)\)", markdown):
        if target.startswith("http") or target.startswith("#"):
            continue
        targets.append(target.split("#")[0])
    return targets


# ---------------------------------------------------------------------------
# Prose, for the plain-language check
# ---------------------------------------------------------------------------
#
# `test_plain_language.py` holds the pages in `docs/` to a sentence length, an
# em dash count and a word list. Before it can do that, something has to decide
# which part of a page is *writing*. A table cell is not a sentence. A heading
# is not a sentence. A `bash` block is not English at all, and a word-count rule
# applied to a command line would fail a page for quoting a command correctly.
#
# That definition lives here rather than in the test file for this module's own
# stated reason: a second reader would drift the first time somebody fixed one
# of them. It is also the boundary issue #133's counts were measured across, so
# changing it changes what the standard itself covers.

# `~~~` is the other fence markdown allows. No page in `docs/` uses it today,
# and a reader that only knew about backticks would start counting a command as
# a sentence the day somebody did.
_FENCE = re.compile(r"^\s*(```|~~~)")

_HTML_COMMENT = re.compile(r"<!--.*?-->", flags=re.DOTALL)

# A list item: a bullet or a number, and the space after it. The space is what
# separates `- the point` from the `---` rule between two sections.
_LIST_ITEM = re.compile(r"^([-*+]|\d+[.)])\s")

_ADMONITION = re.compile(r"^(!!!|\?\?\?)\s")

# A blockquote. `prose` below drops the whole line, because a blockquote is
# somebody else being quoted and the plain-language standard is about what this
# repo wrote. See that function for the whole argument.
_QUOTE_MARK = re.compile(r"^\s*>\s?")

# A sentence ends at `.`, `!` or `?`, but only where what follows looks like the
# start of the next one: whitespace, then a capital, a quote or an opening
# bracket. Without that second half the reader cuts "TxDOT's spec.md file" and
# "Python 3.11 or newer" into fragments.
#
# **An abbreviation before a capital still reads as a break**, so "the U.S.
# Geological Survey" would come back as two sentences. There is no guard against
# that, because no page in `docs/` does it -- every one of `Mr. Dr. St. Inc. No.
# vs.` and the `U.S.` shape was searched for and found zero times before a
# capital. A guard written for cases nobody has is a comment claiming a
# measurement that was not made.
#
# It is also the safe direction if it ever happens. A sentence cut in two is
# under the word limit, so the reader under-reports rather than failing a page
# for a sentence nobody wrote.
_SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]]?\s+(?=[\"'(\[A-Z])")

# Three words or fewer is a fragment, not a sentence. "Not this." is something
# these pages do on purpose, and counting it would put noise in front of the
# sentences that are genuinely too long.
_FRAGMENT_WORDS = 3


def prose(markdown):
    """The parts of a page that are writing, with everything else blanked out.

    Out come fenced code, HTML comments, blockquotes, table rows, headings,
    list items, raw HTML tags and the `!!!` line that opens an admonition. The
    admonition's own body stays, because it is prose; only the marker is
    typesetting.

    **A blockquote goes out whole, mark and words together.** It used to have
    only its `> ` taken off, which left the quotation to be counted as though
    this repo had written it. `docs/governance/` is where that became untenable:
    four of its sentences run past forty words because the Texas Legislature and
    the board wrote them that way, and shortening one would falsify a citation.
    The same reasoning is already in this function for a command line. A word
    limit applied to quoted text fails a page for quoting something correctly.

    **The cost is real and a reviewer carries it.** A blockquote used as a
    callout holds this repo's own writing, and there are such callouts in
    `docs/governance/ai-use-policy.md`. Those are no longer counted. See the
    plain-language skill, which says so where it lists what the test cannot see.

    **A removed line becomes a blank line rather than disappearing.** A table
    sitting between two paragraphs is a paragraph break, and dropping its rows
    outright would join the paragraph above to the one below and invent a
    sentence that runs across both.

    **A list item takes its continuation lines with it.** Only the first line of
    a bullet carries the bullet; the rest are indented under it. Blanking the
    marker line alone would leave the tail of every wrapped bullet behind as a
    paragraph starting in the middle of a sentence.
    """
    kept = []
    fenced = False
    # The indent of a list item whose continuation lines are still being
    # skipped, or None. A blank line does not clear it, because a loose list
    # puts a blank line between one item and the next.
    inside_item = None
    for line in _HTML_COMMENT.sub("", markdown).splitlines():
        if _FENCE.match(line):
            fenced = not fenced
            kept.append("")
            continue
        if fenced:
            kept.append("")
            continue
        if _QUOTE_MARK.match(line):
            kept.append("")
            continue
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        indent = len(line) - len(line.lstrip())
        if inside_item is not None:
            if indent > inside_item:
                kept.append("")
                continue
            inside_item = None
        if _LIST_ITEM.match(stripped):
            inside_item = indent
            kept.append("")
            continue
        if stripped[0] in "|#<" or _ADMONITION.match(stripped) or set(stripped) <= set("-*_ "):
            kept.append("")
            continue
        kept.append(line)
    return "\n".join(kept)


def paragraphs(markdown):
    """The prose of a page, one entry per paragraph, each on a single line.

    Every page in `docs/` is hard-wrapped at about eighty characters, so a
    sentence is almost never on one line. `flat` above does this for a whole
    document; a sentence check needs the paragraph breaks kept, because a
    sentence does not run across one.
    """
    found = []
    for block in re.split(r"\n\s*\n", prose(markdown)):
        one_line = flat(block)
        if one_line:
            found.append(one_line)
    return found


def sentences(markdown):
    """Every sentence of writing on a page, with the typesetting taken off.

    Fragments of three words or fewer are dropped. See `_SENTENCE_END` for
    where the cut is made and what it gets wrong.
    """
    found = []
    for paragraph in paragraphs(markdown):
        for part in _SENTENCE_END.split(unemphasized(paragraph)):
            part = part.strip()
            if len(part.split()) > _FRAGMENT_WORDS:
                found.append(part)
    return found
