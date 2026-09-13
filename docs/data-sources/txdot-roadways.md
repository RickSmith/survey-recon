# The TxDOT Roadways service

**What we use it for:** the corridor's centerline. You give the tool a route
name and two Distance From Origin numbers — "SH16 from Loop 410 to Gibeaut Rd"
— and this is the service that turns those three things into a line on the
ground. Everything else in a screening run hangs off that line.

Written under [issue #21](https://github.com/RickSmith/survey-recon/issues/21).
Read live on 2026-09-13.

There are two traps here and both bite on the **first thing you type**.

---

## The service

```
https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Roadways/FeatureServer/0
```

| | |
|---|---|
| Published by | Texas Department of Transportation |
| Layer | **0** |
| Shape it returns | polylines, **with M values** — see below |
| Coordinate system it stores in | WKID 102100 / 3857, Web Mercator |
| Paging cap | 2,000 |
| Last edited | 2026-09-01, per the service's own `editingInfo` |
| Key or account | none |

**WKID** is Esri's number for a coordinate system, the way an EPSG code is. This
service stores in Web Mercator; the tool asks for `outSR=4326` — longitude and
latitude — and TxDOT's server does the conversion.

No datum transformation happens inside this tool, which is deliberate. The TxDOT
Survey Manual states that **"TxDOT will not accept any datum transformations for
control"** ([Survey Manual, Ch. 3](https://www.txdot.gov/manuals/row/ess/index.html)).
Screening is not control work, but a tool that quietly reprojects teaches the
wrong habit.

---

## Trap one: `SH16` is not a route name, and neither is `SH0016`

Both return **nothing at all**. No error, no rows. Just an empty answer to a
question about a highway that plainly exists.

The name TxDOT publishes is `SH0016-KG`, and the suffix is not decoration. It
is the **roadbed**. Around SH16 there are eight of them, read live on
2026-09-13:

| Route name | `RDBD_TYPE` | What it is |
|---|---|---|
| `SH0016-KG` | Single Roadbed | **The main lanes.** What you almost always want |
| `SH0016-LG` | Left Roadbed | The left side, where the highway is divided |
| `SH0016-RG` | Right Roadbed | The right side |
| `SH0016-XG` | Left Frontage | Frontage road, left |
| `SH0016-AG` | Right Frontage | Frontage road, right |
| `SH0016-CN` | Connector | |
| `SH0016-RP` | Ramp | |
| `SH0016-TA` | Turnaround | |

So the route argument for the SH16 corridor is `SH0016-KG`: **state highway 16,
single roadbed**. Zero-padded to four digits, then the roadbed code.

**Check it yourself.** Neither this table nor the `COUNTY` finding below is in
the committed capture — the tool only ever asks for the one route it was given —
so both are reproduced with a query rather than asserted:

```
POST .../TxDOT_Roadways/FeatureServer/0/query
where=RTE_NM LIKE 'SH0016%'
outFields=RTE_NM,RDBD_TYPE,DES_DRCT,COUNTY
returnGeometry=false
```

**Why this matters more than a naming quirk.** A tool that answers an unknown
route name with an empty parcel list, rather than a complaint, would produce a
clean-looking screening of nothing. That is why the alignment step raises
`AlignmentError` on an empty result and stops the run, and why the wrong-file
check prints the corridor length and both end points before any other service is
called. A misread route does not look like a subtle error — it looks like a
four-thousand-mile corridor on line one.

## Trap two: the `COUNTY` field is `_` on every segment

The layer publishes a `COUNTY` field. On every SH16 segment read on 2026-09-13
its value is a single underscore.

```
WHERE RTE_NM='SH0016-KG' AND COUNTY='Bexar'   →  0 rows
```

So you cannot narrow this service by county, and a query that tries gets an
empty answer rather than an error — the same shape of silent wrong answer as
trap one. The tool never filters on it. It cuts the route by DFO and then works
from geometry, and `CNTY_NM` on the ROW map and parcel services is where county
names actually live.

We did not establish **why** the field is empty. It may be populated on other
routes, or reserved, or abandoned. We looked at the SH16 segments and at the
layer's own field list; we did not ask TxDOT.

---

## The M values are the DFO, and that is what makes the corridor honest

This is the load-bearing fact of the whole alignment step, so it was checked
rather than assumed.

An ArcGIS polyline can carry a third number on each vertex, called an **M
value** — a measure along the line. TxDOT publishes this layer with M values,
and **those M values are the Distance From Origin**.

Read live on 2026-09-13, on the segment the SH16 corridor sits in:

| | |
|---|---|
| Segment attributes | `BEGIN_DFO` 256.923, `END_DFO` 356.367 |
| Vertices returned | 1,800 |
| First and last M | 256.923, 356.367 |
| M increasing all the way along | yes |

So when the tool cuts the route at 347.7 and 356.367, it is cutting on **TxDOT's
own measure**, at the vertex where TxDOT says that mile is — not guessing a
position from coordinates. Ask for it with `returnM=true`.

### The route has gaps in it, and they are real

`SH0016-KG` comes back as seven segments, and their DFO ranges do not join up:

```
    0.00 –  28.74
   28.79 –  66.26      ← a 0.05 mile gap
   71.46 – 114.09      ← a 5.2 mile gap
  114.72 – 162.23
  165.21 – 256.79
  256.92 – 356.37      ← the SH16 corridor is in here
  372.76 – 566.14
```

A route can leave the state highway system and come back. The alignment reader
keeps each run separate and **never joins across a gap**, because closing one
would invent centerline TxDOT never published. A corridor with a break in it is
legitimate, and `run_count` in the output says how many runs there are.

---

## The fields

Seventeen, of which the tool asks for three.

| Field | What it contains |
|---|---|
| `RTE_NM` | The route name with its roadbed suffix. See trap one |
| `BEGIN_DFO`, `END_DFO` | The segment's limits on TxDOT's linear measure, in miles |
| `RTE_PRFX`, `RTE_NBR`, `RTE_SFX` | The name broken into its parts — `SH`, `0016`, and the suffix |
| `RDBD_TYPE` | The roadbed, spelled out: `Single Roadbed`, `Ramp`, `Left Frontage` … |
| `DES_DRCT` | Designated direction. `Southbound` on every SH16 segment read |
| `SYSTEM` | `On` for on-system highway |
| `COUNTY` | `_` on every segment read. See trap two |
| `MAP_LBL`, `ZOOM`, `RTE_GRID`, `GID`, `EXT_DATE` | Cartography and housekeeping |

---

## What the tool asks for

```
WHERE RTE_NM='SH0016-KG' AND BEGIN_DFO<=356.367 AND END_DFO>=347.7
outFields  RTE_NM,BEGIN_DFO,END_DFO
returnGeometry  true      returnM  true      outSR  4326
```

Every segment that overlaps the window, cut to it on the M values, with the
surviving runs put in DFO order. The captured response is committed at
`txdot-roadways/route-sh0016-kg-offset-0`, with its capture date and the exact
request in the `.meta.toml` beside it.

---

## What this service does not tell you

**The existing right-of-way width.** That is `ROW_MIN` on
`Roadway_Inventory_2023`, a different TxDOT service, which this tool does not
yet call. The `roadway` block of the output says `not-screened` and names it
rather than leaving a blank — see [the capture note](../scenarios/sh16/capture-note.md).

**Where the ROW actually is.** This is a centerline. The right of way around it
is drawn on the [ROW map sheets](row-map-sheets.md), and the corridor this tool
builds is a **stated** half-width either side of the centerline, never a
measured one.
