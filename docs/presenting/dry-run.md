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
them up, says what to type and what should come back, and adds the one thing
none of them has: a sheet somebody can write on.

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

## Set the room up

In this order. The last step is the one that catches a broken laptop while
there is still time to care.

1. **Open a terminal in the `corridor-screen` folder.** Not the repo root.
   Every command on this page is written from there, and the `--out
   ../project-sh16` on them only means the right thing from there.
2. **Open a second window on the repo root**, for opening files and for
   `git status` afterward.
3. **Open the deck in presenter view**, so the speaker notes are where they
   will be on the day. The notes carry the block times and the six
   interjections.
4. **Put the deck PDF on the laptop.** See below — this one is a step, not a
   check.
5. **Print [the fallback card](fallbacks.md) and this page.** One copy of this
   page per timekeeper.
6. **Start a clock everybody can see**, at zero, when the presenter starts
   talking.
7. **Prove the tool runs, before anybody is watching.** Run the cache-only line
   from [the cold open](#000-cold-open) once. It takes about a second and a
   half, it touches no network at all, and it ends on `parcels 524`. If it does
   not, you have found your first problem and you have found it early.

**Do not fix anything you find in the first ten minutes of the run itself.**
Write it down and keep going. A rehearsal that stops to fix things measures
nothing.

### Put the deck on the laptop

Two blocks of this session are nothing but slides — *What is an agent* at 0:08
and *Vocabulary of managing one* at 0:20. Twenty-two minutes with no demo to
run and no file to open. If the network goes, those are the two blocks with
nothing behind them.

The deck is rendered to a PDF on every push and published with the site. **It
lives on the web, and the web is the thing that fails.** So download it:

```
https://ricksmith.github.io/survey-recon/slides/beyond-the-prompt.pdf
```

Then do the part people skip. **Turn the Wi-Fi off and open the file.** A
download that landed in the wrong folder, or landed as a zero-byte file, looks
exactly like a download that worked until the moment you need it.

**Do it again before 8 October.** The deck re-renders every time anybody pushes
to the repo, and the copy on your laptop does not. A PDF pulled down for the
rehearsal is the rehearsal's deck, and it will not say so on its face — it will
just quietly be missing the last three weeks of edits.

*Why this is a step rather than a file in the repo:* nothing rendered is
committed here, and a stale PDF sitting in a clone that nobody re-renders is a
worse trap than no PDF at all. The decision is
[#123](https://github.com/RickSmith/survey-recon/issues/123).

## What the rehearsal changes in the repo

**Rehearsing the live demos modifies committed files.** Nothing warns you, and
it is not obvious from the screen. Two of them do it:

| What you run | What it writes over |
|---|---|
| The screening run, with `--out ../project-sh16` | `project-sh16/screening.json`, and everything under `project-sh16/cache/` |
| The live NGS cross-check, same `--out` | Two files under `project-sh16/cache/ngs-data-explorer/` |

The screening run's `run_id` carries a timestamp, so **the working tree is
dirty after every single run**, even one that found exactly the same numbers.
And `corridor-screen/tests/test_plan_of_record.py` reads `screening.json` and
holds the plan of record's Act II row against it, so a rehearsal that got
*different* numbers leaves the repo dirty and failing its own tests.

**For the rehearsal, send the output somewhere else.** Same command, one flag
changed:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../../dry-run-scratch
```

**Then check before you close the laptop:**

```bash
git status
```

Expect nothing. If anything is listed, decide there and then whether it is a
real result worth committing through a work order, or a rehearsal artifact to
throw away — and do it while you still remember which.

**On the day itself, use the real `--out ../project-sh16`.** The demo is
supposed to write into the project folder; that is what the room is watching.
It is only the rehearsal that wants the output elsewhere, because a rehearsal
should not be able to break the thing it is rehearsing.

---

## Running the two hours

One section per block, in clock order. Each says what is on screen, what to do,
what to type, and **what should come back** — because a demo that prints
nothing for four seconds and a demo that has hung look the same from a podium.

Every command is run from the `corridor-screen` folder.

### 0:00 · Cold open

**On screen.** The terminal, at full size. The title slide and *The job we just
handed it* sit beside or behind it. Two slides for eight minutes — the terminal
is the thing they are watching.

**You do.** Start the run, then introduce yourselves while it goes. Do not
explain the tool. Nothing in this block defines a single term, on purpose.

**Run:**

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16
```

**You should see** fourteen services answer, then a wrong-file check, then the
findings, ending on the parcel count. The whole run took **19 seconds** on
2026-09-13, and the committed run of that morning took 21:

```
corridor-screen 0.1.0  run texas-bexar-sh0016-kg-20260913T213813  mode live
  ping  TxDOT_Roadways     ok       264 ms
  ping  ArcGIS_Geometry    ok       266 ms
  ...
  field lists confirmed on every layer

  Wrong-file check -- read these numbers before anything else
    corridor length   8.69 miles
    starts at         29.574516, -98.688309
    ends at           29.482460, -98.599690
```

and ending:

```
  parcels     524
  warnings    0
```

**Point at the wrong-file check.** It prints the corridor length, both end
coordinates and a map link *before* it does anything else. A corridor drawn
from the wrong route looks exactly like the right one until somebody reads
those numbers, and this tool reads them out first. That is a beat in its own
right and it costs ten seconds.

**Wrong rather than slow.** A `ping` line that says anything but `ok` names the
service that is refusing. If the run stops there, that is the tool doing what
[ADR 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md) tells it to —
a dead service stops the run rather than quietly returning less. Switch to the
cache. A finish on any parcel count other than **524** is not a slow demo, it
is a different answer, and it needs saying out loud rather than reading past.

**If the network is gone**, same line with one flag added. It makes no network
call at all, not even the reachability ping, and it finishes in about a second
and a half:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only
```

Every service then reads `skipped  0 ms  cache-only run makes no network
calls`, which is the line that proves to a room it is not quietly calling out.
**Say you have switched, the moment you switch** — the wording is on [the
fallback card](fallbacks.md), and undisclosed caching costs you the room if
anybody notices it.

**Seneca lands here**, while the run is still going, on whose data that is. The
answer is in the speaker note of *The job we just handed it*.

### 0:08 · What is an agent

**On screen.** Slides only. A section break, then four: prediction, then
chatbot against copilot against agent, then the loop, then where it breaks.

**You do.** Talk. Nothing to run, nothing to open.

**Wrong rather than slow.** The only failure available in this block is the
projector, and the only fallback is the PDF you put on the laptop. There is no
committed file that stands in for these twelve minutes — see [the fallback
card](fallbacks.md).

### 0:20 · Vocabulary of managing one

**On screen.** A section break, then five: markdown, the repo and git, issues
and pull requests, context, tokens.

**You do.** Talk. Introduce each term by its survey equivalent first — the
table is in [`CONTEXT.md`](https://github.com/RickSmith/survey-recon/blob/main/CONTEXT.md).

**Note.** The token slide is **Cut 3 of 3**. It is marked in its own speaker
note. If the clock is already behind here, this is the first place you can
spend nothing to get two minutes back.

### 0:30 · Act I — The grilling

**On screen.** The agent, live, at full size. The three *Live:* slides are
holding cards — switch away from each one immediately.

**You do.** Run the grilling against the SH16 scope, on the projector. Let the
silences sit; the questions are the content. Then the spec. Then the work
orders.

**Run, in the agent, in the repo:**

```
/grill-with-docs
```

```
/to-spec
```

```
/to-tickets
```

**You should see** an interview, then a written scope, then real work orders
appearing on GitHub. Scroll the spec once, slowly. Do not read it out.

**Wrong rather than slow.** If the live run will not start, open
`corridor-screen/captures/the-grilling/README.md` and say plainly that it is a
**transcript, not a recording** — there is no video of that session and there
never was. That README is the whole of Act I on one screen: 19 questions, what
the agent recommended, what Rick answered. If `/to-spec` will not run, the
scope it produced is committed at
[`docs/corridor-screen/spec.md`](../corridor-screen/spec.md) and you can open
the real thing and say so.

**This is the hinge of the session.** It is on the never-cut list. If the clock
is bad, take the time from somewhere else.

**Seneca lands here**, after the last bullet of *Why this is the hinge*, on
nineteen questions before any work started.

### 0:46 · The money slide

**On screen.** A section break, then the billable-hour math, then rework
against speed.

**You do.** Talk the math. The argument is rework, not speed, and the phrase
that carries it is *cannot be invoiced*.

**Open beside it, if you want the figures on screen:**
[`project-sh16/crew-day.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/crew-day.md)
— 38 crew-days, 18 office days, rate `A4` — and
[the principals brief](../for-principals/index.md) for the second slide.

**Wrong rather than slow.** Nothing can break here that is not the projector.
Both slides were written out of files already committed, and a test fails if
the slide and the build-up ever disagree.

**Do not claim hours saved.** Nobody measured it. The speaker note says so and
so does the brief.

### 0:52 · Stretch + questions

**On screen.** One section break slide. Five minutes.

**You do.** Get the room standing. Take questions.

**Wrong rather than slow.** Nothing on screen to lose.

**Seneca lands here**, once the floor has gone quiet. This is the skeptical
one, and its own note says so — it asks what the agent actually saved, in
hours, on this job, and the answer is that nobody measured it.

### 0:57 · Act II — Find the control

**On screen.** A section break, then six: what we asked it to find, the NGS
marks, the TxDOT control points, the ROW map sheets, the datum gap, and the one
genuinely live call.

**You do.** Read the findings off the run. Three of them are easy to say
wrongly:

- **11 NGS marks, every one `MARK NOT FOUND`.** Not "several." Every one.
- **4 TxDOT control records naming 2 distinct monuments.** A record count is
  not a monument count, and a crew drives to the monument.
- **69 ROW sheets reach the corridor, 15 of them SH16's own.** The county
  figure is 27. Both are right. Say which one you are quoting.

**Open:** [`docs/scenarios/sh16/capture-note.md`](../scenarios/sh16/capture-note.md),
which reads the findings out in the order you need them, and
`project-sh16/screening.json` behind it.

**Then run the one live call:**

```bash
python -m corridor_screen.live_check --out ../project-sh16
```

**You should see** a live answer compared against the committed capture:

```
  Live check -- NGS Data Explorer, 29.528488, -98.644635

  This call was live, just now.

    marks in both        5
    conditions agreeing  5
```

**Wrong rather than slow.** Five is what it found last time, not a promise —
it is a live call. If NGS does not answer, say so and move on. Losing it costs
the live moment and nothing else; the screening run is unaffected either way,
and the command says so itself when there is no network.

**Remember this one writes to the cache.** In the rehearsal, point `--out` at
your scratch folder, or expect two modified files in `git status` afterward.

**Seneca lands here**, after the first bullet of *The NGS marks*, on eleven out
of eleven not found.

### 1:18 · Act III — The estimate package

**On screen.** A section break, then three: the bid memo, the flagged parcel
table, the crew-day build-up.

**You do.** Open the two documents, then build the third in front of them.

**Open:**
[`project-sh16/bid-memo.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/bid-memo.md)
— the document a principal reads before pricing — then
[`project-sh16/flagged-parcels.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/flagged-parcels.md),
**8 of 524 tracts**, sorted so the one needing a phone call soonest is first.
`project-sh16/flagged-parcels.svg` is the projector drawing of the same thing.

**Run the build-up live:**

```bash
python -m corridor_screen.crew_day --out ../project-sh16
```

**You should see** the field and office totals kept apart, and the two lines
that have no total at all:

```
  field     299.29 hours  =  38 crew-days of 2
  office    138.26 hours  =  18 office days
  The two are never added together.
```

**The missing lines are the point, not an embarrassment.** Two rows say an
input was never measured, and their hours are missing from the figures rather
than counted as zero. Every rate carries a handle, `A1` to `A12`, and all of
them are somebody's assumption rather than TxDOT's. Invite the room to argue
with a row instead of with a total.

**Wrong rather than slow.** The build-up is **Cut 2 of 3** — if the clock is
bad, open the committed
[`project-sh16/crew-day.txt`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/crew-day.txt)
as finished output instead of building it. The commands behind the other two
documents are `python -m corridor_screen.bid_memo` and `python -m
corridor_screen.parcel_table`, same `--out`, if you ever want to write one in
front of the room.

**Seneca lands here**, after the first bullet of *The flagged parcel table*, on
five hundred and twenty-four.

### 1:36 · Review, seal — and the three failures

**On screen.** A section break, then five: where the work got sent back, the
three beats, and *You seal it. You own it.*

**You do.** Show the sending-back first, from the repo rather than from GitHub,
then run the three beats in order.

**Open:** [the force push](../managing-your-agent/the-force-push.md) and [the claim we got
wrong](../managing-your-agent/the-claim-we-got-wrong.md).

**Beat 1 — the superseded manual:**

```bash
python -m corridor_screen.manual_links --show
```

It prints both addresses, what each serves, and the revision the agent cited —
March 2025 against the April 2026 that replaced it. Every line reads from disk
and needs no network.

**Beat 2 — wrong, not missing:**

```bash
python -m corridor_screen.elevation_trap --show
```

One question asked twice, one word apart: `units=Feet` answers a JSON number in
feet, `units=US_Feet` answers a JSON string in meters. HTTP 200 both times, no
error either time, and nothing in the reply saying which unit.

**Beat 3 — the error in our own work order:** open
`corridor-screen/captures/the-work-order/issue-7.txt`, which holds acceptance
criterion 4 and then the comment that refused to write it, and [the seal
page](../governance/seal-and-responsible-charge.md) for what PAO 71 actually
says.

**Wrong rather than slow.** Both commands have a committed `.txt` beside them
for a podium where Python will not start — they are on [the fallback
card](fallbacks.md). **Beat 3 is the one that changes the shape of the talk**
and it needs about three minutes to land, because the room has to see the work
order before it sees the catch. If you are behind at 1:36, cut **beat 2**, not
beat 3.

**Seneca lands here**, after the last bullet of *You seal it. You own it.*, on
what it means to seal something an agent produced.

### 1:48 · Hermes

**On screen.** A section break, then *The letter nobody remembers to send*.

**You do.** Run it and walk the three steps that derive day 21.

**Run:**

```bash
python -m corridor_screen.roe --show
```

**You should see** the tract, where day 21 comes from, and the clock writing
the second letter on its own:

```
    2026-09-13   day 0   request 1 of 2 written
    2026-10-03   day 20  nothing due
    2026-10-04   day 21  request 2 of 2 written -- no human action
```

**The number is derived, not quoted.** No published right-of-entry turn-around
was found in any TxDOT manual this repo read, so 21 comes from the lead-time
table: the longest confirmed wait is 45 days, half of it is 22, rounded down to
whole weeks is 21. Change the table and the day changes. There is no 21 written
anywhere in the tool.

**Wrong rather than slow.** This block is **Cut 1 of 3** — first on the cut
line, and the one most likely to be played from a file. The recording is at
`corridor-screen/captures/the-letter-that-sends-itself/the-demo.txt`.

### 1:54 · Accountability · Monday morning · the live issue

**On screen.** A section break, then three: the pattern said out loud, Monday
morning, and the form.

**You do.** Say the pattern — **corridor → public data → flagged list → lead
times** — and say out loud that it works for a ranch boundary and an ALTA as
well as for a highway. Then open one issue live and fill the first box in
yourself, so the room watches somebody do it once.

**Where to go:** `github.com/RickSmith/survey-recon` → Issues → New →
*Introduce yourself*. The form itself is
`.github/ISSUE_TEMPLATE/introduce-yourself.yml`.

**Say the public-and-permanent line out loud** rather than letting them read
it. No client names, no job numbers.

**Wrong rather than slow.** It cannot collect a single reply without GitHub,
and that is a fact about the ask rather than a failure of it. With no network,
put the form file on screen, read the question out, and ask the room to do it
from their seats that evening. **The short link and the QR code do not exist
yet** — [#10](https://github.com/RickSmith/survey-recon/issues/10), then
[#38](https://github.com/RickSmith/survey-recon/issues/38) — so the route on
the slide is typed rather than scanned.

**This block is on the never-cut list.**

---

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

1. **Run `git status` first**, before anybody closes a laptop. See [what the
   rehearsal changes](#what-the-rehearsal-changes-in-the-repo)
2. Go round the room once. The watchers first, because they will not volunteer
3. Open one issue per problem. Not one issue holding a list
4. Say what went wrong and where, using the block name from the timing sheet
5. Label it `ready-for-agent` if it is fully specified, `ready-for-human` if a
   person has to do it. [What the labels mean](../agents/triage-labels.md) has
   the rest
6. Close [#36](https://github.com/RickSmith/survey-recon/issues/36) with a
   comment naming the issues that came out of it

The timing sheet goes in too. Photograph it and attach it to the closing
comment, so the next person to run this has real numbers rather than a plan.

## How this page is kept honest

`corridor-screen/tests/test_dry_run.py` reads this page on every test run and
holds it to the documents it is quoting:

- the eleven blocks, their names, their planned starts and their lengths, against
  [the plan of record](../plan-of-record.md) §5 — and **every block has a section
  above**, so a block added to the session cannot quietly arrive without
  instructions
- the two screening lines, character for character, against
  `corridor-screen/README.md`, which is where a presenter is told to copy them
  from rather than retype them
- the six interjections, counted against the deck rather than against this page
- the cut line and the never-cut list, against §7

That matters because this is the third place the run of show is written down —
the plan of record sets it, the deck's speaker notes carry it, and this page
hands it to a timekeeper. A third copy nobody tests is a third copy that rots,
and this repo has published four corrections already for exactly that.

**What no test can check** is whether the output quoted above is still what
these commands print. Those blocks were captured from real runs on 2026-09-13 —
live and cache-only both, and each of the beats — and they are here so a
presenter knows the difference between a demo that is slow and a demo that is
wrong. If you run one in the rehearsal and it does not look like this, that is
a finding, and it becomes an issue like any other.
