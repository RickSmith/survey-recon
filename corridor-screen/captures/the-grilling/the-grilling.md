# The grilling, as it ran

Captured from the Claude Code session that ran `/grill-with-docs` on
[issue #5](https://github.com/RickSmith/survey-recon/issues/5) on 12 September 2026.
It is the run that produced [the corridor-screening spec](../../../docs/corridor-screen/spec.md).

**This is the grilling and nothing else.** What each block is, and what was
left out and why, is in [the README](README.md) beside this file. Read that
first if you are looking for one screen rather than the whole run.

**Every word below is what was said.** One thing was taken out: the worktree
notice the app stamps onto a turn, which sat on top of Rick's Round 2 answers
and carried the path of the machine it ran on. Nobody wrote it and it says
nothing about the tool. Beyond that, the search for a path or an address came
back empty — there was nothing else in these blocks to take out.


---

**ROUND 1 — nine questions.** Everything from here to the next rule is verbatim.

**The agent:**

I read the repo. Nothing is built yet — `corridor-screen/` does not exist. But the facts are already very good: `docs/txdot-research.md` has every endpoint verified live.

**Two things in `CONTEXT.md` fight with what the data can do. I flag them inside the questions below.**

Here is Round 1. These are the decisions with nothing blocking them. Answer by number. Short answers are fine — "yes", "your way", or "no, do X".

---

❓ **Q1** — **What do I hand the tool?**

Three ways to say "SH16, Loop 410 to Gibeaut Rd":

- **A route name plus two DFO numbers.** TxDOT's own `TxDOT_Roadways` service holds `RTE_NM`, `BEGIN_DFO`, `END_DFO`. The tool asks that service for the centre line. Clean, and it is TxDOT's own language. But a surveyor must first look up two DFO numbers they do not carry in their head.
- **A bounding box.** Four numbers. Dead simple. But the research already proved this fails: a bbox on SH16 pulled **~55,000 parcels**. A corridor is a ribbon, not a square.
- **A GeoJSON line you supply.** Most flexible. But then you must make the line first, and most of your audience cannot.

Note: `CONTEXT.md` already defines corridor screening as "**Buffer an alignment**". That wording assumes a line, not a box. So the glossary has half-answered this.

➡️ **Route name plus two DFO numbers, with a GeoJSON line as an override.** The tool resolves the line from TxDOT, then caches it. A bbox is never an input — it is only an internal step. I would also let you pass two cross-street names later, but not in version one, because that needs geocoding and geocoding lies quietly.

---

❓ **Q2** — **How wide is the corridor?**

You need a half-width — how far each side of the centre line counts as "in".

- **One fixed number you type in.** Default 300 ft. You can defend it on stage in one sentence.
- **Derived from the road.** `Roadway_Inventory_2023` carries `ROW_MIN`, the existing ROW width. The tool could read it and add your widening. Smarter. Harder to explain, and it hides a number that changes the parcel count.

➡️ **One fixed number, default 300 ft, printed in the output header.** Screening is a first pass. A number you chose and can argue with beats a number the tool chose for you. Reading `ROW_MIN` is still worth doing — but as a *reported fact* about the road, not as the thing that sets the buffer.

---

❓ **Q3** — **Who does the buffer maths — my code, or their server?**

- **My code.** I would need `shapely` and `pyproj`. `CLAUDE.md` says standard library plus `requests` where possible, and every dependency needs a justification. This is two dependencies, and they are heavy ones.
- **Their server.** The ArcGIS query API takes a line, a `distance`, and `units`, and does the buffering itself. Zero new dependencies. One catch: I never hold a corridor polygon, so there is nothing to draw, stamp, or hand you.

➡️ **Their server, but I still ask for the buffer polygon once and cache it.** One extra call gets me a real polygon for the output header and for a map later. After that, every service query just carries the line plus the distance. No new dependency.

⚠️ One risk you should hear: the 3DEP failure in your own notes was *a server quietly ignoring a parameter*. If a server ignores `distance`, I get the whole county back and it looks fine. Q7 covers how I catch that.

---

❓ **Q4** — **What comes out, and in what shape?**

- **One JSON file.** Machine-readable. Every later output — the bid memo, the parcel table, the crew-day build-up — reads it. It is the single source.
- **A Markdown table straight out.** Readable on stage right away. But then three different outputs each re-query the services, and they will drift apart.

➡️ **One JSON file, and the parcel is the row.** A header block holds the run itself: route, limits, half-width, run date, every service called, and whether each one worked. Then an array of parcels. Turning that JSON into a memo or a table is a *different* job, in a different issue. One fetch, many renderings.

---

❓ **Q5** — **What order do I call the services in, and why?**

Two honest orders:

- **Spine first, risk last.** Centre line → buffer → parcels → flags → control → ROW sheets. Parcels are the spine everything joins to. The two flaky things (`maps.dot.state.tx.us`, anything elevation) sit at the end where a failure costs least.
- **Risk first.** Call the flaky ROW-sheet server first. If it is blocking today, you learn in five seconds instead of two minutes.

➡️ **Spine first, risk last — plus a five-second reachability ping across every service before any real work starts.** That gets you both. The ping tells you immediately that the ROW server is sulking. The real order still protects the useful work. The ping result goes in the output header.

---

❓ **Q6** — **What happens when a service is simply dead?**

➡️ **The tool never dies, and it never stays quiet.** A dead service becomes a *recorded fact* in the output, not a missing field. Each service gets a status: `ok`, `failed`, or `from-cache`. A parcel that could not be checked for schools says `unknown`, never `no`. `unknown` and `no` are different words and they must stay different, because one of them sends a crew to a locked gate.

The tool exits non-zero if any service failed, so you cannot miss it. But it still writes the file.

Do you agree, or do you want a hard stop on certain services? I would argue parcels are the one worth stopping for — without parcels there is no list at all.

---

❓ **Q7** — **What happens when a service answers, but the answer is wrong?**

This is your failure beat, and it is the hardest thing in the spec. The 3DEP case returned a *plausible number*, not an error.

➡️ **Every service gets a small sanity check that runs on every response, and the results go in the output.** Not clever. Just blunt and cheap:

- Did I get more parcels back than a corridor this long can hold? Then `distance` was ignored.
- Did every returned point land inside my corridor? If one is 40 miles away, the spatial filter failed.
- Is the record count exactly 500, 1000, or 2000? That is a paging cap, not an answer.
- Did the layer ID I used actually return the fields I expected? Your own notes say control is layer **67**, not 0 — and a wrong layer fails *silently*.
- Is a number impossible? Negative acres, a recovery date in the future.

Each check that trips writes a warning into the output next to the data. **The tool does not hide it and does not fix it.** A human decides.

Do you want any check to be fatal rather than a warning?

---

❓ **Q8** — **How does caching work?**

➡️ **Every single HTTP response is written to `project-sh16/cache/`. One response, one file, plus a small sidecar file beside it.**

The sidecar carries, at minimum:

- the exact request URL, with every parameter
- the capture date and time, with the time zone
- the HTTP status
- the service name and layer ID
- a hash of the request, which is also the filename
- the record count returned
- any sanity check that tripped

Three run modes: `live` (fetch, and write cache), `cache-first` (use cache if present — the default), `cache-only` (never touch the network; fails loudly if something is missing). `cache-only` is what makes the tool testable offline and is your safety net if the venue Wi-Fi dies.

Your plan of record says keep **one genuinely live call** on stage, and names NGS `/radial` as the most reliable. I would wire that as a named flag, so it is a deliberate choice and not an accident.

---

❓ **Q9** — **Which flags, and where does the lead-time table live?**

⚠️ **This is the glossary conflict.** `CONTEXT.md` defines a flagged parcel as one with "school, cemetery, railroad, pipeline, **gated access, livestock**."

**There is no public service that tells you a parcel is gated or has livestock.** Your research found layers for cemeteries, schools, railroads, pipelines, hospitals, ambulance, fire/EMS and historic sites. Nothing for gates. Nothing for cattle. The glossary is promising something the data cannot deliver, and for this repo that matters — the docs get read by people who will trust them.

Two ways out:

- **Trim the definition** to what public data supports, and say plainly that gates and livestock are field knowledge.
- **Keep the definition** and mark those flags `not-screenable` in the output, so the gap is visible in the artifact rather than hidden.

➡️ **Keep the definition, and make the gap visible.** Option two is more honest and it is a better teaching moment. A tool that says "I cannot see this, you must" is exactly the thesis of your session.

And on lead times: ➡️ **the lead-time table is checked-in data, not code.** One row per parcel type, with a mandatory source column — `HSC § 711.041`, `Util. Code ch. 251`, and so on. Your `CLAUDE.md` says numbers with legal consequence get a source link next to them. If the table is data, that rule is enforceable. If it is buried in code, it rots.

---

## What waits for Round 2

I am deliberately not asking these yet. Each one needs your answers above first:

- The field-by-field output schema (needs Q4 and Q9)
- Cache folder layout and file names (needs Q8)
- How a flag attaches to a parcel — does a school 50 ft outside the buffer count? (needs Q2)
- The command-line surface (needs Q1 and Q8)
- Whether a flagged parcel carries a confidence value (needs Q7)

Answer Round 1 and I will recompute.


---

**RICK ANSWERS ROUND 1.** Verbatim.

**Rick:**

Q1) accept a geojson, shapefile, kml, kmz, a route name plus two DFO numbers.
Q2) your recommendation
Q3) your recommendation
Q4) your recommendation
Q5) your recommendation
Q6) hard stop with option to retry
Q7) warning
Q8) your recommendation
Q9) your recommendation


---

**WHAT THE AGENT DID WITH THEM.** Verbatim.

**The agent:**

Answers logged. Two of mine got overridden — **Q6 hard stop** and **Q1 now takes four file formats**. Both change things downstream. I will come back to that.

First, the glossary. Nine terms are now settled, so I write them down now rather than at the end.


---

**ROUND 2 — seven questions.** Verbatim.

**The agent:**

Python 3.11.9 is here. And a useful fact: **GeoJSON, KML and KMZ all read with the standard library. Shapefile does not.** That drives the first question.

---

❓ **Q10** — **Shapefile is the only format that costs something. Pay for it, or write it?**

Your four formats break down like this:

| Format | What reads it | Cost |
|---|---|---|
| GeoJSON | `json` | free, built in |
| KML | `xml.etree` | free, built in |
| KMZ | `zipfile` + `xml.etree` | free, built in |
| **Shapefile** | **nothing built in** | **this is the question** |
| Route + 2 DFO | an HTTP call | free, built in |

Everything else in the tool is also standard library. So **this one format decides whether the tool needs zero installs or one.**

- **Write it myself.** About 60 lines. A shapefile's line format is a published, simple binary layout. The tool then needs **nothing installed at all** — clone it, run it with the Python you already have. I would only support plain lines, and reject anything else with a clear message telling you to convert to GeoJSON.
- **Use `pyshp`.** Pure Python, MIT, no compiler needed, but it is a `pip install`. Battle-tested. Handles every odd shapefile a surveyor might actually own.

➡️ **Write it myself.** Your `CLAUDE.md` sets a hard line on dependencies, and "runs with no install" is worth real money to this audience. The risk of my own reader being quietly wrong is the right worry — but it cannot stay quiet, because Q11 makes the tool print the corridor length and both end points before it does anything. A mis-read shapefile shows up as a 4,000-mile corridor on line one.

*Good news on projections: your shapefiles are probably Texas State Plane, not lat/lon. The `.prj` beside them is plain text, and ArcGIS accepts that text directly. I forward it and let their server do the maths. No projection library either.*

---

❓ **Q11** — **What are the rules when the file is not what I hoped?**

Real cases, real rules:

- **Many line features in one file** → merge them into one alignment. Do not try to join the gaps. A corridor with a break is a legitimate corridor.
- **A polygon, or points** → reject, and say what to do instead.
- **Z or M values** → drop them. Screening is flat.
- **Nothing at all** → reject.

➡️ **Those four rules, plus this: before any service is called, print the corridor length in miles and both end point coordinates, and require them in the output header.** That one line is your cheapest protection against running a perfect screening on the wrong file.

---

❓ **Q12** — **"Hard stop with option to retry" — what exactly?**

You overrode me here, so let me get it exactly right. Three parts:

1. **Automatic first.** Retry 3 times with a growing wait before declaring the service dead. Most blocks are momentary — your own notes say `maps.dot.state.tx.us` failed and then worked minutes later.
2. **Then ask, if someone is there.** If a person is at the keyboard, stop and offer: retry, skip this service, or abort. If nobody is there, exit non-zero and do not hang. A tool that waits forever for an answer in an automated run is a broken tool.
3. **The reachability ping is the better place to stop.** It runs first and costs seconds. If the ROW server is blocking today, you decide *up front* — not ninety seconds in, holding a half-finished run.

➡️ **All three. And a hard stop still writes the output file, marked `incomplete`,** listing what finished and what stopped. The cached responses are already on disk, so re-running in cache-first mode picks up almost where it left off, nearly free. Throwing away good work because the last service sulked would be the wrong behaviour on stage.

---

❓ **Q13** — **How does a school become a flag on a parcel?**

A school is a point. A parcel is a shape. They have to be joined, and the join rule changes your numbers.

- **Strict.** The school must sit inside the parcel. Clean and defensible. But a point can be plotted badly, and a school whose fence runs along your parcel line will not flag it.
- **Loose.** Flag anything within some distance. Safer for a crew, but it inflates the list and the number is arbitrary.

➡️ **Both, in two different words.** A flag inside the parcel is `on`. The same flag within a stated neighbour distance is `adjacent`. Both are recorded, never merged. `adjacent` is a real thing a party chief needs to know and a real thing an estimator should not double-count.

**And a second half:** some things do not belong to any one parcel — a pipeline easement crosses many, a railroad crosses the corridor. Anything that cannot attach to a parcel goes into a **corridor-level** flag list, so it is never silently dropped.

---

❓ **Q14** — **What makes a parcel a parcel?**

BCAD gives `AcctNumb`. That is the natural key. Two edge cases:

- **No account number.** Happens with road ROW and odd slivers.
- **TxDOT already owns it.** Your research found a `2025_Land_Parcels` layer of TxDOT-owned land.

➡️ **`AcctNumb` is the key. If it is missing, make a stable one from the shape and mark it `synthetic`. Never drop a parcel for lacking a key.** And include TxDOT-owned parcels, clearly marked — "no right of entry needed here" is a useful estimating fact, not noise.

---

❓ **Q15** — **Where does the spec file live?**

The site nav in `mkdocs.yml` has no place for it yet.

➡️ **`docs/corridor-screen/spec.md`, added to the nav, with `corridor-screen/README.md` pointing at it.** One copy. It publishes to the site, because attendees should be able to read the scope of work that produced the tool. That is half the lesson.

---

❓ **Q16** — **Do you want an ADR for the Q6 / Q7 split?**

You chose: a **dead** service stops the run, but a **wrong-looking** answer only warns. That is backwards from what most people would guess, and a future reader will ask why.

➡️ **Yes, write one.** The reasoning is worth keeping: a dead service is a fact, so stopping is safe. A tripped sanity check is only a guess — and if a guess could halt a run, one false alarm on stage would teach everyone to switch the checks off. A warning that always fires and never blocks stays trusted. The licensed human decides. That is your whole thesis in one design rule.

This would be `docs/adr/0001-*.md`. The folder does not exist yet; I would create it.

---

## Round 3 waits on these

- The output schema, field by field — needs Q13 and Q14
- Cache folder layout and file names — needs Q12
- The command-line surface — needs Q10 and Q12

Answer and I will recompute.


---

**RICK ANSWERS ROUND 2.** Verbatim, less the worktree notice described above.

**Rick:**

Q10) Write it yourself
Q11) All of that plus a rendering of the corridor.
Q12) Your recommendation.
Q13) Your recommendation.
Q14) Your recommendation. However, parcels may vary widely depending on the source, so be prepared to understand other parcel layers and adapt to a different primary key.
Q15) Your recommendation.
Q16) Your recommendation.


---

**WHAT THE AGENT DID WITH THEM.** Verbatim.

**The agent:**

Logged. Two things you added change the shape: **a corridor rendering**, and **parcel sources must be swappable**. Both land in Round 3.

First, the ADR you approved and the terms that are now settled. Reading the house format before I write.


---

**ROUND 3 — three questions.** Verbatim.

**The agent:**

ADR and glossary are on disk. Now Round 3 — the last big one. Three questions.

---

❓ **Q17** — **The corridor rendering: what format, and how many?**

**Format.** Two real choices:

- **SVG.** It is plain text. Zero dependencies. It commits to git and shows a readable diff. It embeds in the MkDocs site **and** in your Marp slides. It stays sharp on a projector at any size. The catch: no basemap. You see your own shapes on white.
- **HTML with a web map.** A real basemap — you can see it really is Bandera Road. But it fetches a map library from the internet when viewed, will not embed in a slide, and is a blob in git.

➡️ **SVG — and the tool also prints a plain map link centred on the corridor.** One click in a browser confirms the real-world location against a real basemap. You get the basemap check without putting a network dependency inside the artifact.

**How many.** ➡️ **Two.**

1. **The quick one**, drawn right after reading your file, before a single service is called. Alignment and buffer only. This is the wrong-file check — it costs nothing and catches the most embarrassing mistake.
2. **The full one**, at the end. Parcels, flag markers, parcels shaded by how many flags they carry, north arrow, scale bar, corner coordinates, and the run stamp — date, half-width, source set.

---

❓ **Q18** — **Swappable parcel sources: where does that description live?**

You said parcel layers vary and the key may differ. That is a bigger change than it sounds. It turns this from *a Bexar County tool* into *a tool you point at a county*.

- **Config files, checked in.** One file per area. It names the parcel endpoint, the layer, the key field, the owner field, the acreage field, and every flag layer. Adding Travis County means adding one file and writing no code. It gets reviewed in a pull request like anything else.
- **Command-line flags.** `--parcel-url ... --parcel-key ...`. Flexible, but a dozen flags every run, and nothing is reusable or reviewable.

➡️ **Config files — and not just for parcels. Every service gets described the same way.** Then the whole catalogue is data, and the tool genuinely does not know it is in Bexar County. That is your generalisation slide made real instead of asserted.

➡️ **Format: TOML.** Python 3.11 reads it with nothing installed, and TOML has real comments. In a repo where a surveyor is meant to open the config and understand it, comments are not a luxury.

The command line then stays small:

```bash
corridor-screen --alignment sh16.kmz --half-width 300 --area texas-bexar --mode cache-first --out project-sh16/
```

➡️ **One more rule inside this: if a config file names a field the service does not actually have, that is a hard error at load time, before any query runs.** This is the `layer 67, not 0` trap from your own research — a wrong layer returns data that looks fine and is silently wrong. Checking the field list up front costs one request and kills that whole failure class.

---

❓ **Q19** — **Cache layout — what goes where?**

➡️ My recommendation, in three parts:

**The response file.** `project-sh16/cache/<service>/<readable-name>__<short-hash>.json` — exactly the bytes the server sent. Never edited. Grouped by service so the folder reads like a table of contents rather than a pile of hashes.

**The provenance record.** Beside it, same name, `.meta.toml`. It carries the exact request URL with every parameter, the capture time with time zone, the HTTP status, the service and layer id, the record count, and any sanity check that tripped.

**The index.** `project-sh16/cache/INDEX.md`, generated. One line per cached response, with its date and URL. **This is the file you point at on stage** when you say the captures are from September 20th.

Two rules behind that:

- **The response stays untouched** because the sidecar holds the stamp. The moment you write metadata *into* the response, "this is real data the server really sent" stops being true, and that sentence is load-bearing for your session.
- **The cache never expires on its own.** `--mode live` is the only refresh. A cache that quietly re-fetches on the morning of October 8th is a hazard, not a feature.

---

## What is left after this

Only the output schema, field by field. It needs Q18 settled first, because a swappable parcel source changes how a parcel identifies itself.

I will draft that schema in full for you to redline rather than ask you open questions about it. Answer these three and that is the last round.


---

**RICK ANSWERS ROUND 3.** Verbatim.

**Rick:**

Q17) Your recommendation
Q18) Nevermind for this, let's just stick to Bexar county.
Q19) Your recommendation


---

**THE SCHEMA DRAFT, AND THE END OF THE FRONTIER.** Verbatim.

**The agent:**

Noted — **Bexar only**. That kills the whole config-file idea from Q18, which is a real simplification.

One judgment call I am making rather than asking: I will keep the Bexar field names in **one named block at the top of the parcel module**, not scattered through the code. Same behaviour today, but swapping counties later is a small edit instead of a hunt. Costs nothing now.

The frontier is down to one item. Here is the schema draft. **Redline the shape, not every field name** — the full field list goes in the spec file.

---

## The output file

One JSON file. Eleven top-level blocks.

```
schema_version

run             the header — who ran what, when, and how
alignment       what file you gave me and what I made of it
corridor        the buffered ribbon
roadway         facts about the road itself (existing ROW width, lanes, traffic)
services        one entry per service called — the honesty block
control         NGS marks + TxDOT control points
row_maps        sheet count, date range, control sections
parcels         the rows
corridor_flags  things that belong to no single parcel
warnings        every sanity check that tripped
```

### `parcels` — the row

```
id                    AcctNumb, or synthetic
id_source             which of those two
owner, situs, legal_description, legal_acres, property_use
acres_in_corridor     how much of it is actually inside
fraction_in_corridor
txdot_owned           true/false
roe_required          yes | no | unknown
screened_for          [ list of flag types actually checked ]
flags                 [ ... ]
max_lead_time_days    the one number that drives scheduling
lead_time_driver      which flag sets that number
```

### A `flag` on a parcel

```
type                  school | cemetery | railroad | pipeline | church | federal | historic
relation              on | adjacent
distance_ft           only when adjacent
name                  the feature's own name
source_service        which service said so
screenable            true
lead_time_days        14
lead_time_source      HSC § 711.041
lead_time_url         the link
```

---

## Four things I want you to look at

**1. `screened_for` is how `unknown` stays different from `no`.**
A parcel lists which flag types were actually checked *for it*. Anything not on that list is unknown, not clear. If the schools service died and the run stopped, the parcels already written say so on their own. This is ADR 0001 made real instead of promised.

**2. `not_screenable` sits in `run`, not on every parcel.**
Gated access and livestock go in the header once — type plus reason, "no public source." Stamping a fake flag onto 400 parcels would bury it. One prominent entry, and it also prints on the rendering.

**3. `acres_in_corridor` is separate from `legal_acres`.**
A 200-acre ranch clipped by a 300-ft corridor is not a 200-acre problem. Screening should say how much of each parcel is actually in play, because that number is what a crew-day estimate hangs off.

**4. `max_lead_time_days` plus `lead_time_driver`.**
One number per parcel, and the name of the flag that set it. That is the column you sort by to find what delays the job, and the driver name is there so nobody has to guess why.

---

## Where I am being cautious

`roe_required` defaults to **`unknown`**, not `yes`. It only says `no` for parcels the TxDOT-owned layer confirms. Texas has no self-executing entry right — Tex. Occ. Code § 1071.3585 says a surveyor *may seek* a court order. I am not going to have a tool assert a legal conclusion about access to someone's land from a parcel polygon.

---

**Say "yes" and I write the spec, or redline any of the above.** Once you sign off, the frontier is empty and I write `docs/corridor-screen/spec.md`, add it and the ADR to the site nav, and commit.


---

**RICK APPROVES THE DRAFT.** Verbatim.

**Rick:**

yes


---

**THE GRILLING ENDS.** Verbatim.

**The agent:**

Frontier is empty. Writing the spec now.
