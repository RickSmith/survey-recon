# The SH16 capture: what happened

**What was run:** SH16 (Bandera Road), Loop 410 to Gibeaut Road, Bexar County —
8.69 miles, 300-foot half-width. Every step the tool has been built to do, against
the live services.

**When:** most of it on 2026-09-13; **9 of the 39 responses were captured on
2026-09-12** while the services were being worked out, and were re-checked
rather than re-fetched because nothing about them had changed. Every response is
committed in
[`project-sh16/cache/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/cache),
each with a `.meta.toml` beside it carrying its own capture time, the exact
request URL and every parameter of the request. The per-file stamps are the
authority; this paragraph is a summary of them.

**Say this on stage.** *"These were captured on the 12th and 13th of September,
so we're not at the mercy of the hotel Wi-Fi. The code is live code and you can
run it yourself."* Undisclosed caching, if noticed, costs you the room.

Written under [issue #20](https://github.com/RickSmith/survey-recon/issues/20).

---

## The run

Fourteen services. **Every one answered**, no sanity check tripped, and the run
finished `complete`.

| Service | Returned | Ping |
|---|---:|---:|
| `TxDOT_Roadways` | 1 | 218 ms |
| `ArcGIS_Geometry` | 1 | 266 ms |
| `BCAD_Parcels` | 530 | 311 ms |
| `USGS_Structures_Schools` | 39 | 546 ms |
| `USGS_Structures_Cemeteries` | 6 | 421 ms |
| `USGS_Transportation_Railroads` | **0** | 469 ms |
| `RRC_TPMS_Pipelines` | **0** | 186 ms |
| `NGS_Datasheets` | 31 | 235 ms |
| `TxDOT_Primary_Control_Points` | 8 | 311 ms |
| `TxDOT_ROW_Maps` | 69 | 141 ms |
| `USGS_Structures_Hospitals` | 33 | 358 ms |
| `USGS_Structures_Ambulance` | 33 | 328 ms |
| `USGS_Structures_Fire_EMS` | 140 | 344 ms |
| `USGS_Structures_Police` | 57 | 358 ms |

And what it found:

| | |
|---|---|
| Parcels in the corridor | **524** |
| Parcels carrying a flag | 8 |
| Screened for | cemetery, pipeline, railroad, school |
| NGS marks in the corridor | **11**, every one `MARK NOT FOUND` |
| TxDOT control points in the corridor | 4 records, **2 distinct monuments** |
| ROW map sheets over the corridor | 69, of which **15 are SH16's own** |
| Nearest hospital | 2.05 mi — Audie L Murphy VA |
| Warnings recorded | 0 |

### What was not run

Three things the specification names are not built yet. The output file says so
itself rather than leaving a reader to notice:

| Not run | What it would have added | How the output says so |
|---|---|---|
| **Roadway facts** — spec §5 step 5 | `ROW_MIN`, lane count, traffic, from `Roadway_Inventory_2023` | the `roadway` block reads `not-screened` and names the service |
| **Historic sites** — USGS `structures` layer 11 | a fifth flag type | `screened_for` lists four types, so no parcel reads as clear of a fifth |
| **TxDOT-owned land** — `2025_Land_Parcels` layer 328 | `txdot_owned` on each parcel row | the field is absent rather than false |

That is the `unknown` against `no` rule turned on the tool's own coverage. A
parcel this run never checked for a historic site is not a parcel reported as
having none.

---

## The surprises

These are the material. Every one came from reading a service rather than its
documentation, and most of them would have put a wrong number in front of a
surveyor.

### Every NGS mark in this corridor is one nobody could find

All eleven. `MARK NOT FOUND` on every one, with recovery attempts running from
1995 to 2002. A tool that reported "11 marks in the corridor" and stopped would
have an estimator pricing recovery on eleven monuments that three decades of
looking could not turn up.

This is the single most useful thing the tool found, and it is a number that
moves an estimate from recovery to setting new.

### Two of the fourteen services returned nothing, and that is a finding

Railroads: zero. Pipelines: zero. Both services answered correctly — there is
no railroad and no mapped pipeline within 300 feet of this centerline.

The tool reports `0 returned` rather than leaving the flag type off the list,
because "we looked and found none" and "we did not look" are different answers.
`screened_for` on every parcel names all four types, so no parcel reads as
clear of something nobody checked.

### The ROW sheet dates crash on Windows, rather than coming out wrong

TxDOT's ROW map service publishes real date fields, which ArcGIS sends as
milliseconds since 1970 — so every sheet older than 1970 is a **negative**
number, and on SH16 that is two thirds of them. Python's
`datetime.fromtimestamp` raises `OSError` on a negative value on Windows.

Not a wrong date. A crash, on exactly the oldest sheets, which are exactly the
ones that put time on an estimate. Written up on
[the ROW map sheets page](../../data-sources/row-map-sheets.md).

### The corridor's 15 sheets and the county's 27 are both right

[Issue #16](https://github.com/RickSmith/survey-recon/issues/16) predicted 27
sheets spanning 1937–1998. That is correct for SH16 across the whole of Bexar
County, over three control sections. This corridor sits inside **one** of those
three and reaches 15 of them, 1944–1998. 15 + 8 + 4 = 27.

Both numbers were captured and both are in the cache, so the difference can be
read rather than taken.

### `ROW_MAP_ID` looks like a key and is not

Six of the 27 share the value 993. Counting distinct identifiers gives 22, not
27 — a wrong number that looks right.

### `1900-01-01` appears 368 times, and we could not confirm what it means

Across 20,276 ROW sheet records, 368 carry exactly that date and **not one
record has an empty one**. That looks like a placeholder for "no date recorded." We could
not confirm it: the same layer holds 501 records dated after 1900 and before
1917.

So the tool does not guess. It reports the range the data gives and names the
sheet each end came from. Where we looked is written down, and it says "not
found" rather than "does not exist."

### Every layer on the USGS structures server exists twice

Hospitals are layer 14 **and** layer 49 — one set under a `Labels` group, one
under `Features`. Queried live on the same 25-mile box, both copies of all four
safety layers returned identical counts and identical identifier sets.

A trap that does not bite, and only because somebody checked.

### The nearest hospital is two miles away, and also eight

Audie L Murphy VA is 2.05 miles from the centerline and 2.05 miles from the
corridor's south end — and **7.99 miles from the north end**. A crew working
the north end who read only the first number would be wrong by nearly six miles.

Every place on the crew safety sheet carries three straight-line distances for
that reason. And every one of them is labeled a straight line, because an
ambulance drives roads.

### The honesty block was not being honest about one field

Found while proving the offline replay. The output names four values a service
may report, one of which is `from-cache` — and the word appeared **nowhere in
any file this tool had ever written**. Every call site passed the literal `ok`
while the responses underneath carried the truth.

So a run replayed entirely from disk looked identical to one that had just
called fourteen services, on the single field whose job is to say where the
answer came from. Fixed under
[issue #19](https://github.com/RickSmith/survey-recon/issues/19).

---

## The one call that stays live

```bash
python -m corridor_screen.live_check --out ../project-sh16
```

Everything above replays from disk. This one call goes out to NGS while the
room watches, and it is worth making because **it asks a different NGS endpoint
than the screening run uses** — the Data Explorer API with a point and a radius,
against the datasheets feature service with a corridor. Different service,
different query, even different spellings of the same fields.

Run on 2026-09-13 against this capture:

```
    marks in both        5
    conditions agreeing  5
    only the live call   8
    only the capture     6

    Every one of the 5 marks in both says the same thing live as it did
    in the capture.
```

Five marks appear in both. All five conditions agree — `MARK NOT FOUND` on
every one. That is a cross-check rather than a recording agreeing with itself.

**If the venue has no network,** the command says so plainly and says the
screening run is unaffected. It is a separate command rather than a mode for
exactly that reason: the worst a dead network can do is cost the live moment.

---

## Checking any of this yourself

Replay the whole corridor with no network at all:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only
```

A live run and a replay of this capture were compared and differ in **74
places, every one of them the run's own account of itself** — when it ran, its
mode, and the ping and status fields on each service. Every parcel, flag, lead
time, mark, sheet and the whole crew safety sheet are identical. The comparison
is itself a command, and it runs in the test suite with the network taken away.

See [the corridor-screen README](https://github.com/RickSmith/survey-recon/blob/main/corridor-screen/README.md)
for both.
