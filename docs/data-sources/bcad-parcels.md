# The BCAD parcels service

**What we use it for:** the parcels in the corridor. This is the **spine** of a
screening run — every flag hangs off a parcel, the lead times are per parcel,
and nothing useful exists in the output before this service answers. On SH16 it
returns 530 records, 524 of which land in the corridor.

Written under [issue #21](https://github.com/RickSmith/survey-recon/issues/21).
Read live on 2026-09-13.

---

## The service

```
https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/BCAD_Parcels/FeatureServer/0
```

| | |
|---|---|
| Published by | City of San Antonio, from Bexar Appraisal District data |
| Layer | **0**, named `BCAD Parcels` |
| Shape it returns | polygons, one per parcel |
| Coordinate system it stores in | WKID 102740 / **2278** — NAD 83 Texas South Central, US survey feet |
| Paging cap | 2,000 |
| Key or account | none |

**2278 is NAD 83 Texas South Central**, the State Plane zone Bexar County falls
in — the zone covers a good deal more of Texas than this one county — and it is
in the units a Texas surveyor works in.

The tool asks for `outSR=4326` and lets the server convert. It performs no datum
transformation of its own, which is not only convenience: the TxDOT Survey
Manual states that **"TxDOT will not accept any datum transformations for
control"** ([Survey Manual, Ch. 3](https://www.txdot.gov/manuals/row/ess/index.html)).
Screening is not control work, but a tool that quietly reprojects teaches the
wrong habit. If you want the parcels back in State Plane, ask this service for
2278 and it hands them over directly.

---

## How fresh it is, from the service's own mouth

The layer's description says so in one sentence:

> Basic parcel attribute information. Data provided by Bexar County Appraisal
> District (`box.bcad.org`). **Updated weekly.**

And the service publishes when it was last actually edited, which is a firmer
answer than "weekly":

| | |
|---|---|
| `dataLastEditDate` | **2026-09-07** |
| Our capture | 2026-09-13 |

So the parcels in the committed capture are as BCAD had them on **7 September
2026**, six days before we asked. That is a fact about the data, not about our
cache, and it is worth saying on stage: a screening run is never more current
than the appraisal roll behind it, whether you cache it or not.

**What "weekly" does not mean.** It does not mean the ownership shown is current
as of this week. A weekly refresh is how often the *service* is rebuilt from the
appraisal roll; how quickly a transfer reaches that roll in the first place is a
separate question, and **we did not confirm it**. Where we looked: this
service's own description and `editingInfo`. We did not ask the appraisal
district and we have cited no statute.

What the field is safe for is what the tool uses it for: **how many tracts** the
corridor crosses, and **roughly who** to start asking. It is not a title search,
the tool does not present it as one, and an RPLS pricing acquisition will go to
the county records regardless.

---

## The trap: two Bexar parcel services, and the specification named the other one's fields

Both [spec section 10](../corridor-screen/spec.md) and
[the research notes](../txdot-research.md) originally listed the parcel fields
as `AcctNumb`, `Owner`, `LglDesc`, `LglAcres` and `PropUse`.

**Those field names are real. They belong to the other service** — Bexar
County's own at `maps.bexar.org` — not to this one, which the specification
tells the tool to prefer. Both were read on 2026-09-12 and the two field lists
compared. This service publishes `Geo_id`, `PropID`, `Owner_Name`, `legal_desc`,
`legal_acre` and `state_cd`.

A tool that asked this service for `AcctNumb` would get nothing back and raise
nothing — every parcel unidentified, quietly. The code follows the service
rather than the document, `sources.BEXAR_PARCEL_FIELDS` records which name went
where, and the difference was raised on
[PR #52](https://github.com/RickSmith/survey-recon/pull/52) rather than patched
over. Rick ruled on 2026-09-13 and section 10 now carries the real names.

---

## The fields

Twenty-three, of which the tool asks for seven.

### What the tool reads

| Output field | Service field | What it actually contains |
|---|---|---|
| `id` | `Geo_id` | The appraisal district's geographic identifier — what a parcel should be quoted by |
| `id` (fallback) | `PropID` | An integer property id. Used when `Geo_id` is blank, which happens on road slivers and similar |
| `owner` | `Owner_Name` | The name on the roll. See the lag note above |
| `situs` | `Situs` | The property's own address, in full — `9355 BANDERA RD, SAN ANTONIO, TX 78250`. Not just the street line |
| `legal_description` | `legal_desc` | As the district writes it — `NCB 17919 BLK 8 LOT 28 (CONCORD ANNEXTN) CAMINO BANDERA`. **NCB** is New City Block, San Antonio's own block numbering. 254 characters, so a long description is cut |
| `legal_acres` | `legal_acre` | The district's acreage. **Not measured by us** — see below |
| `property_use` | `state_cd` | A Texas state property-use code — usually two characters, `F1`, `A1`, `C1`, but **not always**: one parcel on this corridor carries a bare `C`. A code, not a description, and this tool does not decode it |

### What the use codes look like on this corridor

Every one of the 530 records in the committed capture, counted:

| Code | Parcels | | Code | Parcels |
|---|---:|---|---|---:|
| `F1` | 325 | | `B1` | 2 |
| `A1` | 103 | | `O1` | 1 |
| `C1` | 59 | | `C` | 1 |
| `E1` | 10 | | `F2` | 1 |
| *(blank)* | 10 | | `D1` | 1 |
| `F3` | 9 | | | |
| `B2` | 8 | | **total** | **530** |

**We do not translate these and neither does the tool.** They are Texas state
property-use codes; **we did not confirm which published list is authoritative
or what any individual code means**, and we have not cited one, so nothing here
decodes them. Where we looked: the service's own field list and the values it
returns. Guessing that `F1` means one thing, and putting that guess in front of
a surveyor pricing a job, is exactly the confident wrongness this repo exists to
warn about. The code is reported as the code it is.

Every row also says in `id_source` which of the three identifiers it got —
`Geo_id`, `PropID` or `synthetic` — because only the first two can be quoted
back to Bexar County.

### A blank here is a space, not a null, and that has bitten

Ten of the 530 records come back with **every text field set to a single
space** and a **negative `PropID`** — `-1020`, `-1021`, `-1022`, `-1060`. Four of
them fall in the corridor.

Two things follow, and both are visible in the committed output:

- **A null check does not find them.** `WHERE Situs IS NOT NULL` matches them
  happily, because `' '` is not null. This is the same trap the NGS datasheets
  service sets with its condition field, and the reason `arcgis.attribute`
  treats a whitespace-only string as an absent value rather than a value.
- **The tool falls back and says so.** With `Geo_id` blank it uses `PropID`, so
  those rows read `id: "-1022"` with `id_source: "PropID"` and `owner: null` —
  not `owner: " "`. A negative identifier is a signal to go and look, and it is
  left visible rather than tidied away.
- **And `PropID` is not unique across them.** The ten records carry only four
  distinct values: `-1021` appears six times, `-1060` twice, `-1020` and `-1022`
  once each. So a negative id identifies a *kind* of record, not a parcel, and
  two rows in the output can share one. Nothing downstream keys on it.

What they actually are we did not establish. Road slivers and similar
non-taxed remnants would fit the pattern, and the tool does not guess. It
reports four parcels it can only quote by a negative property id, which is
enough for somebody to ask Bexar County about them.

### What it also publishes, and we do not ask for

| Field | What it actually contains |
|---|---|
| `addr_line1` … `addr_line3`, `addr_city`, `addr_state`, `zip`, `zip4`, `country_cd` | The **owner's mailing address**, which is not the property address. Checked, not assumed — see below |
| `Exemptions` | An exemption code where one applies. `EX-XV` on the church parcel read; a single space on the commercial one beside it |
| `neighborho` | The district's neighborhood code, e.g. `15090` |
| `GBA_Living` | Gross building area, in square feet, as a string |
| `LandSqft` | The district's land area in square feet. Close to `legal_acre` × 43,560 but **not reliably equal to it** — see below |
| `ParcelArea` | The polygon's own area in square feet. Disagrees with both, often by several percent — see below |
| `Shape__Area`, `Shape__Length` | Esri's own geometry measures |

**The mailing address really is somewhere else.** One commercial parcel on
Bandera Road, read live on 2026-09-13, sits at a San Antonio `Situs` and is
owned from an address in **Clearwater, Florida**.

That is a real fact about a job. An out-of-state owner means notice takes
longer, and a right of entry is a phone call to another state rather than a
visit. It is the kind of thing an estimator wants to know early.

**The tool does not carry the field, and this page does not print one.** The
street address is left out deliberately — the point lands without it, and a
public teaching repo putting owners' mailing addresses on a projector is not a
habit worth teaching even where the record is public. A firm running this for
real adds the field in one line of `sources.BEXAR_PARCEL_FIELDS`, and then owns
the decision about where that output goes.

### Three acreages, and the two that matter disagree

The service publishes a tract's size three ways, and a surveyor needs to know
which is which. Measured across **2,000 records** read live on 2026-09-13, not
across the handful it is tempting to check:

**`LandSqft` is close to `legal_acre` × 43,560, and not the same number.**

| | |
|---|---:|
| Exactly equal, to within half a square foot | 902 of 2,000 |
| Within one square foot | 1,238 of 2,000 |
| Differing by more than a square foot | **762 of 2,000** |
| Largest difference seen | 213 sq ft |

So they are two roundings of one measurement rather than two measurements — but
they are **not** interchangeable, and a page that told you they were would be
wrong 38 % of the time.

**`ParcelArea` is the polygon's own area, and it disagrees with the district's
acreage by a lot more than you would guess.**

| | |
|---|---:|
| Median difference from `legal_acre` | **+0.65 %** |
| The middle 80 % of parcels | −7.1 % to +13.2 % |
| Full range seen | −100 % to +886 % |

An earlier draft of this page quoted "about one percent larger," from two
parcels. **Across 2,000 records only 21 fall in that band.** The honest summary
is that the GIS polygon and the appraisal acreage routinely disagree by several
percent in either direction, and occasionally by far more.

**Why, we did not establish.** Digitizing tolerance, a different basis for the
legal acreage, road right of way excluded from one and not the other, and the
projection the area was computed in are all plausible; none is confirmed here.
Where we looked: 2,000 records from this service and its own field list.

**What the tool does about it.** It carries `legal_acres` through as the
district's number, and measures `acres_in_corridor` itself from the polygon
against the ribbon. It never mixes the two, and it never presents either as a
survey.

### `legal_acres` is the district's number, not ours

It is carried through as published and never recomputed. Separately, the tool
measures `acres_in_corridor` from the parcel's own outline against the ribbon,
and reports both. They answer different questions: one is what Bexar County
thinks the tract is, the other is how much of it the corridor crosses.

A negative or absurd acreage would mean a unit or a coordinate was misread, so
`checks.check_impossible_acres` looks for it and records a warning rather than
silently using it. It did not trip on SH16.

---

## What the tool asks for

Not a bounding box. A box around SH16 returns roughly 55,000 parcels; the
corridor is a ribbon, not a square. The query passes the alignment as a polyline
with a distance and a unit, and lets the server do the buffering:

```
geometry       the alignment, as an Esri polyline
geometryType   esriGeometryPolyline
distance       300        units  esriSRUnit_Foot
spatialRel     esriSpatialRelIntersects
outFields      Geo_id,PropID,Situs,Owner_Name,legal_desc,legal_acre,state_cd
returnGeometry true       outSR  4326
```

**`returnGeometry=true` is not optional here.** The sanity check that follows
asks whether any part of each returned parcel comes near the corridor, which is
the same question the query was asked. A 189-acre tract clipped by a 600-foot
ribbon belongs in the list and its center point is a quarter of a mile outside,
so testing centers would throw away exactly the parcels that matter most to an
estimate.

The captured response is committed at `bcad-parcels/parcels-offset-0`, with its
capture date and the exact request in the `.meta.toml` beside it.

---

## The unit code that answers wrong rather than erroring

Worth knowing because it belongs to this query. The `units` parameter takes
`esriSRUnit_Foot`. The numeric code `9003` is also "foot" in other Esri
contexts, and the parcel query **accepts it and answers differently**. It is
written up on [the ArcGIS geometry service page](arcgis-geometry-service.md),
which is where the corridor polygon is built and where the same trap lives.

---

## What this service does not tell you

**Whether TxDOT already owns it.** That is `2025_Land_Parcels` layer 328, a
TxDOT service this tool does not yet call, so `txdot_owned` is absent from every
parcel row rather than reported as false.

**Whether you may enter.** Nothing here is a right of entry. A parcel polygon is
not permission, and [spec section 11](../corridor-screen/spec.md) is blunt that
the tool will not assert a legal conclusion about access from one.
