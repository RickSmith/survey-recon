# The TxDOT ROW map sheet index

**What we use it for:** counting the right-of-way map sheets over the corridor,
and finding out how far back they go. A ROW map sheet is the historical record
drawing of a right of way. A 1944 sheet means hand retracement off a scan that
may barely be legible, and that is time somebody has to price.

Written under [issue #16](https://github.com/RickSmith/survey-recon/issues/16).
Every endpoint below was queried live on 2026-09-12 and returned real results.

There are three traps here. One of them does not return a wrong answer — it
stops the run.

---

## The service

```
https://maps.dot.state.tx.us/arcgis/rest/services/ROW/ROW_Maps_CL_2017/MapServer/0
```

| | |
|---|---|
| Published by | Texas Department of Transportation, ROW Division |
| Layer | **0**, named `RPAM.RPAM.VW_ROW_MAP_HyLink` |
| Shape it returns | one polyline per drawing — the stretch of route centerline that sheet covers |
| Paging cap | 5,000 |
| Records statewide | 20,276 |
| Key or account | none |

It is a **MapServer**, not a FeatureServer. Every other service the corridor
tool calls is a FeatureServer on a cloud host; this one is TxDOT's own server.
The URL shape is the same, `<base>/<layer>/query`, so nothing in the tool had
to change to reach it.

[Spec section 5](../corridor-screen/spec.md) calls this host **"the least
reliable host, deliberately last,"** and this repo's own
[research](../txdot-research.md) recorded it failing and then succeeding minutes
later. That is why the ROW map step is step 8 of 8, why it can be skipped
without costing the rest of the run, and why the reachability ping earns its
keep here more than anywhere else.

---

## Trap one: the dates are real dates, and two thirds of them are negative

This is the one that does not return a wrong answer. It raises an exception.

Every other service the tool calls publishes its dates as text. NGS sends
`19950413` as a string. **This service publishes `MAP_FROM_DT` and `MAP_TO_DT`
as `esriFieldTypeDate`,** and ArcGIS sends a date field as the number of
milliseconds since 1 January 1970.

Sheets older than 1970 are therefore **negative** numbers. On SH16 that is
two thirds of them. The 1937 sheet arrives as `-1020384000000`.

Handed to Python the obvious way, on Windows:

```python
datetime.utcfromtimestamp(-1020384000000 / 1000)
# OSError: [Errno 22] Invalid argument
```

`datetime.fromtimestamp` fails the same way. Not a wrong date — a crash, on
exactly the oldest sheets, which are exactly the ones that put time on an
estimate. Confirmed on Windows 11 with Python 3.11 on 2026-09-12.

What works has no such limit:

```python
datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=value)
```

**The reading is checkable, and it is checked.** TxDOT builds each sheet name
as `District-ControlSection-Route-MapDate`, so
`SAT-029110-SH0016-19980306` states its own date a second time. The name and
the field agree on all 27 SH16 sheets, which is what says the milliseconds are
being read in the time zone ArcGIS sends them in. There is a test on that.

## Trap two: `ROW_MAP_ID` looks like a key and is not

Six of the 27 SH16 sheets in Bexar County share `ROW_MAP_ID` 993, and it is the
only value in that set that repeats. Counting distinct identifiers gives **22**,
not 27 — a wrong number that looks right.

`MAP_NM` is the name that is one per drawing, including the `-1` suffix TxDOT
adds when two sheets carry the same date, as in
`SAT-029110-SH0016-19971212` and `SAT-029110-SH0016-19971212-1`. The tool
counts records and carries `row_map_id` through as what it is.

## Trap three: `1900-01-01` appears 368 times, and we could not confirm what it means

Across the whole layer, **368 of 20,276 records carry exactly `1900-01-01`**,
and **no record has a null date at all**. A date column with no nulls and a
368-record spike on one day looks like a placeholder for "no date recorded."

**We could not confirm that.** Against it: the layer also holds
`LRD-001801-IH0035-19000608`, which is a June 1900 date rather than the January
one. It also holds **501 records dated after `1900-01-01` and before 1917**,
which is before the Texas Highway Department existed. So early dates are common
here for reasons we have not established, and `1900-01-01` may be one of them
rather than a blank.

Where we looked: the layer's own field metadata, which documents nothing about
it; and four record counts by date, queried live on 2026-09-12 and cached at
`txdot-row-maps/date-tally-*` with the exact `where` clause of each in the
`.meta.toml` beside it. We did not ask the ROW Division. Until somebody does,
treat a `1900-01-01` sheet as a date you should check against the drawing.

**The output carries this doubt, not just this page.** The `row_maps.notes`
block holds a `the oldest date may not be a date` entry. The tool says the same
thing on screen when the range starts on `1900-01-01`. A caveat kept somewhere
else is a caveat nobody reads at the moment they are about to quote 1900.

**The tool does not guess.** It reports the range the data gives and names the
sheet each end came from, so `1900-01-01` arrives attached to
`SAT-052104-IH0410-19000101` and a reader can see what they are looking at
rather than take a number on trust.

---

## What the tool asks for, and what it does with the answer

A box around the corridor, grown by the half-width. That is the same envelope
the NGS marks are asked about, and for the same reason. It is written up in
[the flag services](flag-services.md). Asked with a polyline and a distance, a
service can buffer into the wrong county and answer without erroring.

Every returned sheet is then measured against the centerline, and one is over
the corridor when any part of its line comes within the half-width. A sheet is
a line, so the test is the one used for a parcel, not the strict point test
used for a survey mark.

**Crossing routes are reported, not dropped.** SH16 from Loop 410 to Old Bandera Rd
meets two major interchanges, and the right of way at an interchange is drawn
on the crossing route's sheets. Those are records a crew has to pull. So the
count covers every route that reaches the corridor, and `by_route` in the
output is what keeps the corridor's own route readable on its own.

---

## The corridor answer, and the county answer, and why they differ

[Issue #16](https://github.com/RickSmith/survey-recon/issues/16) predicted **27
sheets spanning 1937 to 1998** for SH16 through Bexar. That number is right, and
it is not the number the corridor run reports. Both were read live on
2026-09-12 and both are cached.

| Question | Sheets | Dates | Control sections |
|---|---|---|---|
| SH16 across the whole of Bexar County | **27** | 1937-09-01 to 1998-03-06 | 0291-09, 0291-10, 0613-01 |
| SH16 where it reaches this corridor | **15** | 1944-01-01 to 1998-03-06 | 0291-10 only |
| Every route reaching this corridor | **69** | 1900-01-01 to 2005-04-30 | six |

**The corridor is not the county.** It is 8.69 miles of SH16, from Loop 410 to
Old Bandera Rd, and that stretch lies entirely inside one of the route's three
control sections. All 15 of control section 0291-10's sheets reach it; the 8
sheets on 0291-09 and the 4 on 0613-01 are elsewhere on SH16 and do not. 15
plus 8 plus 4 is 27.

The county-wide figure was captured as a cross-check so the difference can be
read rather than taken. It is in the project cache at
`txdot-row-maps/sh16-bexar-county-wide-cross-check`, with its full request in
the `.meta.toml` beside it, and it is the same shape of evidence as the NGS
`pid-cross-check` recorded in [the NGS datasheets](ngs-datasheets.md). The
query behind it:

```
POST https://maps.dot.state.tx.us/arcgis/rest/services/ROW/ROW_Maps_CL_2017/MapServer/0/query
where=CNTY_NM='BEXAR' AND RTE_NM='SH0016'
```

---

## No field gives you the drawing

There is no PDF link anywhere in this layer. What you get is the sheet count,
the dates, the control sections and the sheet names.

The drawings come through **RPAM**, TxDOT's Real Property Asset Map. In
TxDOT's own words, it is "an online application populated with geo-referenced
features that represent all real property assets comprising the highway right
of way and is the replacement for paper right-of-way maps." A map not available
there is obtained by **Open Records Request**, quoting the `MAP_NM` values.
([TxDOT, Real Property Asset Map](https://www.txdot.gov/data-maps/right-of-way-maps/real-property-asset-map.html))

The output says so in its own `notes` block rather than leaving a blank, which
is what [spec section 10](../corridor-screen/spec.md) asks for.

---

## The fields

| Output field | Service field | Notes |
|---|---|---|
| `map_name` | `MAP_NM` | One per drawing. `District-ControlSection-Route-MapDate` |
| `row_map_id` | `ROW_MAP_ID` | **Not unique.** See trap two |
| `control_section` | `CTRL_SECT_NBR` | Six digits, so `029110` is control section 0291-10 |
| `csj` | `CSJ_NBR` | Empty on every SH16 sheet. Reported as it came |
| `route` | `RTE_NM` | `SH0016`, `IH0410`, `SL1604` … |
| `county` | `CNTY_NM` | Answers as `Bexar`, and matches a `where` clause written `BEXAR` — this server's text comparison ignores case |
| `map_from_date` | `MAP_FROM_DT` | Milliseconds. See trap one |
| `map_to_date` | `MAP_TO_DT` | Empty on every SH16 sheet |
| `total_pages` | `TOTL_MAP_PAGE_QTY` | `1` on every SH16 sheet |
| `limit_from`, `limit_to` | `MAP_LMT_FROM_DSCR`, `MAP_LMT_TO_DSCR` | TxDOT's own words for where the sheet starts and stops |

!!! note "Two differences from the specification, amended 2026-09-13 on [PR #56](https://github.com/RickSmith/survey-recon/pull/56)"
    Until then [spec section 10](../corridor-screen/spec.md) named this block as
    `sheet_count · date_range · control_sections · sheets`, each sheet
    "carrying `MAP_NM`, `ROW_MAP_ID`, `CTRL_SECT_NBR`, `CSJ_NBR`, `MAP_FROM_DT`
    and `MAP_TO_DT`."

    **The service's field names are not used as output names.** Every field is
    present and none is dropped, but each is written the way this tool writes
    every other output field — `map_name`, `row_map_id`, `map_from_date`. The
    parcels and the NGS marks already do exactly this, and the table above
    records which name went where.

    **There are more keys than four.** `by_route`, `sheets_without_a_shape` and
    `notes`. Neither contradicts section 10; both are a superset of it.

    Settled on the same ruling, because it is a judgment about what a reader
    will quote rather than a fact. The `sheet_count` and `date_range` keys
    cover **every** route reaching the corridor, and they stay that way. So on
    SH16 they read 69 and 1900–2005, while the corridor's own route reads 15
    and 1944–1998 inside `by_route`.

    Amending a settled specification is not the agent's call — the precedent is
    `AcctNumb` on [PR #52](https://github.com/RickSmith/survey-recon/pull/52),
    `NPMS` on [PR #53](https://github.com/RickSmith/survey-recon/pull/53) and
    the `not-screened` control blocks on
    [PR #54](https://github.com/RickSmith/survey-recon/pull/54). All three were
    raised on the pull request and ruled on by Rick. So was this.

The layer also publishes `ORIG_CTRL_SECT_NBR`, `CURR_CTRL_SECT_NBR`, `RTE_NM2`,
`RTE_NM3`, `MAP_LOCN_DSCR`, `DIST_NBR` and the usual create and edit stamps. On
the SH16 sheets `ORIG_CTRL_SECT_NBR` and `CURR_CTRL_SECT_NBR` both equal
`CTRL_SECT_NBR`, so the tool does not ask for them. A corridor where a control
section was renumbered would want all three.
