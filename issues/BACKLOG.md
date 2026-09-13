# Backlog

Feed this to `/to-tickets` alongside `docs/plan-of-record.md` §7. Issue #1 already exists by hand as `001-scaffold-mkdocs-marp.md`.

Phases match the schedule. **The dates are real and the deadline does not move.**

---

## Phase: Corridor screening tool — Sep 15–17
*Highest-risk build item, and the one genuinely unspecified piece. Start with `/grill-with-docs` on this tool, not with code — that grilling session doubles as a rehearsal of the session's centerpiece demo.*

- Specify the tool: inputs (route and limits? alignment geometry? bbox?), output schema, service call order, failure behavior, cache strategy
- Implement corridor buffering from a route and limits
- Query NGS marks along the corridor, carrying the `condition` field so `MARK NOT FOUND` becomes visible recovery risk
- Query TxDOT `Primary_Control_Points` — **note layer ID is 67, not 0**
- Query TxDOT `ROW_Maps_CL_2017` for sheet count and date range
- Query parcels from the CoSA BCAD service (weekly refresh, fresher than the county's)
- Query ancillary flags: schools, cemeteries, railroads, pipelines, hospitals and EMS
- Join everything to a flagged parcel list with a statutory lead-time column
- Cache every response with capture date and request URL
- Make the whole thing runnable offline from cache

## Phase: The worked example — Sep 18–23

- Run the SH16 scope end to end and capture what actually happens
- Build the bid memo output
- Build the flagged parcel table output
- Build the crew-day build-up, with the math shown and arguable
- Capture and commit the complete demo cache
- Record fallback captures for every demo step, as the work happens rather than afterward
- Script the failure beat: the superseded `onlinemanuals.txdot.gov` citation, the USGS answer that is wrong rather than missing, and the false TBPELS claim the agent caught in its own work order (issue #7)
- Verify all three failures are reproducible on demand. Beat 3 is reproducible by reading, not by running - the issue, its correction comment, the commit and `docs/managing-your-agent/the-claim-we-got-wrong.md` are the artifacts

## Phase: Take-home kit — Sep 24–28

- `docs/day-0/` — setup from zero, screenshot-heavy, tested by someone who has never done it
- `docs/for-principals/` — one page, no terminal: what to tell your team Monday, what it costs, what your policy should say, what you are still liable for
- `toolkit/CLAUDE.md` — the firm-ready employee handbook template
- Vendor the curated five-command subset of mattpocock/skills into `toolkit/.claude/skills/`, retaining the MIT LICENSE and crediting Matt Pocock
- `docs/data-sources/` — every verified endpoint from `docs/txdot-research.md`, with fields and quirks
- `docs/governance/` — firm AI-use policy, what-never-leaves-the-office checklist, seal and responsible-charge language
- `docs/going-further/` — Hermes, the full mattpocock set, the npx route, a QC starter
- `.github/ISSUE_TEMPLATE/` — work order template plus the "introduce yourself" template

## Phase: Slides and Hermes — Sep 29–Oct 2

- Draft the Marp deck against the run of show in `docs/plan-of-record.md` §5
- Port the reusable concept slides from the original brain-dump deck: LLM basics, chatbot→copilot→agent, the agentic loop, markdown, the reality check
- Build the money slide: billable-hour math, rework framing, "cannot be invoiced"
- Build the datum-gap slide, framed as an open question with no blame
- Build the Hermes demo: the second ROE letter that sends itself on day 21
- Write Seneca's audience-proxy interjections — roughly six, scripted and rehearsed

## Phase: Dry run and freeze — Oct 3–7

- Full two-hour dry run in front of Seneca and CBI staff
- Cut against the clock, following the cut line in `docs/plan-of-record.md` §7
- Re-record fallbacks cleanly
- Tag the `teaching-moment` pull requests so they can be found on stage
- Print the handout with QR code
- Freeze the repo

## Standing / ongoing

- Recruit one RPLS to walk the repo cold during week three — *the single highest-value outside check available*
- Pull TCP(S-1)-08A manually; the host blocks automated fetch and it is the crew-time document
- Decide the short link and generate the QR code
