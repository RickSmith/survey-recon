"""THROWAWAY. What a job page costs git, measured rather than guessed.

Issue #192 asked whether half a megabyte per run belongs in git, and its case
against was that "each regeneration is a large diff nobody reads." That is a
claim about a number, and nobody had the number. This gets it.

Run it with::

    python corridor-screen/prototypes/measure_churn.py

It builds the job page from the committed SH16 run, builds it again with one
thing changed, and counts the lines between them. It writes nothing and it
changes nothing.

----

What it measures, and why each one
==================================

**A page carrying one variant.** The prototype carries three so somebody can
compare them. A real page carries one, so three-variant figures overstate the
real thing -- the header alone appears three times.

**A re-run with the same data.** This is the case #192 complained about: the
committed artifacts were regenerated four times in one working session. If
that is a wall of diff, the ticket is right.

**A re-run where the data actually moved.** A tract loses its flag. This is
the control: a real change *should* be visible, and a measurement that only
shows small diffs has not proved anything until it also shows a big one.

----

What it found, on 2026-09-22
============================

===================================  =====================
Change                               Lines the page moves
===================================  =====================
A re-run, same data                  4
A tract loses its flag               91
===================================  =====================

The page is 1,270 lines and 318 KB, of which the map is 280 KB -- 88% of it.

Four lines, because the generators here write one element per line and a
re-run only moves the footer stamp. Ninety-one lines when a tract changes,
which is the artifact doing its job.

So the ticket's case against was not true of this repo, and #192 settled on
**commit it**. The four is also why that ticket asks for a test: the number is
the reason, and an untested reason stops being true without telling anybody.
"""

import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import job_page_prototype as J  # noqa: E402
from corridor_screen import drawings  # noqa: E402


def one_variant_page(document, capture):
    """The page as a real run would write it: one variant, not three."""
    f = J.facts(document)
    return J.page([("B", J.variant_b(f))], J.map_svg(document, capture, f))


def moved(before, after):
    """How many lines differ between two builds."""
    return sum(1 for line in difflib.unified_diff(before, after, n=0)
               if line[:1] in "+-" and line[:2] not in ("++", "--"))


def same_data(document):
    """A re-run on another day. The data did not move; the run did."""
    document["run"]["run_id"] = "texas-bexar-sh0016-kg-20260922T091500"
    document["run"]["finished_at"] = "2026-09-22T09:15:17-05:00"


def data_moved(document):
    """The control: one tract stops carrying a flag."""
    for parcel in document["parcels"]:
        if parcel["flags"]:
            parcel["flags"] = []
            parcel["max_lead_time_days"] = None
            return


def main():
    document, capture = drawings.load(J.PROJECT)
    baseline = one_variant_page(document, capture).splitlines()
    text = "\n".join(baseline)
    print(f"the page, carrying one variant: {len(baseline):,} lines, "
          f"{len(text.encode('utf-8')):,} bytes")

    for words, change in (("a re-run, same data", same_data),
                          ("a tract loses its flag", data_moved)):
        again, capture_again = drawings.load(J.PROJECT)
        change(again)
        after = one_variant_page(again, capture_again).splitlines()
        print(f"  {words:<26} {moved(baseline, after):>4} lines move")


if __name__ == "__main__":
    main()
