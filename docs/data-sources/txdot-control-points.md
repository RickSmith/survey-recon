# The TxDOT primary control points service

**What we use it for:** finding TxDOT's own primary control along the corridor,
beside the NGS marks. A corridor with TxDOT control already set in it is one
where a crew ties into something that exists. A corridor without it is one where
control gets set, and those are different lines on an estimate.

Written under [issue #15](https://github.com/RickSmith/survey-recon/issues/15).
Every endpoint below was queried live on 2026-09-12 and returned real results.

There are four traps on this service. One of them is that the trap this repo
kept warning about is not the trap that is actually here.

---

## The service

```
https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Primary_Control_Points/FeatureServer/67
```

| | |
|---|---|
| Published by | TxDOT. Its published title is **San Antonio District Primary Control Points** |
| Layer | **67**, and it is the only layer on the service |
| Shape it returns | one point per record |
| Paging cap | 2,000 |
| Its own coordinates | WKID 103161 — Texas South Central, in US Survey Feet |
| Records | 766, read 2026-09-12 |
| Key or account | none |

Two pieces of vocabulary, because they are used throughout this page:

- **WKID** — *Well-Known ID.* Esri's number for a coordinate system, the way a
  CSJ is TxDOT's number for a project. `4326` is plain longitude and latitude in
  degrees; `103161` is Texas South Central in US Survey Feet.
- **ArcGIS Online** — Esri's hosted map platform. TxDOT publishes its public map
  services there under an organization account, which is why every TxDOT
  endpoint in this repo begins `services.arcgis.com/KTcxiTD9dsQw4r7Z`.

---

## Trap one: layer 0 does not do what we said it did

[Spec section 6](../corridor-screen/spec.md), [the research
note](../txdot-research.md) and issue #15 all say the same two things. The first
is right: **control is layer 67.** The second is what we checked:

> A tool that assumes layer 0 does not error — it returns the wrong data,
> quietly.

Asked for layer 0 on 2026-09-12, this service answers:

```
HTTP 400 — The requested layer (layerId: 0) was not found.
```

`2025_Land_Parcels` answers the same way about *its* layer 0, and layer 328 is
the only layer there. So on both of the services this repo keeps naming, a
hardcoded layer 0 fails loudly and immediately. It is a good error. You cannot
miss it.

**The trap is real all the same, and it is one step further out.** The thing
that answers quietly is not the wrong *layer*, it is the wrong *service*:

```
https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Control_Sections/FeatureServer/0
```

That exists. It is layer 0. It answers a corridor query without erroring. And it
holds **control sections** — the numbered highway segments in
[CONTEXT.md](https://github.com/RickSmith/survey-recon/blob/main/CONTEXT.md),
like SH16's 0291-09 — which are not survey control and are not monuments. Two
TxDOT datasets, both called "control," one of them a line and one of them a
monument.

An agent told to find "TxDOT control" and reaching for layer 0 lands there and
gets a plausible answer to the wrong question. That is the failure mode issue
#15 described. It just lives in the service name rather than the layer number.

**The guard is the same either way**, and it runs before any query is sent:
`checks.confirm_fields` reads the layer's published field list and refuses to go
on unless the fields we expect are on it. Control sections publish `RTE_NM` and
`CTRL_SECT_NBR` and nothing resembling `MONUMENT_COND_DSCR`, so a run pointed
there stops on its first request.

---

## Trap two: this is one district's control, not the state's

The service's title says **San Antonio District**. The research note records
"766 statewide." Both are accurate and together they mislead.

All 766 records are there. Where they are:

| TxDOT district | Records | Counties they are in |
|---|---|---|
| **15 — San Antonio** | **715** | Bexar 376, Comal 84, Guadalupe 72, Uvalde 62, Wilson 29, Kendall 26, Medina 23, and others |
| 14 — Austin | 22 | Caldwell 12, Hays 6, Travis 3, Gillespie 1 |
| 13 — Yoakum | 14 | Gonzales 13, Lavaca 1 |
| 16 — Corpus Christi | 9 | Karnes 5, Goliad 2, Bee 1, Refugio 1 |
| 22 — Laredo | 4 | Kinney 3, Dimmit 1 |
| 7 — San Angelo | 2 | Edwards 1, Real 1 |

Bexar County alone holds 376 of them. The counties are listed because they are
what makes the district numbers checkable — the service publishes
`TXDOT_DIST_NBR` as a bare number and never spells the district out.

For SH16 in Bexar this is the right dataset and a complete one. **Pointed at a
corridor in Lubbock or Tyler it returns nothing** — and nothing reads as "TxDOT
has set no control here."

That is `unknown` reported as `no`, which CONTEXT.md is bluntest about. The
tool's area is `texas-bexar`, so the limit does not bite today. It is written
here, and in `sources.py`, so that whoever points this at another county reads
it before the count does the damage.

**We did not find a statewide TxDOT primary control service.** Searching TxDOT's
ArcGIS Online organization for "control" on 2026-09-12 returned control sections,
access control, government control and this district service, and no statewide
equivalent. Not found, rather than does not exist — and that is where we looked.

---

## Trap three: `N/A` is this service's blank, and it is a non-empty string

The NGS datasheets service writes a single space where it has nothing, and
trimming whitespace makes that disappear on its own. This service writes the
three characters `N/A` instead:

| Field | Records saying `N/A` (of 766) |
|---|---|
| `NGS_PERM_ID` | 649 |
| `MONUMENT_COND_DSCR` | 24 |
| `MONUMENT_STBL_CD` | 10 |
| `GEOID_NM` | nearly all |
| `PROJ_NBR` | nearly all |

Trimmed, `N/A` is still a non-empty string. So a tool that only trims whitespace
reads a condition of `N/A` as a condition somebody reported, and **a monument
nobody has assessed goes into an estimate as control you have.** The same
consequence as `unknown` against `no`, reached by a different route.

`control.published` is what turns it back into nothing.

The condition values on this service, read live:

| `MONUMENT_COND_DSCR` | Records | What this tool says |
|---|---|---|
| `Good` | 706 | condition reported |
| `N/A` | 24 | condition unknown |
| `Destroyed` | 18 | **monument destroyed** |
| `Unknown` | 9 | condition unknown |
| `Poor` | 9 | condition reported |

**`Destroyed` is kept apart from the NGS `MARK NOT FOUND`.** They cost a crew
the same trip, but they are different claims — one says somebody looked and
could not find it, the other says it is gone — and the second is the stronger
statement. Merging them would lose which of the two TxDOT actually said.

`Good` and `Poor` are reported and left alone. What `Poor` is worth to a
particular crew is the sealing surveyor's call, not this tool's.

---

## Trap four: the same monument, twice

The service holds **766 records carrying only 492 distinct station names.** 274
names appear twice, which accounts for 548 of the 766 records.

On the SH16 corridor this comes out as **four records naming two monuments**.
The pairs sit about half a foot apart, with different object ids and different
control sheets attached.

A crew drives to the monument, not to the record. Reporting four where there are
two doubles the control an estimator believes is already set, and that is a
discount on a price nobody chose to give.

So the output reports both numbers — `points_in_corridor` counts records,
`distinct_stations` counts monuments — and **drops neither record.** All 274
duplicated pairs agree on condition, so there is no call to be made about which
record to believe, only a count to be honest about.

---

## The control sheets are attachments, not a link field

The research note lists `SRVY_CTRL_DCMNT_ADDR` as "(PDF link)".

**Read on 2026-09-12, that field is null on all 766 records.** `PDF_Filename`
does carry a name — `SCP_32.pdf` — but it is a bare filename, and TxDOT
publishes no base address anywhere to hang it on. Neither field gets a reader to
the document.

The sheet is an **attachment**. The layer answers `hasAttachments: true`, and
one call to `queryAttachments` resolves every point in a corridor at once:

```
.../FeatureServer/67/queryAttachments?objectIds=10,11,12&f=json
```

which answers with an attachment id per record, and the document itself is at:

```
.../FeatureServer/67/{objectid}/attachments/{attachmentid}
```

Confirmed for `SCP_32.pdf` on 2026-09-12 and cached with every other response.

This matters for the same reason the NGS datasheet link does. `Destroyed` is the
beginning of a decision, not the end of one, and the sheet carries the to-reach
description, the adjustment date and the scale factors the decision gets made
from.

---

## The fields we read, and why

| Output field | Service field | Why it is on the row |
|---|---|---|
| `station` | `STATN_NM` | The identifier. This service publishes no PID of its own |
| `condition` | `MONUMENT_COND_DSCR` | The field the whole block exists for |
| `recovery` | *derived* | `monument destroyed`, `condition unknown` or `condition reported` |
| `ngs_pid` | `NGS_PERM_ID` | Where a TxDOT monument and an NGS mark are the same monument. Real on 98 of 766 |
| `last_recovered` | `LAST_RCOV_DT` | Set on only 14 of 766 records |
| `marker` | `MRKR_DSCR` | What the monument physically is, e.g. `Aluminum Cap in Concrete` |
| `stamping` | `MONUMENT_STAMPING_TXT` | What is stamped on it |
| `stability` | `MONUMENT_STBL_CD` | TxDOT's stability code |
| `quality_level` | `TXDOT_QLTY_LEVEL_CD` | TxDOT's control quality code. `2` on 764 of 766, `3` on the other two. **What the code means is not found** — see below |
| `monument_logo` | `MONUMENT_LOGO_TYPE_NM` | Whose disk it is, e.g. `TxDOT Alum Disk` |
| `units` | `UOM_NM` | The units for the coordinates, elevation and intervisible distance. `US Survey Feet` on all 766 |
| `geoid` | `GEOID_NM` | The geoid model. `N/A` on effectively every record — see the datum gap below |
| `route` · `county` · `district` | `RTE_NM` · `CNTY_NM` · `TXDOT_DIST_NBR` | Where TxDOT files the monument |
| `pdf_filename` | `PDF_Filename` | The control sheet's filename, e.g. `SCP_32.pdf`. A bare name with no address — see above |
| `intervisible_station` | `INTERVSBL_STATN_NM` | **TxDOT requires primary control in intervisible pairs.** Set on 752 of 766 |
| `intervisible_distance` | `INTERVSBL_DSTNCE_MS` | How far the partner is, in `UOM_NM` units |
| `northing` · `easting` · `elevation` | `STATN_NORTHING_MS` · `STATN_EASTING_MS` · `STATN_EL` | Grid coordinates, in `UOM_NM` units |
| `grid_scale_factor` · `elevation_factor` · `combined_scale_factor` | `STATN_GRID_SCL_FCTR_MS` · `STATN_EL_FCTR_MS` · `STATN_COMBN_SCL_FCTR_MS` | **TxDOT requires all control coordinates in surface and grid both.** These convert between them |
| `spc_zone` | `STATE_PLN_ZN_NM` | `4204` is Texas South Central |
| `horizontal_datum` · `vertical_datum` | `HRZNTL_DATUM_NM` · `VERT_DATUM_NM` | Reported exactly as spelled — see below |
| `published_latitude` · `published_longitude` | `STATN_LAT` · `STATN_LON` | The service's own degrees, held against the geometry it returned |
| `to_reach` | `STATN_LOCN_DSCR` | How to find it on the ground, in TxDOT's own words |
| `control_sheet_url` | *resolved* | The attachment, per the section above |

**The scale factors are reported, never applied.** The Survey Manual is blunt
that **"TxDOT will not accept any datum transformations for control"**
([Survey Manual, Ch. 3 — Control
Points](https://www.txdot.gov/manuals/row/ess/index.html)), and a screening run
is not control work. A tool that quietly reprojects is a tool that teaches the
wrong habit.

The same chapter is the source for the two other TxDOT requirements this page
leans on: that **"all control coordinates will be provided in surface and
grid"**, and that primary control is set in **intervisible pairs**.

### What `TXDOT_QLTY_LEVEL_CD` means is not found

The service publishes `2` on 764 of its 766 records and `3` on the other two.

Survey Manual Ch. 3 gives primary control as **Level 2A** and secondary as
**Level 3**. This service publishes a bare `2`, with no `A`. Whether the two
numbering schemes are the same scheme is not something the service says.

**We could not confirm it.** We looked in the Survey Manual chapter list, which
does not mention this field, and in the layer's own metadata, which carries no
description and no coded-value list. So the code travels into the output exactly
as published, and no estimate here rests on a mapping this tool guessed.

### The datum spellings are inconsistent, and are reported as they came

| Field | Values, as published |
|---|---|
| `HRZNTL_DATUM_NM` | `NAD83` (759), `NAD 83` (7) |
| `VERT_DATUM_NM` | `NAVD88` (753), `NAVD 88` (7), `Assumed` (3), `NGVD29` (3) |
| `STATE_PLN_ZN_NM` | `4204` (756), `4204 - South Central` (7), `4203` (3) |

Three records report an **assumed** vertical datum and three report **NGVD29**.
Those are not NAVD 88, and an estimator reading a corridor count would never see
that if the tool had normalized the spellings. They are carried through exactly
as the service wrote them.

This sits alongside the datum gap recorded in [the research
note](../txdot-research.md): the April 2026 Survey Manual names no NAD 83
realization, no epoch and no geoid model. `GEOID_NM` on this service says `N/A`.

---

## The projection trap, and the check that catches it

This layer stores its geometry in **WKID 103161** — Texas South Central, in US
Survey Feet. Ask it for features without `outSR=4326` and it answers with
coordinates like `x: 2166836.612`. That is a real position, correctly returned,
in the units it was stored in. **Nothing errors.** The tool then reads it as a
longitude, every point lands far outside the corridor, and the corridor comes
back with no control in it.

Every query this tool sends carries `inSR=4326` and `outSR=4326`, which
`_extent_query` already did for every other service here.

The layer also publishes `STATN_LAT` and `STATN_LON` as plain attributes, always
in degrees. So the service answers the same question twice, in two ways, and
`checks.check_published_position` holds one against the other. Two independent
pieces of geometry agreeing is the strongest thing a screening run can say for
itself — the same argument the parcel check makes on
[PR #52](https://github.com/RickSmith/survey-recon/pull/52).

On the SH16 run the two agree to about three feet on every point.

---

## What SH16 returns

Run on 2026-09-12, 300 ft half-width, `SH0016-KG` DFO 347.7 to 356.367:

| | |
|---|---|
| Returned from the box around the corridor | 8 |
| Records inside the 300 ft ribbon | 4 |
| **Distinct monuments** | **2** |
| `Destroyed` | 0 |
| Condition unknown | 0 |
| Condition `Good` | 4 records |

The two monuments are `Z0151105` and `Z0151225`, both aluminum caps on rods,
both quality level 2, both about 95–108 ft off the centerline, and both carrying
a control sheet PDF.

The box is wider than the ribbon, so "8 returned, 4 used" is a normal and honest
pair of numbers. The honesty block in the output carries both.

!!! note "This is fewer than the research note predicted, and here is every step"
    [The research note](../txdot-research.md) records "TxDOT Primary Control
    Points in corridor — **18**." The tool reports 4. Neither number is wrong;
    they are answers to three different questions, and the whole ladder was
    re-queried on 2026-09-12 so that no step has to be taken on trust.

    | What was asked | Records | Distinct stations |
    |---|---|---|
    | The research bounding box `-98.66,29.45,-98.56,29.56` | **18** | 11 |
    | The box around this corridor's alignment, grown by the 300 ft half-width | **8** | 4 |
    | Inside the 300 ft ribbon itself | **4** | **2** |

    **18 → 8 is two different rectangles.** The research box was drawn over the
    general area before there was an alignment to work from. It reaches east to
    longitude −98.56 and south to latitude 29.45, both of which are off this
    corridor, and it stops short of the corridor's own western end at −98.69. It
    overlaps the corridor without being it.

    **8 → 4 is the box against the ribbon**, and that gap is normal and is
    reported on every service asked about a box: the box is a rectangle and the
    corridor is a ribbon inside it. The honesty block carries both numbers.

    **4 → 2 is [trap four](#trap-four-the-same-monument-twice)** — four records
    naming two monuments.

    The tool's number is the one with a stated half-width attached to it, and
    the half-width is stated on every run precisely so the count can be argued
    against a figure a person chose.

---

## Cached responses

Every response is on disk under `project-sh16/cache/txdot-primary-control-points/`,
with the exact request URL, the capture date, the HTTP status and the record
count beside it:

| What | Cache key |
|---|---|
| The layer's own description, including its field list | `txdot-primary-control-points-layer-67-me__8b04fd67b764` |
| The corridor query | `txdot-control-offset-0__b994285d5935` |
| The control sheet attachments | `txdot-control-attachments__f04e379578c8` |
