# The flag services

**What we use them for:** finding the things on a parcel that cost time — a
school, a cemetery, a railroad, a pipeline — so that a lead time can be attached
to each one.

Written under [issue #17](https://github.com/RickSmith/survey-recon/issues/17).
Every endpoint below was queried live on 2026-09-12 and returned real results.

Two of the four had a trap in them. Both are written up in full, because both
are the kind that answers you rather than erroring at you.

---

## The four services

| Flag | Service | Layer | Shape it returns |
|---|---|---|---|
| School | USGS `structures` on `carto.nationalmap.gov` | **23** | point |
| Cemetery | USGS `structures` on `carto.nationalmap.gov` | **2** | point |
| Railroad | USGS `transportation` on `carto.nationalmap.gov` | **38** | line |
| Pipeline | **TPMS**, Railroad Commission of Texas | 0 | line |

```
https://carto.nationalmap.gov/arcgis/rest/services/structures/MapServer/23
https://carto.nationalmap.gov/arcgis/rest/services/structures/MapServer/2
https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer/38
https://gis.rrc.texas.gov/server/rest/services/rrc_public/tpms/MapServer/0
```

All four are public, need no key and no account, and support paging. All four
cap a single answer at 2,000 records — 1,000 for TPMS — so every query pages
until the server stops setting `exceededTransferLimit`.

**TPMS** is the Texas Pipeline Mapping System, published by the Railroad
Commission of Texas. **NPMS** is the National Pipeline Mapping System, run by
the federal Pipeline and Hazardous Materials Safety Administration; the service
carrying its name on ArcGIS Online is the subject of trap two below.

---

## The fields we ask for, and what they hold

Only these are requested. A service that stops publishing one of them fails the
field-list check before a single query is sent, which is deliberate — see
[spec section 8](../corridor-screen/spec.md).

### USGS `structures`, layers 23 and 2 — schools and cemeteries

| Field | What it holds |
|---|---|
| `NAME` | the school's or cemetery's own name. This is what appears on the flag |
| `PERMANENT_IDENTIFIER` | a stable GUID for the feature. Recorded as `source_feature_id` |
| `FTYPE` | a numeric feature type — `730` for schools, `820` for cemeteries |
| `FCODE` | a finer numeric code — `73003` elementary, `73004` middle, `73005` high |

Geometry comes back as a single `x`/`y` point per record.

**These names are published in capitals and answered in lower case.** See trap
three.

### USGS `transportation`, layer 38 — railroads

| Field | What it holds |
|---|---|
| `name` | the subdivision or yard name. Frequently `null` on short-line track |
| `permanent_identifier` | a stable GUID. Recorded as `source_feature_id` |
| `railowner` | the operating railroad, e.g. `Union Pacific Railroad Company` |

Geometry comes back as `paths`. Where `name` is empty the flag falls back to
`railowner`, because "Union Pacific" tells a party chief more than a blank does.

The layer also publishes `railusage`, `railclassification`, `railsubdivision`,
`railownercode` and `lengthkm`. None is requested; the tool asks for what it
prints.

### TPMS, layer 0 — pipelines

| Field | What it holds |
|---|---|
| `TPMS_ID` | the Railroad Commission's own identifier. Recorded as `source_feature_id` |
| `OPER_NM` | the operator's name — who you would actually be calling |
| `CMDTY_DESC` | what the line carries, in words. This is what appears on the flag |
| `STATUS_CD` | whether the line is in service |

Geometry comes back as `paths`. The layer publishes forty-odd fields including
`DIAMETER`, `COUNTY`, `INTERSTATE` and `SYS_NM`; only the four above are asked
for.

!!! warning "`COUNTY` is not a usable filter on TPMS"
    `COUNTY='BEXAR'` returns zero records, while a spatial query over the same
    ground returns hundreds. Whatever that column holds, it is not the county
    name in capitals. The tool filters spatially and never by that attribute.

---

## What we ask them

**A box, not a ribbon.** Every flag service is asked about an envelope — the
rectangle drawn around every parcel in the corridor, grown by the neighbor
distance.

That is deliberate and it is not the same extent the parcel query uses. A flag
is `on` a **parcel**, and a parcel reaches well past the ribbon. A cemetery at
the back of a tract whose frontage is on the pavement is on that tract, and
belongs on that row. Asking only about the ribbon would miss it.

The precise work — is this feature on this parcel, beside it, or neither — is
then done by the tool's own geometry, against the parcel outlines. The service
narrows the search. It does not decide the answer.

---

## Trap one — the polyline buffer that answers with the wrong county

**This is the important one.**

The parcel query is asked with a **polyline and a distance**, and the ArcGIS
server buffers it. That works, and [the spec](../corridor-screen/spec.md)
section 4 is built on it.

Asked the same way, the USGS `structures` service answers wrong.

Tested live on 2026-09-12, with the SH16 Bexar centerline — a line that begins
and ends inside Bexar County — and a 400 ft distance:

| Asked with | Schools returned | Where they were |
|---|---|---|
| polyline + `distance=400`, `esriSRUnit_Foot` | 7 | 4 on the corridor, **3 in Kerrville and Fredericksburg** |
| polyline + `distance=2000` | 21 | 12 on the corridor, **9 in Bandera, Medina, Kerrville and Fredericksburg** |
| the same line thinned to 90 vertices | 6 | 3 on the corridor, **3 still 60 miles away** |
| a short two-point segment on Bandera Rd | 1 | correct |
| **an envelope** | 42 | **all 42 inside the envelope** |

Fredericksburg is roughly sixty miles up SH16 from the corridor. The query's
geometry stopped inside Bexar County. **No error was returned.**

Thinning the line did not fix it, so it is not a vertex-count limit. A short
segment was fine and an envelope was fine every time, so the geometry filter
itself works. Something about that server's buffer of a long polyline does not.

**What we did about it.** The flag queries use an envelope. And they are checked
anyway, by `checks.check_records_in_requested_extent`, which tests every
returned record against the box that was asked for. A service that starts
answering for the wrong extent will trip that check and put a warning next to
its own data.

!!! note "The pattern this belongs to"
    This is the third recorded case in this repo of a service returning a
    plausible wrong answer rather than an error. The first was
    [USGS 3DEP](../txdot-research.md) ignoring `sr=4326` and reading longitude
    and latitude as Web Mercator meters. The second was the parcel query reading
    the unit code `9003` as meters and returning 2,132 parcels where the right
    unit returned 658 — written up on
    [the geometry service page](arcgis-geometry-service.md).

    Three different services, three different parameters, same failure: the
    parameter is ignored and the answer looks fine. It is the single strongest
    argument in this repo for checking an answer you were given rather than
    trusting it.

---

## Trap two — the pipeline service that holds no Texas data

Until 2026-09-13, [the spec](../corridor-screen/spec.md) section 6 and
[TxDOT research](../txdot-research.md) both named `NPMS_Pipelines_2022` on
`services.arcgis.com/G4S1dGvn7PIgYd6Y` as the pipeline source.

Read on 2026-09-12:

| Question | Answer |
|---|---|
| Total records | 543 |
| Records where `ST_MIXED = 'Texas'` | **0** |
| Records where `CNTY_MIXED = 'Bexar'` | **0** |
| First five operators | all in **Chester County, Pennsylvania** |
| The layer's own extent | about longitude −76, latitude 40 |

It is a Pennsylvania dataset with a national-sounding name. A Texas query
returns zero records and no error, which reads exactly like "there are no
pipelines here."

This repo's own research already records the same trap for a different service:
`FEMA_Flood_Zones` on services9, which *"ranks high in search but is Salem, MA
only. Easy trap."* The research fell into its own documented trap a second time,
and the only reason it was caught is that a corridor with zero pipelines looked
odd enough to check the county, and then the state.

**What we used instead.** The **Texas Pipeline Mapping System (TPMS)**,
published by the Railroad Commission of Texas, which is the Texas authority for
pipeline location.

| Question | Answer |
|---|---|
| Total records | 490,375 |
| Within a box around Bexar County | 598 |
| Within the SH16 corridor's parcel envelope | **0** |
| Within about a mile of it | 1 |
| Within about seven miles of it | 39 |

So zero pipelines on this corridor is a real answer from a source that plainly
holds data there, rather than an empty answer from a source that holds none.

!!! success "Ruled on 2026-09-13, on [PR #53](https://github.com/RickSmith/survey-recon/pull/53)"
    Correcting a settled specification is not the agent's call, so the tool
    followed the service, recorded the difference here and at the bottom of
    `corridor-screen/corridor_screen/sources.py`, and raised section 6 for a
    ruling — the same route
    [PR #52](https://github.com/RickSmith/survey-recon/pull/52) took for the
    parcel field names.

    **Rick ruled that section 6 should name the source that holds Texas data.**
    It now names TPMS, with a note recording the amendment. The specification
    and the code agree again.

---

## Trap three — field names that change case between asking and answering

Smaller, but it would have shipped every school unnamed.

The USGS `structures` layers **publish** their fields in capitals —
`NAME`, `PERMANENT_IDENTIFIER`, `FTYPE`, `FCODE` — and **answer** a query in
lower case: `name`, `permanent_identifier`. The `transportation` layers on the
same host publish and answer in lower case.

So the field list check passes, the query succeeds, and
`feature["attributes"]["NAME"]` quietly finds nothing. Every flag comes out with
no name and nobody is told.

`flags.attribute` reads attributes case-insensitively, which is why it exists
rather than a plain dictionary lookup.

---

## What this added to spec section 10

[Spec section 10](../corridor-screen/spec.md) is a settled contract, and these
nine entries were **not in it** when the flags were built. They were listed here
rather than slipped in, so the ruling on whether they belonged was a person's to
make.

Nothing named in section 10 was removed or renamed.

!!! success "Ruled on 2026-09-13, on [PR #53](https://github.com/RickSmith/survey-recon/pull/53)"
    **Rick ruled to keep all nine.** Section 10 now names them, with a note
    recording the amendment, so the contract and the file agree again. The table
    below is kept as the account of what was added and why.

    Eight of the nine exist to keep a number honest rather than to add a number.
    That is the shape of what this ticket turned out to be: the flags were the
    easy half, and saying exactly how much each figure is worth was the rest.

| Field | Where | Why it is here |
|---|---|---|
| `lead_time_basis` | on every flag | Two working days and two calendar days are different promises. § 251.151(a) excludes weekends and holidays; § 711.041 does not. A bare number is what a reader turns into a date and gets wrong |
| `lead_time_confirmed` · `lead_time_statutory` | on every flag | Issue #17 asks for "code and section **where it is statutory**." A reader has to be able to tell a statute from a company's published procedure |
| `lead_time_not_found` | on every flag, and on the parcel row | Issue #17 asks that an unconfirmed lead time say "not found" and say where it looked. On the row it is what stops a school-only parcel reading as clear |
| `lead_time_days_low` · `lead_time_note` · `lead_time_verified_on` · `lead_time_driver_detail` | on every flag | The railroad figure is a published *range*; carrying only the planning number hides what it was chosen from. The note and the date are what make a citation checkable a year later |
| `max_lead_time_basis` | on the parcel row | Same reason as `lead_time_basis` |
| `parcels_crossed` | on a corridor-level flag | The number that stops one easement's notice period being counted once per parcel |
| `records_used` | on each service in the honesty block | "39 returned, 6 used" rather than a bare 6 |
| `run.screened_for` · `run.lead_times` | on the run | The flag types checked run-wide, and the citation for each, so the file can be checked without this repo beside it |
| `relation: "corridor"` | on a corridor-level flag | Section 10 defines `relation` as `on` or `adjacent`, and separately says a corridor flag carries the "same fields." A corridor flag therefore needs *some* third value, and this is it |

---

## What SH16 actually returns

At a 300 ft half-width and a 100 ft neighbor distance, run 2026-09-12:

| Flag | Returned in the box | On a corridor parcel |
|---|---|---|
| School | 39 | 6 |
| Cemetery | 6 | 1 |
| Railroad | 0 | 0 |
| Pipeline | 0 | 0 |

Eight of 524 parcels carry a flag. The longest wait on the corridor is **14
days**, on the Episcopal Church parcel at 11093 Bandera Rd, which carries the
Church of the Holy Spirit Columbarium.

**Zero railroads is a checked answer, not an empty one.** The same USGS layer
returns 412 records across Bexar County, including Union Pacific, BNSF and San
Antonio Central yards. There simply is no track within 300 ft of this stretch of
Bandera Road.

The pair of numbers in each row matters. The honesty block in `screening.json`
carries both — `record_count` and `records_used` — so a reader sees "39 returned,
6 used" rather than a bare 6. The 33 schools that were not used are a normal
answer to the question that was asked, because the box is wider than the
corridor. Hiding them would make the 6 look like the whole world.
