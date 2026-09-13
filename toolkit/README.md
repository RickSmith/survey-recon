# The take-home toolkit

**Copy this folder into your own project and you have a supervised agent.**

Nothing in here is specific to this repo, to TxDOT, or to the SH16 example. It is
the part you take home.

---

## What is in it

| File or folder | What it is |
|---|---|
| `CLAUDE.md` | The employee handbook. Your firm's rules, which the agent reads first every session |
| `CONTEXT.md` | The glossary. The words your firm uses, so the agent stops guessing |
| `docs/agents/` | Three short files telling the agent where work orders live and what the labels mean |
| `.claude/skills/` | The five commands. Plain markdown, copied from Matt Pocock's set under MIT license |

`.claude/skills/README.md` explains which five and why. Read it second.

## What you need

Three things:

1. **git** — <https://git-scm.com/downloads>
2. **a GitHub account** — <https://github.com/signup>
3. **the Claude desktop app** — <https://claude.ai/download>

**Nothing here needs Node, npm, npx, Docker, Python, or an API key.**

**One asterisk.** To keep work orders as GitHub issues, add
[GitHub CLI](https://cli.github.com) — a fourth thing to install. One program, no
Node, no API key, no account beyond the one you already made. If that is a
problem, skip it: `docs/agents/issue-tracker.md` also describes keeping work
orders as plain files in the job folder, which needs nothing at all.

New to all three? Start at
[Day 0: Setup](https://ricksmith.github.io/survey-recon/day-0/), which does it
from zero with screenshots.

## Putting it in

Copy everything **inside** this folder to the top of your own job folder. Not the
folder itself — its contents.

On Windows, in PowerShell, from inside your job folder:

```powershell
Copy-Item -Path "<path-to>\survey-recon\toolkit\*" -Destination . -Recurse -Force
```

On macOS or Linux, in Terminal, from inside your job folder:

```bash
cp -R <path-to>/survey-recon/toolkit/. .
```

**Watch for the hidden folder.** `.claude` starts with a dot, so Windows File
Explorer and macOS Finder both hide it by default. If you drag files across by
hand instead of running the command above, you will very likely leave it behind
and wonder why the commands do not exist. Turn on hidden files first, or use the
command.

When you are done, the top of your job folder looks like this:

```
your-job-folder/
├── .claude/
│   └── skills/
├── docs/
│   └── agents/
├── CLAUDE.md
└── CONTEXT.md
```

## Filling it in

Two files have blanks in them. Anything in «guillemets» is one.

1. **`CLAUDE.md`** — firm name, who signs, and the list of what never leaves the
   office. **That last list is the one with real consequences.** Spend the time
2. **`CONTEXT.md`** — six words you are tired of explaining. Six is plenty for a
   first version

Then `docs/agents/issue-tracker.md`, which needs your project name if you are
using GitHub.

You can skip everything else on the first pass.

## Checking that it worked

Open the Claude desktop app, point it at your job folder, and type:

```
/grill-with-docs
```

If it starts interviewing you about the job, everything is wired up. If it says
it does not know that command, the `.claude` folder did not come across — see the
hidden-folder warning above.

## The order the five commands run in

```
/grill-with-docs   →  it interviews you about the job
/to-spec           →  the conversation becomes a written scope of work
/to-tickets        →  the scope becomes separate work orders
/implement         →  one work order gets done, on a working copy
/code-review       →  the change gets checked before you accept it
```

You stop wherever you like. Plenty of useful days end after `/to-spec`.

**You accept the work. Not the agent.** That is the whole shape of it.

## License

The five commands and the four supporting skills in `.claude/skills/` are
copyright © 2026 **Matt Pocock**, used under the MIT license. The license text
sits beside them at `.claude/skills/LICENSE`, and `.claude/skills/README.md`
records exactly which version and commit were copied, and when.

Everything else in this folder is part of `survey-recon` and carries that
repository's license.
