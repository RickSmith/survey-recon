# Captured evidence — the grilling that wrote the spec

This is the fallback for **Act I**, the block at `0:30–0:46`. If the agent will
not start, or the network is gone, this is what goes on the projector.

**Open this page first.** The table below is the whole of Act I on one screen.
The full run is in [`the-grilling.md`](the-grilling.md) beside it, and the work
orders of this project — including the one this grilling ran on — are in
[`the-tickets.md`](the-tickets.md).

It is a transcript, not a recording. There is no video of that session and
there never was. What is here is what was typed, by both sides, in order.

## One thing in it is wrong, and it stays wrong

Question 1 of the transcript opens *"Three ways to say 'SH16, Loop 410 to
Gibeaut Rd'"*. **There is no Gibeaut Rd in Bexar County.** The corridor's north
end is where Bandera Rd meets **Old Bandera Rd**, in Old Town Helotes.

The name was invented here, on 12 September, and then copied into thirteen
files without anybody checking it against a map. Rick caught it on 13 September
reading it off a slide. The corridor itself never moved — DFO 347.7 to 356.367,
8.691 miles, so not one figure in this repo changed.
[Issue #99](https://github.com/RickSmith/survey-recon/issues/99) has the
account; `CONTEXT.md` has the corrected name and the two sources it was checked
against.

**The transcript is not edited.** It is a record of what was typed, and a record
that gets quietly corrected is not a record. It is also, on its own, a small
version of the thing this session is about: the agent wrote a plausible name
down, repeated it thirteen times, and never doubted it. One human read it once.

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
| **Q7** | What happens when a service answers, but wrongly? | A cheap sanity check on every response. *"Do you want any check to be fatal rather than a warning?"* | Warning |
| **Q8** | How does caching work? | Every response to disk with a sidecar; three run modes | Your recommendation |
| **Q9** | Which flags, and where does the lead-time table live? | Keep the glossary's definition and mark what public data cannot see; lead times as checked-in data | Your recommendation |
| **Q10** | Shapefile is the only format that costs something. Pay for it, or write it? | Write it myself — the tool then needs nothing installed | Write it yourself |
| **Q11** | What are the rules when the file is not what I hoped? | Four rules, and print the corridor length and both end points before any service is called | **Added to it.** All of that plus a rendering of the corridor |
| **Q12** | "Hard stop with option to retry" — what exactly? | Retry three times, then ask if somebody is there, and still write the file marked `incomplete` | Your recommendation |
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

**Five answers changed the shape of the tool** — Q1, Q6, Q11, Q14 and Q18. Q14
is in both counts, because it says "your recommendation" and then adds a
condition to it, so the two numbers overlap by one rather than adding to
eighteen. Every
one of them is a judgment a licensed surveyor has and an agent does not: which
file formats a firm actually owns, what a tool should do when a source is down,
that you look at the drawing before you trust the numbers, that parcel data
differs county to county, and that scope has to be cut somewhere.

**Q18 is the one to dwell on.** The agent had just designed a general,
config-driven tool that would work in any county. Rick cut it to Bexar in nine
words. The agent's own reply is in the transcript: *"That kills the whole
config-file idea from Q18, which is a real simplification."* Nobody argued.

## What is here

| File | What it is | Where it came from |
|---|---|---|
| `the-grilling.md` | The three rounds of questions, Rick's three sets of answers, and what the agent did with each | The Claude Code session that ran `/grill-with-docs` on [issue #5](https://github.com/RickSmith/survey-recon/issues/5), 12 September 2026 |
| `the-tickets.md` | The 35 work orders of this project, and the 89 seconds they took | `gh issue list --state all --limit 100 --json number,title,createdAt,state,labels`, run on 2026-09-13 |
| `the-tickets.json` | Exactly what that command returned, unedited | the same command, same run |

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

On stage, Act I runs `/grill-with-docs`, then `/to-spec`, then `/to-tickets`, in
that order. **This session did the first two.** It never ran `/to-tickets`.

And the real order was the other way round. The 35 work orders were written in a
different session **earlier the same evening** — 20:32 to 20:33 — and one of
them was *"Specify the corridor-screening tool," issue #5*. The grilling then
ran on that work order, hours later. So the tickets did not come out of this
grilling; **this grilling came out of one of the tickets.**

That is worth saying on stage rather than hiding, because it is how the loop
actually runs once a project is going: the work orders come first, and the
grilling is what you do to the one that is not specified well enough to hand to
anybody.

So `the-tickets.md` is the *result* of a `/to-tickets` run rather than a
recording of one. If the live demo dies at that point, the honest line is
*"here is what it wrote, and here is how long it took."*
