"""Reading a committed markdown document, for the tests that check one.

Four test files hold a page in `docs/` to what it claims:

* `test_fallbacks.py` — the fallback card, against the run of show
* `test_deck.py` — the slide deck, against the same table
* `test_plan_of_record.py` — the run of show's own Act II figures, against the
  SH16 run in `project-sh16/screening.json`
* `test_principals_brief.py` — the one-page handout, against the crew-day
  build-up its cost figures are read out of

All of them have to open a file, find a heading, and read a table out from under
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
