# The letter that sends itself — the recording

**This is not a failure beat.** The three folders beside it hold work that was
confidently wrong and then caught. Nothing in this one is wrong. It is the
Hermes segment, 1:48–1:54 on the run of show, committed as text so it can be
played rather than run.

Its work order asks for exactly that: the segment is **first on the cut line**,
so it was built to survive being reduced to a recording.

| File | What it is |
|---|---|
| `the-demo.txt` | The demo as `--show` renders it, written by `python -m corridor_screen.roe --write-fallback` and pinned to the code by a test |

## What it shows

Three things, in order.

1. **The tract**, read out of [`project-sh16/screening.json`](../../../project-sh16/screening.json)
   — parcel `15664-003-0040`, a cemetery on it, 14 calendar days of written
   notice behind [Tex. Health & Safety Code § 711.041(c)(2)](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm).
2. **Where day 21 comes from.** No published TxDOT right-of-entry turn-around
   was found, so there is no number to quote. The interval is derived from the
   checked-in lead-time table in three steps, printed on screen.
3. **The clock.** Day 0 writes the first letter. Day 20 has nothing due. Day 21
   writes the second, with no human action.

## There are no captured responses here

Every other folder under `captures/` holds saved HTTP responses, because those
beats are claims about what a server said. This one makes no claim about a
server. Its inputs are two files already committed in this repo — the SH16
screening run and
[`lead_times.toml`](../../corridor_screen/lead_times.toml) — so there is
nothing to capture that is not already under version control.

That is also why this module exports `demo` rather than `beat`:
`tests/test_beats.py` finds beat modules by looking for a callable named
`beat`, and would rightly demand captures with URLs behind them. See
[`beats.py`](../../corridor_screen/beats.py), *The shape a beat module has*.

## What it borrows from the beats

**The plain-ASCII rule.** It prints to the same podium console, so it is
rendered through `beats.render`, which refuses a character a Windows console
that has not been told otherwise cannot print. That guard earned its place
here on the first run: Union Pacific's own page title carries an em dash, and
printing the citation as its title rather than its URL failed immediately.
