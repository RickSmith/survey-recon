# Data sources

Every public service this tool calls, with its exact endpoint, the fields it
actually returns, and its quirks — **including the ones that return a plausible
wrong answer instead of an error.**

All of it is public data. No client data, ever, and the repo stays public.

**Every service the tool calls** was queried live and returned real results, and
every response a run receives is committed in
[`project-sh16/cache/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/cache)
with its capture date and the exact request beside it.

Two things are **not** in that cache, and each page says so where it matters.
Some findings come from queries a run never makes — the roadbed table on
[TxDOT Roadways](txdot-roadways.md) is one, and it carries the query to
reproduce it. And the sources on
[sources we did not use](not-used.md) include two FEMA rows **we never tested at
all**, carried across from older notes.

Where something could not be confirmed, the page says "not found" and says where
we looked.

---

## The services, in the order a run calls them

| Step | Source | Page |
|---|---|---|
| 1 | **TxDOT Roadways** — the centerline | [txdot-roadways.md](txdot-roadways.md) |
| 2 | **Esri geometry service** — builds the corridor polygon | [arcgis-geometry-service.md](arcgis-geometry-service.md) |
| 3 | **BCAD parcels** — the spine everything joins to | [bcad-parcels.md](bcad-parcels.md) |
| 4 | **The flag services** — schools, cemeteries, railroads, pipelines | [flag-services.md](flag-services.md) |
| 5 | **NGS datasheets** — survey marks and their condition | [ngs-datasheets.md](ngs-datasheets.md) |
| 6 | **TxDOT control points** — layer 67 | [txdot-control-points.md](txdot-control-points.md) |
| 7 | **TxDOT ROW map sheets** — the historical record drawings | [row-map-sheets.md](row-map-sheets.md) |
| 8 | **The crew safety services** — nearest hospital, EMS, police | [crew-safety.md](crew-safety.md) |

Two more that are not steps of a run:

| Source | What it is | Page |
|---|---|---|
| **NGS Data Explorer** | The one call kept genuinely live, so a session can show the wires are real. A second NGS endpoint rather than a second source — which is exactly what makes the cross-check worth anything | [ngs-datasheets.md](ngs-datasheets.md) |
| **Sources we looked at and did not use** | Including the USGS elevation service the whole warn-versus-stop design was written around | [not-used.md](not-used.md) |

---

## The traps, by kind

Most of what is worth reading here is on this list. They are grouped by **how**
they fail, because that is the part that transfers to a service this repo has
never seen.

### It answers, and the answer is about the wrong place

The most expensive kind. No error, no delay, no clue.

- **A pipeline service holding only Pennsylvania.** Named in this repo's own
  specification. 543 real records, zero in Texas, and a Texas query returns zero
  rows without complaint — [the flag services](flag-services.md)
- **A USGS layer buffering into the wrong county.** Asked with a polyline and a
  distance it returned schools sixty miles up the road, for a query whose
  geometry stopped inside Bexar. Asked with an envelope it was correct every
  time — [the flag services](flag-services.md)
- **A flood layer holding Salem, Massachusetts**, which ranks high in a search.
  Recorded in older notes and **not verified by us** —
  [sources we did not use](not-used.md)

### It answers, and you asked the wrong thing

- **Layer numbers are load-bearing.** TxDOT control is layer 67 and land parcels
  is layer 328. But the trap this repo kept warning about is not the one that is
  actually there — layer 0 *hard-errors* on that service. The quiet wrong answer
  comes from a **differently named service** that does answer at layer 0 and
  holds highway segments rather than monuments —
  [TxDOT control points](txdot-control-points.md)
- **`SH16` is not a route name. Neither is `SH0016`.** Both return nothing at
  all. The name is `SH0016-KG`, and the suffix is the roadbed —
  [TxDOT Roadways](txdot-roadways.md)
- **A unit code that is accepted and answered differently.** `9003` is the EPSG
  code for the US survey foot, and the parcel query takes it and hands back a
  different corridor — [the geometry service](arcgis-geometry-service.md)
- **The same silence on a second, unrelated service.** The USGS elevation
  endpoint takes `US_Feet`, the surveyor's own unit, and answers in meters. The
  answer is a believable number, and no field anywhere says which unit it is —
  [sources we did not use](not-used.md)

### The field is not called what the document says

- **`LAST_COND`, not `condition`.** NGS's two endpoints spell the same field
  differently, and asking for the wrong one returns nothing and raises nothing —
  [the NGS datasheets](ngs-datasheets.md)
- **`Geo_id`, not `AcctNumb`.** The specification carried one Bexar service's
  field names across to the other — [BCAD parcels](bcad-parcels.md)
- **Published in capitals, answered in lower case.** The USGS structures layers
  do this, and a plain dictionary lookup finds nothing —
  [the flag services](flag-services.md)

### The data is not shaped the way you assume

- **Dates that crash rather than come out wrong.** ArcGIS sends a real date
  field as milliseconds, so every ROW sheet older than 1970 is a negative
  number. On Windows the obvious way to read one raises an error, on
  exactly the oldest sheets — [ROW map sheets](row-map-sheets.md)
- **An identifier that is not unique.** Six of the 27 SH16 sheets share one
  `ROW_MAP_ID` — [ROW map sheets](row-map-sheets.md)
- **A date that may not be a date.** `1900-01-01` appears 368 times in 20,276
  records, with no empty dates anywhere. Whether it is a placeholder **could not
  be confirmed** — [ROW map sheets](row-map-sheets.md)
- **A field that exists and is empty.** `COUNTY` is a single `_` character on
  every roadway segment read — [TxDOT Roadways](txdot-roadways.md)
- **Every layer published twice.** Hospitals are layer 14 *and* layer 49. Both
  copies returned identical counts and identifier sets, so it does not bite.
  That is known only because somebody checked —
  [the crew safety services](crew-safety.md)

### The host is unreliable, or the data is older than it looks

- **`maps.dot.state.tx.us` blocks intermittently.** The same URL failed and then
  succeeded minutes later. It is why the ROW step is deliberately last —
  [ROW map sheets](row-map-sheets.md)
- **A host that fails without failing.** The pipeline service answered
  `HTTP 200` carrying a `503`, so the status line said everything was fine while
  the body said nothing was. Watched happen on 2026-09-13. A `200` is a delivery
  receipt, not an answer — [the flag services](flag-services.md)
- **The parcel service rebuilds weekly**, says so itself, and publishes the date
  it was last edited. How fast a transfer reaches the appraisal roll in the first
  place is a separate question we did not confirm —
  [BCAD parcels](bcad-parcels.md)
- **USGS records carry the date they were loaded, not the date anybody checked.**
  On the SH16 corridor they run from 2016 to 2025 —
  [the crew safety services](crew-safety.md)

---

## Two rules these pages follow

**Cite it, or say you could not confirm it.** Numbers with consequences carry a
source next to them. Where we looked and found nothing, the page says "not
found" and says where it looked. It never says "does not exist."

**TxDOT URLs use `txdot.gov`.** Never `onlinemanuals.txdot.gov`, which is
superseded and which search engines still surface.

---

## The working notes these came from

[TxDOT research](../txdot-research.md) is the notebook the endpoints were found
in. It is kept as a record of how, and where it disagrees with a page here,
**the page is the one that was checked.** The 3DEP re-test in
[sources we did not use](not-used.md) is a worked example of the two
disagreeing — and of what to do about it.
