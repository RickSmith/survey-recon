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
| **ALTA survey** | Short for an ALTA/NSPS Land Title Survey — a boundary survey to a national standard set jointly by the American Land Title Association and the National Society of Professional Surveyors, ordered when a commercial property changes hands. Named here because it is the second worked example the closing slides offer: the same four steps, a different set of services |

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
| **RPAM** | Real Property Asset Map. TxDOT's own words: "an online application populated with geo-referenced features that represent all real property assets comprising the highway right of way and is the replacement for paper right-of-way maps" ([TxDOT, Real Property Asset Map](https://www.txdot.gov/data-maps/right-of-way-maps/real-property-asset-map.html)). It is the **fallback** for a sheet with no PDF, along with an Open Records Request. Until 2026-09-19 this repo said it was the only route to a drawing, which was wrong — see `pdf_url` below |
| **`pdf_url`** | The address of one ROW map sheet's own scanned drawing, on each sheet the corridor tool reports. **Built from the sheet's own name rather than published by the service**, because no field carries it and the folder cannot be listed. So it is the one address in the output that TxDOT did not hand over, and the tool does not re-check it on each run: a drawing since withdrawn will answer 404 rather than open. The rule and the evidence are on [the ROW map sheets page](docs/data-sources/row-map-sheets.md) |
| **TMUTCD** | Texas Manual on Uniform Traffic Control Devices. The 2025 edition took effect January 18, 2026 |
| **TCP** | Traffic Control Plan. TxDOT publishes **six** standard sheets for surveying operations — TCP(S-1)-08A, TCP(S-2)-08A, TCP(S-2c)-10, TCP(S-3)-08, TCP(S-4)-08A and TCP(S-5)-08. All six are conventional roads only. Which one applies decides whether a shadow vehicle is drawn, which decides the crew cost. See [`tcp-s-family.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/manual-pulls/tcp-s-family.md) |
| **TMA** | Truck-Mounted Attenuator — the crash cushion on a shadow vehicle. Needing one changes the crew cost. **A sheet that draws a plain work vehicle offers the TMA as an option; a sheet that draws a shadow vehicle only lets you swap it out for work under one hour.** The distinction is in the drawing, not the notes |
| **Shadow vehicle** | A truck parked to be hit instead of the crew. On these sheets it is drawn carrying a **TMA**, and the legend gives the TMA its own symbol — a small solid black chevron on the end facing traffic. A plain work truck has no chevron. A shadow vehicle is a truck *and* an operator, which is why which one a sheet draws decides the day rate |
| **Channelizing devices** | TxDOT's term for the cones, drums and vertical panels that steer traffic away from the work space. Time to set out and time to pick up, not a vehicle |
| **Short duration** | TxDOT's term, printed identically on all six TCP(S-\*) sheets: work that occupies a location **up to 1 hour**. **Short term stationary** is the next band up — *daytime* work that occupies a location for more than 1 hour within a single daylight period. Crossing into it costs the reliefs the hour bought. Both definitions are on every sheet; see [TxDOT research](docs/txdot-research.md) for what each sheet's relief actually is |
| **RRC** | Railroad Commission of Texas. Despite the name it regulates oil, gas and pipelines, not railroads. It publishes **TPMS** |
| **TPMS** | Texas Pipeline Mapping System — the RRC's public pipeline map service. The source this repo uses for pipelines |
| **NPMS** | National Pipeline Mapping System — the federal equivalent, run by PHMSA. The ArcGIS service carrying its name holds Pennsylvania data only; see [the flag services page](docs/data-sources/flag-services.md) |
| **PHMSA** | Pipeline and Hazardous Materials Safety Administration — the federal pipeline regulator |

## Project vocabulary

| Term | Meaning |
|---|---|
| **The worked example** | SH16 (Bandera Rd), Loop 410 → Old Bandera Rd, Bexar County. Route `SH0016-KG`, **DFO 347.7 to 356.367**, 8.691 miles. **This row is where the corridor is defined**; every other page agrees with it rather than restating it. The DFO pair is the corridor — the two road names are a label for it, and the label has been wrong once. See [the end point](#the-end-point-and-how-it-got-its-name) |
| **Corridor screening** | Buffer an alignment, query public services, emit a flagged parcel list with lead times. The tool this repo is named for |
| **Flagged parcel** | A tract with something that costs time — school, cemetery, railroad, pipeline, gated access, livestock |
| **Lead time** | Statutory or procedural delay before you can enter. Railroad 30–45 days, cemetery 14 days, Texas 811 48 hours |
| **Crew-day build-up** | The hours estimate, shown as arguable math rather than a single number |
| **Rate handle** | A short name stamped on one rate in the crew-day build-up — `A1` through `A12` — so a reader can disagree with that one rate out loud, by name, instead of disagreeing with the total. Like a note number on a sheet: you say *note 8*, not *the drawing* |
| **The grilling** | `/grill-with-docs` — the agent interviewing you about scope before it touches anything. The session's centerpiece |
| **The failure beat** | Three deliberate, scripted moments showing work being confidently wrong and then caught. Two show the agent wrong. The third shows a licensed human wrong — a false statement of law written into a work order — and the agent catching it. The direction runs both ways, which is the point |
| **The recursion** | This repo is built the way the session tells attendees to work, so its git history is itself a teaching artifact |
| **Run of show** | The minute-by-minute plan for the two hours — which block is on screen when. A stage term, not a software one. It is the table in `docs/plan-of-record.md` §5, and it is the definitive list of what the session does |
| **Cut line** | The order things get dropped in if the session runs long, decided in advance rather than at the podium. `docs/plan-of-record.md` §7 |
| **Fallback capture** | A committed file that stands in for a live demo step when the live thing will not run. Every one of them is on the card at `docs/presenting/fallbacks.md`, which is checked against the run of show on every test run |
| **The plain-language standard** | How a page in `docs/` has to read for a surveyor: 40 words a sentence, one em dash, and none of the 55 words on the list. Written down at `toolkit/.claude/skills/plain-language/SKILL.md` and counted by `corridor-screen/tests/test_plain_language.py`. #133 set it; #134 built it |
| **The allowlist** | Gone, and named here because older issues and commits still say it. It was `corridor-screen/tests/plain_language_allowlist.txt` — the pages that did not meet the standard yet, skipped until they did. A debt, not an exemption: each child of #133 deleted its own lines, the file emptied on 2026-09-15, and #147 deleted it. No page can opt out now |
| **Exempt** | Held out of the plain-language standard for good, which is the opposite of on the allowlist. `docs/corridor-screen/spec.md` and `docs/txdot-research.md` are the agent's own dated output, and rewriting them would make the stage demo a lie. Two more paths are exempt for reasons of their own. **The list is in [ADR 0003](docs/adr/0003-produced-artifacts-stay-as-produced.md)**, not here, and a test holds the ADR to the list the code enforces |

### The end point, and how it got its name

Until 2026-09-13 every page in this repo called the north end of the corridor
**Gibeaut Rd**. There is no such road in Bexar County. The name came out of the
grilling on 12 September, was written into thirteen files, and was never checked
against a map until Rick read it on a slide.

**The corridor never moved.** `SH0016-KG`, DFO 347.7 to 356.367, 8.691 miles,
half-width 300 ft — unchanged, so no figure anywhere in this repo shifted. Only
the label was wrong. The account is
[issue #99](https://github.com/RickSmith/survey-recon/issues/99).

The name it has now was checked twice against public sources, both on
2026-09-13, at the run's own north end — 29.574516, −98.688309:

| Source | What it answered |
|---|---|
| [Nominatim reverse geocode](https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=29.574516&lon=-98.688309&zoom=17) | `Bandera Road, Helotes, Bexar County, Texas, 78023` |
| [Overpass](https://overpass-api.de/), named highways within 40 m | exactly two — **Bandera Road** (SH16 itself) and **Old Bandera Road** |
| Nominatim search, `Gibeaut, Bexar County, Texas` | **zero results** |

The south end answers `Northwest Loop 410, Leon Valley`, which is what it was
always called.

**TxDOT's own roadway inventory was not consulted**, because the SH16 run does
not call it — `Roadway_Inventory_2023` is recorded as `not-screened`. So this
name rests on OpenStreetMap rather than on the department's data. That is a
weaker source than most things in this repo cite, and it is written down here
rather than left for somebody to discover.

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
| **Second request letter** | The follow-up right-of-entry letter. TxDOT ships its own template for one, `020-11-tem`, beside the first request `020-10-tem` — the department designed for non-response rather than treating it as an exception. It is the letter real firms forget, because forgetting it costs nothing on the day |
| **Follow-up interval** | How long the first right-of-entry letter is left sitting before the second one is written. **Not a published figure** — no ROE turn-around was found in any TxDOT manual read, so it is *derived* from the [lead-time table](#corridor-screening-vocabulary): longest confirmed wait counted in calendar days, halved so the second letter gets the window the first one had, rounded down to whole weeks because a letter moves in weeks. 21 days on the committed table. It is firm policy rather than a property of a tract, which is why the row that sets it can be a flag the corridor does not carry. Settled in [issue #34](https://github.com/RickSmith/survey-recon/issues/34); the arithmetic is on [the right-of-entry letters page](docs/corridor-screen/roe-letters.md) |
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
| **Soft-404** | The sharpest case of the row above: the server answers **HTTP 200** and the body is a "page not found" screen. Nothing in the status code warns you, so a program files the error page as if it were the document. `www.dot.state.tx.us/insdtdot/...` does this for every standard sheet under it, and one of those dead addresses was cited as a source in [#68](https://github.com/RickSmith/survey-recon/pull/68) before anything fetched it. The defense is to fetch the URL you are about to cite and hash what comes back |
| **`NoData`** | What an elevation service returns for a point it holds no height for — the sea off the coast, a gap in the survey. A legitimate answer in its place, and a **wrong** one when the service was asked about the right point and misread the question. **This page said USGS 3DEP did that here, and no capture supports it** — the token is in no response committed in `corridor-screen/captures/silent-nodata/`, and the Gulf of Mexico point, the one a `NoData` would belong to, answers plain text that is not JSON at all (`no-data-gulf.txt`). What the service does instead is quieter, and it is the unit rather than the position: **`units` is silently ignored** unless it is one of a short list of words the service knows. `units=Feet` answers `866.8668528742528` as a JSON **number**, in feet; `units=US_Feet` — the unit a Texas surveyor works in — answers `"264.221008301"` as a JSON **string**, the same ground in meters. So do `ft`, `Furlongs` and no `units` at all (`units-ft.json`, `units-furlongs.json`, `units-omitted.json`): every value the service does not know falls through to meters. `units-meters.json` is byte-identical to the `US_Feet` answer, which is what rules out a conversion going wrong in the middle. **HTTP 200** and no error any of those times. Nearest survey parallel is a total station left on the wrong unit: the shot is clean, the number is real, and nothing on the readout says which unit it is in. Beat 2 of [the failure beat](#project-vocabulary); how the wrong description got here is [the description that outlived its evidence](docs/managing-your-agent/the-description-that-outlived-its-evidence.md) |
| **Null, and blank** | Not the same thing. `null` is "no value recorded"; a field holding a single space is a value, and a query asking for `IS NOT NULL` will match it. Both BCAD and NGS do this, and it is why `arcgis.attribute` treats whitespace as absent |
| **DNS** | The phone book of the internet: it turns a name like `txdot.gov` into the number a computer actually dials. A name can still be in the book after the office behind it has closed -- which is exactly what `onlinemanuals.txdot.gov` does, and why a dead manual looks like bad Wi-Fi rather than a missing page. Settled in [issue #25](https://github.com/RickSmith/survey-recon/issues/25) |
| **Capture** | A saved copy of a whole page or response, kept so a claim about it can be checked later without going back to the web. The screening cache is one kind; `corridor-screen/captures/` holds the other, for pages that are not service responses. Like a photocopy of the deed you worked from, filed with the job |
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
| Seam | The one place a rule or a shape lives, so everything using it inherits the rule rather than restating it. The standard detail every sheet references, instead of the same note redrawn on each |
| Markdown | Plain text with a few marks — anyone can read it, and it opens in nine years without software. **Not** "a field book"; that is git, and a commit is the entry |
| Context window | What is spread on the desk right now. Anything off it might as well not exist |
| Token | A crew-hour for the machine — the unit the tool counts and bills *you* in, never the unit you bill a client in |
