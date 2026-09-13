# Corridor screening — specification

**Status:** settled 2026-09-12, from the grilling on [issue #5](https://github.com/RickSmith/survey-recon/issues/5).
**Amended:** 2026-09-13 — section 6, the pipeline source; section 8, how a returned record is tested against the corridor; section 10, the parcel field names, and nine additions for the flags. See the notes there.
**Scope of work for:** the `corridor-screen/` tool.

A note on words. A **spec** is a scope of work. A **schema** is an agreed field list — the column headings on a parcel table that everybody uses the same way. An **endpoint** is the web address you ask a question of. A **cache** is a saved copy of an answer you already got. Everything else is in [CONTEXT.md](https://github.com/RickSmith/survey-recon/blob/main/CONTEXT.md).

---

## 1. What this does

You give it the centerline of a corridor. It widens that line into a ribbon, asks a fixed list of public map services what is inside the ribbon, and writes out one file: every parcel in the corridor, what about each one costs time, and how many days of notice each of those things needs.

It is a first pass before you price a job. It is desktop reconnaissance, which is what this repo is named for.

## 2. What this does not do

Saying this plainly matters more than the feature list.

- **It does not decide anything.** It reports. An RPLS reads it and decides.
- **It does not touch client data.** Public sources only. Every source is listed in section 6.
- **It does not assert a right of entry.** See section 11.
- **It cannot see gates or livestock.** No public source publishes them. See section 12.
- **It does not produce the bid memo, the parcel table, or the crew-day build-up.** Those are separate jobs that read this file. One fetch, many renderings.

## 3. Inputs

### 3.1 The alignment

The centerline. Five ways to give it:

| Form | How it is read | Notes |
|---|---|---|
| GeoJSON | standard library | already latitude and longitude |
| KML | standard library | KML is always WGS 84 by its own specification |
| KMZ | standard library | a zipped KML; unzipped, then read as KML |
| Shapefile | **our own reader** | see 3.2 |
| Route name + two DFO numbers | one request to TxDOT | `TxDOT_Roadways`, fields `RTE_NM`, `BEGIN_DFO`, `END_DFO` |

**A bounding box is never an input.** A box around SH16 returns roughly 55,000 parcels. A corridor is a ribbon, not a square.

### 3.2 The shapefile reader

Shapefile is the only one of the five formats the Python standard library cannot open. Everything else in this tool is standard library, so this one format decides whether the tool needs anything installed.

**We write the reader ourselves.** About sixty lines, reading only the polyline shape types. The tool then installs nothing at all.

The projection comes free. A shapefile's `.prj` companion is a plain text file describing its coordinate system — commonly Texas State Plane in US survey feet, not latitude and longitude. ArcGIS services accept that text directly as the input spatial reference. We forward it untouched and let their server do the conversion.

No projection library, and no datum transformation performed by us. That second point is not just convenience: the TxDOT Survey Manual states plainly that **"TxDOT will not accept any datum transformations for control"** ([Survey Manual, Ch. 3](https://www.txdot.gov/manuals/row/ess/index.html)). Screening is not control work, but a tool that quietly reprojects is a tool that teaches the wrong habit.

### 3.3 Rules when the file is not what we hoped

| Case | Rule |
|---|---|
| Several line features in one file | merge into one alignment; do **not** join the gaps — a corridor with a break is legitimate |
| Polygons or points | reject, and name the accepted forms |
| Z or M values present | drop them; screening is flat |
| Empty file | reject |

### 3.4 The wrong-file check

Before any service is called, the tool prints, and records in the output:

- the corridor length in miles
- both end point coordinates
- a link to a public web map centered on the corridor
- **a rendering** of the alignment and its buffer (see section 9)

This is the cheapest protection in the whole tool. A misread shapefile does not look like a subtle error. It looks like a four-thousand-mile corridor on line one.

### 3.5 Other inputs

| Input | Default | Why |
|---|---|---|
| Half-width | **300 ft** | stated, never derived. The parcel count must always be arguable against a number a person chose |
| Adjacent distance | **100 ft** | how close a feature must be to earn an `adjacent` flag |
| Run mode | `cache-first` | `live`, `cache-first`, or `cache-only` |
| Output directory | — | where the JSON, the renderings and the cache are written |

The existing right-of-way width is read from `Roadway_Inventory_2023` (`ROW_MIN`) and **reported as a fact about the road**. It does not set the buffer.

### 3.6 The command line

```bash
corridor-screen --alignment sh16.kmz --half-width 300 --mode cache-first --out project-sh16/
```

## 4. The corridor

The buffer is done by the service, not by us. The ArcGIS query operation accepts a line, a distance and a unit, and applies the buffer itself. That keeps a geometry library out of the tool.

We additionally request the buffer polygon **once** and cache it, so there is a real corridor shape to draw, to stamp into the output, and to hand to somebody later.

**One risk, stated openly.** The 3DEP failure recorded in [our research](../txdot-research.md) was a server quietly ignoring a parameter. If a server ignores the distance, we get a whole county back and it looks fine. Section 8 is how that gets caught.

## 5. Order of operations, and why

```
1  Reachability ping        every service, seconds, before any real work
2  Read the alignment       plus the wrong-file check (3.4)
3  Buffer                   fetch and cache the corridor polygon
4  Parcels                  the spine everything joins to
5  Roadway facts            ROW_MIN, lanes, traffic
6  Flags                    schools, cemeteries, railroads, pipelines, hospitals, EMS, historic
7  Control                  NGS marks, TxDOT primary control points
8  ROW map sheets           the least reliable host, deliberately last
```

**The reason, recorded.** Parcels are the spine — every flag joins to a parcel, so nothing useful exists before step 4. Control and ROW sheets are independent of the parcel list, so a failure there costs the least, and they go last.

**The ping exists because last is not soon enough to find out.** Our research recorded `maps.dot.state.tx.us` failing and then succeeding minutes later. A five-second ping tells you the host is blocking today *before* you spend ninety seconds building a run you are about to abandon. The ping result is recorded in the output.

## 6. Services called

Every endpoint below was queried live on 2026-09-12 and returned real results. Full detail and field lists are in [TxDOT research](../txdot-research.md).

| Purpose | Service | Layer |
|---|---|---|
| Parcels | `BCAD_Parcels` via CoSA, on `services.arcgis.com/g1fRTDLeMgspWrYp` | 0 |
| TxDOT-owned land | `2025_Land_Parcels` | **328** |
| Roadway facts | `Roadway_Inventory_2023` | 0 |
| Route geometry | `TxDOT_Roadways` | 0 |
| Control | `Primary_Control_Points` | **67** |
| Control | NGS Data Explorer `/radial`, and the NGS datasheets feature service | 1 |
| ROW sheets | `ROW_Maps_CL_2017` on `maps.dot.state.tx.us` | 0 |
| Cemeteries · Historic · Hospitals · Ambulance · Fire and EMS · Schools | USGS `structures` | 2 · 11 · 14 · 15 · 16 · 23 |
| Railroads | USGS `transportation` | 38 |
| Pipelines | **TPMS** `rrc_public/tpms` on `gis.rrc.texas.gov`, the Railroad Commission of Texas | 0 |

**Layer numbers are load-bearing.** Control is layer 67. TxDOT land parcels is layer 328. A tool that assumes layer 0 does not error — it returns the wrong data, quietly. Section 8 checks this at startup.

!!! note "Amended 2026-09-13, on [PR #53](https://github.com/RickSmith/survey-recon/pull/53)"
    Until then the pipeline row read `NPMS NPMS_Pipelines_2022`, on
    `services.arcgis.com/G4S1dGvn7PIgYd6Y`. That service is real, and it holds no
    Texas data at all.

    Read live on 2026-09-12 while building
    [#17](https://github.com/RickSmith/survey-recon/issues/17): **543 records in
    total, zero in Texas, zero in Bexar County**, and every sample record in
    Chester County, Pennsylvania. Its own extent sits around longitude −76,
    latitude 40. A Texas query returns zero records and no error — which reads
    exactly like "there are no pipelines here."

    **NPMS** is the National Pipeline Mapping System, run by the federal Pipeline
    and Hazardous Materials Safety Administration. **TPMS** is the Texas Pipeline
    Mapping System, run by the Railroad Commission of Texas. Two bodies, two
    datasets, similar acronyms, and only one of them covers Texas. That
    similarity is most of how the wrong one got into this section.

    TPMS holds **490,375 records**, 598 of them within a box around Bexar County,
    and a genuine zero inside the SH16 corridor. So "no pipelines on this
    corridor" is now a checked answer from a source that plainly holds data
    there, rather than an empty answer from a source that holds none.

    This is the second time this repo's research has named a national-sounding
    service that covers one distant county. The first was `FEMA_Flood_Zones` on
    services9 — *"ranks high in search but is Salem, MA only. Easy trap"* — which
    was recorded in [TxDOT research](../txdot-research.md) **before** the pipeline
    row was written. Writing a trap down is not the same as not falling into it.

    Rick ruled on 2026-09-13 that this section should name the source that holds
    Texas data. The full comparison is in
    [the flag services page](../data-sources/flag-services.md).

**Scope.** Bexar County only, for now. The Bexar field names live in one named block at the top of the parcel module rather than scattered through the code, so pointing this at another county later is an edit and not a rewrite. Building a general source-configuration system is explicitly out of scope.

## 7. When a service is dead

**A dead service stops the run.**

1. **Retry three times automatically**, with a growing wait. Most blocks are momentary.
2. **Then ask, if a person is there.** Retry, skip this service, or abort. If nobody is at the keyboard, exit non-zero rather than wait. A tool that hangs forever in an unattended run is a broken tool.
3. **The ping is the better place to stop.** It runs first and costs seconds, so the decision happens up front rather than ninety seconds in.

**A stopped run still writes its output**, marked `incomplete`, naming what finished and what stopped. The responses already fetched are already cached, so re-running in `cache-first` mode resumes almost free.

## 8. When a service answers, but the answer is wrong

**A sanity check records a warning. It never halts a run.** The reasoning is in [ADR 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md) and it is deliberate.

The checks are blunt on purpose:

| Check | What it catches |
|---|---|
| Field list confirmed at startup, before any query | the wrong layer — the "layer 67, not 0" trap. **Hard error**, because it is a configuration bug and free to catch |
| Record count is exactly 500, 1000 or 2000 | a paging cap mistaken for an answer |
| More parcels than a corridor this long can hold | the distance was ignored and we got the county |
| **Any part** of every returned record falls within the half-width plus a stated margin of the centerline | the spatial filter failed |
| Impossible values — negative acreage, a recovery date in the future | a coordinate or a unit was misread |

Every warning that trips is written into the output next to the data it doubts. **The tool does not hide it and does not fix it.**

!!! note "Amended 2026-09-13, on [PR #52](https://github.com/RickSmith/survey-recon/pull/52)"
    That fourth check used to read "every returned **point** falls inside the
    corridor." A point is the wrong thing to test a parcel against, and the
    corridor is the wrong thing to test it with.

    A parcel is a polygon, and the query asked which parcels *intersect* the
    corridor. So the honest test of that answer is whether any part of the
    parcel comes near the corridor — not where its center point sits. The
    parcels this gets wrong are exactly the ones that matter most to an
    estimate: a 189-acre tract clipped by a 600-foot ribbon has its frontage on
    the pavement and its center point a quarter of a mile away.

    **The margin is stated, not derived**, like the half-width beside it, and
    it is settable with `--sanity-margin-ft`. It defaults to **500 ft**, so a
    parcel at the default half-width is doubted only when every part of it is
    more than 800 ft from the centerline. It is slack for a filter that is
    working, not a second corridor.

    Run against SH16 with the margin set to **zero**, the check agrees with the
    CoSA service's own spatial filter on all 530 returned records. That is the
    strongest thing that can be said for it: two independent pieces of geometry,
    same answer.

    The strict "inside the corridor" form stays correct for services that return
    points — NGS marks, TxDOT control — and belongs with the first of those,
    under [#14](https://github.com/RickSmith/survey-recon/issues/14) or
    [#15](https://github.com/RickSmith/survey-recon/issues/15).

## 9. Renderings

**SVG** — a drawing stored as plain text rather than as pixels. Being text, it commits to git and shows a readable diff. It embeds in this site and in the Marp slides. It stays sharp on a projector at any size. It needs nothing installed.

Two are produced:

1. **The quick one**, after reading the alignment, before any service is called. Alignment and buffer only. This is the wrong-file check.
2. **The full one**, at the end. Parcels, flag markers, parcels shaded by how many flags they carry, north arrow, scale bar, corner coordinates, the not-screenable notice, and the run stamp.

There is no basemap — that would mean a network dependency inside the artifact. Instead the tool prints a public web-map link centered on the corridor, so one click confirms the real-world location against real imagery.

## 10. Output, field by field

One JSON file. JSON is a plain text format that both a person and a program can read.

### Top level

```
schema_version   run   alignment   corridor   roadway
services   control   row_maps   parcels   corridor_flags   warnings
```

### `run`

| Field | Meaning |
|---|---|
| `run_id` | stable identifier for this run |
| `started_at`, `finished_at` | ISO 8601, with time zone |
| `status` | `complete` or `incomplete` |
| `stopped_at_service` | empty, or the service that halted the run |
| `mode` | `live`, `cache-first`, `cache-only` |
| `tool_version` | which version produced this file |
| `half_width_ft`, `adjacent_distance_ft` | the two stated distances |
| `sanity_margin_ft` | the third stated distance — how far outside the ribbon a record may sit before the run doubts it. See the section 8 note |
| `area` | `texas-bexar` |
| `not_screenable` | list of type and reason — see section 12 |
| `renderings` | paths to both SVG files |
| `map_link` | public web-map URL centered on the corridor |
| `screened_for` | the flag types this run checked for, run-wide. Built from the services that actually answered, never from the list of types the tool knows about |
| `lead_times` | the number and its citation for each type in `screened_for`, so the file can be checked without this repo beside it |

### `alignment`

| Field | Meaning |
|---|---|
| `source_kind` | `geojson`, `kml`, `kmz`, `shapefile`, `route-dfo` |
| `source_path` | the file given, or the route and its two DFO values |
| `feature_count` | how many line features were merged |
| `length_mi` | the wrong-file check, recorded |
| `start`, `end` | latitude and longitude of both ends |
| `bbox` | the corner coordinates |
| `crs_in` | what the file said its coordinate system was |
| `dropped_z`, `dropped_m` | true if height or measure values were discarded |

### `corridor`

`half_width_ft` · `area_sq_mi` · `bbox` · `polygon_cache_key`, which points at the cached buffer polygon.

### `roadway`

`row_min_ft`, the existing right-of-way width · `num_lanes` · `adt_current`.

### `services` — one entry per service

| Field | Meaning |
|---|---|
| `name`, `url`, `layer_id` | exactly what was asked, and of what |
| `purpose` | `parcels`, `control`, `flag:schools`, and so on |
| `ping` | `ok`, `blocked` or `slow` |
| `ping_ms` | how long that ping took |
| `ping_detail` | why, when a ping came back `blocked` |
| `status` | `ok`, `failed`, `from-cache`, `skipped` |
| `attempts` | how many times it was tried |
| `record_count` | how many records came back |
| `records_used` | flag services only: how many of those were used, and how |
| `cache_files` | relative paths to the saved responses — one per page, since a capped answer is fetched in several |
| `captured_at` | when that response was captured |
| `warnings` | sanity checks that tripped on this service |

This block is the honesty block. It is what lets somebody else decide whether to trust the file.

**`records_used` sits beside `record_count` because the two are rarely equal, and the gap is not a fault.** A flag service is asked about a box drawn around every parcel in the corridor, which is wider than the ribbon, so a school at the far corner of that box is a correct answer to the question that was asked and is simply not this corridor's problem. Recording only the six that were used would make six look like the whole world. The honesty block says "39 returned, 6 used" instead.

### `control`

`ngs_marks` and `txdot_points`, each an array. **The `condition` field is carried through, never dropped** — a mark stamped `MARK NOT FOUND` is visible recovery risk, and it is the whole reason to look. `recovery_risk` counts them.

### `row_maps`

`sheet_count` · `date_range` · `control_sections` · `sheets`, each carrying `MAP_NM`, `ROW_MAP_ID`, `CTRL_SECT_NBR`, `CSJ_NBR`, `MAP_FROM_DT` and `MAP_TO_DT`.

**No field in this service gives a direct PDF link.** You get the sheet count and the identifiers. The drawings still come through the ROW Division or the RPAM viewer. The output says so rather than leaving a blank.

### `parcels` — the rows

| Field | Meaning |
|---|---|
| `id` | `Geo_id`, or `PropID`, or a synthetic identifier |
| `id_source` | `Geo_id`, `PropID` or `synthetic` |
| `owner`, `situs`, `legal_description`, `legal_acres`, `property_use` | as published by the appraisal district |
| `acres_in_corridor` | how much of the parcel is actually inside the ribbon |
| `fraction_in_corridor` | that figure as a proportion |
| `txdot_owned` | true if the TxDOT land layer confirms it |
| `roe_required` | `yes`, `no`, `unknown` — see section 11 |
| `screened_for` | the flag types actually checked **for this parcel** |
| `flags` | see below |
| `max_lead_time_days` | the one number that drives scheduling |
| `max_lead_time_basis` | which days that number counts — `calendar days` or `working days` |
| `lead_time_driver` | which flag set that number |
| `lead_time_not_found` | flag types on this parcel whose lead time could not be confirmed |
| `warnings` | anything doubted about this row |

#### Where each of those comes from

The CoSA service is the one section 6 prefers. These are the fields it publishes.

| Output field | CoSA `BCAD_Parcels` field |
|---|---|
| `id` | `Geo_id`, falling back to `PropID` |
| `owner` | `Owner_Name` |
| `situs` | `Situs` |
| `legal_description` | `legal_desc` |
| `legal_acres` | `legal_acre` |
| `property_use` | `state_cd` — the Texas state property-use code, not a description |

!!! note "Amended 2026-09-13, on [PR #52](https://github.com/RickSmith/survey-recon/pull/52)"
    Until then this section named `AcctNumb` as the parcel identifier, and
    [TxDOT research](../txdot-research.md) listed `Owner`, `LglDesc`, `LglAcres`
    and `PropUse` beside it. Those field names are real, but they belong to the
    **Bexar County** service at `maps.bexar.org` — not to the **CoSA** service
    section 6 tells us to prefer. One service's field list had been carried
    across to the other.

    Both were read again on 2026-09-12 while building the tracer bullet, and the
    tables above are what the preferred service actually publishes. This is the
    first amendment to a settled section of this spec, and it is recorded here
    rather than made quietly, because a spec that changes without saying so is
    not a contract.

    `PropID` is a genuine fallback, not a tidy-up: some records — road slivers
    and the like — publish no `Geo_id`. A parcel with neither gets an identifier
    made from its shape, and `id_source` always says which of the three it got,
    because only the first two can be quoted back to Bexar County.

**`screened_for` is how `unknown` stays different from `no`.** Anything not on that list was not checked, and is never reported as clear. If a service died and the run stopped, the parcels already written say so on their own.

**`lead_time_not_found` sits beside `max_lead_time_days` for the same reason.** A parcel whose only flag is a school has no confirmed number, and a blank there reads as "no delay". It is not clear. It is unmeasured, which is a different thing — the same distinction as `unknown` against `no`, one row further down. A parcel carrying both a cemetery and a school shows **14 calendar days** *and* `school` in the not-found list, because 14 is the longest figure anybody can stand behind and it is not the whole answer.

**`acres_in_corridor` is separate from `legal_acres` on purpose.** A 200-acre ranch clipped by a 300-foot corridor is not a 200-acre problem, and the crew-day estimate hangs off the difference.

### A `flag` on a parcel

| Field | Meaning |
|---|---|
| `type` | `school`, `cemetery`, `railroad`, `pipeline`, `church`, `federal`, `historic` |
| `relation` | `on`, meaning inside the parcel, `adjacent`, or `corridor` — see `corridor_flags` below |
| `distance_ft` | only when `adjacent` |
| `name` | the feature's own name |
| `source_service`, `source_feature_id` | which service said so, and which record |
| `screenable` | true |
| `lead_time_days` | from section 13 |
| `lead_time_basis` | **which days that number counts** — `calendar days` or `working days` |
| `lead_time_days_low` | the bottom of a published range, where the figure is one. `lead_time_days` carries the top |
| `lead_time_confirmed` | false where no figure could be confirmed. Then `lead_time_days` is empty and `lead_time_not_found` is filled |
| `lead_time_statutory` | true for a code section, false for somebody's published procedure. They are different kinds of promise |
| `lead_time_source` | the statutory or procedural citation |
| `lead_time_url` | the link to it |
| `lead_time_verified_on` | the date that link was opened and read |
| `lead_time_driver_detail` | what actually causes the delay, in words |
| `lead_time_note` | the limits on the number — what the surveyor still has to judge |
| `lead_time_not_found` | where we looked, when no figure was confirmed. Begins with the words "Not found" |
| `parcels_crossed` | corridor-level flags only: how many parcels in this corridor it crosses |

`on` and `adjacent` are recorded separately and never merged. A party chief needs to know about both. An estimator must not count both.

**`lead_time_basis` is not optional and is never converted.** Two working days and two calendar days are different promises — [Tex. Util. Code § 251.151(a)](https://statutes.capitol.texas.gov/Docs/UT/htm/UT.251.htm) excludes Saturdays, Sundays and legal holidays, and [Tex. Health & Safety Code § 711.041](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm) does not. Turning one into the other would mean the tool inventing a calendar of Texas legal holidays it does not have and cannot check, so it states the basis and leaves the calendar to the reader. The lead-time table loader refuses a confirmed row that does not say which days.

### `corridor_flags`

Things that cost time but belong to no single parcel — a pipeline easement crossing many of them, a railway crossing the route. Same fields, recorded against the run. Nothing gets quietly dropped for being hard to attach.

There are **two** ways to belong to no single parcel, and both land here:

- A feature on **no** parcel that is still inside the corridor — a pipeline in a road right of way no appraisal district taxes.
- A feature on **many** parcels, which is the pipeline easement named above. It stays on every parcel it touches, because a party chief needs to know which ones, **and** it is recorded once here, because an estimator adding one easement's notice period thirty times has the wrong number. The two records are separate and never merged, for the same reason `on` and `adjacent` are.

How many parcels count as many is **stated, not derived**, like the half-width. It defaults to **5** and is settable with `--corridor-flag-parcels`.

### `warnings`

Every sanity check that tripped, run-wide: `check`, `service`, `severity` — always `warning`, per ADR 0001 — `detail`, and `what_to_do`.

!!! note "Amended 2026-09-13, on [PR #53](https://github.com/RickSmith/survey-recon/pull/53)"
    Nine entries were added to this section when the flags were built under
    [#17](https://github.com/RickSmith/survey-recon/issues/17). **Nothing named
    here before was removed or renamed.**

    They were built first and named here second, which is the wrong way round.
    The tool emitted them, the difference was listed in
    [the flag services page](../data-sources/flag-services.md) rather than
    slipped in, and Rick ruled on 2026-09-13 to keep all nine. This section now
    names them, so the contract and the file agree again.

    | Added | Where | Why |
    |---|---|---|
    | `lead_time_basis` | flag | Two working days and two calendar days are different promises. A bare "days" is what a reader turns into a date and gets wrong |
    | `lead_time_confirmed` · `lead_time_statutory` | flag | #17 asks for "code and section **where it is statutory**." A reader has to be able to tell a statute from a company's published procedure |
    | `lead_time_not_found` | flag, and the parcel row | #17 asks that an unconfirmed lead time say "not found" and say where it looked. On the row it is what stops a school-only parcel reading as clear |
    | `lead_time_days_low` · `lead_time_note` · `lead_time_verified_on` · `lead_time_driver_detail` | flag | The railroad figure is a published **range**; carrying only the planning number hides what it was chosen from. The note and the date are what make a citation checkable a year later |
    | `max_lead_time_basis` | parcel row | Same reason as `lead_time_basis` |
    | `parcels_crossed` | corridor-level flag | The number that stops one easement's notice period being counted once per parcel |
    | `records_used` | services | "39 returned, 6 used" rather than a bare 6 |
    | `screened_for` · `lead_times` | run | The flag types checked run-wide, and the citation for each |
    | `relation: "corridor"` | flag | This section defined `relation` as `on` or `adjacent`, and separately said a corridor flag carries the "same fields". A corridor flag therefore needed some third value |

    Eight of the nine exist to keep a number honest rather than to add a number.
    That is the shape of what this ticket turned out to be: the flags were the
    easy half, and saying exactly how much each figure is worth was the rest.

    **Four more were found while checking this amendment, and they are not from
    #17.** Walking every field in `screening.json` against the tables above
    turned up four the file has carried since earlier work and this section never
    named: `sanity_margin_ft` on the run, from
    [PR #52](https://github.com/RickSmith/survey-recon/pull/52); and `ping_ms`,
    `ping_detail` and `cache_files` on a service, from
    [#13](https://github.com/RickSmith/survey-recon/issues/13). This section had
    said `cache_file`, singular, and the tool has always written a list, because
    a capped answer is fetched one page at a time.

    They are named now. The claim above — that the contract and the file agree
    again — is only worth making if somebody checked, and checking is what found
    these.

## 11. On right of entry

`roe_required` defaults to **`unknown`**. It says `no` only where the TxDOT-owned land layer confirms the parcel.

Texas has no self-executing right of entry for surveyors. **Tex. Occ. Code § 1071.3585** says an RPLS denied permission *may seek* a court order. **Tex. Occ. Code § 1071.358** says an LSLS acting officially *is entitled to* one. Two words apart in the statute book, and worlds apart in practice.

A tool will not assert a legal conclusion about access to somebody's land from a parcel polygon. TxDOT's own procedure is that every request is documented by written letter, and that **oral right of entry is valid for one day and for the one person who received it** ([Survey Manual Ch. 2 §3](https://www.txdot.gov/manuals/row/ess/surveying_procedures/right_of_entry.html)).

## 12. What this cannot see

[CONTEXT.md](https://github.com/RickSmith/survey-recon/blob/main/CONTEXT.md) defines a flagged parcel as one carrying a school, cemetery, railroad, pipeline, **gated access or livestock**.

**No public source publishes gates or livestock.** We kept the definition rather than trimming it, and made the gap visible instead: `run.not_screenable` names both types with the reason, and the rendering prints the notice.

A tool that says "I cannot see this, you must" is more use than one that quietly returns a shorter list.

## 13. Lead times

**The lead-time table is checked-in data, not code.** One row per parcel type, in TOML — a plain text settings format meant for people to read and edit — with a mandatory source column. Python 3.11 reads TOML with nothing installed, and TOML carries comments, which matters when every row needs a citation beside it.

| Type | Driver | Lead time |
|---|---|---|
| Railroad | separate corporate agreement, insurance, flagging | **30–45 days** |
| Cemetery | [Tex. Health & Safety Code § 711.041](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm) — written notice outside owner-set hours | **14 days** |
| Pipeline | [Tex. Util. Code ch. 251](https://statutes.capitol.texas.gov/Docs/UT/htm/UT.251.htm) — notice 14 days to 48 hours before excavation | **48 hr floor** |
| School | district board approval; [Tex. Educ. Code § 22.0834](https://statutes.capitol.texas.gov/Docs/ED/htm/ED.22.htm) background checks where duties are continuing and contact is direct | board cycle plus badging |
| Church | no statute; trustee or vestry authority, monthly meetings | board cycle |
| Federal or tribal | special-use permit; tribal council and BIA. **Not verified** | assume months |
| Gated or agricultural | no statute | not screenable |

Two notes that change the number:

- Chapter 251 defines excavation as mechanised equipment disturbing soil **16 inches or more**, so hand-driven monuments may fall outside it. The table records the floor. The surveyor judges the case.
- A cemetery discovered that was not previously known must be reported to the county clerk within **10 days** ([HSC § 711.011](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm)).

**Federal and tribal lead times are marked not verified.** We looked and did not confirm a figure. That is written as "not found," not as "does not exist."

## 14. Caching

Every response is saved. The network at a conference venue is not something to bet a session on, and a saved response also makes the tool testable offline and hands attendees the real data.

```
project-sh16/cache/
  <service>/
    <readable-name>__<short-hash>.json        exactly the bytes the server sent
    <readable-name>__<short-hash>.meta.toml   the provenance record
  INDEX.md                                    generated, one line per response
```

**The provenance record carries** the exact request URL with every parameter · the capture time with its time zone · the HTTP status · the service name and layer id · the record count · any sanity check that tripped.

**The response file is never edited.** The stamp lives in the sidecar file beside it. The moment you write metadata into a response, "this is real data the server really sent" stops being true — and that sentence is load-bearing.

**The cache never expires on its own.** `--mode live` is the only refresh. A cache that quietly re-fetches on the morning of a session is a hazard, not a feature.

**`INDEX.md` is the file you point at** when you say on stage that the captures are from a particular date. Caching that is disclosed is a demo rig. Caching that is not is something else.

## 15. Not settled here

- The bid memo, the flagged parcel table and the crew-day build-up. Separate work orders, all reading this file.
- Any county but Bexar.
- Elevation and topography. USGS 3DEP timed out on three attempts of four, and returned a silent wrong answer on the fourth. It stays off the critical path.
- TCP(S-1)-08A. The host blocks automated fetch, so it must be pulled by hand. It is the crew-time document, and the traffic-control cost cliff is real: a twenty-minute shot on a 55 mph highway turns a two-person crew into a crew plus a shadow truck with an attenuator.
