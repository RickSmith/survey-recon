# The TxDOT route centerline service

The first thing the tool needs is the road. Not a drawing of it, and not
coordinates: TxDOT's own centerline, asked for by the name TxDOT uses and the
two mile markers you give it, as in "SH16 from Loop 410 to Old Bandera Rd."
This is the service that turns those three things into a line on the ground.
Everything else in a screening run hangs off that line.

Read live on 19 September 2026. There are three traps here. Two of them bite on
the **first thing you type**. The third one took the service away.

---

## The service

```
https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Roadway_Inventory/FeatureServer/0
```

| | |
|---|---|
| Published by | Texas Department of Transportation |
| Layer | **0**, named `Roadway_Inventory` |
| Shape it returns | polylines, **with M values** — see below |
| Coordinate system it stores in | WKID 4269, NAD83 geographic |
| Paging cap | 2,000 |
| Fields | 133, of which the tool asks for three |
| Key or account | none |

**WKID** is Esri's number for a coordinate system, the way an EPSG code is. The
tool asks for `outSR=4326`, which is longitude and latitude, and TxDOT's server
does the conversion.

No datum transformation happens inside this tool, which is deliberate. The TxDOT
Survey Manual states that **"TxDOT will not accept any datum transformations for
control"** ([Survey Manual, Ch. 3](https://www.txdot.gov/manuals/row/ess/index.html)).
Screening is not control work, but a tool that quietly reprojects teaches the
wrong habit.

---

## Trap one: the service you were using can be withdrawn without notice

This tool read `TxDOT_Roadways` until 2026-09-19. On that day the service began
answering `HTTP 200` carrying `error 499: Token Required`, and it is no longer
in the organization's public service list. The other 763 services there still
answer without a token. One service was withdrawn, rather than the account being
locked.

**A token was not an option.** `CLAUDE.md` is blunt about it: anything that
needs an API key does not belong in the attendee path.

Two near-replacements were measured before this one was taken. Both are worth
recording, because both look correct until you use them.

| Layer | Publishes the old three fields | Declares M | Holds M |
|---|---|---|---|
| `TxDOT_Roadways_Unsegmented` | yes | **no** | no |
| `TxDOT_Roadbed_Base` | yes | yes | **every value null** |
| `TxDOT_Roadway_Status` | yes | yes | **every value null** |

The last two carry the same linework as the withdrawn service, agreeing to
5.2e-10 degrees. They would have passed a field list check and then produced
nothing a corridor could be cut from. **A layer can declare measures and hold
none.**

`TxDOT_Roadway_Inventory` names the same three things differently and has the
measures populated. The swap was made under
[work order #180](https://github.com/RickSmith/survey-recon/issues/180).

### The two centerlines are the same line

This was measured rather than assumed. The corridor was cut to DFO 347.7 and
356.367 from each service, and the two results compared:

| | |
|---|---|
| Length from the withdrawn service, captured 2026-09-13 | 8.691209 miles |
| Length from this service, captured 2026-09-19 | 8.691209 miles |
| Largest gap between the two centerlines | **0.00 ft**, both directions |
| Parcels found by the whole run, before and after | **524**, unchanged |

The run's own comparison command reports 35 differences between the two runs.
Two are this swap showing in the output, `alignment.feature_count` and
`alignment.run_count`, which move from 1 to 40. Five are Bexar County parcel
owners that really changed in those six days. The other 28 are capture dates and
cache keys.

---

## Trap two: `SH16` is not a route name, and neither is `SH0016`

Both return **nothing at all**. No error, no rows. Just an empty answer to a
question about a highway that plainly exists.

The name TxDOT publishes is `SH0016-KG`, and the suffix is not decoration. It
is the **roadbed**. This layer publishes five of them around SH16, read live on
2026-09-19:

| Route name | `RDBD_ID` | What it is |
|---|---|---|
| `SH0016-KG` | `KG` | **The main lanes.** What you almost always want |
| `SH0016-LG` | `LG` | The left side, where the highway is divided |
| `SH0016-RG` | `RG` | The right side |
| `SH0016-XG` | `XG` | Frontage road, left |
| `SH0016-AG` | `AG` | Frontage road, right |

The route field is `RIA_RTE_ID` here, not `RTE_NM`. The value is spelled exactly
as it was on the withdrawn service, so the `--route SH0016-KG` you type has not
changed.

!!! note "One difference from the withdrawn service"
    `TxDOT_Roadways` also published `SH0016-CN`, `SH0016-RP` and `SH0016-TA`:
    the connectors, ramps and turnarounds. This layer is a roadway inventory and
    does not carry them.

    Nothing in this tool ever asked for them, and the main lanes are what a
    corridor is screened along. A corridor that needed a ramp would need a
    different service, and this page is where somebody should find that out.

**Check it yourself.** This table is not in the committed capture, because the
tool only ever asks for the one route it was given. So it is reproduced with a
query rather than asserted:

```
POST .../TxDOT_Roadway_Inventory/FeatureServer/0/query
where=RIA_RTE_ID LIKE 'SH0016%'
outFields=RIA_RTE_ID,RDBD_ID
returnGeometry=false
returnDistinctValues=true
```

**Why this matters more than a naming quirk.** A tool that answers an unknown
route name with an empty parcel list, rather than a complaint, would produce a
clean-looking screening of nothing. That is why the alignment step raises
`AlignmentError` on an empty result and stops the run, and why the wrong-file
check prints the corridor length and both end points before any other service is
called. A misread route does not look like a subtle error. It looks like a
four-thousand-mile corridor on line one.

## Trap three: the county fields are numbers, and the tool does not use them

The withdrawn service published a `COUNTY` field holding a single `_` on every
SH16 segment. This layer publishes `CO` and `MSA_CNTY` instead, and both hold
numbers. On all 40 corridor segments, read live on 2026-09-19, `CO` is `15` and
`MSA_CNTY` is `1`.

**We did not confirm which list those numbers index.** No field on this layer
spells a county name, and we did not ask TxDOT.

It does not matter to the run, and that is the part worth keeping. The tool
never filters this service by county. It cuts the route by DFO and then works
from geometry, and `CNTY_NM` on the ROW map and parcel services is where county
names actually live.

---

## The M values are the DFO, and that is what makes the corridor honest

This is the load-bearing fact of the whole alignment step, so it was checked
rather than assumed.

An ArcGIS polyline can carry a third number on each vertex, called an **M
value**, a measure along the line. TxDOT publishes this layer with M values, and
**those M values are the Distance From Origin**.

Read live on 2026-09-19, on the segments the SH16 corridor sits in:

| | |
|---|---|
| Records returned for the corridor window | 40 |
| Vertices returned | 243 |
| First and last M | 347.311, 356.367 |
| Vertices with no M | **none** |

So when the tool cuts the route at 347.7 and 356.367, it is cutting on **TxDOT's
own measure**, at the vertex where TxDOT says that mile is. It is not guessing a
position from coordinates. Ask for it with `returnM=true`.

### Forty records where there used to be one

The withdrawn service answered the SH16 corridor with a single record of 1,800
vertices. This one answers with 40 inventory segments. Both describe the same
line, and the output says which it read: `alignment.feature_count` and
`alignment.run_count` both read 40 where they used to read 1.

That is why the alignment reader sorting its runs by DFO is load-bearing rather
than tidy. A service is free to return its records in any order, and on a single
record you would never find out.

### The route has gaps in it, and they are real

`SH0016-KG` comes back as 1,450 inventory segments. Joined where they touch,
they make seven continuous runs, and those runs do not join up:

```
    0.00 –  28.74
   28.79 –  66.26      ← a 0.05 mile gap
   71.46 – 114.09      ← a 5.2 mile gap
  114.72 – 162.23
  165.21 – 256.79
  256.92 – 356.37      ← the SH16 corridor is in here
  372.76 – 566.14
```

**These are the same seven runs the withdrawn service published**, to the same
two decimal places. That agreement is the strongest evidence that this is the
same linear referencing system under a different name.

A route can leave the state highway system and come back. The alignment reader
keeps each run separate and **never joins across a gap**, because closing one
would invent centerline TxDOT never published. A corridor with a break in it is
legitimate, and `run_count` in the output says how many runs there are.

---

## The fields

133, of which the tool asks for three.

| Field | What it contains |
|---|---|
| `RIA_RTE_ID` | The route name with its roadbed suffix. See trap two |
| `FRM_DFO`, `TO_DFO` | The segment's limits on TxDOT's linear measure, in miles |
| `RDBD_ID` | The roadbed code: `KG`, `LG`, `RG`, `XG`, `AG` |
| `CO`, `MSA_CNTY`, `DI` | Numbers, not names. See trap three |
| `ROW_MIN` | The existing right-of-way width. See below |
| `NUM_LANES`, `SPD_MAX`, `ADT_CUR`, `SUR_W` | Inventory attributes this tool does not read |

The other 120 are inventory detail: traffic counts, pavement, shoulders, tolls,
bridges and housekeeping.

---

## What the tool asks for

```
WHERE RIA_RTE_ID='SH0016-KG' AND FRM_DFO<=356.367 AND TO_DFO>=347.7
outFields  RIA_RTE_ID,FRM_DFO,TO_DFO
returnGeometry  true      returnM  true      outSR  4326
```

Every segment that overlaps the window, cut to it on the M values, with the
surviving runs put in DFO order. The captured response is committed at
`txdot-roadway-inventory/route-sh0016-kg-offset-0`, with its capture date and
the exact request in the `.meta.toml` beside it.

**The field names are not written in the query.** They come from
`sources.ROADWAY_FIELDS`, which is the same mapping the field list check reads.
That is deliberate, and trap one is why.

A half-finished rename would not crash. The field check would pass, because it
reads the source's own list. The query would then ask for columns the layer does
not have, the service would answer with no records, and the run would report a
route that does not reach the corridor.

---

## What this service does not tell you

**Where the ROW actually is.** This is a centerline. The right of way around it
is drawn on the [ROW map sheets](row-map-sheets.md), and the corridor this tool
builds is a **stated** half-width either side of the centerline, never a
measured one.

### One thing it now does tell you, and the tool does not yet read

`ROW_MIN` is on this layer. It holds `180` on all 40 SH16 corridor segments,
read live on 2026-09-19.

The `roadway` block of the output still says `not-screened` and names a
different service, because that was true of the service this one replaced. It is
no longer true of this one. Reading it is a change with its own consequences and
is not made here. See [the capture note](../scenarios/sh16/capture-note.md) for
what that block says today.

---

## Where this came from

This service was worked out under [work order #21](https://github.com/RickSmith/survey-recon/issues/21).

!!! note "Amended 2026-09-19, under [work order #180](https://github.com/RickSmith/survey-recon/issues/180)"
    Until then this page described `TxDOT_Roadways`, which TxDOT withdrew that
    day. Every fact on this page was re-read against the replacement rather than
    carried over.

    Three things changed and are recorded above: the field names, the record
    count for a corridor, and the roadbed list.

    Two things did not change, and checking them is what says the replacement is
    the same road: the seven continuous runs of `SH0016-KG`, and the
    8.691209-mile corridor the run cuts from them.
