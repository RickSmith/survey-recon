# Plan of Record — TSPS 2026 "Beyond the Prompt"

**This is the spec.** Section 1 is settled; do not re-open it. Section 8 lists what is genuinely still open.

**Session:** Beyond the Prompt: Getting Started with Agentic AI for Geomatics Tools and Workflows
**Presenters:** Rick Smith + Seneca Holland (audience proxy)
**Date:** Thursday, October 8, 2026 · 2 hours · watch-only
**Audience:** mostly firm owners and principals
**Repo:** `survey-recon`
**Rev 5:** 2026-09-12

Companion: `txdot-research.md` — verified endpoints, TxDOT rules, ROE lead times.

---

## 1. Decisions locked

| # | Decision | Choice |
|---|---|---|
| 1 | Length / format | 2 hours, watch-only; hands-on afterward via the repo |
| 2 | Agent tooling | Claude Code as the spine + Hermes (Nous Research) for autonomous work |
| 3 | Repo | `survey-recon` — Rick's personal GitHub, public |
| 4 | Content format | Markdown-first repo + MkDocs Material site via GitHub Actions |
| 5 | Presenting surface | Markdown slides in the repo (Marp) → site + PDF. No PowerPoint. |
| 6 | Session spine | TxDOT SH16, Loop 410 → Old Bandera Rd (Bexar County), start to finish |
| 7 | SDLC depth | Full loop, translated to survey language |
| 8 | On-ramp | Desktop app first — git, a GitHub account and issues are required |
| 9 | Cost framing | Billable-hour math, not subscription pricing |
| 10 | Lifecycle skills | mattpocock/skills — curated 5-command subset, vendored (MIT) |
| 11 | Control data | Public sources only |
| 12 | Reclaimed Sep 15–17 | Build the corridor-screening tool properly |
| 13 | Datum gap | Name it plainly as an open question — no blame |
| 14 | Failure beat | Yes — deliberate, scripted, reproducible |
| 15 | Act III output | All three: bid memo + flagged parcel table + crew-day build-up |
| 16 | ROE letters | Hermes beat — the second letter that sends itself |
| 17 | QC / compliance | Out of scope. Starter in repo only |
| 18 | Generalization | Patterns named explicitly on stage + live "next example" issue |
| 19 | Who builds it | Rick directs, the agent builds — git history becomes a teaching artifact |
| 20 | Demo rig | Cache everything, replay live |

**Where a decision above got narrowed.** The table stands as written; this is the pointer, not an edit to it. **Decision 2** named Hermes (Nous Research) for autonomous work, and **decision 16** filed the ROE letters as the Hermes beat. What was built under [#34](https://github.com/RickSmith/survey-recon/issues/34) is a scheduled GitHub Actions workflow, which is autonomous and is not Hermes. The account is [ADR 0002](adr/0002-the-hermes-segment-runs-on-a-schedule.md): the cron job stays, the name stays, and the presenter says so out loud. Overriding a decision is allowed here. Overriding one quietly is not.

**On the name:** "recon" is the audience's own word for the desktop work before a bid — it describes the work rather than the arithmetic, survives the generalization problem (you recon a ranch boundary the same as a corridor), and carries no "AI" branding to date it.

---

## 2. The recursion

If the agent builds this repo under Rick's direction using the mattpocock lifecycle, then by October 8 `survey-recon` contains a **real history of real work**: issues written, specs drafted, PRs redlined, reviews signed off, commits that fixed what was caught.

**The "managing your agent" segment stops being a demo and becomes evidence.**

> *"Everything you're looking at was built the way I'm telling you to work. Here are the issues. Here are the pull requests. Here's where I sent it back. Here's one I approved that I shouldn't have."*

That last clause is the failure beat, already paid for.

**What this requires:**
- Every piece of work goes through an issue first, even when it's faster not to
- Every agent change lands as a PR that is actually reviewed, with comments visible
- Don't squash the history clean — the messy parts are the curriculum. Broken once on day one, knowingly; the account is [The rule we broke on day one](managing-your-agent/the-force-push.md)
- Tag two or three PRs `teaching-moment` as you go

Directing is also cheaper than building, which is how this survives a day job.

---

## 3. Audience — firm owners and principals

Principals are **buyers and risk-owners, not operators.** They will not install anything that week. They need something to hand their staff and something to tell their insurer.

1. **Money slide moves up** to ~0:46, right after they've seen the agent scope a job. Owners need the frame before investing attention in 45 more minutes of demo.
2. **Rework is the argument, not speed.** TxDOT's manual: *"There is no acceptable failure rate for any TxDOT survey"* — and non-compliant surveys **cannot be invoiced.** For an owner, that's a sentence about money.
3. **Governance is a primary take-home** — firm AI-use policy, what client data never leaves the office, seal and responsible-charge language.
4. **`docs/for-principals/`** — one page, no terminal: what to tell your team Monday, what it costs, what your policy should say, what you're still liable for, which one person to point at the repo.

**Datum gap framing for this room:** a scope-and-liability question, not a geodesy question — *"what datum do you certify to, and what does your survey report say when the manual doesn't tell you?"*

---

## 4. Demo rig — cache everything, replay live

Pre-fetch every API response into the repo as committed JSON; the agent reads local files during the session but **the code is the real code.**

Justified: the TxDOT ROW map server blocks intermittently, USGS elevation timed out 3 of 4 attempts, venue Wi-Fi unknown. Caching also makes the tool testable offline and hands attendees the actual data.

**Three rules:**
- **Say so on stage.** *"These were captured September 20th so we're not at the mercy of the hotel Wi-Fi — the code is live code and you can run it yourself."* Undisclosed caching, if noticed, costs you the room.
- **Stamp every cached file** with capture date and exact request URL.
- **Keep one genuinely live call** — NGS `/radial` was the most reliable endpoint tested. One live moment proves it isn't a movie.

---

## 5. Run of show (2:00)

| Time | Min | Block |
|---|---|---|
| 0:00–0:08 | 8 | **Cold open.** Hand the agent the SH16 job; let it run while you introduce yourselves. |
| 0:08–0:20 | 12 | **What is an agent.** Prediction → chatbot/copilot/agent → the loop → where it breaks. |
| 0:20–0:30 | 10 | **Vocabulary of managing one.** Markdown · repo & git · issues · context. One token slide. |
| 0:30–0:46 | 16 | **Act I — The grilling.** `/grill-with-docs` live → `/to-spec` → `/to-tickets` → real issues on the projector. *The hinge.* |
| 0:46–0:52 | 6 | **The money slide.** Billable-hour math. Rework, not speed. "Cannot be invoiced." |
| 0:52–0:57 | 5 | Stretch + questions |
| 0:57–1:18 | 21 | **Act II — Find the control.** 11 NGS marks, every one `MARK NOT FOUND`; 4 TxDOT control records naming 2 distinct monuments; 69 ROW sheets reach the corridor, 15 of them SH16's own. |
| 1:18–1:36 | 18 | **Act III — The estimate package.** Bid memo + flagged parcel table with statutory lead times + crew-day build-up. |
| 1:36–1:48 | 12 | **Review, seal — and the three failures.** |
| 1:48–1:54 | 6 | **Hermes.** The second ROE letter that sends itself on day 21. |
| 1:54–2:00 | 6 | **Accountability · Monday morning · the live issue.** |

**Where Act II's figures come from.** They are read out of
[`project-sh16/screening.json`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/screening.json)
— the SH16 run of 2026-09-13 — and `corridor-screen/tests/test_plan_of_record.py`
fails if this page and that run ever disagree. Two of them are easy to say wrongly
to a room:

- **A record count is not a monument count.** TxDOT keeps two records for many of
  its stations. The 4 records in this corridor name **2 distinct monuments**, and a
  crew drives to the monument rather than to the record. See **Distinct stations**
  in `CONTEXT.md`.
- **A corridor figure and a county figure answer different questions.** 69 sheets
  reach this corridor, because the right of way at an interchange is drawn on the
  crossing route's sheets rather than on this one's. 15 of those 69 are SH16's own,
  dating **1944–1998**. SH16 across the whole of Bexar County has **27** sheets,
  **1937–1998**, over three control sections — 15 + 8 + 4. Both numbers are right,
  so say which one you are quoting.

Until 2026-09-13 this row read *13 NGS marks (several `MARK NOT FOUND`), 18 TxDOT
control points, 27 ROW sheets 1937–1998*. All three predated the tool running: 13 is
the NGS radial call two miles from the corridor midpoint, 18 has no capture behind it
and reads like a record count, and 27 is the county figure. The account is
[issue #80](https://github.com/RickSmith/survey-recon/issues/80).

### The failure beat (1:36–1:48)
Placed **after** an hour of the agent succeeding — that's when it lands.

1. **The superseded manual.** Search still points at dead `onlinemanuals.txdot.gov` URLs while content moved to `txdot.gov/manuals/row/ess/`. The agent confidently cites a revision no longer in force. *"It didn't lie to you. It found the wrong document and believed it — which is exactly what a new hire does."*
2. **The silent `NoData`.** USGS 3DEP ignored the coordinate-system parameter, read lon/lat as Web Mercator meters, and returned a plausible non-answer instead of an error. *"It didn't fail. It answered. That's worse."*
3. **The error in the work order — ours.** [Issue #7](https://github.com/RickSmith/survey-recon/issues/7) instructed the agent, in writing, to publish "TBPELS has not spoken directly to AI." That is a false statement of law, and it was already on four pages of this repo. The agent went looking for the citation our own rules demand, found [PAO 71](https://pels.texas.gov/nm/2024/pao-71-response.pdf) — 14 Nov 2024, public for nearly two years — and stopped rather than write it. *"A licensed human wrote that error. The agent caught it. If your checking only runs one direction, you've built half of it."*

**Beat 3 is the one that changes the shape of the talk**, so do not let it get cut for time. Beats 1 and 2 say the agent is confidently wrong and the human catches it, which is the thing everyone already half-believes walking in. Beat 3 reverses it in front of them, using this repo's own public history, and it is checkable from the projector — the issue, the comment, the commit and the correction page are all there.

What saved it was not cleverness. It was a rule written in `CLAUDE.md` for a different purpose entirely: *never invent a requirement — cite the section and its URL, or say you could not confirm it.* The claim had no citation, so the agent went to find one, and the search that was meant to confirm it disproved it. **The rule that catches an error is usually boring and was written for something else.** That is the argument for writing the handbook before you need it.

Punchline for owners: **you seal it, you own it.** TBPELS *has* spoken directly to AI — PAO 71 — and its answer is that AI is a tool and the licensee is responsible for whatever they sign and seal. The existing responsibility doctrine is the answer, from the board's own mouth.

*(That punchline said the opposite until 2026-09-12, on four pages. The account is at [The claim we got wrong](managing-your-agent/the-claim-we-got-wrong.md), beside the force-push record.)*

**Timing warning.** This block is 12 minutes and now carries review, seal and three failures. Beat 3 needs about three minutes to land, because the audience has to see the work order before they see the catch. If the run is behind by 1:36, cut **beat 2** — the silent `NoData` is the most technical of the three and the least about accountability.

### The close (1:54–2:00)
Open **one** GitHub issue live, doing three jobs at once:
> **"Introduce yourself and tell us what you'd automate."**

Teaches issues · instruments adoption · the replies pick the next worked example. Say the pattern out loud first: **corridor → public data → flagged list → lead times** works for a ranch boundary and an ALTA as well as a highway.

---

## 6. Repo structure

```
survey-recon/
├── README.md
├── mkdocs.yml
├── .github/
│   ├── workflows/{docs.yml, slides.yml}
│   └── ISSUE_TEMPLATE/        # work orders + "introduce yourself"
├── docs/
│   ├── day-0/                 # setup, screenshot-heavy
│   ├── for-principals/        # the no-terminal one-pager
│   ├── vocabulary/
│   ├── managing-your-agent/   # curated 5-command lifecycle + THIS REPO'S OWN PRs
│   ├── scenarios/sh16/
│   ├── data-sources/          # verified endpoints from txdot-research.md
│   ├── toolkit/
│   ├── going-further/         # Hermes · full mattpocock set · npx route · QC starter
│   ├── governance/            # firm AI policy · what never leaves · seal language
│   └── slides/
├── toolkit/
│   ├── CLAUDE.md · CONTEXT.md
│   └── .claude/skills/        # vendored subset + Matt Pocock MIT LICENSE
├── corridor-screen/           # the reusable tool (Sep 15–17)
└── project-sh16/
    ├── cache/                 # committed API responses, date + URL stamped
    └── outputs/               # memo, parcel table, crew-day build-up
```

---

## 7. Schedule

| Dates | Phase | Done when |
|---|---|---|
| **Sep 13–14** | Scaffold | `survey-recon` public, MkDocs + Marp building on push. **Issue-and-PR discipline starts now.** |
| **Sep 15–17** | Corridor-screening tool | Buffer an alignment → hit the verified services → flagged parcel list with lead times |
| **Sep 18–23** | Acts I–III + cache | Full SH16 run; cache captured and committed; outputs built |
| **Sep 24–28** | Toolkit · Day 0 · for-principals · governance | Take-home kit complete |
| **Sep 29–Oct 2** | Slides · Hermes · failure beat | Deck drafted; ROE-letter demo working; all three failures scripted and reproducible |
| **Oct 3–5** | **Dry run** | Full 2 hours in front of Seneca + CBI staff. Cut against the clock. |
| **Oct 6–7** | Freeze | Tag teaching-moment PRs, freeze repo, print handout with QR |
| **Oct 8** | Deliver | |

### Cut line, in order
1. Hermes segment → recorded teaser
2. Crew-day build-up → shown as finished output, not built live
3. Token slide → footnote to repo

**Never cut:** the cold open, the grilling, the failure beat, the accountability close.

---

## 8. Open questions
1. **Recruit one RPLS** to walk the repo cold in week three.
2. ~~**TCP(S-1)-08A** — pull manually; it's the crew-time document and the host blocks automated fetch.~~ **Closed 2026-09-13.** Pulled by hand, along with the other five sheets in the TCP(S-\*) family, under [#68](https://github.com/RickSmith/survey-recon/pull/68) and [#69](https://github.com/RickSmith/survey-recon/issues/69). They are committed with provenance in [`project-sh16/manual-pulls/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/manual-pulls). What still has no answer is which protective vehicle **TCP(S-5)-08** requires — its drawing and its notes disagree — and what covers **freeway** survey work, since all six sheets read "Conventional Roads Only." Both are recorded as "not found."
3. **Short link + QR** for `<user>.github.io/survey-recon`.

---

## Appendix — Scenario source material (verbatim, from a Texas RPLS)

**ROW retracement**
- When retracing a ROW you get all PDF maps with info as to baseline and monuments found. Surveyors have to draw by hand the baseline and manually create those ROW points to create a stakeout file. If that could be automated to a point, that would be helpful.
- Some of those maps are not legible.

**Estimating a project**
- Trying to figure out how many tracts affecting and how many monuments they are looking for.
- What's the topography look like along the route?
- How far is nearest emergency facilities are located, hotel, food, police (safety sheet for field crew).
- Expected weather.
- Physical access.
- Identifying right of entry issues like schools and cemeteries.
- Counting manholes and culverts because that affects crew time. How many manholes do they need to pop? If on the road, then they have to shut down the road?
- Check to see if you have any data already in that area. Are there any NGS monuments? Use TXDOT control map.
- How long for field crew needs. Often times field crew takes more time than expected.

**Typical TxDOT project example**
- Surveying for preliminary design ROW mapping, east road widening.
- SH16 from Loop 410 to Gibeaut Rd. Already topo survey that needed to updated but also needed ROW mapping to expand on both sides of the road.

!!! note "The name in the line above is left as it was said"
    **There is no Gibeaut Rd in Bexar County.** The corridor's north end is the
    junction of Bandera Rd and **Old Bandera Rd**, in Old Town Helotes — checked
    against two public sources on 2026-09-13 under
    [issue #99](https://github.com/RickSmith/survey-recon/issues/99), and
    recorded in `CONTEXT.md`.

    This appendix is a **verbatim quotation from a Texas RPLS** and is not
    edited. What somebody said is a record; correcting it silently would make
    the record useless. Decision 6 above carries the corrected name.

    The corridor itself never moved. DFO 347.7 to 356.367, 8.691 miles.

**Reference:** TxDOT Surveyor Toolkit — https://www.txdot.gov/business/resources/surveyor-toolkit.html

**Existing asset:** `Beyond the Prompt...pptx` in the parent folder — Rick's initial brain dump, not an official abstract. Reusable content on LLM basics, chatbot→copilot→agent, the agentic loop, markdown, tokens/context, the development cycle, the reality-check slide, takeaways.
