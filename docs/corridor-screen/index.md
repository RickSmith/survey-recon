# Corridor screening

You have seen the numbers on the [worked example](../scenarios/sh16/index.md).
Before you trust one of them, you want to know what the tool actually did to
get it, and what it will never do. This page is that.

## What it does

You give it a road and two mile markers. On SH16 that was TxDOT's own name for
the route, `SH0016-KG`, and the two distances along it, 347.7 and 356.367.
Nothing else. No drawing, no coordinates.

It asks TxDOT for the centerline between those two markers. Then it widens
that line into a ribbon, three hundred feet either side, and asks a fixed list
of public map services what is inside the ribbon. County parcels. Schools,
cemeteries, railroads and pipelines. Survey marks and their condition. TxDOT's
own monuments. The right-of-way map sheets on record. The nearest hospital,
ambulance, fire station and police station.

Every answer is saved to disk with the date it came back and the exact
question that produced it. Then everything it found goes into one file, and
three documents are written from that file: a memo, a table of the tracts that
cost time, and a crew-day build-up you can argue with one line at a time.

That is the whole tool. It is a first pass, made at a desk, before you price a
job.

![How the screening works: one line in, fourteen services asked, one file out, three documents, one surveyor](../scenarios/sh16/img/how-it-works.svg)

## What it refuses to do

**It does not decide anything.** It reports. A licensed surveyor reads the
report and decides.

**It does not guess.** When a public service has no answer, the tool says *not
found* and says where it looked. It never turns *we could not find a number*
into *zero*. Seven of the eight flagged tracts on SH16 say *wait not found*
because no notice period for school land is published anywhere the tool could
find. That is a phone call, not a clear tract.

**It does not treat *unknown* as *no*.** A tract the tool could not check for a
locked gate is not a tract without one. One of those two words sends a crew to
a locked gate, so the tool never confuses them.

**It does not fetch quietly.** Every answer it uses is on disk with a date on
it, so a run can be repeated later with no network at all and compared with
the original. The saved answers are for reliability in a conference hall, not
for pretending to be live. Every page that shows them says when they were
captured.

**It does not enter anywhere.** Nothing it produces is permission to set foot
on a tract. Texas has no automatic right of entry for a surveyor, and a parcel
map does not create one.

## When a service does not answer

Public servers have bad days. The tool checks every service it needs before it
starts real work, so a blocked host is known in seconds and not halfway
through a run. If a service is dead, the run pauses, names it, and asks a
person: skip that service, or stop. Skip it and the output says so, on every
tract, so no tract reads as clear of something nobody checked. Run it with
nobody watching and a dead service simply stops the run.

If a service answers but the answer looks wrong, the tool records a warning
and keeps going. A warning is for a plausible wrong answer: a list cut off at
a round number, a filter the server ignored. It is written into the output
where a reader will see it. It never stops a run, because a stopped run tells
you nothing and a run with a warning on it tells you almost everything.

## The three pages behind this one

<div class="grid cards" markdown>

-   **[The specification](spec.md)**

    The scope of work, settled in an interview before any code was written.
    What goes in, what comes out, every service it calls, and what happens
    when one fails. It is long, because a scope of work is. It is also a
    record: things settled later are struck through and answered underneath,
    not rewritten, so you can see what was decided and when.

-   **[Lead times and their sources](lead-times.md)**

    Where every number of days in the tool comes from. Each row carries the
    statute and a link somebody opened on a stated date. Three rows say *not
    found*, and say where they looked. A lead time with no citation is a
    rumor with a number on it, and the tool refuses to load one.

-   **[The right-of-entry letters](roe-letters.md)**

    Right of entry is not a statutory right in Texas. What the two statutes
    actually say, how the tool writes the first request letter from public
    records, and how the twenty-one-day follow-up was worked out rather than
    looked up, because no manual publishes one.

</div>

## Which page answers which question

| What you want to know | Where it is |
|---|---|
| What the tool does, and what it refuses to do | This page, then [the specification](spec.md), sections 1 and 2 |
| Which public services it asks, and how each one can answer wrong | [Data sources](../data-sources/index.md) |
| Why the railroad row says 30 to 45 days | [Lead times](lead-times.md) |
| Whether a tract needs a right-of-entry letter | [The specification](spec.md), section 11, then [the letters](roe-letters.md) |
| Where the twenty-one-day follow-up came from | [The letters](roe-letters.md). It is derived, not published |
| What the tool cannot see at all | [The specification](spec.md), section 12 |

## One name that needs explaining

The session plan calls one part of this *Hermes*. Hermes is a clock. It is a
task a computer runs every day by itself, with nobody starting it, which
checks whether the follow-up right-of-entry letter has come due and writes it
if so. Software people call a task like that a *cron job*. The name Hermes was
chosen before the thing was built, and both the name and the plainer
description were kept. The [letters page](roe-letters.md) shows the clock
running.

---

## Where this came from

The scope was settled in an interview on 12 September 2026, recorded on
[work order #5](https://github.com/RickSmith/survey-recon/issues/5). The
decision that a wrong-looking answer warns and a dead service stops is
[decision record 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md).
The decision to keep the name Hermes beside the plain description is
[decision record 0002](../adr/0002-the-hermes-segment-runs-on-a-schedule.md).
