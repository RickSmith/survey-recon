# The crew safety services

**What we use them for:** finding the nearest hospital, ambulance service, fire
or EMS station and police station for a corridor — and how far each one is.

This is the only block in the output that nobody prices. Every other part of a
screening run answers a bid question. This one answers a party chief's question,
asked before the truck leaves the yard: **if somebody gets hurt out here, where
do we go.**

Written under [issue #18](https://github.com/RickSmith/survey-recon/issues/18).
Every endpoint below was queried live on 2026-09-13 and returned real results.

---

## Read this part first

**Every distance on this sheet is a straight line.** Not a drive time, not a
road distance. The line does not know about the river with no crossing, the
freeway with no turnaround, or the locked gate on the ranch road — and an
ambulance does. Two miles on this sheet can be a twenty-minute drive.

**This is a screening aid. It is not a safety plan.** The tool finds published
points and measures straight lines to them. It does not know opening hours,
whether a hospital has an emergency department, whether an ambulance service
runs at night, or what mutual-aid agreement covers the county line. It has never
been near the corridor. The party chief makes the call.

Both of those are notes in the output file itself, not only on this page,
because the person who needs them is standing on a road rather than reading
documentation.

---

## The services

All four are layers on the same USGS server the school and cemetery flags
already use.

```
https://carto.nationalmap.gov/arcgis/rest/services/structures/MapServer
```

| Kind | Layer | Name on the service |
|---|---|---|
| Hospital | **14** | `Hospitals/Medical Centers` |
| Ambulance | **15** | `Ambulance Services` |
| Fire and EMS | **16** | `Fire Stations/EMS Stations` |
| Police | **18** | `Police Stations` |

| | |
|---|---|
| Published by | U.S. Geological Survey |
| Shape they return | one point per place |
| Paging cap | 2,000 |
| Key or account | none |
| Field list | identical on all four |

---

## Trap one: every layer exists twice, and the copies are identical

The service publishes two group layers — `Labels` at 0 and `Features` at 35 —
and **every feature layer appears once under each**. Hospitals are layer 14 and
also layer 49. Ambulance services are 15 and also 50. Fire and EMS are 16 and
also 51. Police stations are 18 and also 53.

Read live on 2026-09-13, both copies of all four answered **the tool's own
25-mile envelope around the SH16 corridor** — `-99.105, 29.1204` to
`-98.1843, 29.9365` — with the same count:

| Kind | Lower layer | Count | Upper layer | Count |
|---|---|---|---|---|
| Hospital | 14 | 33 | 49 | 33 |
| Ambulance | 15 | 33 | 50 | 33 |
| Fire and EMS | 16 | 140 | 51 | 140 |
| Police | 18 | 57 | 53 | 57 |

Those are the same four counts quoted under *How "nearest" is worked out*
below, because it is the same box.

So this is a trap that does not bite — but only because it was checked. Both
are plain point feature layers with the same fields. The tool uses the lower
set, which is what [spec section 6](../corridor-screen/spec.md) names and what
the school and cemetery flags on this same server already use.

## Trap two: EMS is two layers, and asking one of them answers half the question

USGS splits it. `Ambulance Services` is layer 15 and `Fire Stations/EMS
Stations` is layer 16, and on the SH16 corridor they return **different
places**: the nearest ambulance service is Alamo Area Ambulance, and the
nearest fire or EMS station is Helotes Fire Department. Neither is a subset of
the other.

Issue #18 asks for "nearest EMS." Asking only one of the two layers would have
answered that with half the data, so both are asked and both are reported,
separately rather than merged.

## Trap three: the field names are answered in a different case than they are published

The same trap [the flag services](flag-services.md) page records for the school
and cemetery layers on this exact server. The fields are published as
`PERMANENT_IDENTIFIER`, `NAME`, `ADDRESS` and answered as
`permanent_identifier`, `name`, `address`. A plain dictionary lookup finds
nothing, raises nothing, and every hospital comes out unnamed.
`arcgis.attribute` is what handles it.

## `LOADDATE` is a real date field, so it arrives as milliseconds

Same trap as TxDOT's ROW map sheet dates, written up on
[the ROW map sheets page](row-map-sheets.md): ArcGIS sends a real date field as
milliseconds since 1970, and on Windows the obvious way to read one raises an
error on any value before 1970. `arcgis.from_epoch_ms` is the one function both
services read their dates through — it was written for the ROW sheets and moved
when this service turned out to need it too.

**It matters here for a different reason.** `LOADDATE` is the day USGS loaded
the record, **not** the day anybody confirmed the place is still there. On the
SH16 corridor those dates run from **2016 to 2025**. A fire station that closed
in 2017 is still in a record loaded in 2016. The date is carried into every
place as `source_load_date` and the reader decides.

---

## How "nearest" is worked out

**A box around the corridor, 25 miles by default.** Much wider than every other
extent in the tool, and deliberately so. Every other step asks what is *in* the
corridor; this one asks where the nearest help is, and the nearest hospital to a
rural corridor is not in the corridor. A box sized to the ribbon would find
nothing, and that nothing would read as an answer.

An envelope rather than a line and a distance, for the reason written up on
[the flag services](flag-services.md) page: asked with a polyline and a
distance, **this exact server** buffered into the wrong county and answered
without erroring.

25 miles is chosen to be wrong in the safe direction. On SH16 the answers are
identical at 5 miles and at 15, so it is far more than urban Bexar needs. In
West Texas a smaller number would report a corridor as having no hospital when
what happened is that nobody looked far enough. Change it with
`--safety-search-miles`.

At 25 miles this corridor returns 33 hospitals, 33 ambulance services, 140 fire
or EMS stations and 57 police stations — all well under the 2,000 cap.

### Nearest to the line is not nearest to the crew

A corridor is miles long, and this one is 8.69 miles. So every place carries
**three** straight-line distances: to the nearest point of the centerline, to
the start of the corridor, and to the end.

The SH16 run shows exactly why:

| | |
|---|---|
| Nearest hospital | Audie L Murphy Veterans Affairs Hospital |
| Distance to the centerline | **2.05 mi** |
| Distance from the corridor's south end | **2.05 mi** |
| Distance from the corridor's north end | **7.99 mi** |

A crew working the north end that read only "2.05 miles" would be wrong by
nearly six miles. One number would have been tidier and would have been wrong at
one end.

### Three answers per kind, never two

| What happened | What the file says |
|---|---|
| Places found | `nearest`, plus the two behind it in `others` |
| Service answered, nothing inside the radius | `nearest: null`, the kind named in `not_found_within_the_radius`, beside the radius searched |
| Service never asked — a blocked host | the kind named in `not_checked`, and reported nowhere as absent |

The middle row is the one that matters. "None within 25 miles" and "there is no
hospital" are different claims, and only one of them is checkable. The bottom
row is the same `unknown` against `no` rule this repo applies everywhere — and
here the cost of getting it wrong is a crew that believes it has no cover.

---

## What the SH16 corridor returns

Read live on 2026-09-13, searching 25 miles.

| Kind | Nearest | To the line | Address |
|---|---|---|---|
| Hospital | Audie L Murphy Veterans Affairs Hospital | 2.05 mi | 7400 Merton Minter Boulevard, San Antonio |
| Ambulance | Alamo Area Ambulance | 0.08 mi | 5706 Mobud Drive, San Antonio |
| Fire and EMS | Helotes Fire Department | 0.08 mi | 12951 Bandera Road, Helotes |
| Police | Leon Valley Police Department | 0.06 mi | 6400 El Verde Road, Leon Valley |

Helotes Fire Department is on Bandera Road, which is SH16 itself.

### Every one of those responses is on disk

Captured on 2026-09-13 and committed, under
`project-sh16/cache/usgs-structures-hospitals/`,
`.../usgs-structures-ambulance/`, `.../usgs-structures-fire-ems/` and
`.../usgs-structures-police/` — the query and the layer's own field list for
each. The `.meta.toml` beside every response carries the capture time, the
exact request URL and every parameter of the request, so the numbers above can
be checked rather than taken.

The cache is there so a run works on a conference network that may not, and so
this page can be read against the bytes the server actually sent. It is not
there to make a demo look like a live call: `--mode cache-only` says in the run
header that it made no network calls at all.

---

## The fields

| Output field | Service field | Notes |
|---|---|---|
| `name` | `NAME` | |
| `address`, `city`, `state`, `zipcode` | `ADDRESS`, `CITY`, `STATE`, `ZIPCODE` | A name with no address is a name somebody has to look up on a phone that may have no signal |
| `distance_from_centerline_mi` | — | Straight line to the nearest point of the centerline. What the places are ranked by |
| `distance_from_start_mi`, `distance_from_end_mi` | — | Straight lines to each end of the corridor |
| `longitude`, `latitude` | the point geometry | |
| `source_load_date` | `LOADDATE` | Milliseconds. The day USGS loaded the record, not the day anybody checked |
| `usgs_id` | `PERMANENT_IDENTIFIER` | |

The layers also publish `FTYPE`, `FCODE`, `ADMINTYPE`, `SOURCE_ORIGINATOR`,
`GNIS_ID` and `POINTLOCATIONTYPE`. `ADMINTYPE` was null on every hospital read
around this corridor, so none of them is asked for.

---

!!! note "Three differences from the specification, amended 2026-09-13 on [PR #57](https://github.com/RickSmith/survey-recon/pull/57)"
    **Section 10 gained a top-level block.** Until the ruling its list held ten
    keys and no `crew_safety`. It is a new top-level block rather than a field
    inside an existing one, which is exactly what
    [PR #56](https://github.com/RickSmith/survey-recon/pull/56) established gets
    section 10 raised explicitly. It now names it.

    **Police was not in section 6.** It listed this server's layers as
    "Cemeteries, Historic, Hospitals, Ambulance, Fire and EMS, Schools — 2, 11,
    14, 15, 16, 23," with no police row.
    [Issue #18](https://github.com/RickSmith/survey-recon/issues/18) asks for
    "nearest hospital, nearest EMS, nearest police" in as many words, so layer
    18 is called. Section 6 now carries it, and its row is split in two because
    the flags and the safety sheet are different steps asked different
    questions.

    **Hospitals and EMS are a separate output, not flags.** Section 5 put them
    in step 6, among the flags that hang off a parcel. Issue #18 says this "is
    a different output from the flagged parcel list. It answers a field-crew
    safety question, not a bid question." They are step 9 now, writing their
    own `crew_safety` block and attached to no parcel.

    **One section 8 check is deliberately not applied.** Section 8 asks that
    "any part of every returned record falls within the half-width plus a
    stated margin." That test is right for a parcel and wrong for this sheet: a
    hospital two miles off the centerline is a correct answer, and doubting it
    for being outside the ribbon would be a warning that teaches the reader to
    ignore warnings. What *is* applied is
    `checks.check_records_in_requested_extent`, which tests each record against
    the 25-mile box that was actually asked about — and that one matters here
    more than anywhere, because its documented failure case is this very
    server returning schools in Fredericksburg and Kerrville for a query whose
    geometry stopped inside Bexar County. An earlier pass of this ticket
    skipped it on a confusion between the two checks. That was wrong and the
    review caught it.

    All three followed the ticket rather than the section, and were raised
    rather than made quietly. Amending a settled specification is not the
    agent's call — the precedent is `AcctNumb` on
    [PR #52](https://github.com/RickSmith/survey-recon/pull/52), `NPMS` on
    [PR #53](https://github.com/RickSmith/survey-recon/pull/53), the control
    blocks on [PR #54](https://github.com/RickSmith/survey-recon/pull/54) and
    the ROW map block on
    [PR #56](https://github.com/RickSmith/survey-recon/pull/56). All four were
    raised on the pull request and ruled on by Rick. So were these, on
    2026-09-13 — sections 5, 6 and 10 now say what this page describes.
