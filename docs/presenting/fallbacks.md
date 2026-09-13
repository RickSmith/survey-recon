# If it breaks on the day

**Find your row by the clock.** The left column is the time on the session
timer. The third column is the one thing to open or type. Nothing in it needs a
network connection.

Print this page. A page you have to load is a page you cannot load at the
moment you need it.

| Time | What is on screen | Reach for | What it stands in for |
|---|---|---|---|
| 0:00–0:08 | Cold open — the agent takes the SH16 job | `python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only` | The whole screening run. Fourteen services, every answer off the disk, finishing at `parcels 524`. It makes no network calls at all, not even the reachability ping |
| 0:08–0:20 | What is an agent | not recorded — #12, then #31 | The deck. There is nothing to fall back to until the slides exist. Export the PDF onto the laptop as soon as they do |
| 0:20–0:30 | Vocabulary of managing one | not recorded — #12, then #31 | The same deck. The words themselves are in `CONTEXT.md`, which is not a slide and will not save this block |
| 0:30–0:46 | Act I — the grilling | not recorded — #75 | The live grilling, and the work orders it writes onto the projector. **There is a degraded version** and it is written out below. Read it before the day, not on the day |
| 0:46–0:52 | The money slide | not recorded — #32 | The slide itself |
| 0:52–0:57 | Stretch and questions | nothing live | Nothing on screen to lose |
| 0:57–1:18 | Act II — find the control | `docs/scenarios/sh16/capture-note.md` · `project-sh16/screening.json` | Eleven NGS marks, every one `MARK NOT FOUND`; two distinct TxDOT monuments; 69 ROW sheets reaching the corridor, of which 15 are SH16's own. The capture note reads the findings out in the order you need them |
| 0:57–1:18 | The one genuinely live call | `docs/scenarios/sh16/capture-note.md` | The NGS cross-check as it ran on 2026-09-13 — five marks in both, five conditions agreeing. Losing it costs the live moment and nothing else. Say that out loud and move on |
| 1:18–1:36 | Act III — the bid memo | `project-sh16/bid-memo.md` | The document a principal reads before pricing, exactly as the tool wrote it |
| 1:18–1:36 | Act III — the flagged parcels | `project-sh16/flagged-parcels.md` · `project-sh16/flagged-parcels.svg` | Eight of 524 tracts, sorted so the one needing a phone call soonest is first. The `.svg` is the projector drawing |
| 1:18–1:36 | Act III — the crew-day build-up | `project-sh16/crew-day.txt` · `project-sh16/crew-day.md` | The build-up as the console prints it. The `.md` carries every rate and its handle, `A1` through `A12`, for the argument afterward |
| 1:36–1:48 | Review and seal | `docs/managing-your-agent/the-force-push.md` · `docs/managing-your-agent/the-claim-we-got-wrong.md` | Where work got sent back, told from the repo instead of from GitHub |
| 1:36–1:48 | Beat 1 — the superseded manual | `python -m corridor_screen.manual_links --show` · `corridor-screen/captures/superseded-manual/the-beat.txt` | Both URLs, what each one serves, and the revision the agent cited. The `.txt` is the same beat for a podium where Python will not start |
| 1:36–1:48 | Beat 2 — the silent `NoData` | `python -m corridor_screen.elevation_trap --show` · `corridor-screen/captures/silent-nodata/the-beat.txt` | One question asked twice, one word apart, answered in feet and then in meters with no error either time |
| 1:36–1:48 | Beat 3 — the error in our own work order | `corridor-screen/captures/the-work-order/issue-7.txt` · `docs/governance/seal-and-responsible-charge.md` | Acceptance criterion 4, then the comment that refused it. The governance page carries what PAO 71 actually says, so the opinion needs no network either |
| 1:48–1:54 | Hermes — the letter that sends itself | not recorded — #34 | The demo. It is first on the cut line, and its own work order asks for a recording |
| 1:54–2:00 | Accountability, Monday morning, the live issue | `.github/ISSUE_TEMPLATE/introduce-yourself.yml` | The form you would have opened, on screen. It cannot collect a single reply without GitHub, so ask the room to do it from their seats. **The short link and the QR code are not made yet** — #10, then #38. Until they are, this row is a form nobody can reach |

## How to use it

**Run every command from the `corridor-screen` folder.** The `--out
../project-sh16` on the cold-open line is written from there.

**Do not retype the cold-open line.** It is 119 characters and five flags, and
the day you need it is the day you will mistype it. The same line is in
`corridor-screen/README.md` under *If the network is down* — copy it from
there, or have it open in a second window before you start.

**Say what you are doing.** The plan of record is blunt about this: undisclosed
caching, if noticed, costs you the room. The line is already written —
*"these were captured on the 12th and 13th of September, so we're not at the
mercy of the hotel Wi-Fi. The code is live code and you can run it yourself."*

**Open a file rather than a website.** Every path above is a file in this
repo, on the laptop, in a folder. None of them is a link.

## What has no fallback yet, and why

**5 blocks have nothing to reach for**, and four pieces of work would close
them — the deck accounts for two of the five blocks on its own.

Three of the four are waiting on something that does not exist yet, so an audit
can do nothing but name them: the deck (#12, then #31), the money slide (#32)
and the Hermes demo (#34).

**Act I is the different one.** The grilling already happened — the spec it
produced is `docs/corridor-screen/spec.md` and the work orders are on the issue
tracker. What was never recorded is the *run*: the agent working, and the
issues appearing. That is sixteen minutes and it is the hinge of the session,
so it has its own work order, #75, and it is a recording job rather than a
rehearsal.

If Act I dies on the day and #75 is still open, put the spec on screen and walk
it. It is the output of the real grilling, so it is honest. It is not the demo.

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
exactly one — the Act I spec — so if that file ever moves, this page will not
notice and you will.

A fallback page that is out of date is worse than no page, because it gets
followed. This one fails the test suite instead.

**Somebody still has to run that suite.** GitHub Actions builds this site and
the deck on every push and does not run a single test — so the check above runs
when a person types it, or when an agent does before a pull request. That gap
is #78. Until it closes, run this before the dry run and before the day:

```bash
cd corridor-screen && python -m unittest discover -s tests -t .
```

Written under [issue #27](https://github.com/RickSmith/survey-recon/issues/27),
which asked whether the set was complete. It was not, and the gaps above are
the answer.
