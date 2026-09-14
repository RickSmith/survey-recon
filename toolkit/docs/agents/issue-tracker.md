# Where the work orders live

A **work order** is one job, written down, before anybody starts it. Software
people call it an *issue*. Same thing.

At «FIRM NAME» work orders live as **GitHub issues** on «OWNER/REPO».

This file tells the agent how to read and write them. Edit it if you track work
somewhere else — the last section covers the version that needs no extra tools.

---

## The command line tool

The agent works through `gh`, GitHub's own command line tool. Run inside a job
folder, `gh` works out which project it is in by itself. You never tell it.

**`gh` is a fourth thing to install.** Git, a GitHub account and the Claude
desktop app get you everything else in this kit; work orders on GitHub need this
as well. It is one program from <https://cli.github.com>, and it needs no Node,
no npm and no API key — but it is still a fourth install, and somebody in your
firm may have to approve it.

Install it, then sign in:

```bash
gh auth login
```

**If that is a problem, skip it.** The last section of this file puts work orders
in plain files instead, and needs nothing at all.

## The everyday commands

| To do this | Run |
| --- | --- |
| Open a work order | `gh issue create --title "..." --body "..."` |
| Read one, with its comments | `gh issue view <number> --comments` |
| Comment on one | `gh issue comment <number> --body "..."` |
| Add or remove a label | `gh issue edit <number> --add-label "..."` / `--remove-label "..."` |
| Hand it to somebody | `gh issue edit <number> --add-assignee <user>` |
| Close one | `gh issue close <number> --comment "..."` |

For a body longer than a line or two, write it to a file first and pass
`--body-file`. Quoting a long message straight onto the command line will bite
you eventually.

To list them:

```bash
gh issue list --state open --json number,title,labels
```

Narrow it with `--label` and `--state`.

## Two phrases the skills use

The five commands are written to work on any project, so they say general things.
Here is what those mean here.

- **"Publish to the issue tracker"** — create a GitHub issue
- **"Fetch the relevant ticket"** — run `gh issue view <number> --comments`

## Recording what blocks what

`/to-tickets` produces work orders that depend on each other. Some jobs cannot
start until others finish, the same way you cannot set final monuments before the
control is in.

Record it as a line at the top of the blocked work order's body:

```
Blocked by: #12, #14
```

A job is ready when every work order it names is closed.

GitHub also has a built-in way to link them, which shows up on the web page
without anybody reading the body text. Use it if your project has it switched on;
the plain line above works everywhere and is easier to check.

## One trap worth knowing

GitHub numbers work orders and check prints out of the same pot, so a bare `#42`
might be either one. Resolve it with `gh pr view 42`, and fall back to
`gh issue view 42` when that comes back empty.

---

## If you do not have `gh`

Everything above assumes GitHub. It does not have to.

Work orders can live as plain markdown files in the job folder. Nothing extra is
needed — no account, no tool, no network. `/to-tickets` already knows how to
write them this way, so use its layout rather than inventing one:

- One folder per piece of work, at `.scratch/<short-name>/`
- The scope of work goes in `.scratch/<short-name>/spec.md`
- One job per file, at `.scratch/<short-name>/issues/<NN>-<slug>.md`, numbered
  from `01` in the order they must happen
- A `Status:` line near the top, holding one of the five states from
  [`triage-labels.md`](triage-labels.md)
- A `Blocked by: 03, 05` line near the top, where it applies
- Conversation appends to the bottom, under a `## Comments` heading

Then **"publish to the issue tracker" means write a new file under
`.scratch/`**, and **"fetch the relevant ticket" means read the file**.

**`.scratch` starts with a dot.** Finder hides it. File Explorer shows it, but a
name like that is easy to skim past. It is also the kind of name that tools
ignore by habit — check your `.gitignore` and make sure it is not in there, or
your work orders will never be saved. If you would rather they lived somewhere
obvious, rename the folder here and the agent will follow.

This is a real option, not a consolation prize. The whole point of a work order
is that the job is written down before it starts. A folder of files does that.

What you give up is everybody being able to see the list without opening the job
folder, which matters as soon as more than one person is involved.
