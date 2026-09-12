# survey-recon

**Reconnaissance for survey work, with an AI agent doing the legwork.**

Before you price a job you do a recon — what control already exists, how many tracts you're crossing, who you need permission from, how long the field crew really needs. This repo shows how to hand that work to an AI agent, and more importantly, how to supervise one well enough to trust the answer.

Built for the TSPS 2026 convention session *"Beyond the Prompt."*

📖 **Read it as a website: <https://ricksmith.github.io/survey-recon/>**

---

## Start here

**You do not need to be a programmer.** You do need three things: a GitHub account, git installed, and the Claude desktop app. The setup chapter walks through all three with screenshots.

→ **[Day 0: Setup](https://ricksmith.github.io/survey-recon/day-0/)** — start from zero
→ **[For principals](https://ricksmith.github.io/survey-recon/for-principals/)** — one page, no terminal, what to tell your team
→ **[The worked example](https://ricksmith.github.io/survey-recon/scenarios/sh16/)** — a real TxDOT ROW job, start to finish
→ **[Slides](https://ricksmith.github.io/survey-recon/slides/)** — the deck from the session, in a browser or as a PDF

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

---

## Previewing locally

**Nobody needs this to read the site.** The link at the top is always current — every push to `main` rebuilds and republishes it automatically. This section is for whoever is editing the pages.

### The website

Needs Python 3.9 or newer. From the repo folder:

```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements-docs.txt
```

On Windows, activate it with `.venv\Scripts\activate` instead.

Then:

```bash
mkdocs serve
```

That prints a local address — usually <http://127.0.0.1:8000/survey-recon/> — and rebuilds every time you save a file. Use the address it prints, `/survey-recon/` and all; that path is part of where the site lives. `Ctrl+C` stops it.

To check the site the way the robot checks it, which fails on a broken link rather than warning about it:

```bash
mkdocs build --strict
```

### The slide deck

Needs [Docker](https://docs.docker.com/get-started/get-docker/). Nothing else — the renderer and the browser it uses both live inside the container.

```bash
docker run --rm --init -v "$PWD:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" marpteam/marp-cli:v4.5.1 docs/slides/beyond-the-prompt.md --theme-set docs/slides/themes --html --output _slides/deck.html
```

Open `_slides/deck.html` in a browser. Swap `deck.html` for `beyond-the-prompt.pdf` and add `--pdf` to get the PDF instead.

If you would rather watch the slides update as you type, the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension previews the same file live. Point it at `docs/slides/themes/tsps.css` so the type sizes match.

### What gets published, and by what

| File | What it does |
|---|---|
| `mkdocs.yml` | The whole configuration for the website. Readable top to bottom |
| `.github/workflows/docs.yml` | Builds the site on every push and pull request; publishes it from `main` |
| `.github/workflows/slides.yml` | Renders the deck to HTML and PDF, and hands them to `docs.yml` |
| `requirements-docs.txt` | The one thing the site builder needs installed |

**Attendees never need any of this.** Node, npm, Docker and Python are maintainer tools. The attendee path is a GitHub account, git, and the Claude desktop app.

## Credits

The development-lifecycle skills are a curated subset of [mattpocock/skills](https://github.com/mattpocock/skills), MIT licensed, copyright © 2026 Matt Pocock. Vendored here so you don't need Node installed. See `toolkit/.claude/skills/`.
