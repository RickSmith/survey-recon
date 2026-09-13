# CONTEXT

Shared vocabulary for this repo. Read before doing anything here. If you find yourself guessing what a term means, it belongs in this file — add it.

---

## What we are building

A public teaching repo, `survey-recon`, that accompanies a two-hour TSPS 2026 convention session on October 8, 2026. It has two jobs and they pull in different directions, so keep both in mind:

1. **A curriculum** — teach licensed surveyors enough software-development management discipline to supervise an AI agent.
2. **A working tool** — actually estimate a TxDOT right-of-way survey job from public data.

When the two conflict, **clarity for a beginner wins.** An elegant abstraction that a surveyor cannot read is a failure here, not a success.

## Who reads this

**Texas land surveyors, mostly firm owners and principals.** Assume: deeply expert in surveying, geodesy, and Texas land law. Assume: little or no programming background, and no patience for being condescended to about it. Many have never opened a terminal. Most have never used git.

They are buyers and risk-owners. They are not going to install things themselves — they are deciding whether to point someone in their firm at this.

---

## Surveying vocabulary

| Term | Meaning |
|---|---|
| **RPLS** | Registered Professional Land Surveyor — the Texas license. An RPLS signs and seals, and carries the liability |
| **LSLS** | Licensed State Land Surveyor — a separate, rarer license for work on Texas state lands. Has stronger statutory access rights than an RPLS |
| **TBPELS** | Texas Board of Professional Engineers and Land Surveyors — the licensing board |
| **TSPS** | Texas Society of Professional Surveyors — the professional association hosting the session |
| **Seal** | The surveyor's stamp. To seal a document is to take personal professional responsibility for it |
| **Responsible charge** | The doctrine that the sealing surveyor is accountable for work done under their supervision — regardless of who or what performed it. In the Texas rules it is **the same standard as direct supervision**, not a looser one: 22 Tex. Admin. Code § 131.2(38) |
| **Direct supervision** | 22 Tex. Admin. Code § 131.2(11). Control over, and detailed professional knowledge of, the work — and personally reviewing and approving proposed decisions **before they are acted on**. The "before" is the part that shapes how an agent must be worked |
| **PAO** | Policy Advisory Opinion. TBPELS answering a question in public, in writing, about how its existing rules apply to something. Not a new rule. **PAO 71** (14 Nov 2024) is the one on AI |
| **22 TAC** | Title 22 of the Texas Administrative Code — the board rules, as opposed to the statute. Surveyor conduct and sealing rules live in **Chapter 138**. They used to be Chapter 663, which is superseded and still all over the internet |
| **Recon** | Desktop reconnaissance before pricing a job. The repo is named for this |
| **Retracement** | Re-establishing a boundary that was surveyed before, from records and recovered monuments |
| **Monument** | A physical marker of a surveyed point — a disk, a rod, a capped rebar |
| **Recovery** | Finding a monument that already exists. Cheaper than setting a new one, which is why recovery-vs-set drives estimates |
| **Control** | Points of known position that everything else is measured from. Primary control is the project backbone; secondary densifies it |
| **Intervisible** | Two monuments you can see from one another. TxDOT requires primary control in intervisible pairs |
| **Closure** | The error you get when a traverse doesn't return exactly to its start. A quality measure |
| **Metes and bounds** | A boundary described as a sequence of bearings and distances |
| **Party chief** | The person running a field crew |

## Geodetic vocabulary

| Term | Meaning |
|---|---|
| **NSRS** | National Spatial Reference System — the national coordinate framework, maintained by NGS |
| **NGS** | National Geodetic Survey (NOAA). Publishes survey marks and their datasheets |
| **PID** | Permanent Identifier — an NGS mark's unique ID, e.g. `AY0713` |
| **Datasheet** | NGS's record for a mark: position, datum, stamping, condition, recovery history |
| **CORS** | Continuously Operating Reference Station — a permanent GNSS station |
| **PACS / SACS** | Primary and Secondary Airport Control Stations — the marks tying an airport survey to the national framework. NGS flags them on a datasheet, and the corridor tool carries the flag through as `pacs_sacs` |
| **MARK NOT FOUND** | The condition NGS records when somebody looked for a mark and could not find it. Not "destroyed" and not "gone" — a report, with a date on it. It is the value that turns a control estimate from recovery into setting new |
| **OPUS** | NGS's Online Positioning User Service — submit GNSS observations, get a position back |
| **NAD 83 / NAVD 88** | The current horizontal and vertical datums TxDOT requires |
| **SPCS** | State Plane Coordinate System. Texas has multiple zones; Bexar County is Texas South Central |
| **Grid vs surface** | Grid coordinates live on the map projection; surface coordinates are scaled to real ground distance. TxDOT requires **both** |
| **Scale factor** | The number converting between grid and surface. TxDOT publishes these per county |
| **NATRF2022 / NAPGD2022 / SPCS2022** | The modernized replacements for NAD 83, NAVD 88 and SPCS. **TxDOT's April 2026 Survey Manual does not mention any of them.** See the datum-gap note in `docs/txdot-research.md` |

## TxDOT vocabulary

| Term | Meaning |
|---|---|
| **ROW** | Right of way — the land corridor a highway occupies |
| **ROE** | Right of Entry — written landowner permission to enter property. **Not a statutory right in Texas** |
| **CSJ** | Control-Section-Job number — TxDOT's project identifier, e.g. `2552-04-041` |
| **Control section** | A numbered segment of a highway. SH16 through Bexar spans 0291-09, 0291-10, 0613-01 |
| **DFO** | Distance From Origin — TxDOT's linear referencing measure along a route |
| **ROW map sheet** | The historical record drawing of a right of way. SH16 across the whole of Bexar County has 27, dating 1937–1998, over three control sections. The demo corridor is 8.69 miles inside one of those sections and reaches 15 of them, dating 1944–1998 — a corridor figure and a county figure are different questions, and [the ROW map sheets page](docs/data-sources/row-map-sheets.md) works the difference through |
| **ORD** | OpenRoads Designer — the MicroStation product TxDOT requires for design survey graphics |
| **ProjectWise / OnBase** | TxDOT's document systems. Design surveys go to ProjectWise; final ROW maps to OnBase |
| **RPAM** | Real Property Asset Map. TxDOT's own words: "an online application populated with geo-referenced features that represent all real property assets comprising the highway right of way and is the replacement for paper right-of-way maps" ([TxDOT, Real Property Asset Map](https://www.txdot.gov/data-maps/right-of-way-maps/real-property-asset-map.html)). A map not available there is obtained by Open Records Request. The corridor tool reports sheet numbers and dates; the drawings come from here |
| **TMUTCD** | Texas Manual on Uniform Traffic Control Devices. The 2025 edition took effect January 18, 2026 |
| **TCP** | Traffic Control Plan. TCP(S-1)-08A is the standard sheet for surveying operations |
| **TMA** | Truck-Mounted Attenuator — the crash cushion on a shadow vehicle. Needing one changes the crew cost |
| **RRC** | Railroad Commission of Texas. Despite the name it regulates oil, gas and pipelines, not railroads. It publishes **TPMS** |
| **TPMS** | Texas Pipeline Mapping System — the RRC's public pipeline map service. The source this repo uses for pipelines |
| **NPMS** | National Pipeline Mapping System — the federal equivalent, run by PHMSA. The ArcGIS service carrying its name holds Pennsylvania data only; see [the flag services page](docs/data-sources/flag-services.md) |
| **PHMSA** | Pipeline and Hazardous Materials Safety Administration — the federal pipeline regulator |

## Project vocabulary

| Term | Meaning |
|---|---|
| **The worked example** | SH16 (Bandera Rd), Loop 410 → Gibeaut Rd, Bexar County |
| **Corridor screening** | Buffer an alignment, query public services, emit a flagged parcel list with lead times. The tool this repo is named for |
| **Flagged parcel** | A tract with something that costs time — school, cemetery, railroad, pipeline, gated access, livestock |
| **Lead time** | Statutory or procedural delay before you can enter. Railroad 30–45 days, cemetery 14 days, Texas 811 48 hours |
| **Crew-day build-up** | The hours estimate, shown as arguable math rather than a single number |
| **The grilling** | `/grill-with-docs` — the agent interviewing you about scope before it touches anything. The session's centerpiece |
| **The failure beat** | Three deliberate, scripted moments showing work being confidently wrong and then caught. Two show the agent wrong. The third shows a licensed human wrong — a false statement of law written into a work order — and the agent catching it. The direction runs both ways, which is the point |
| **The recursion** | This repo is built the way the session tells attendees to work, so its git history is itself a teaching artifact |

## Corridor-screening vocabulary

Settled during the grilling for [issue #5](https://github.com/RickSmith/survey-recon/issues/5).

| Term | Meaning |
|---|---|
| **Screening run** | One pass of corridor screening over one corridor. The unit that every cached response and every output is stamped against |
| **Alignment** | The centerline of the corridor being screened. Either drawn and handed to the tool, or named as a route with two limits |
| **Half-width** | How far each side of the alignment counts as inside the corridor. Screening states this number rather than deriving it, so the parcel count can always be argued against a number a person chose |
| **Reachability ping** | A cheap check of every service before real work begins, so a blocked host is known in seconds rather than part-way through a run |
| **Sanity check** | A blunt test applied to a service's answer, to catch a plausible wrong one — a paging cap mistaken for a result, a filter the server ignored. It records a warning. It never halts a run. See [ADR 0001](docs/adr/0001-sanity-checks-warn-dead-services-stop.md) |
| **Not-screenable** | A flag type no public source can detect. Gated access and livestock are the two. Named in the output so the gap is visible rather than silent |
| **Run mode** | Whether a run may reach the network: live, cache-first, or cache-only. Cache-only is what makes a run repeatable away from a working network |
| **Provenance record** | What is written beside every cached response: the exact request URL, the capture date, the HTTP status, and the record count. Caching without it is undisclosed caching |
| **`unknown` vs `no`** | A parcel that could not be checked is `unknown`. It is never `no`. One of those two words sends a crew to a locked gate |
| **On / adjacent** | Two strengths of the same flag. A feature inside the parcel is `on` it. The same feature within a stated neighbor distance is `adjacent`. Recorded separately and never merged — a party chief needs to know about both, and an estimator must not count both |
| **Corridor-level flag** | Something that costs time but belongs to no single parcel — a pipeline easement crossing many of them, a railway crossing the route. Recorded against the run rather than against a parcel, so it cannot be quietly dropped |
| **Incomplete run** | A screening run that stopped before every service answered. It still produces an output, marked incomplete, naming what finished and what stopped. Half an answer that says so beats no answer |
| **Synthetic parcel id** | An identifier made from a parcel's shape, used when its source gives no usable key. Always marked synthetic, because it is ours and not the appraisal district's |
| **Wrong-file check** | The length, end points and quick rendering printed before any service is called, so a corridor built from the wrong file is obvious immediately rather than after a clean-looking run |
| **Honesty block** | The part of a screening output recording every service called, whether it answered, when its answer was captured, and what was doubted about it. It is what lets a reader decide whether to trust the rest of the file |
| **Lead-time table** | The checked-in list of how many days of notice each flag type costs, with a mandatory citation on every row. Data rather than code, so the person accountable for a number can change it without touching Python. Settled in [issue #17](https://github.com/RickSmith/survey-recon/issues/17); the citations are in [`docs/corridor-screen/lead-times.md`](docs/corridor-screen/lead-times.md) |
| **Not found** | A lead time we looked for and could not confirm from a published source. Written as "not found," never as "does not exist," and always with an account of where we looked. On a parcel it appears as `lead_time_not_found` beside `max_lead_time_days` — because a parcel with no number is unmeasured, not clear. Same distinction as [`unknown` vs `no`](#corridor-screening-vocabulary) |
| **Lead-time driver** | Which flag on a parcel set its longest wait. Recorded beside the number so nobody has to scan a list of flags to find the one that moves the schedule |
| **Replay** | Running the whole tool from the saved responses instead of calling the services, with `--mode cache-only`. It is a replay and not a recording: the same code runs, and only one function -- `arcgis.Fetcher.get_json` -- knows where a response came from. A replayed run reports when its data was captured rather than implying it is fresh. Settled in [issue #19](https://github.com/RickSmith/survey-recon/issues/19) |
| **The run's account of itself** | The parts of an output file that describe how a run went rather than what it found -- the run id, the start and finish times, the mode, and the ping fields on each service. A faithful replay differs from a live run in exactly these and nothing else. Named once in `corridor_screen/replay.py`, with a reason beside each, so the list can be argued with |
| **Crew safety sheet** | The nearest hospital, ambulance service, fire or EMS station and police station for a corridor, each with a distance. A party chief's output rather than an estimator's, and kept apart from the flagged parcel list for that reason. Every distance on it is a **straight line, not a drive time** — an ambulance drives roads. Settled in [issue #18](https://github.com/RickSmith/survey-recon/issues/18); the sources are on [the crew safety page](docs/data-sources/crew-safety.md) |
| **Recovery risk** | An NGS mark in the corridor whose last recorded condition is `MARK NOT FOUND` — somebody looked and did not find it. Counted separately from the marks in the corridor, because a count of marks reads as control you have and this is control you may have to set. Settled in [issue #14](https://github.com/RickSmith/survey-recon/issues/14); the source is on [the NGS datasheets page](docs/data-sources/ngs-datasheets.md) |
| **Condition unknown** | An NGS mark or TxDOT control point the service publishes no condition for. Counted apart from recovery risk and never folded in with the monuments reported present, for the same reason as [`unknown` vs `no`](#corridor-screening-vocabulary): nobody looking is not the same as somebody looking and failing, and neither is a monument you have. On the TxDOT service the word `Unknown` and the placeholder `N/A` both land here |
| **Monument destroyed** | The condition TxDOT publishes for one of its own primary control points that is gone. Recorded separately from the NGS `MARK NOT FOUND` rather than merged with it: one says somebody looked and could not find it, the other says it is gone, and the second is the stronger claim. Both cost a crew the same trip. Settled in [issue #15](https://github.com/RickSmith/survey-recon/issues/15); the source is on [the TxDOT control points page](docs/data-sources/txdot-control-points.md) |
| **Distinct stations** | How many *monuments* the TxDOT control records in a corridor actually name, as against how many records came back. The service holds two records for 274 of its 492 stations, so the two numbers differ — on SH16, four records name two monuments. Reported beside the record count and never in place of it, because a crew drives to the monument and an estimator must not count it twice |

## Reading a map service

These turn up all over [the data-source pages](docs/data-sources/index.md). None
of them is a surveying idea; they are the words the services themselves use, and
they are collected here so no page has to stop and explain them twice.

| Term | Meaning |
|---|---|
| **Endpoint** | The web address you ask a question of. A service usually has several |
| **Layer** | One table inside a service, numbered. TxDOT's control points are layer 67 of theirs. **The number is load-bearing** — asking the wrong one can answer without complaining |
| **WKID** | Well-Known ID. Esri's number for a coordinate system — 4326 is longitude and latitude, 2278 is NAD 83 Texas South Central in US survey feet |
| **EPSG** | A different numbering of the same idea, by a different body. `9003` is EPSG's code for the US survey foot, and it is the one that answers wrong in [the geometry service](docs/data-sources/arcgis-geometry-service.md) |
| **Polyline** | A line, as a service returns it: a list of points to join up |
| **M value** | A third number on each point of a polyline — a measure along the line rather than a position. On TxDOT's roadways the M values **are** the DFO |
| **Envelope** | A rectangle, given as its four corner coordinates. Asking with an envelope instead of a line and a distance is what stopped a USGS service answering about the wrong county |
| **SVG** | A drawing stored as text rather than as pixels — the shape is written down as instructions, so it redraws itself at whatever size it is shown at. Closest thing in survey work is a vector plot against a raster scan: one stays sharp when you enlarge it, the other goes blocky. Being text, it commits to git and a change to it shows a readable diff |
| **Paging cap** | The most records a service will hand over at once. Ask for more and it gives you the cap **and a flag saying there is more** — a tool that ignores the flag reports the cap as if it were the answer |
| **HTTP 200** | The web's code for "here is your answer." It says the request arrived and got a reply. **It does not say the reply is an answer** — several services return a 200 carrying an error message, and a caller that checks only the code sees success |
| **Null, and blank** | Not the same thing. `null` is "no value recorded"; a field holding a single space is a value, and a query asking for `IS NOT NULL` will match it. Both BCAD and NGS do this, and it is why `arcgis.attribute` treats whitespace as absent |
| **Robots-blocked** | A server refusing automated requests by policy, via a `robots.txt` file naming what may be fetched. It is a rule rather than a failure, and a polite tool obeys it |

## Translation table — used throughout the docs

| Software term | Survey term |
|---|---|
| Issue | Work order |
| Branch | A working copy nobody else is affected by |
| Commit | A field book entry |
| Pull request | The check print you redline |
| Merge | You sign and seal |
| Spec | Scope of work |
| Code review | Checking the work before it goes out the door |
| Rewriting history | Going back and altering field book entries already made |
| Force push | Tearing a page out of the field book and writing a new one in its place |
