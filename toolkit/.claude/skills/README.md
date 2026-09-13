# The five commands

A **skill** is a written procedure the agent reads before it starts. Same thing as
the one-page procedure taped inside a survey vehicle: *how we do a boundary
retracement here.* You do not hand it to a crew every morning. It sits there, and
they follow it.

A **slash command** is how you call for one by name. You type `/grill-with-docs`
and the agent opens that procedure and works through it.

Each folder below holds one skill. The file is called `SKILL.md` and it is plain
markdown — open it and read it. Nothing is compiled, generated, or hidden.

---

## The five

These five carry one job from "somebody wants something" to "it is signed." They
run in order. You can stop after any of them.

| # | Command | Survey equivalent | What it does |
|---|---|---|---|
| 1 | `/grill-with-docs` | The scoping call, before you quote | Interviews **you** about the job. Relentlessly. Writes down the words and the decisions as they get settled |
| 2 | `/to-spec` | Writing the scope of work | Turns that conversation into a written scope. No further questions — just what was already said |
| 3 | `/to-tickets` | Splitting the scope into work orders | Breaks the scope into separate jobs, each one saying which other jobs must finish first |
| 4 | `/implement` | Handing one work order to a crew | Does one job, on a working copy nobody else is affected by |
| 5 | `/code-review` | Checking the work before it goes out the door | Reads the change twice: once against how your firm writes things, once against what the work order actually asked for |

### Why these five, and not the other sixteen

The upstream set has twenty-five skills. Most of them are for people who write
software every day. These five are the ones that map onto work a survey firm
already does, and the ones that hold the accountability chain together.

**`/grill-with-docs` is the one that earns the rest.** An agent that starts
typing before the scope is settled produces a confident, fast, wrong answer.
Getting interviewed for twenty minutes feels like a delay. It is the same twenty
minutes you already spend on the phone before quoting a job, and skipping it
costs the same as it always did.

**`/to-spec` and `/to-tickets` make the work visible before it happens.** A scope
you can read is a scope you can argue with. A list of work orders is a list you
can hand to someone, refuse, or reorder. Without these two the agent's plan lives
only in the conversation, and a plan you cannot see is a plan you cannot
supervise.

**`/implement` is deliberately fourth.** It is the only one that changes anything.
Putting it fourth is the point.

**`/code-review` is what keeps the seal meaningful.** Something has to happen
between "the agent finished" and "you signed." This is that something. It does
not replace you reading it. It catches the obvious so your attention goes to the
rest.

What we left out, and roughly why:

- **Skills for running a large project** (`/wayfinder`, `/triage`) — real, useful,
  and more machinery than a first project needs
- **Skills for diagnosing existing software** (`/diagnosing-bugs`,
  `/improve-codebase-architecture`) — they assume a codebase you already have
- **Everything else** — writing tools, teaching tools, setup tools for other
  people's stacks

The full set is worth a look once these five feel ordinary. See
[Going further](https://ricksmith.github.io/survey-recon/going-further/).

---

## Four more skills are in here, and you will not type them

`/grill-with-docs` and `/implement` call other skills by name while they run. If
those are missing, the command fails part-way through. So they are vendored too,
and so is everything **they** call:

| Folder | Called by | Why |
|---|---|---|
| `grilling/` | `/grill-with-docs` | The interview itself — the questions, and the rounds they come in |
| `domain-modeling/` | `/grill-with-docs` | Writes the glossary and the decision records as terms get settled |
| `tdd/` | `/implement` | How to write a check that proves a piece of code does what it claims |
| `codebase-design/` | `tdd` | The words `tdd` uses for the shape of a piece of software |

You can read them. You will not normally call them by name.

**Every skill the five actually call is in here.** That was worth chasing: a
command that fails half way through, in front of somebody, is worse than one that
was never offered. The chain stops at `codebase-design`, which calls nothing
further.

**One skill is named and deliberately left out**: `setup-matt-pocock-skills`. It
is a setup command, its output is already on disk, and nothing calls it while
work is happening. The last section explains what to do if it ever gets
mentioned.

**About `tdd/` and `codebase-design/`:** their examples are written in
TypeScript, a programming language you are unlikely to use. The ideas underneath
are not about TypeScript — test the behaviour somebody asked for, not the way you
happened to build it. We left the examples alone rather than rewriting them,
because a rewrite we did not test would be worse than an example in the wrong
language.

---

## Where these came from

| | |
|---|---|
| Project | [mattpocock/skills](https://github.com/mattpocock/skills) |
| Author | **Matt Pocock** — <https://www.aihero.dev> |
| Licence | MIT. The full text is in [`LICENSE`](LICENSE) beside this file |
| Copyright | © 2026 Matt Pocock |
| Version | 1.2.3 |
| Exact commit | [`068b6e0`](https://github.com/mattpocock/skills/commit/068b6e0c62393147daf03530149cdce209c93da8) |
| Captured | 2026-09-12 |

The commit is written down so you can check this copy against the original. Open
that link, open the file beside it, and compare. **Take the commit, not the
version number** — a version number can be reissued; a commit cannot.

**Thank you to Matt Pocock.** The supervision loop in this kit is his work. We
chose five of his skills, wrote the survey translation around them, and changed
nothing inside them.

### What we changed

Nothing. Every `SKILL.md` here is byte-for-byte the upstream file.

That includes their spelling. This repository writes US English, and these files
do not. They stay British, because correcting somebody else's document is how a
byte-for-byte claim quietly stops being true.

That is on purpose. A modified copy that still carries somebody else's name is
how a document ends up being blamed on the wrong person. If one of these needs to
say something different for your firm, say it in your `CLAUDE.md` instead — the
agent reads that too, and then the difference is visibly yours.

### What we did not copy

- The other sixteen skills in the upstream set
- **`setup-matt-pocock-skills`** — the command that writes the two configuration
  files below. This kit ships those files already written, so there is nothing
  for it to do. See the last section
- The `agents/openai.yaml` file in each upstream folder. Those tell a different
  AI tool how to find the skill. This kit is for the Claude desktop app

### Why copied and not installed

The usual way to get these is a package manager called npm, through a command
called `npx`. That needs Node.js installed, which needs a terminal, which needs
a Windows administrator in a lot of firms.

Copying the markdown skips all of it. **Nothing in this kit needs Node, npx, npm,
or an API key.** Git, a GitHub account, and the Claude desktop app is the whole
list.

The cost of copying is that these files do not update themselves. When you want a
newer version, go to the upstream project and copy the newer `SKILL.md` over the
top. Note the date you did it, the same way you would note the revision date on a
manual you are working from.

---

## What the skills expect to find, and the one command we left out

Three of the five start by checking that somebody already told them how **your**
firm tracks work. `/to-spec` and `/to-tickets` want two files. `/code-review`
wants one. If a file is missing, they stop and tell you to run
`/setup-matt-pocock-skills`.

**That command is not in this kit.** Its whole job is to interview you and write
those files, and this kit ships them already written, at `docs/agents/`:

- `issue-tracker.md` — where your work orders live, and the exact commands for
  reading and writing them
- `triage-labels.md` — the five states a work order can be in

So there is nothing for it to do. Read both, and edit them to match your firm —
they are the two files most worth your time.

**If you ever do see that message**, it means the agent did not read those files,
not that they are absent. Point it at `docs/agents/` and carry on. Do not go
looking for the setup command; the answer it would write is already on disk.

`docs/agents/domain.md` is a third file in the same folder, and it is what stops
that happening: it tells the agent to read all three before it starts work. Keep
it.
