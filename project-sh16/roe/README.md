# Right-of-entry letters — SH16

**There is one letter in this folder and there should be two.** That is the
demonstration, not an oversight.

| File | Day | Status |
|---|---|---|
| `roe-letter-1.md` | day 0 — 2026-09-13 | written, and committed |
| `roe-letter-2.md` | day 21 — 2026-10-04 | **not due yet** |

Day 0 is the day the SH16 screening run finished and flagged the tract. Day 21
is derived from the checked-in
[lead-time table](../../docs/corridor-screen/lead-times.md) rather than typed
anywhere — the arithmetic is in
[the right-of-entry letters page](../../docs/corridor-screen/roe-letters.md),
and `corridor-screen/tests/test_roe.py` fails if it ever becomes a constant.

## Why this matters

Right of entry is **not a statutory right** in Texas. You ask, and the owner may
say no or say nothing at all. TxDOT ships **two** templates in its Surveyors'
Toolkit — a first request letter and a second request letter — because
non-response is the ordinary case rather than the exception.

The second letter is real work that real firms forget, because nobody is
holding a calendar for a tract nobody has heard back about.

## Running it

From the `corridor-screen` folder:

```bash
python -m corridor_screen.roe --show
```

That prints the six-minute demo — the tract, the arithmetic behind day 21, and
the clock. It reads from disk and makes no network call.

To write whatever is due today:

```bash
python -m corridor_screen.roe --write ../project-sh16/roe
```

Run it before 2026-10-04 and it writes one letter and says the second is not
due. Run it on or after that date and it writes both, and nobody had to
remember. That is the whole claim.

To see it from the other side of day 21 without waiting:

```bash
python -m corridor_screen.roe --write ../project-sh16/roe --as-of 2026-10-04
```

That writes `roe-letter-2.md`. So does the plain command above, on or after
2026-10-04 — which is the demo working, not a mistake.

**You do not have to remember to delete it.** `roe-letter-2.md` is in
`.gitignore`, so it never reaches a commit, and the test suite checks that git
is not tracking it rather than that the file is missing from the disk. A demo
about people forgetting things should not depend on a person remembering one.

## What these letters are not

They are **specimens**. Nothing here was mailed, nothing was signed, and no
letter carries a mailing address — the appraisal district publishes one and this
repo is public.

Every value in them came from
[`screening.json`](../screening.json), which is public record: the parcel
identifier, the owner as the Bexar Appraisal District publishes it, and the
cemetery flag with its statute. **No client data was used.**

An **RPLS** signs a real one and remains accountable for it — 22 Tex. Admin.
Code § 131.2(38).
