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

**2278 is Bexar County's own State Plane zone**, in the units a Texas surveyor
works in. The tool asks for `outSR=4326` and lets the server convert, for the
reason [spec section 3.2](../corridor-screen/spec.md) records: TxDOT will not
accept datum transformations for control, and a screening tool that quietly
reprojects teaches the wrong habit. If you want the parcels back in State Plane,
ask this service for 2278 and it will give them to you directly.

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

**What "weekly" does not mean.** It does not mean the ownership is current to
the week. An appraisal district's roll lags the courthouse — a deed filed on
Friday is not in the roll on Monday. This service is the right place to find out
**how many tracts** and **roughly who**; it is not a title search and the tool
says so.

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
| `property_use` | `state_cd` | The Texas state property-use code, two characters — `F1`, `A1`, `C1`. A code, not a description, and this tool does not decode it |

### What the use codes look like on this corridor

Read off the committed capture, all 530 records:

| Code | Parcels |
|---|---:|
| `F1` | 325 |
| `A1` | 103 |
| `C1` | 59 |
| `E1` | 10 |
| `F3` | 9 |
| `B2` | 8 |
| `B1` | 2 |
| *(blank)* | 10 |

**We do not translate these and neither does the tool.** They are the Texas
Comptroller's property classification codes, and the authoritative list is the
Comptroller's, not ours. Guessing that `F1` means one thing and putting that
guess in front of a surveyor pricing a job is exactly the kind of confident
wrongness this repo is about. The code is reported as the code it is.

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
  those four rows read `id: "-1022"` with `id_source: "PropID"` and `owner:
  null` — not `owner: " "`. A negative identifier is a signal to go and look,
  and it is left visible rather than tidied away.

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
| `LandSqft` | The district's land area in square feet. **Equals `legal_acre` exactly** — see below |
| `ParcelArea` | The polygon's own area in square feet. **Does not equal `LandSqft`** |
| `Shape__Area`, `Shape__Length` | Esri's own geometry measures |

**The mailing address really is somewhere else.** One parcel on Bandera Road,
read live on 2026-09-13:

| | |
|---|---|
| `Situs` | 9355 BANDERA RD, SAN ANTONIO, TX 78250 |
| `Owner_Name` | LARAMIE FORDS LANDING LTD |
| Owner's mailing address | GERICHO ATRIUM, 851 BAYWAY BLVD APT 805, **CLEARWATER, FL 33767** |

An out-of-state owner is a real fact about a job — notice takes longer and a
right of entry is a phone call to Florida. The tool does not carry the field
anyway, and that is a deliberate omission rather than an oversight: this repo is
public, and mailing addresses of private individuals are not something a
teaching demo prints on a projector. A firm running this for real adds it in one
line of `sources.BEXAR_PARCEL_FIELDS`.

### Three acreages, and two of them disagree

The service publishes the same tract's size three ways, and a surveyor will want
to know which is which. On the two Bandera Road parcels above:

| | Parcel 1 | Parcel 2 |
|---|---|---|
| `legal_acre` | 4.515 ac | 5.4422 ac |
| `LandSqft` | 196,673 | 237,062 |
| `legal_acre` × 43,560 | **196,673** | **237,062** |
| `ParcelArea` | 199,205 | 239,734 |
| `ParcelArea` in acres | 4.573 ac | 5.504 ac |
| Difference from `legal_acre` | **+1.3 %** | **+1.1 %** |

So `LandSqft` is `legal_acre` in square feet — the same number twice, not a
second measurement. `ParcelArea` is the **polygon's** area, and it runs about
one percent larger than the district's acreage on both.

**We did not establish why**, and one percent on a five-acre tract is a
twentieth of an acre, which is not nothing to somebody pricing a taking.
Digitizing tolerance, a different basis for the legal acreage, and the
projection the area was computed in are all plausible and none is confirmed
here. Where we looked: these two records and the service's own field list. The
tool carries `legal_acres` through as the district's number, and measures
`acres_in_corridor` itself from the polygon — it never mixes the two.

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
