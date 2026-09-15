# Corridor screening

The tool this repo is named for.

You give it the centerline of a corridor. It widens that line into a ribbon,
then asks a fixed list of public map services what is inside the ribbon. Out
comes one file: every parcel in the corridor, what about each one costs time,
and how many days of notice each of those things needs.

It is a first pass before you price a job. **It does not decide anything.** It
reports, and an RPLS reads it and decides.

<div class="grid cards" markdown>

-   **[The specification](spec.md)**

    The scope of work — settled 12 September 2026, amended since, and every
    amendment dated in place rather than rewritten. Inputs, the order of
    operations and why, every service called, what happens when one is dead, what
    happens when one answers wrong, and the output field by field.

-   **[Lead times and their sources](lead-times.md)**

    Where every number in the tool's lead-time table comes from. Each row carries
    its statute and a link somebody opened on a stated date — including the three
    rows no figure was found for, which say "not found" and say where they
    looked.

-   **[The right-of-entry letters](roe-letters.md)**

    Right of entry is not a statutory right in Texas. What the two statutes
    actually say, how the 21-day follow-up was derived rather than published, and
    the scheduled run that proves the day arrives whether or not a person is
    looking.

</div>

---

## Which page answers which question

The specification is long, because a scope of work is. These three questions come
up most, and two of them are answered outside it.

| What you want to know | Where it is |
|---|---|
| What the tool does, and what it refuses to do | [Specification §1 and §2](spec.md) |
| Which public services it calls, and their quirks | [Specification §6](spec.md), then [Data sources](../data-sources/index.md) |
| Why the railroad row says 30–45 days | [Lead times](lead-times.md) |
| Whether a parcel needs a right-of-entry letter | [Specification §11](spec.md), then [The right-of-entry letters](roe-letters.md) |
| Where the 21-day follow-up came from | [The right-of-entry letters](roe-letters.md) — it is derived, not published |
| What the tool cannot see at all | [Specification §12](spec.md) |

---

## The rule all three pages are held to

**A lead time with no citation is a rumor with a number on it.**

That sentence is from the [lead times](lead-times.md) page, and it is the rule the
whole section runs on. It is enforced by code rather than remembered: the loader
refuses a row that has no source and no link, and a row with no confirmed figure
must begin with the words "Not found" and say where it looked. That is checked
too.

Anything softer than "not found" reads as "no delay," and those are not the same
statement.

---

## Two things said plainly, because they are easy to miss

**The specification is a record, not a current-state document.** Entries that were
settled later are struck through and answered underneath, rather than deleted.
Section 15 is the clearest example. It is read on stage as an account of what was
decided and when, and a list that quietly loses its items cannot be read that way.

**The block called Hermes is a cron job** — a *cron job* is a task a computer runs
on a clock, with nobody starting it. The name was locked by a decision before the
thing was built, and what got built is a GitHub Actions schedule reading a
calendar. Both were kept, and the reason is in
[ADR 0002](../adr/0002-the-hermes-segment-runs-on-a-schedule.md). The
[right-of-entry letters](roe-letters.md) page says it too, because a substitution
nobody mentions is the thing this repo's history exists to make visible.
