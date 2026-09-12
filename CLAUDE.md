# CLAUDE.md — how to work in this repo

Read `CONTEXT.md` first for vocabulary. This file is about conduct.

---

## The process rule, which is not optional

**Every piece of work goes through a GitHub issue. Every change lands as a pull request that a human reviews.** Even when it is slower. Even for a one-line fix.

This is not ceremony. This repo's own git history is a teaching artifact that gets shown on stage — the issues, the reviews, the places work got sent back. A clean, squashed, frictionless history would be a *worse* repo for this purpose.

- Do not squash commits or rewrite history
- Do not merge your own work without review
- Write commit messages that explain **why**, not what — the diff already says what
- When a review sends something back, fix it in a new commit rather than amending. The correction is part of the record

## Audience rules

Readers are expert surveyors with little programming background. So:

- **Introduce every software term by its survey equivalent first.** See the translation table in `CONTEXT.md`
- **Never condescend about the programming gap.** These are licensed professionals who know things you do not
- **No unexplained jargon.** If a term is not in `CONTEXT.md`, either define it inline or add it to `CONTEXT.md`
- Prefer short sentences and concrete examples over abstraction
- Screenshots earn their place in setup docs. Use them generously there

## Dependency discipline

Attendees must be able to run this. Prerequisites are **git, a GitHub account, and the Claude desktop app** — nothing else.

- **Do not add a Node dependency to anything attendees run.** The mattpocock skills are vendored as markdown into `toolkit/.claude/skills/` precisely so `npx` is not required
- Python is acceptable for the corridor tool, standard library plus `requests` where possible
- Every new dependency needs a justification in the pull request
- Anything that needs an API key does not belong in the attendee path

## Data rules

- **Public sources only. No client data, ever.** The repo is public and stays public
- Every data source gets documented in `docs/data-sources/` with its endpoint, its fields, and its quirks
- **Cache every API response into `project-sh16/cache/`, stamped with the capture date and the exact request URL.** The conference network is untrusted and the TxDOT ROW server blocks intermittently
- Cached data is for demo reliability, not deception — the docs say plainly that responses were captured, and the code is real code

## Accuracy rules — this repo will be cited by licensed professionals

- **Never invent a TxDOT requirement.** Cite the manual section and its URL, or say you could not confirm it
- **Use `txdot.gov/manuals/row/ess/...` URLs. Never `onlinemanuals.txdot.gov`** — those are superseded, and search engines still surface them. This exact trap is a scripted demo in the session
- When research could not confirm something, write "not found" rather than "does not exist," and say where you looked
- Statutory citations get the code and section number, e.g. Tex. Occ. Code § 1071.3585
- Numbers with legal consequence — accuracy tolerances, notice periods, fees — get a source link next to them

## Tone

The session's thesis is that an agent is a capable new employee who is sometimes confidently wrong, and that the licensed human remains accountable. Documentation should sound like that: **enthusiastic about the capability, unembarrassed about the limits, and absolutely clear about who signs.**

Do not oversell. A surveyor who tries something on Monday because this repo promised too much is a worse outcome than one who never tries at all.

## Agent skills

### Issue tracker

Issues live as GitHub issues on `RickSmith/survey-recon`, driven by the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` at the root, ADRs in `docs/adr/`. See `docs/agents/domain.md`.
