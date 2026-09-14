# The dry run

**Run the whole two hours once, in front of people, before the day.** Not a
read-through. Not the tricky bits. All of it, in order, on the clock.

The point is not to find out whether you know the material. You do. The point
is to find out **where the two hours actually go**, because it is never where
you think, and the only way to cut well is to cut a block you have watched run
long.

This page is the instructions. [The plan of record](../plan-of-record.md) §5
holds the clock, [the fallback card](fallbacks.md) holds what to reach for when
a demo dies, and the deck carries both in its speaker notes. This page joins
them up and adds the one thing none of them has: a sheet somebody can write on.

**Print it.** The timekeeper writes on it. A page on a screen is a page
somebody has to hold a laptop to use.

---

## Who is in the room

Four jobs. The first two are the only ones that talk.

| Job | Who | What they do |
|---|---|---|
| **Presenter** | Rick | Presents. Does not watch the clock — that is somebody else's job, and a presenter checking a watch is a presenter who has stopped presenting |
| **Audience proxy** | Seneca | Delivers the six interjections where the deck's speaker notes put them. Rehearsed here so they do not sound rehearsed there |
| **Timekeeper** | One person, and not one of the above | Writes the wall-clock time each block starts. Says nothing during the run |
| **Watchers** | CBI staff | Sit and watch. Write down anything that confused them. They are standing in for three hundred firm owners |

**The timekeeper is a real job.** It is the one that makes the rehearsal worth
running, and it cannot be done by the person talking. Ask somebody by name
before the day, so that it is not handed to whoever sat closest.

## Before you start

- The laptop the session will actually run from. Not a different one
- [The fallback card](fallbacks.md), **on paper**
- This page, **on paper**, one copy per timekeeper
- A second window already open in the `corridor-screen` folder, so the cold-open
  command can be copied rather than typed
- The deck open in presenter view, so the speaker notes are where they will be
- A clock everybody can see, started at zero when the presenter starts talking

**Do not fix anything you find in the first ten minutes.** Write it down and
keep going. A rehearsal that stops to fix things measures nothing.

## The timing sheet

Eleven blocks. Two hours.

**Write the time each block starts, not how long it took.** A timekeeper doing
arithmetic in a dark room while listening will get it wrong, and the arithmetic
can be done afterward by anybody. Reading a clock is a job somebody can do
while paying attention to the talk.

Drift adds up on its own. If the Cold open starts at 0:00 and Act I starts at
0:33, you are three minutes down before the hinge of the session, and every
number below it is three minutes optimistic.

| Planned | Min | Block | Actual start | Notes |
|---|---|---|---|---|
| 0:00 | 8 | Cold open | | |
| 0:08 | 12 | What is an agent | | |
| 0:20 | 10 | Vocabulary of managing one | | |
| 0:30 | 16 | Act I — The grilling | | |
| 0:46 | 6 | The money slide | | |
| 0:52 | 5 | Stretch + questions | | |
| 0:57 | 21 | Act II — Find the control | | |
| 1:18 | 18 | Act III — The estimate package | | |
| 1:36 | 12 | Review, seal — and the three failures | | |
| 1:48 | 6 | Hermes | | |
| 1:54 | 6 | Accountability · Monday morning · the live issue | | |
| 2:00 | | **End** | | |

The **Notes** column is for one thing: what made this block run long. "Demo
took three goes." "Lost them on the token slide." "Nobody laughed." Three words
is enough. It is a pointer to a conversation afterward, not the conversation.

## When it runs long

It will. Every rehearsal does, and the first one usually runs fifteen or twenty
minutes over. That is the rehearsal working.

**Cut in this order, and do not skip down the list.** This order is
[the plan of record](../plan-of-record.md#cut-line-in-order)'s, and each of the
three is marked in the speaker notes of the exact slide it would take out, as
`Cut 1 of 3`, `Cut 2 of 3` and `Cut 3 of 3`. Every block opens with a section
break slide, so cutting one is deleting from one break to the next.

| Order | What goes | What it becomes |
|---|---|---|
| **Cut 1 of 3** | The Hermes segment | A recorded teaser |
| **Cut 2 of 3** | The crew-day build-up | Shown as finished output, not built live |
| **Cut 3 of 3** | The token slide | A footnote to the repo |

**Never cut these four:**

- the cold open
- the grilling
- the failure beat
- the accountability close

Those four are the session. The deck's own tests refuse to let them be marked
as cuts, so this is not a preference somebody can quietly change under time
pressure the night before.

**One more, inside a block.** If the run is behind by 1:36, the failure beat
drops **beat 2** — wrong, not missing. It is the most technical of the three
and the least about accountability. Beat 3 is the one that changes the shape of
the talk, and it needs about three minutes to land. [The plan of
record](../plan-of-record.md) says both, under the failure beat.

## Afterward, the same day

**Every problem becomes a work order.** A work order is a GitHub issue — one
job, written down, before anybody starts it. That is how everything else in
this repo got built, and a rehearsal finding is not a special case.

Do it the same day. Impressions fade in hours, and "something felt off in Act
II" is not a job anybody can pick up.

1. Go round the room once. The watchers first, because they will not volunteer
2. Open one issue per problem. Not one issue holding a list
3. Say what went wrong and where, using the block name from the timing sheet
4. Label it `ready-for-agent` if it is fully specified, `ready-for-human` if a
   person has to do it. [What the labels mean](../agents/triage-labels.md) has
   the rest
5. Close [#36](https://github.com/RickSmith/survey-recon/issues/36) with a
   comment naming the issues that came out of it

The timing sheet goes in too. Photograph it and attach it to the closing
comment, so the next person to run this has real numbers rather than a plan.

## How this page is kept honest

The eleven blocks above are the run of show's, and `corridor-screen/tests/
test_dry_run.py` fails if this page and [the plan of
record](../plan-of-record.md) §5 ever disagree — on a block name, a planned
start, a length, or the order they come in.

That check exists because this is now the third place the same table is
written: the plan of record sets it, the deck's speaker notes carry it, and
this page hands it to a timekeeper. A third copy nobody tests is a third copy
that rots, and this repo has published four corrections already for exactly
that. The tests run on every pull request.

The cut line and the never-cut list are checked the same way, against §7.
