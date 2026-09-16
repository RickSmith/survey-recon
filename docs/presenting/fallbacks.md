# If it breaks on the day

**Find your row by the clock.** The left column is the time on the session
timer. The third column is the one thing to open or type. Nothing in it needs a
network connection.

Print this page. A page you have to load is a page you cannot load at the
moment you need it.

| Time | What is on screen | Reach for | What it stands in for |
|---|---|---|---|
| 0:00–0:08 | Cold open — the agent takes the SH16 job | `python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only` | The whole screening run. Fourteen services, every answer off the disk, finishing at `parcels 524`. It makes no network calls at all, not even the reachability ping |
| 0:08–0:20 | What is an agent | on the laptop — the deck PDF, put there by [the dry run](dry-run.md) | The block itself. These twelve minutes are slides and nothing else, so the slides are the fallback. The PDF is rendered on every push and published with the site, which is exactly where you cannot reach it, so it gets downloaded before the day rather than during it |
| 0:20–0:30 | Vocabulary of managing one | on the laptop — the same PDF, put there by [the dry run](dry-run.md) | The same ten-minute answer, from the same file. The words themselves are in `CONTEXT.md`, which is not a slide and will not save this block |
| 0:30–0:46 | Act I — the grilling | `corridor-screen/captures/the-grilling/README.md` · `corridor-screen/captures/the-grilling/the-grilling.md` · `corridor-screen/captures/the-grilling/the-tickets.md` | The real `/grill-with-docs` run that wrote the spec. The README is Act I on one screen — 19 questions, what the agent recommended, what Rick answered. Open that first; the other two are the full run and the 35 work orders that followed |
| 0:46–0:52 | The money slide | `project-sh16/crew-day.md` · `docs/for-principals/index.md` | The two money slides, each from the file it was written out of. The build-up carries every figure on the first (38 crew-days, 18 office days, rate `A4`) because that is where the slide reads them from. The principals brief carries the second, including the TxDOT sentence about a non-compliant survey and its citation |
| 0:52–0:57 | Stretch and questions | nothing live | Nothing on screen to lose |
| 0:57–1:18 | Act II — find the control | `docs/scenarios/sh16/capture-note.md` · `project-sh16/screening.json` | Eleven NGS marks, every one `MARK NOT FOUND`; two distinct TxDOT monuments; 69 ROW sheets reaching the corridor, of which 15 are SH16's own. The capture note reads the findings out in the order you need them |
| 0:57–1:18 | The one genuinely live call | `docs/scenarios/sh16/capture-note.md` | The NGS cross-check as it ran on 2026-09-13 — five marks in both, five conditions agreeing. Losing it costs the live moment and nothing else. Say that out loud and move on |
| 1:18–1:36 | Act III — the bid memo | `project-sh16/bid-memo.md` | The document a principal reads before pricing, exactly as the tool wrote it |
| 1:18–1:36 | Act III — the flagged parcels | `project-sh16/flagged-parcels.md` · `project-sh16/flagged-parcels.svg` | Eight of 524 tracts, sorted so the one needing a phone call soonest is first. The `.svg` is the projector drawing |
| 1:18–1:36 | Act III — the crew-day build-up | `project-sh16/crew-day.txt` · `project-sh16/crew-day.md` | The build-up as the console prints it. The `.md` carries every rate and its handle, `A1` through `A12`, for the argument afterward |
| 1:36–1:48 | Review and seal | `docs/managing-your-agent/the-force-push.md` · `docs/managing-your-agent/the-claim-we-got-wrong.md` | Where work got sent back, told from the repo instead of from GitHub |
| 1:36–1:48 | Beat 1 — the superseded manual | `python -m corridor_screen.manual_links --show` · `corridor-screen/captures/superseded-manual/the-beat.txt` | Both URLs, what each one serves, and the revision the agent cited. The `.txt` is the same beat for a podium where Python will not start |
| 1:36–1:48 | Beat 2 — wrong, not missing | `python -m corridor_screen.elevation_trap --show` · `corridor-screen/captures/silent-nodata/the-beat.txt` | One question asked twice, one word apart, answered in feet and then in meters with no error either time |
| 1:36–1:48 | Beat 3 — the error in our own work order | `corridor-screen/captures/the-work-order/issue-7.txt` · `docs/governance/seal-and-responsible-charge.md` | Acceptance criterion 4, then the comment that refused it. The governance page carries what PAO 71 actually says, so the opinion needs no network either |
| 1:48–1:54 | Hermes — the letter that sends itself | `python -m corridor_screen.roe --show` · `corridor-screen/captures/the-letter-that-sends-itself/the-demo.txt` | The tract, the three steps that derive day 21 from the lead-time table, and the clock writing the second letter on its own. The `.txt` is the same demo for a podium where Python will not start |
| 1:54–2:00 | Accountability, Monday morning, the live issue | `.github/ISSUE_TEMPLATE/introduce-yourself.yml` | The form you would have opened, on screen. It cannot collect a single reply without GitHub, so ask the room to do it from their seats. **The short link and the QR code are not made yet** — #10, then #38. Until they are, this row is a form nobody can reach |

## How to use it

**Run every command from the `corridor-screen` folder.** The `--out
../project-sh16` on the cold-open line is written from there.

**Do not retype the cold-open line.** It is 119 characters and five flags, and
the day you need it is the day you will mistype it. The same line is in
`corridor-screen/README.md` under *If the network is down* — copy it from
there, or have it open in a second window before you start.

**Say what you are doing — this is the line for when you have fallen back, not
the opening script.** The plan is to run live, and the SH16 run really did call
all fourteen services on 13 September. The cold-open slide promises real code
and real data, and names the cache as the backup. So you only need this the
moment you actually switch to it:

> *"This is running off answers we captured on the 12th and 13th of September,
> so we're not at the mercy of the hotel Wi-Fi. The code is live code and you
> can run it yourself."*

Say it the moment you switch, not at the end. Undisclosed caching, if noticed,
costs you the room — the plan of record is blunt about that, and it is why the
disclosure is on the slide as well as here.

**Open a file rather than a website.** Every path above is a file in this
repo, on the laptop, in a folder. None of them is a link.

**One row is a file that is not in this repo**, and it says so: the deck PDF,
for the two blocks that are nothing but slides. Nothing rendered is committed
here, so that copy gets onto the laptop because a person put it there.
[The dry run](dry-run.md) carries the step, under *Put the deck on the
laptop*, and it is the reason a row of that kind is allowed to name something
this repo cannot check for you.

## What has no fallback yet, and why

**0 blocks have nothing to reach for**. Every block of the two hours now has a
file, a command, or a copy the runbook puts on the laptop before the day.

**The deck used to be on this list and is not any more**, and it is the only
row here that was closed by writing down a step rather than by committing
something. It is worth reading, because the shape of it will come round again.

Two blocks, 0:08 and 0:20, are slides and nothing else. That is twenty-two
minutes with no demo to run. Their slides were written under #81 through #86.
This card went on saying those blocks had nothing, for as long as it took
somebody to notice that **written is not the same as reachable**. The file
`slides.yml` renders the PDF on every push. Then `docs.yml` publishes it with
the site, which is precisely where a presenter with no network cannot get at
it. The deck's **source** is committed, and it is still not the fallback. Every
slide carries its speaker note. Several of those notes are about handling the
room rather than the subject. That is a crib sheet, not something to put on a
projector.

Committing the rendered PDF would have closed it in one line. It was decided
against under [#123](https://github.com/RickSmith/survey-recon/issues/123), on
two grounds. Nothing rendered is committed here. And a stale binary nobody
re-renders is a worse trap than a missing one: it opens, it looks right, and it
is three weeks old. So the fallback is a step instead: [the dry
run](dry-run.md) has the presenter download it and open it once with the
network off, and again before 8 October.

**That is a weaker guarantee than every other row on this card, and it is the
honest one.** Everything else here is checked on every pull request. This one
cannot be, because the file is not in the repo. What is checked is that the
step exists and gives the right address. `test_dry_run.py` is what checks it.
That is the most a test can do about a thing a person has to remember.

**The money slide used to be on this list and is not any more**, and nothing had
to be recorded for it. Both of its slides were written out of files that were
already committed. The billable-hour math is read out of
`project-sh16/crew-day.md`, and `corridor-screen/tests/test_money_slide.py`
fails if the slide and the build-up ever disagree — so the build-up is not a
stand-in for that slide, it is where that slide came from. The block's own
speaker note has named it as the fallback all along. This card is what did not
say so. The rework argument, and the TxDOT sentence that carries it, is on
`docs/for-principals/index.md` with its citation.

**Hermes used to be on this list and is not any more.** The demo was built
under #34 and the recording its own work order asked for is committed at
`corridor-screen/captures/the-letter-that-sends-itself/the-demo.txt`. That
mattered more than for most rows: the segment is **first on the cut line**, so
it is the block most likely to be played from a file rather than run.

**Act I used to be on this list and is not any more.** The grilling that wrote
the corridor-screening spec really happened on 12 September 2026, and the
session it happened in was still on the presenter's machine. It is committed
now, redacted and cut to the grilling itself, under #75.

Two honest limits on it, both written on the capture. It is a **transcript, not
a recording** — there is no video of that session and there never was. And that
run did `/grill-with-docs` and `/to-spec` but never `/to-tickets`. So the work
orders are captured as a **result** (35 of them, stamped across 89 seconds)
rather than as a run.

## How this page is kept honest

`corridor-screen/tests/test_fallbacks.py` reads this page on every test run and
holds it to all of this:

- every block in the run of show has a line here, and no line here is for a
  block the run of show does not have
- every file in the **reach for** column is committed, is not empty, and opens;
  the drawing carries nothing it would have to go and fetch
- every command in that column **runs with the network taken away** — removed
  at the socket, which is the door every program goes through to reach a
  network, so nothing above it can quietly find a way out
- every gap says it is a gap, and names the work order that would close it
- the count of gaps in the paragraph above matches the number of rows that
  actually say so

Files named in the prose rather than in the table are not checked. There is
exactly one, the Act I spec. So if that file ever moves, this page will not
notice and you will.

**A named work order is checked for shape, not for state.** The test reads the
`#` and the number beside it. It cannot ask GitHub whether that issue is still
open, because the suite runs with the network taken away on purpose — that is
what proves the rest of the card works at a podium. So a work order can close
without the gap closing, and this page goes on pointing at finished work.

That is not hypothetical. It is what these rows did. #12 built the deck
skeleton, #31 ported the concept slides and #32 built the money slide. All three
closed. All three rows still read `not recorded`. A presenter reading down the
page would have taken the gap as closed along with them. The slides landed.
The export did not. The reason the check stays out of the suite is in the test
file beside the test it is about.

A fallback page that is out of date is worse than no page, because it gets
followed. This one fails the test suite instead.

---

## Where this came from

This card was written under
[work order #27](https://github.com/RickSmith/survey-recon/issues/27), which
asked whether the set of fallbacks was complete. It was not, and the section
above is the answer. The finding that a closed work order is not a closed gap
came out of [#96](https://github.com/RickSmith/survey-recon/issues/96).
