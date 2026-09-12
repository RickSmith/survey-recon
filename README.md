# survey-recon

**Reconnaissance for survey work, with an AI agent doing the legwork.**

Before you price a job you do a recon — what control already exists, how many tracts you're crossing, who you need permission from, how long the field crew really needs. This repo shows how to hand that work to an AI agent, and more importantly, how to supervise one well enough to trust the answer.

Built for the TSPS 2026 convention session *"Beyond the Prompt."*

---

## Start here

**You do not need to be a programmer.** You do need three things: a GitHub account, git installed, and the Claude desktop app. The setup chapter walks through all three with screenshots.

→ **[Day 0: Setup](docs/day-0/)** — start from zero
→ **[For principals](docs/for-principals/)** — one page, no terminal, what to tell your team
→ **[The worked example](docs/scenarios/sh16/)** — a real TxDOT ROW job, start to finish

## What's in here

| | |
|---|---|
| **The worked example** | Estimating a TxDOT ROW retracement on SH16 in Bexar County, using only public data |
| **The corridor screening tool** | Buffer an alignment, query public services, get back a flagged parcel list with statutory lead times |
| **Agent configuration** | A `CLAUDE.md` employee handbook and a working skill set you can copy into your own firm's projects |
| **Data sources** | Verified, working endpoints for TxDOT GIS, NGS, county parcels, and more |
| **Governance** | A firm AI-use policy, a what-never-leaves-the-office checklist, and seal and responsible-charge language |

## The idea

An agent is a new kind of employee — capable, fast, tireless, and occasionally confidently wrong in ways a new hire is confidently wrong. Managing one well takes the same things managing any new hire takes: a clear scope of work, small assignments, visible progress, and somebody checking the work before it goes out the door.

Software developers already built that discipline. This repo borrows it and translates it:

| Their word | Your word |
|---|---|
| Issue | Work order |
| Branch | A working copy nobody else is affected by |
| Commit | A field book entry |
| Pull request | The check print you redline |
| Merge | You sign and seal |

**The accountability never moves.** TBPELS has not spoken directly to AI, but responsibility doctrine already covers it: you seal it, you own it.

## Credits

The development-lifecycle skills are a curated subset of [mattpocock/skills](https://github.com/mattpocock/skills), MIT licensed, copyright © 2026 Matt Pocock. Vendored here so you don't need Node installed. See `toolkit/.claude/skills/`.
