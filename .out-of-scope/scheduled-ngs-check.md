# A scheduled check on the live NGS call

This repo does not run the NGS live check on a timer. It is typed by a person,
when a person wants to know.

## Why this is out of scope

**Rick's reason, in his words on 2026-09-15: it was a one-off, and he does not
see the need to check on a regular basis.**

The live check exists to prove one thing in one moment — that the tool really
talks to NGS, while a room watches. It is not monitoring. Nothing in this repo
depends on the endpoint being up, and nothing breaks when it is down: the
screening run replays a committed capture and makes no network calls at all.

So a scheduled run would watch a thing that has no alarm attached to it. The
right time to know whether NGS is answering is when somebody is about to stand
up and ask it, and that person can type the command.

## What was proposed, and why it looked reasonable

Work order #128 asks for a daily check until 2026-10-01, after the endpoint
returned an empty list one day and refused with a 403 an hour later. Sixteen
days of somebody remembering is a weak link, and it is weak in two directions:
forget a day and the record has a hole, remember twice and you have made two
calls. That second one matters, because the leading guess for the 403 is that
three of our own calls in ninety minutes tripped a rate limiter.

The pattern was there to copy. `.github/workflows/roe-followup.yml` already runs
a command daily, in public, writes the outcome to the run summary, and commits
nothing.

It was a fair suggestion. It was also an agent solving for a tidier record
rather than for a real need, which is the failure mode this folder exists to
catch.

## What replaces it

Nothing automatic. #128 keeps its by-hand check and its own caution, written
before any of this came up: **once a day, and not once more.** With no scheduled
run in the way, a call typed by a person is the only call that day, which is
simpler than the thing that was proposed and does the same job.

## If this comes round again

Ask before opening it. The answer has been given once.

The answer would genuinely change if something in this repo ever *depended* on
NGS being reachable. It does not today, by design, and `live_check.py` says so
in its own header: the worst a dead network can do is cost the live moment.

## Prior requests

- #150 — "Run the NGS live check on a schedule, so nobody has to remember."
  Opened and closed on 2026-09-15. Raised during triage of #128 rather than by
  anybody asking for it
