# Toolkit

**The part you take home.** Copy one folder into your own project and you have a
supervised agent: a handbook it reads, a glossary it uses, and five commands that
carry a job from "somebody wants something" to "you signed it."

Nothing in it is about TxDOT, SH16, or this repo.

[Open the toolkit folder on GitHub](https://github.com/RickSmith/survey-recon/tree/main/toolkit){ .md-button .md-button--primary }

---

## Two words first

A **skill** is a written procedure the agent reads before it starts — the same
thing as the one-page procedure taped inside a survey vehicle. A **slash
command** is how you call for one by name: you type `/grill-with-docs` and the
agent opens that procedure and works through it.

Everything in this kit is one or the other, written in plain text you can open
and read.

## What you need

**git, a GitHub account, and the Claude desktop app.** Nothing in the toolkit
needs Node, npm, npx, Docker, Python, or an API key.

That is not an accident. The usual way to get these commands is a package manager
called npm, run through a command called `npx`, which needs Node.js installed,
which needs a terminal and often a Windows administrator. Copying the markdown
skips all of it.

!!! warning "One honest asterisk: `gh`"
    The kit is set up to keep work orders as GitHub issues, and that needs
    [GitHub CLI](https://cli.github.com) — **a fourth thing to install.** It is
    one program, no Node and no API key, but somebody in your firm may still have
    to approve it.

    If that is a problem, skip it. The kit's
    [`issue-tracker.md`](https://github.com/RickSmith/survey-recon/blob/main/toolkit/docs/agents/issue-tracker.md)
    also describes keeping work orders as plain files in the job folder, which
    needs nothing at all.

If you have never installed any of the three, start at
[Day 0: Setup](../day-0/index.md).

---

## What is in it

| File or folder | What it is |
|---|---|
| [`CLAUDE.md`](https://github.com/RickSmith/survey-recon/blob/main/toolkit/CLAUDE.md) | The employee handbook. Your firm's rules, read first every session |
| [`CONTEXT.md`](https://github.com/RickSmith/survey-recon/blob/main/toolkit/CONTEXT.md) | The glossary. The words your firm uses, so the agent stops guessing |
| [`docs/agents/`](https://github.com/RickSmith/survey-recon/tree/main/toolkit/docs/agents) | Where work orders live, and what the labels mean |
| [`.claude/skills/`](https://github.com/RickSmith/survey-recon/tree/main/toolkit/.claude/skills) | The five commands |

The [installation notes](https://github.com/RickSmith/survey-recon/blob/main/toolkit/README.md)
have the exact copy command for Windows and for macOS, and the one trap worth
knowing — `.claude` starts with a dot, and dragging it across by hand is easy
to get wrong. Finder hides it. File Explorer shows it, but sorts it away from
the files you are looking at.

---

## The five commands

They run in this order. You stop wherever you like.

| # | Command | Survey equivalent |
|---|---|---|
| 1 | `/grill-with-docs` | The scoping call, before you quote |
| 2 | `/to-spec` | Writing the scope of work |
| 3 | `/to-tickets` | Splitting the scope into work orders |
| 4 | `/implement` | Handing one work order to a crew |
| 5 | `/code-review` | Checking the work before it goes out the door |

!!! tip "The first one is the one that earns the rest"
    An agent that starts typing before the scope is settled produces a
    confident, fast, wrong answer. Being interviewed for twenty minutes feels
    like a delay. It is the same twenty minutes you already spend on the phone
    before quoting a job, and skipping it costs what it always did.

**Notice where `/implement` sits.** It is the only one of the five that changes
anything, and it is fourth. That is the point.

Why these five and not the other sixteen, and what each one actually does, is
written down in
[the skills README](https://github.com/RickSmith/survey-recon/blob/main/toolkit/.claude/skills/README.md).

Four more skills ship alongside them — `grilling`, `domain-modeling`, `tdd` and
`codebase-design`. You will not type those. The five call them by name while they
run, so they have to be there. **Every skill the five actually call is in the
kit**, which is worth more than it sounds: a command that fails half way through,
in front of somebody, is worse than one you never offered.

One is named and deliberately left out — a setup command whose answers this kit
already ships, written down. The skills README says what to do if it ever comes
up.

---

## Two files to fill in before you start

Anything in «guillemets» is a blank.

**`CLAUDE.md`** wants your firm name, who signs, and a list of what never leaves
the office. **That last list is the one with real consequences** — everything you
hand an agent goes to a company's servers, so treat it as though you had emailed
it outside the firm. Spend the time on it.

**`CONTEXT.md`** wants six words you are tired of explaining. Six is plenty for a
first version. It grows on its own after that, and `/grill-with-docs` adds to it
as terms get settled.

Everything else can wait.

---

## Credit and license

The five commands, and the four skills that support them, are a curated subset of
[mattpocock/skills](https://github.com/mattpocock/skills) — copyright © 2026
**Matt Pocock**, MIT licensed. Version 1.2.3, commit
[`068b6e0`](https://github.com/mattpocock/skills/commit/068b6e0c62393147daf03530149cdce209c93da8),
captured 2026-09-12. The commit is written down so you can check the copy against
the original yourself.

**They are copied byte-for-byte. We changed nothing inside them.** A modified
copy still carrying somebody else's name is how a document ends up blamed on the
wrong person. Where this kit needed to say something different, it says it in
`CLAUDE.md` instead — where the difference is visibly ours.

The license text travels with them, at
[`.claude/skills/LICENSE`](https://github.com/RickSmith/survey-recon/blob/main/toolkit/.claude/skills/LICENSE).

The trade-off of copying rather than installing is that these files do not update
themselves. When you want a newer version, copy the newer file over the top and
note the date — the same way you note the revision date on a manual you are
working from.

---

## Next

- **[Managing your agent](../managing-your-agent/index.md)** — the supervision
  loop in practice, using this repo's own check prints as the worked example
- **[Going further](../going-further/index.md)** — the full skill set, the npx
  route, and what else is out there
