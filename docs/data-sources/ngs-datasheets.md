# The NGS datasheets service

**What we use it for:** finding the NGS survey marks along the corridor, and
carrying through the condition each one was last left in. Recovery costs less
than setting new, so which of those two you are pricing is the single biggest
lever in a control estimate — and a mark stamped `MARK NOT FOUND` is not a mark
you have.

Written under [issue #14](https://github.com/RickSmith/survey-recon/issues/14).
Every endpoint below was queried live on 2026-09-12 and returned real results.

There is one trap here and it is the quiet kind: a field that is called one
thing in the specification and another thing on the service, where reading the
wrong name returns nothing and raises nothing.

---

## The service

```
https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NGS_Datasheets_Feature_Service/FeatureServer/1
```

| | |
|---|---|
| Published by | National Geodetic Survey (NOAA) |
| Layer | **1**, and it is the only layer on the service. Its name is `ALL_DATASHEETS` |
| Shape it returns | one point per mark |
| Paging cap | 2,000 |
| Key or account | none |

---

## Two services publish the same marks, and only one takes a corridor

[Spec section 6](../corridor-screen/spec.md) names both: "NGS Data Explorer
`/radial`, and the NGS datasheets feature service."

**The NGS Data Explorer API** lives at `https://geodesy.noaa.gov/api/nde/`. Its
endpoints are `/radial` (a point and a radius), `/bounds` (a north-south-east-west
box), `/pid` (named marks) and `/meta`. It caps at 500 records.

**The datasheets feature service** is a plain ArcGIS feature service. It takes
arbitrary geometry, pages at 2,000, and answers in the same shape as every other
source this tool calls — which means the reachability ping, the field-list check,
the paging loop and the provenance record all reach it without a second code
path.

So the tool calls the feature service. The API was still worth one call, for the
reason in the next section.

---

## The trap: the condition field is not called `condition`

[Spec section 11](../corridor-screen/spec.md) says the `condition` field is
carried through and never dropped. Issue #14 names `MARK NOT FOUND` as the value
that matters. The Data Explorer API does publish a field called `condition`.

**The feature service does not.** It publishes `LAST_COND`.

The research note had already warned about this, in one line: "Field names
differ from the NDE API." Read past that line, a tool asks the feature service
for `condition`, gets nothing back, raises nothing, and reports every mark in the
corridor as having no known condition. On SH16 that would turn eleven marks
nobody could find into eleven unknowns — and an unknown reads to an estimator as
"go and look," which is exactly the trip this field exists to prevent.

**It was confirmed rather than assumed.** Both services were asked about the same
three PIDs on 2026-09-12:

| PID | Feature service `LAST_COND` | Data Explorer `condition` |
|---|---|---|
| `AY1052` | `MARK NOT FOUND` | `MARK NOT FOUND` |
| `AY0710` | `MARK NOT FOUND` | `MARK NOT FOUND` |
| `AY1102` | `MARK NOT FOUND` | `MARK NOT FOUND` |

Same values, and the same recovery dates beside them. The Data Explorer answer
is cached at `ngs-data-explorer/pid-cross-check-ay0713-ay0710-ay1102`, beside the
feature-service capture it is checked against. The mapping from
`LAST_COND` to the output's `condition` is recorded in
[`sources.py`](https://github.com/RickSmith/survey-recon/blob/main/corridor-screen/corridor_screen/sources.py),
in `NGS_MARK_FIELDS`, next to the parcel mapping that does the same job.

!!! note "The pattern this belongs to"
    This is the third time in this repo that a document and a service have
    disagreed about a field name, and the third time the code followed the
    service and wrote down the difference. The other two are `AcctNumb` on the
    parcels and `NPMS` on the pipelines, both on the
    [flag services page](flag-services.md) and in `sources.py`.

    This one is milder than those: nothing in the specification is wrong. Section
    11 describes the **output file**, and the output file does carry `condition`.
    It is a mapping, not a correction.

---

## The fields we ask for, and what they hold

Only these are requested. A service that stops publishing one of them fails the
field-list check before a single query is sent.

NGS's own definitions of these fields are at `geodesy.noaa.gov/api/nde/meta`,
cached at `ngs-data-explorer/field-definitions-meta`.

| Field | Output field | What it holds |
|---|---|---|
| `PID` | `pid` | the mark's Permanent Identifier, e.g. `AY0713`. This is what you look it up by, and what `datasheet_url` is built from |
| `LAST_COND` | `condition` | **the reason we are here.** The condition at the last recovery |
| `LAST_RECV` | `last_recovered` | when that recovery was, as `YYYYMMDD` |
| `LAST_RECBY` | `last_recovered_by` | who reported it, e.g. `USPSQD` |
| `NAME` | `designation` | the mark's designation, e.g. `T 481` |
| `STAMPING` | `stamping` | what is actually stamped on the disk, e.g. `T 481 1935` |
| `MARKER` | `marker` | monument type, as a code and its meaning: `DB = BENCH MARK DISK` |
| `SETTING` | `setting` | what it is set in: `7 = SET IN TOP OF CONCRETE MONUMENT` |
| `STABILITY` | `stability` | the NGS stability code. `A` through `D` across Bexar, and blank on some records |
| `POS_DATUM` / `VERT_DATUM` | `horizontal_datum` / `vertical_datum` | `NAD 83`, `NAVD 88` |
| `ORTHO_HT` | `ortho_height_m` | orthometric height in meters, published as a string |
| `SPC_ZONE` | `spc_zone` | state plane zone. `TXSC` is Texas South Central, which is Bexar |
| `POS_ORDER` / `VERT_ORDER` | `horizontal_order` / `vertical_order` | order of accuracy |
| `CORS_ID` / `PACS_SACS` | `cors_id` / `pacs_sacs` | set where the mark is a CORS, or is flagged **PACS/SACS** — NGS's own wording is "Primary Airport Control Station(PACS) or Secondary Control Airport Station(SACS) indicator", the marks that tie an airport survey to the national framework |

`last_recovered` is written out as `1995-04-13` when the service sends eight
digits, because `19950413` on a projector reads as a number rather than a date.
Anything that is not eight digits is passed through exactly as it came.

**The date matters as much as the condition beside it.** `GOOD` recovered in 1952
and `GOOD` recovered in 2019 are not the same promise.

---

## A blank condition is a single space

Six of the 910 records in a box around Bexar County carry `" "` in `LAST_COND`
— one space, not an empty string and not a null. Sixty-eight of them do the same
in `STABILITY`. That response is cached at
`ngs-datasheets/bexar-box-condition-tally`, so the count can be checked rather
than taken.

Read carelessly that is a non-empty string, and a mark nobody has reported on
since it was set goes into an estimate as a mark you have. The tool reads every
attribute through one helper that treats a blank string as absent, and a mark
with no condition is reported as `condition unknown`.

**Unknown is never counted as found.** `recovery_risk` in the output carries
`mark_not_found` and `condition_unknown` as two separate numbers, beside a
`by_condition` tally of every value the service actually returned. A condition
this tool has never seen shows up in that tally rather than being folded into
something friendlier.

---

## Which marks count as in the corridor

The strict test: **the mark's own point is within the half-width of the
centerline.** No margin, no neighbor distance.

[Spec section 8](../corridor-screen/spec.md) says so in as many words. When the
parcel check was amended on
[PR #52](https://github.com/RickSmith/survey-recon/pull/52) from testing a center
point to testing any part of a shape, the note recorded that the strict form
"stays correct for services that return points — NGS marks, TxDOT control." A
parcel is an area and can be clipped by a ribbon. A mark is a point and is either
in or out.

The query itself asks about a **box** around the corridor, not the ribbon, for
the reason written up on [the flag services page](flag-services.md): asked with a
polyline and a distance, a service can buffer into the wrong county and answer
without erroring. Asked with an envelope it answers about the envelope, and the
tool then measures each mark itself.

So the honesty block reports two numbers, the same way it does for flags: **31
returned, 11 in the corridor.**

---

## The datasheet link, and the claim this page got wrong first

Every mark carries `datasheet_url`, a plain link to its full NGS datasheet —
position, recovery history, and the description of how to find it:

```
https://geodesy.noaa.gov/cgi-bin/ds_mark.prl?PidBox=AY0713
```

`MARK NOT FOUND` starts a decision rather than ending one, and this is what the
decision gets made from.

!!! warning "This page said the opposite, and was wrong"
    The first draft of this page said the link did not work — that a plain
    request answered **HTTP 200 with an empty body**, and that the page needed a
    POST. The output carried no `datasheet_url` because of it.

    That reading came from a `curl` in the working notes whose output file path
    did not exist. Nothing was written, nothing was downloaded, and `curl`
    truthfully reported **0 bytes**. The zero was the measuring instrument, not
    the server.

    It was caught by re-running the same request through the tool's own fetcher
    while caching the evidence — which is the point of the caching rule. A claim
    you cache is a claim somebody can check. The real answer is in the cache at
    `ngs-datasheet-page/ds-mark-plain-get-ay0713`: **5,030 bytes** of datasheet,
    carrying `AY0713`, the designation `T 481` and `MARK NOT FOUND`. (That file
    holds HTML despite its `.json` name — the cache names every response the
    same way, and the provenance record beside it says what it really is.)

    Two agent errors of the same shape now sit in this repo: this one and the
    [NPMS service](flag-services.md) holding Pennsylvania data. Both were
    confident, both were plausible, and both were caught by checking rather than
    by thinking harder.

---

## What SH16 returned

Corridor: SH16 / Bandera Rd, Loop 410 → Old Bandera Rd. 8.69 miles, 300 ft
half-width. Captured 2026-09-12.

| | |
|---|---|
| Marks returned by the box query | 31 |
| Marks inside the 300 ft corridor | **11** |
| Of those, `MARK NOT FOUND` | **11** |
| Of those, condition unknown | 0 |

**Every NGS mark within 300 feet of this centerline is one NGS could not find.**
The nearest sits 5.8 ft off the line; the furthest in the list is 147.9 ft. The
most recent recovery attempt was 2002, the oldest 1995.

That is the whole argument for pulling this field. A run that reported "11 NGS
marks in the corridor" and stopped there would have an estimator pricing recovery
on eleven marks that three decades of recovery attempts could not turn up.

**31 returned here, 54 in the research note — both are right.** The note in
[TxDOT research](../txdot-research.md) records "54 marks in corridor bbox" for
this service. That box is `-98.66,29.45,-98.56,29.56`, a rectangle drawn by hand
around the study area. The box this tool asks about is the alignment's own extent
grown by the half-width: `-98.6905,29.4816,-98.5987,29.5753`. Different
rectangles, so different counts. Both were re-run on 2026-09-12 and returned 54
and 31 exactly as recorded. The tool's box is the one that follows the corridor,
and the exact geometry it asked about is in the provenance record beside the
cached response.

**The two `GOOD` marks are outside the ribbon.** Of the 20 marks the corridor
filter dropped, 18 are also `MARK NOT FOUND` and two are `GOOD`. They are real
and they are close — they are simply further from the centerline than the stated
half-width. Control-hunting is a good reason to run the tool again with a wider
`--half-width`, and the number is settable for exactly that kind of reason.

---

## What this does not tell you

- **TxDOT primary control points are a separate work order**,
  [issue #15](https://github.com/RickSmith/survey-recon/issues/15). They are layer
  **67** on the TxDOT feature server. Until that lands, the output names
  `txdot_points` as `not-screened` rather than leaving it out, so nobody reads a
  missing block as an empty one.
- **NGS's condition is a report, not a survey.** `MARK NOT FOUND` means the last
  person who looked did not find it. It does not mean the mark is gone. Reading
  the datasheet's recovery history, and deciding what it is worth to your crew,
  is the sealing surveyor's call and not this tool's.
- The tool reports `POOR`, `MONUMENTED` and anything else exactly as NGS wrote
  it, and does not grade them.
