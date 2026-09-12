# survey-recon — HANDOVER

**Read this first.** This folder is the complete, self-contained starting state for a conference session and its take-home repo. It was planned in a Claude session that is not transferring; nothing from that session's memory or project workspace comes with it. **These files are the only source of truth.**

---

## What this is

A two-hour session for the **Texas Society of Professional Surveyors (TSPS) 2026 convention on Thursday, October 8, 2026**, titled *"Beyond the Prompt: Getting Started with Agentic AI for Geomatics Tools and Workflows."*

Presented by Rick Smith (Executive Director, Conrad Blucher Institute, TAMU-CC) with Seneca Holland.

The session's thesis: **an AI agent is a new kind of employee, and surveyors need enough of a software-development manager's vocabulary to supervise one properly.** Rather than a PowerPoint, attendees leave with this public GitHub repo — `survey-recon` — containing the worked example, a firm-ready agent configuration, verified public data sources, and governance templates.

The session is **watch-only** in the room. Hands-on happens afterward, from the repo. That makes the repo the actual deliverable; the talk sells it.

## Hard facts

| | |
|---|---|
| Deadline | **October 8, 2026** — immovable |
| Planned on | September 12, 2026 |
| Session length | 2 hours |
| Audience | Mostly **firm owners and principals** — buyers and risk-owners, not operators |
| Repo | `survey-recon`, Rick's personal GitHub, **public** |
| Worked example | TxDOT SH16 (Bandera Rd), Loop 410 → Gibeaut Rd, Bexar County |
| Data policy | **Public sources only.** No client data, ever. |

## Current status

**Planning is complete. Nothing is built yet.**

- [x] Session designed, twenty decisions locked — see `docs/plan-of-record.md`
- [x] Research done and endpoints verified live — see `docs/txdot-research.md`
- [x] Repo name chosen: `survey-recon`
- [ ] Repo created on GitHub
- [ ] Anything else

## What's in this folder

| File | What it is |
|---|---|
| `HANDOVER.md` | This file |
| `README.md` | The repo's public front door (draft) |
| `CONTEXT.md` | Shared domain language — surveying and project vocabulary the agent needs |
| `CLAUDE.md` | How an agent must work in this repo |
| `docs/plan-of-record.md` | Every decision, the run of show, the schedule. **The spec.** |
| `docs/txdot-research.md` | Verified API endpoints, TxDOT rules, ROE lead times, demo-risk ratings |
| `issues/001-scaffold-mkdocs-marp.md` | The first issue, written by hand on purpose |
| `issues/BACKLOG.md` | The rest of the work, ready to become issues |

## Do not re-litigate

The planning conversation ran fourteen questions across two rounds. The decisions in `docs/plan-of-record.md` §1 are **settled**. A new session should read them and build, not re-open them. In particular, do not re-run a project-level grilling session — that already happened, and `docs/plan-of-record.md` is its output.

Three things genuinely remain open, listed in `docs/plan-of-record.md` §8.

## What to do first

1. Create the `survey-recon` repo on GitHub, public. Copy these files in. Pick a license.
2. Install the mattpocock skills for **your own** working copy: `npx skills@latest add mattpocock/skills`, then `/setup-matt-pocock-skills`. *(Note: a curated five-command subset gets vendored into `toolkit/.claude/skills/` later as the attendee artifact. Those are two different things — attendees must not need Node.)*
3. Create issue #1 from `issues/001-scaffold-mkdocs-marp.md`, by hand.
4. Run `/to-tickets` against `docs/plan-of-record.md` §7 and `issues/BACKLOG.md` to generate the rest.
5. Then: `/grill-with-docs` on the **corridor-screening tool** — the one genuinely unspecified piece, and the highest-risk build item. This doubles as a rehearsal of the session's centerpiece demo.

## The one rule that matters most

**Every piece of work goes through an issue, and every change lands as a pull request that Rick actually reviews.** Not because it is faster — it is not — but because the repo's own git history becomes the teaching artifact. On stage Rick says: *"Everything you're looking at was built the way I'm telling you to work. Here are the issues. Here's where I sent it back. Here's one I approved that I shouldn't have."*

**Do not squash the history clean.** The messy parts are the curriculum. Tag two or three instructive pull requests with a `teaching-moment` label as you go.
