# The right-of-entry letters, and the day the second one fires

**Right of entry is not a statutory right in Texas.** You ask, and the owner may
say no or say nothing at all. That single fact is what this page is about, and
it is the reason the second letter is real work rather than paperwork.

- A Registered Professional Land Surveyor who is refused **may seek** a court
  order — [Tex. Occ. Code § 1071.3585](https://statutes.capitol.texas.gov/Docs/OC/htm/OC.1071.htm)
- A Licensed State Land Surveyor acting in an official capacity **is entitled
  to** one, and the Attorney General must promptly apply —
  [§ 1071.358](https://statutes.capitol.texas.gov/Docs/OC/htm/OC.1071.htm)

Neither is a right to walk on somebody's land today. There is no notice-only
entry, no bond, and no self-help.

TxDOT's own procedure requires every request to be documented by written
letter — [Survey Manual, Ch. 2 §3](https://www.txdot.gov/manuals/row/ess/surveying_procedures/right_of_entry.html).
Oral permission is valid for **one day and for the one person who received it**.

**And TxDOT ships two templates**, not one: a first request letter
(`020-10-tem`) and a **second** request letter (`020-11-tem`), both in the
Surveyors' Toolkit. The department did not add a second form for an unusual
case. Non-response is the ordinary case.

The second letter is the one firms forget, because forgetting it costs nothing
on the day and everything six weeks later.

---

## Where day 21 comes from

This is the part worth being slow about, because it is the part an agent would
get wrong.

### First, what it is not

**There is no published right-of-entry turn-around to quote.** Every TxDOT
manual this repo read was searched for one and none states a number. The
account of where we looked is in [TxDOT research](../txdot-research.md),
Part 3. The thirty-day windows in the acquisition process are **offer-stage**
and are a different thing entirely.

So the interval is **not found** — in this repo's sense of those words, which
is "we looked and could not confirm it," never "it does not exist."

That leaves two honest options. Write no follow-up at all, or **derive** an
interval and show the derivation. Typing `21` into a source file is not one of
them: that is inventing a requirement, and it is the single thing
[`CLAUDE.md`](https://github.com/RickSmith/survey-recon/blob/main/CLAUDE.md)
says never to do.

### The derivation, in three arguable steps

Every step below is a choice somebody can disagree with out loud. That is the
point. What nobody can do is find the answer typed somewhere.

**Step 1 — take the longest confirmed lead time the table carries, counted in
calendar days.**

On the committed [lead-time table](lead-times.md) that is the railroad's **45
calendar days**, which is Union Pacific's own published turn-around. It is the
outer clock the corridor is planned against, so it is the schedule a letter
left sitting is spending.

**Step 2 — halve it.** 22 whole days.

A follow-up that fires later than half-way leaves the second letter less time to
be answered than the first one had, which makes it a formality rather than a
second ask. Splitting the window evenly gives each letter the same chance.

**Step 3 — round down to whole weeks.** 21 days.

A letter moves in weeks: mail, an office cycle, a board that meets monthly.
Rounding **down** fires earlier and never later, so the rule can only ever cost
the tool slack — never the schedule. And because the interval is whole weeks,
the second letter always falls on the same weekday as the first, which is a
small thing that makes a schedule easier to read.

```
longest confirmed wait, counted in calendar days   45 days
  set by the railroad row, cited to https://www.up.com/real-estate/tempuse/procedures
half of it, so letter two has the window letter one had   22 days
rounded down to whole weeks, because a letter moves in weeks   21 days (3 weeks)
```

### Prove it is a derivation

Change the table and the day changes with it:

| Railroad row | Follow-up fires on |
|---|---|
| 45 calendar days *(as committed)* | day 21 |
| 60 calendar days | day 28 |
| 30 calendar days | day 14 |
| row removed — cemetery's 14 days becomes the outer clock | day 7 |

`corridor-screen/tests/test_roe.py` runs every row of that table. A derivation
that only ever answers 21 is indistinguishable from a constant, so the tests
are mostly there to tell the two apart.

---

## Three rules the derivation is held to

**Working-day rows are never used.** The pipeline row counts two *working*
days. Converting those to calendar days would mean inventing a calendar of
weekends and Texas legal holidays this tool does not have and could not check.
That rule is already load-bearing in `lead_times.py`, and halving a number is
not a good enough reason to break it. A table whose only confirmed rows are
working-day rows produces **no interval**, and says so.

**An unconfirmed row has nothing to halve.** A row recorded as "not found"
carries no figure. It is not a zero.

**A table too short to make a week refuses rather than answering zero.**
Thirteen calendar days halves to six, which is not a whole week. Zero days
would read as "send both letters on the same morning," and that is not a plan.
So it raises, names the row and the arithmetic, and stops.

## The obvious objection, answered

**"There is no railroad on this corridor."** Correct — the SH16 run found none.
The railroad row still sets the interval, and that is deliberate.

The interval is not a property of this tract. It is **how long a letter may sit
before you ask again**, which is a firm's standing policy, so it comes from the
longest wait the firm plans against anywhere rather than from whatever happens
to be on one parcel. The demo prints that sentence on screen whenever the row
that set the interval is a flag the run did not find.

---

## What the tool actually does

It writes a letter into a file. Nothing else.

- **It does not mail anything.** There is no mail server, no address book and
  no API key. Anything needing a key does not belong in the attendee path
- **It prints no street address.** The appraisal district publishes one and this
  repo is public. A specimen carrying a real mailing address invites being
  mailed
- **It does not know about weekends or holidays.** The interval is calendar
  days. On the committed SH16 run, day 0 and day 21 both fall on a Sunday. The
  clock writes the letter; a person sends it on Monday
- **An RPLS signs it.** 22 Tex. Admin. Code § 131.2(38) — responsible charge is
  the same standard as direct supervision. A letter a machine wrote is a letter
  a licensed human sends

## Running it

From the `corridor-screen` folder:

```bash
python -m corridor_screen.roe --show
```

The six-minute demo — the tract, the arithmetic, the clock. It reads from disk
and makes no network call, and the same text is committed at
`corridor-screen/captures/the-letter-that-sends-itself/the-demo.txt` for a
podium where Python will not start.

```bash
python -m corridor_screen.roe --write ../project-sh16/roe
```

Writes whatever is due today. Before 2026-10-04 that is one letter and a line
saying the second is not due. On or after it, two letters — and nobody had to
remember.

## The clock that runs without anybody

`.github/workflows/roe-followup.yml` runs the same command on a schedule and
puts whatever is due into the run's summary. It commits nothing, mails nothing
and needs no secret. It exists to make one claim checkable: **the day arrives
whether or not a person is looking.**

If the second letter shows up in a scheduled run's summary on 4 October 2026
and nobody started it, the segment has proved itself before the session opens.

Two limits worth knowing before relying on it.

**A scheduled workflow only runs from the default branch.** Until this work is
merged to `main`, nothing is on a timer. Merged before 4 October and the
evidence exists; merged after, and the first scheduled run is whatever day
follows the merge.

**`roe-letter-2.md` is in `.gitignore`.** On or after its day, running the
documented command writes it onto the disk — that is the demo working. It never
reaches a commit, because a follow-up already sitting in the repo is not a
follow-up. The test suite checks git is not tracking it, rather than checking
the file is absent, so a run past day 21 does not turn the suite red four days
before the session.

## On the name "Hermes"

**The block is called Hermes and what runs it is a cron job.** Saying so here
rather than leaving somebody to find out.

[The plan of record](../plan-of-record.md) settles two things about this
segment: decision 2 names "Claude Code as the spine + Hermes (Nous Research)
for autonomous work," and decision 16 files the ROE letters as "the Hermes
beat." What is built is a GitHub Actions schedule reading a clock. It is
genuinely autonomous — nobody starts it — and it is not Hermes.

That is a gap between a locked decision and a delivered thing, and this page is
not the place it gets closed. It is **Rick's call**, and there are three
honest ways out: run the segment on Hermes as decision 2 says; keep the cron
job and record the substitution in an ADR under `docs/adr/`; or keep the name
as the session's label for the block and say plainly on stage what is behind
it. Naming it is the part that could not wait.

---

Built under [issue #34](https://github.com/RickSmith/survey-recon/issues/34).
The session block is 1:48–1:54 on
[the run of show](../plan-of-record.md), and it is **first on the cut line** —
which is why the recording exists.
