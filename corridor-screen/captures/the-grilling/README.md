# Captured evidence — the grilling that wrote the spec

This is the fallback for **Act I**, the block at `0:30–0:46`. If the agent will
not start, or the network is gone, this is what goes on the projector.

**Open this page first.** The table below is the whole of Act I on one screen.
The full run is in [`the-grilling.md`](the-grilling.md) beside it, and the work
orders it led to are in [`the-tickets.md`](the-tickets.md).

It is a transcript, not a recording. There is no video of that session and
there never was. What is here is what was typed, by both sides, in order.

---

## Nineteen questions, in three rounds

Read down the last two columns. That is the shape of the block: **the agent
proposes, the licensed human decides**, and most of the time the human hands it
back.

| | The question | What the agent recommended | What Rick answered |
|---|---|---|---|
| **Q1** | What do I hand the tool? | A route name plus two DFO numbers, with a GeoJSON line as an override | **Widened it.** GeoJSON, shapefile, KML, KMZ, *and* route plus two DFO numbers |
| **Q2** | How wide is the corridor? | One fixed number, default 300 ft, printed in the header | Your recommendation |
| **Q3** | Who does the buffer math — my code or their server? | Their server, but fetch the polygon once and cache it. No new dependency | Your recommendation |
| **Q4** | What comes out, and in what shape? | One JSON file, and the parcel is the row | Your recommendation |
| **Q5** | What order do I call the services in? | Spine first, risk last — plus a reachability ping before any real work | Your recommendation |
| **Q6** | What happens when a service is dead? | The tool never dies; a dead service becomes a recorded fact | **Overrode it.** Hard stop, with an option to retry |
| **Q7** | What happens when a service answers, but wrongly? | A cheap sanity check on every response. *Do you want any of them fatal?* | Warning |
| **Q8** | How does caching work? | Every response to disk with a sidecar; three run modes | Your recommendation |
| **Q9** | Which flags, and where does the lead-time table live? | Keep the glossary's definition and mark what public data cannot see; lead times as checked-in data | Your recommendation |
| **Q10** | Shapefile is the only format that costs something. Pay for it, or write it? | Write it myself — the tool then needs nothing installed | Write it yourself |
| **Q11** | What are the rules when the file is not what I hoped? | Four rules, and print the corridor length and both end points before any service is called | **Added to it.** All of that plus a rendering of the corridor |
| **Q12** | "Hard stop with retry" — what exactly? | Retry three times, then ask if somebody is there, and still write the file marked `incomplete` | Your recommendation |
| **Q13** | How does a school become a flag on a parcel? | Two words, never merged: `on` and `adjacent`. Anything belonging to no parcel goes corridor-level | Your recommendation |
| **Q14** | What makes a parcel a parcel? | `AcctNumb`, a synthetic key when it is missing, never drop a parcel | **Added to it.** Your recommendation, but be ready to adapt to another parcel layer and a different key |
| **Q15** | Where does the spec file live? | `docs/corridor-screen/spec.md`, in the site nav | Your recommendation |
| **Q16** | Do you want an ADR for the Q6 / Q7 split? | Yes — a dead service stops the run, a wrong-looking answer only warns, and a reader will ask why | Your recommendation |
| **Q17** | The corridor rendering: what format, how many? | SVG, two of them — one before any service is called, one at the end | Your recommendation |
| **Q18** | Swappable parcel sources: where does that description live? | TOML config files, one per area, so the tool does not know it is in Bexar County | **Cut it.** Never mind for this, stick to Bexar County |
| **Q19** | Cache layout — what goes where? | The response untouched, a `.meta.toml` sidecar beside it, a generated `INDEX.md` | Your recommendation |

Then a schema draft, redlined in one word: **yes**. The grilling ended there and
the spec was written.

## The three numbers worth saying out loud

**Thirteen of the nineteen answers contain the words "your recommendation."**
That is what delegation looks like when it is working.

**Five answers changed the shape of the tool** — Q1, Q6, Q11, Q14 and Q18. Every
one of them is a judgment a licensed surveyor has and an agent does not: which
file formats a firm actually owns, what a tool should do when a source is down,
that you look at the drawing before you trust the numbers, that parcel data
differs county to county, and that scope has to be cut somewhere.

**Q18 is the one to dwell on.** The agent had just designed a general,
config-driven tool that would work in any county. Rick cut it to Bexar in eight
words. The agent's own reply is in the transcript: *"That kills the whole
config-file idea from Q18, which is a real simplification."* Nobody argued.

## What is here

| File | What it is | Where it came from |
|---|---|---|
| `the-grilling.md` | The three rounds of questions, Rick's three sets of answers, and what the agent did with each | The Claude Code session that ran `/grill-with-docs` on [issue #5](https://github.com/RickSmith/survey-recon/issues/5), 12 September 2026 |
| `the-tickets.md` | The 35 work orders that followed, and the 89 seconds they took | `gh issue list --state all` on 2026-09-13 |
| `the-tickets.json` | Exactly what that command returned, unedited | the same command |

## What was left out, and why

**The session ran long past the grilling.** After the spec was written it
installed MkDocs, pushed a branch, opened [PR #44](https://github.com/RickSmith/survey-recon/pull/44),
waited on CI, merged, deleted branches and archived itself. None of that is Act
I. The capture stops where the grilling stops — at the schema draft and the
word "yes."

**The tool calls are not here either.** The session read files, ran commands and
wrote to disk between questions. Those turns are how the agent got its facts,
and the facts it got are already in the spec. What Act I shows a room is the
questions and the answers.

**One thing was actually removed rather than not selected.** The app stamps a
worktree notice onto some turns, carrying the path of the machine it ran on. It
sat on top of Rick's Round 2 answers. Nobody wrote it, and this repo is public.
Beyond that, the search for a path or an address in these blocks came back
empty.

## Two notes on the text itself

**The spelling is the original.** There is `centre line`, `behaviour`,
`generalisation` and `maths` in there. This repo writes US English — see
`CLAUDE.md` — but a capture is evidence, and evidence does not get tidied. The
same exemption already covers the vendored skills.

**The tool it describes is not quite the tool that exists.** Q18's config files
were cut, so there is no `--area` flag. The command grew different names. Read
the transcript as the decision record it is, and
[the spec](../../../docs/corridor-screen/spec.md) as what was actually built.

## The half of Act I this does not cover

On stage, Act I runs `/grill-with-docs`, then `/to-spec`, then `/to-tickets`.
**This session did the first two.** It never ran `/to-tickets` — the work orders
came out of a different session, earlier the same evening.

So `the-tickets.md` is the *result* of that step rather than a recording of it:
35 work orders, numbered 5 to 39, stamped between 20:32:08 and 20:33:37. If the
live run dies at that point, the honest line is *"here is what it wrote, and
here is how long it took."*
