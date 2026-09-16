# Data sources

Every number on the [worked example](../scenarios/sh16/index.md) came from a
public map service. This section is the list of them: what each one is, the
exact address the tool asks, what comes back, and the ways each one can answer
wrong without saying so.

That last part is most of what is worth reading here. A service that fails is
easy. A service that answers, promptly and politely, about the wrong county,
is the one that puts a wrong number in an estimate.

All of it is public data. No client data, ever.

## Where the answers are

Every answer a run receives is saved in
[`project-sh16/cache/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/cache),
with its capture date and the exact request beside it. Two kinds of finding on
these pages are **not** in that cache, and each page says so where it matters.
Some came from questions a run never asks, like the roadbed table on the
[TxDOT Roadways](txdot-roadways.md) page, which carries the query to reproduce
it. And two flood-map rows on
[sources we did not use](not-used.md) were carried over from older notes and
never tested by us at all.

Where something could not be confirmed, the page says *not found* and says
where it looked.

## The services, in the order a run asks them

| Step | Source | What it is for | Page |
|---|---|---|---|
| 1 | **TxDOT Roadways** | The centerline, by route name and mile marker | [txdot-roadways.md](txdot-roadways.md) |
| 2 | **Esri geometry service** | Widens the centerline into the ribbon | [arcgis-geometry-service.md](arcgis-geometry-service.md) |
| 3 | **BCAD parcels** | Every tract the ribbon touches. Everything else joins to this | [bcad-parcels.md](bcad-parcels.md) |
| 4 | **The flag services** | Schools, cemeteries, railroads, pipelines | [flag-services.md](flag-services.md) |
| 5 | **NGS datasheets** | Survey marks, and whether anybody could find them | [ngs-datasheets.md](ngs-datasheets.md) |
| 6 | **TxDOT control points** | TxDOT's own monuments | [txdot-control-points.md](txdot-control-points.md) |
| 7 | **TxDOT ROW map sheets** | The record drawings, and how far back they go | [row-map-sheets.md](row-map-sheets.md) |
| 8 | **The crew safety services** | Nearest hospital, ambulance, fire, police | [crew-safety.md](crew-safety.md) |

Two more are not steps of a run:

| Source | What it is | Page |
|---|---|---|
| **NGS Data Explorer** | The one call kept live, so a room can see the wires are real. It is a second NGS service, not a second copy of the first, which is what makes comparing the two worth anything | [ngs-datasheets.md](ngs-datasheets.md) |
| **Sources we looked at and did not use** | Including the elevation service the whole warn-or-stop design was written around | [not-used.md](not-used.md) |

## The ways a service answers wrong

Each of these was found by reading what a service sent back, not by reading
its documentation. They are grouped by *how* the answer went wrong, because
that is the part that carries over to a service nobody here has ever seen.

### It answers about the wrong place

The most expensive kind. No error, no delay, no clue.

- A pipeline service, named in the tool's own scope of work, holds 543 real
  records and none of them in Texas. A Texas query returns nothing and does
  not complain. [The flag services](flag-services.md).
- A USGS layer, asked with a line and a distance, returned schools sixty miles
  up the road for a corridor that stops inside Bexar County. Asked with a
  rectangle instead, it was right every time. [The flag services](flag-services.md).
- A flood layer that ranks high in a search holds Salem, Massachusetts. Recorded
  in older notes and not verified by us. [Sources we did not use](not-used.md).

### It answers, and you asked the wrong thing

- **Layer numbers matter.** A service is a set of numbered tables. TxDOT
  control is table 67; land parcels is table 328. Ask a similarly named service
  for table 0 and it answers with highway segments instead of monuments.
  [TxDOT control points](txdot-control-points.md).
- **`SH16` is not a route name, and neither is `SH0016`.** Both return nothing.
  The name is `SH0016-KG`, and the suffix names the roadbed.
  [TxDOT Roadways](txdot-roadways.md).
- **A unit code that is accepted and answered differently.** `9003` is the
  code for the US survey foot. The parcel query takes it and hands back a
  different corridor. [The geometry service](arcgis-geometry-service.md).
- **Feet in, meters out.** The USGS elevation service takes `US_Feet`, the
  surveyor's own unit, and answers in meters. The number is believable and no
  field says which unit it is in. [Sources we did not use](not-used.md).

### The field is not called what the document says

- NGS's two services spell the same field differently: `LAST_COND` on one,
  `condition` on the other. Ask for the wrong one and you get nothing, with no
  error. [The NGS datasheets](ngs-datasheets.md).
- The parcel field is `Geo_id`, not `AcctNumb`. The scope of work carried one
  Bexar service's field names across to the other. [BCAD parcels](bcad-parcels.md).
- The USGS structures layers publish field names in capitals and answer in
  lower case. [The flag services](flag-services.md).

### The data is not shaped the way you assume

- **Dates that crash rather than come out wrong.** The service sends a date as
  milliseconds since 1970, so every sheet older than 1970 is a negative number.
  On Windows, the obvious way to read one raises an error, on exactly the oldest
  sheets. [ROW map sheets](row-map-sheets.md).
- **An identifier that is not unique.** Six of the 27 SH16 sheets share one map
  id. [ROW map sheets](row-map-sheets.md).
- **A date that may not be a date.** `1900-01-01` appears 368 times in 20,276
  records, and the service never publishes an empty date. Whether it is a
  stand-in could not be confirmed. [ROW map sheets](row-map-sheets.md).
- **A field that exists and is empty.** `COUNTY` is a single `_` character on
  every roadway segment read. [TxDOT Roadways](txdot-roadways.md).
- **Every layer published twice.** Hospitals are table 14 and table 49. Both
  copies returned the same records, so it does not bite. That is known only
  because somebody checked. [The crew safety services](crew-safety.md).

### The host is unreliable, or the data is older than it looks

- **One TxDOT host blocks now and then.** The same address failed and then
  succeeded minutes later. It is why the ROW map step is deliberately last.
  [ROW map sheets](row-map-sheets.md).
- **A host that fails without failing.** The pipeline service once sent back
  *everything is fine* in its status line and *service unavailable* in its body.
  Watched happen on 13 September 2026. A success code is a delivery receipt,
  not an answer. [The flag services](flag-services.md).
- **The parcel service rebuilds weekly**, says so, and publishes the date it was
  last edited. How fast a sale reaches the appraisal roll in the first place is
  a separate question, not confirmed. [BCAD parcels](bcad-parcels.md).
- **USGS records carry the date they were loaded, not the date anybody checked
  the place is still there.** On SH16 they run from 2016 to 2025. A station
  that closed in 2017 is still in a record loaded in 2016.
  [The crew safety services](crew-safety.md).

## Two rules every page here follows

**Cite it, or say you could not confirm it.** A number with consequences has
its source beside it. Where the search found nothing, the page says *not found*
and says where it looked. It never says *does not exist*.

**TxDOT addresses use `txdot.gov`.** Never `onlinemanuals.txdot.gov`. That
site is superseded, search engines still hand it out, and citing it is [one of
the failures the session shows on purpose](../managing-your-agent/the-superseded-manual.md).

## The working notes these came from

[TxDOT research](../txdot-research.md) is the notebook the services were found
in. It is kept as a record of how. Where it disagrees with a page here, the
page is the one that was checked. The elevation service re-test on
[sources we did not use](not-used.md) is a worked example of the two
disagreeing, and of what to do about it.
