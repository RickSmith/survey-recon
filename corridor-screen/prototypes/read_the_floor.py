"""THROWAWAY. Proof that the markup floor can actually be stood on.

Issue #196 took three layers of checking for the job page. Two of them need a
browser in a container. The third -- the floor -- is supposed to run on a bare
Python with nothing installed, reading the generated page back with
``html.parser``.

That was the one claim in #196's answer nobody had run. #190 had already found
that ``xml.etree`` **cannot** parse the page, so "just parse it" was not a safe
assumption to leave lying around. This parses it.

Run it with::

    python corridor-screen/prototypes/read_the_floor.py

It writes nothing and changes nothing, and it imports nothing that is not in
the standard library -- which is the whole point, so the imports at the top of
this file are part of the evidence.

----

What a floor is for
===================

It catches a different class from the browser layers, and only that class:
**facts about the file**. A count that disagrees with the run. A flagged tract
with no id on it, so nothing could ever click it. A footer that lost the run
reference. None of those need a browser, none of them need CSS, and every one
of them is the kind of mistake a generator makes while nobody is looking.

What it deliberately cannot see is anything decided by a stylesheet. All three
defects #195 found were CSS, and this file would have passed every one of
them. That is not a gap in the floor; it is the reason the other two layers
exist.

----

Reading the prototype rather than the real page
===============================================

The real job page carries one variant. The prototype carries three so somebody
could compare them, so every count here is per variant and the page-wide
totals are three times what a real page would show. The checks below say which
variant they are reading.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "job-page-prototype.html"


class Floor(HTMLParser):
    """Everything the floor needs, gathered in one pass over the markup."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.variant = None
        self.tracts_on_the_map = []
        self.tract_details = []
        self.rows = []
        self._depth_of_variant = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        self._depth += 1
        at = dict(attrs)
        if at.get("data-variant"):
            self.variant = at["data-variant"]
            self._depth_of_variant = self._depth
        if at.get("data-tract"):
            self.tracts_on_the_map.append(at["data-tract"])
        if at.get("id", "").startswith("detail-"):
            self.tract_details.append((self.variant, at["id"][len("detail-"):]))
        if at.get("data-expand"):
            self.rows.append((self.variant, at["data-expand"]))

    def handle_endtag(self, tag):
        if self._depth == self._depth_of_variant:
            self.variant = None
            self._depth_of_variant = None
        self._depth -= 1


def main():
    if not PAGE.is_file():
        print(f"no page at {PAGE}. Run job_page_prototype.py first.")
        return 1

    markup = PAGE.read_text(encoding="utf-8")
    floor = Floor()
    floor.feed(markup)

    checks, failures = [], 0

    def check(words, got, want):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        checks.append((ok, words, got, want))

    # Every flagged tract on the map can be clicked, because it carries its id.
    check("flagged tracts carrying an id on the map",
          len(floor.tracts_on_the_map), 8)
    check("those ids are all different",
          len(set(floor.tracts_on_the_map)), 8)

    # Each variant tells all eight tracts in full. This is the fact that stops
    # a principal reading a page where one of the eight quietly went missing.
    for key in ("A", "B", "C"):
        check(f"variant {key}: tracts told in full",
              len([1 for v, _ in floor.tract_details if v == key]), 8)

    # Variant B is the page, per #194, and its eight rows are its whole shape.
    check("variant B: expandable rows",
          len([1 for v, _ in floor.rows if v == "B"]), 8)

    # The map's ids and the details agree, so no row points at nothing.
    detail_ids = {t for v, t in floor.tract_details if v == "B"}
    check("variant B: every row has a detail behind it",
          detail_ids >= {t for v, t in floor.rows if v == "B"}, True)

    # The run reference is on the page at all. #195 decided it belongs on every
    # printed page; whether it lands there is a question for the print layer,
    # not this one, and saying so is the point of a floor.
    found = re.findall(r"texas-bexar-sh0016-kg-\d{8}T\d{6}", markup)
    check("the run reference appears", len(set(found)), 1)

    for ok, words, got, want in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {words:<46} {got!r} (want {want!r})")

    print()
    print(f"parsed {len(markup):,} characters with html.parser, "
          f"standard library only, nothing installed")
    if failures:
        print(f"{failures} check(s) failed")
        return 1
    print("the floor holds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
