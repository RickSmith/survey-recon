# Setting up a second machine

**A backup laptop nobody has run the demo on is not a backup.** This page takes
a bare Windows machine to one that can run the whole two hours, in about twenty
minutes, most of which is downloads.

Run it on the backup machine as well as the presenting one. The point of a
second machine is that it has already been proved.

This is not [Day 0](../day-0/index.md). That page sets up an **attendee**, who
copies the toolkit into their own job folder and never runs the corridor tool.
This page sets up a **presenter**, who runs all of it.

---

## Two rules before you start

**1. Do not put the repo in OneDrive.** Put it in `C:\dev`.

The original checkout lives in OneDrive and it causes two real problems.
OneDrive holds folders open, so git prints a wall of `failed to delete ...
Permission denied` after almost every command — harmless, but it looks exactly
like a failed push. And the path runs to about 140 characters before it reaches
a single file, which is long enough that some Windows tools report a file as
missing when it is plainly there. This repo already carries code written
because of a long path.

`C:\dev\survey-recon` has neither problem.

**2. Use Git Bash, not PowerShell.** Every command in
[the dry run](dry-run.md) is written for bash. `mkdir -p` and `cp -r` do not
exist in PowerShell, and the rehearsal setup opens with one of each. Git Bash
installs alongside git in Step 2.

---

## Step 1 — Open a terminal

Press the Windows key, type `terminal`, and open **Windows Terminal**. You need
it only for the installs. After that you switch to Git Bash.

## Step 2 — Install git, Python and the GitHub CLI

**The sure way — three installers.** Click through each and take the defaults.

| What | Where |
|---|---|
| Git for Windows | <https://git-scm.com/download/win> |
| Python 3.12 | <https://www.python.org/downloads/windows/> |
| GitHub CLI | <https://cli.github.com> |

**On the Python installer, check "Add python.exe to PATH" on the first
screen.** It is off by default and easy to miss. If you miss it, run the
installer again and choose Modify.

**The fast way, if you would rather type.** One at a time:

```
winget install --id Git.Git -e
```

```
winget install --id Python.Python.3.12 -e
```

```
winget install --id GitHub.cli -e
```

!!! warning "These three IDs are not verified on a clean machine"
    They are the standard published identifiers, but nobody has yet run this
    page start to finish on a machine that had none of them. If one answers
    "No package found," use the download link in the table above rather than
    going hunting. Correct this note the first time somebody proves it.

**Then close the terminal and open a new one.** Installers change your PATH and
an open terminal does not notice. This is the most common reason the next step
says "not found."

### Python 3.11 is the floor

The tool needs **Python 3.11 or newer, and nothing else** — no `pip install`,
no libraries. 3.11 is the floor because it is the first version that reads TOML
configuration files on its own. See `corridor-screen/README.md`. Python 3.12
above is simply a safe current choice.

## Step 3 — Install the Claude desktop app

Download it from <https://claude.ai/download> and sign in.

## Step 4 — Get the repo

In **Git Bash** (Start menu, "Git Bash"), not PowerShell:

```bash
mkdir -p /c/dev && cd /c/dev && git clone https://github.com/RickSmith/survey-recon.git
```

Git opens a browser window to sign you in to GitHub the first time.

**The clone brings the cache with it.** Every cached response is committed, so
there is nothing to copy across from the other machine. That is the whole point
of the demo rig — see [the plan of record](../plan-of-record.md), decision 20.

## Step 5 — Check Python works

```bash
cd /c/dev/survey-recon/corridor-screen && python --version
```

You want `3.11` or above.

**If the Microsoft Store opens instead**, Windows has a placeholder `python` in
the way. Turn it off: Start → "Manage app execution aliases" → switch off both
**python.exe** and **python3.exe**. Then open a new Git Bash and try again.

## Step 6 — Seed the rehearsal scratch folder

Do this before you test anything, and you never have to write into the real
project folder at all.

```bash
cd /c/dev/survey-recon && mkdir -p ../dry-run-scratch && cp -r project-sh16/cache ../dry-run-scratch/cache
```

**Why:** a rehearsal sends its output somewhere else so that it cannot break
the thing it is rehearsing. But the cache lives *inside* the output folder, so
a fresh scratch folder has no cache and the no-network fallback cannot run.
Copying it across once fixes that. The reasoning is in
[the dry run](dry-run.md#seed-the-scratch-folder-first-or-you-rehearse-without-a-fallback).

## Step 7 — Prove the tool runs

```bash
cd /c/dev/survey-recon/corridor-screen && python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../../dry-run-scratch --mode cache-only
```

About a second and a half. Every service line reads `skipped  0 ms`, and it
must end on:

```
  parcels     524
  warnings    0
```

**If it does, the machine works.** If it does not, stop here. This is much
cheaper to find now than at 0:00.

**Then check you left the repo alone:**

```bash
cd /c/dev/survey-recon && git status
```

Expect nothing, because `--out` pointed outside the repo. This is the same
check the rehearsal ends with, so you may as well learn what a clean answer
looks like while nothing is at stake.

## Step 8 — Put the deck on the laptop

```bash
curl -L -o /c/dev/beyond-the-prompt.pdf https://ricksmith.github.io/survey-recon/slides/beyond-the-prompt.pdf
```

Then **turn the Wi-Fi off and open the file.** A download that arrived as a
zero-byte file looks exactly like one that worked, right up to the moment you
need it.

Two blocks are slides only — *What is an agent* at 0:08 and *Vocabulary of
managing one* at 0:20. That is twenty-two minutes with nothing else behind
them if the network goes. The deck re-renders on every push and the copy on
your laptop does not, so pull it again close to the day.

## Step 9 — Sign in to the GitHub CLI

```bash
gh auth login
```

Choose **GitHub.com**, then **HTTPS**, then **Login with a web browser**.

The close at 1:54 opens an issue live in front of the room, and every finding
from the rehearsal becomes a work order afterward.

## Step 10 — Install the plugin that Act I runs on

**This is the step that is invisible until it is too late.**

Act I runs three commands on the projector — `/grill-with-docs`, then
`/to-spec`, then `/to-tickets`. **None of the three comes from this repo.** All
three come from a plugin installed on the machine, and a fresh clone does not
have it.

Open the Claude desktop app, point it at `C:\dev\survey-recon`, then:

1. Type `/plugin`
2. Install **`mattpocock-skills`** from the **`claude-plugins-official`**
   marketplace
3. Take version **1.2.3** if you are offered a choice, so both machines behave
   the same way

**Then prove it.** Type `/` and confirm all three are in the list:
`grill-with-docs`, `to-spec`, `to-tickets`.

If one is missing, the plugin did not install. Fix it now. Act I is sixteen
minutes, it is the hinge of the session, and it is on the never-cut list.

### Why `toolkit/.claude/skills/` is not the shortcut

The repo does carry these same skills as markdown, vendored under
`toolkit/.claude/skills/`. That copy is for **attendees**, who copy the
toolkit's *contents* into their own job folder so the skills sit at that
folder's root — [Day 0](../day-0/index.md), step 5.

Do not copy it to this repo's root to skip Step 10. Those files are not ignored
by git, so they would sit in `git status` as untracked changes and quietly
spoil the check in Step 7 and at the end of the rehearsal.

---

## You are ready

Open [the dry run](dry-run.md) and follow it. Three things to carry in:

- **Use `--out ../../dry-run-scratch`** on every command that takes it, and run
  the blocks in order — two of them read the cold open's output.
- **Print [the fallback card](fallbacks.md)** and the dry-run page.
- **The live NGS call at 0:57 can fail, and has.** On 14 September it answered
  nothing, then refused the call an hour later. The next day it was back, with
  the same thirteen marks. That is NGS, not your machine. Rehearse saying so
  and moving on.

## When something does not work

| What you see | What it is |
|---|---|
| `python: command not found` | You did not open a new terminal after installing. Close it and open a new Git Bash. |
| The Microsoft Store opens | The Windows placeholder `python`. Step 5 turns it off. |
| `mkdir: illegal option -- p` | You are in PowerShell. Open Git Bash. |
| `no cached response for this request` | You skipped Step 6, the cache seed. |
| `FileNotFoundError` from `crew_day` or `live_check` | You ran the blocks out of order. Send the cold open's screening run to the same folder first. |
| `/grill-with-docs` is not in the `/` list | You skipped Step 10. This one takes out Act I. |
| `HTTP Error 403` from NGS | It has happened before, and it is NGS, not your machine. Say so and move on. |
| A wall of `failed to delete ... Permission denied` | You are in the OneDrive checkout, not `C:\dev`. The git command still worked — read the last line. |

---

## Where this came from

This page was written under
[work order #131](https://github.com/RickSmith/survey-recon/issues/131), after
a second machine turned out to have none of the three Act I commands. The two
days the live NGS call failed, and what it did when it came back, are on
[#128](https://github.com/RickSmith/survey-recon/issues/128).
