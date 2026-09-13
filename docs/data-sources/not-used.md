# Sources we looked at and did not use

Every other page here describes a service the tool calls. This one describes the
ones it does not, and why — because a source that was *considered and rejected*
is worth as much to somebody building their own version as a source that was
kept. The wrong service usually does not announce itself. It answers.

Written under [issue #21](https://github.com/RickSmith/survey-recon/issues/21).

---

## USGS 3DEP elevation — and the coordinate-system silence

**What it is:** the USGS Elevation Point Query Service, which returns ground
elevation at a point.

```
https://epqs.nationalmap.gov/v1/json?x=<lon>&y=<lat>&units=Feet&wkid=4326
```

**Why it is not on the critical path:** this repo's own research recorded two
problems with it, and it is the source the whole warn-versus-stop design in
[ADR 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md) was written
around.

> **3DEP silently returned `NoData`.** Ignored `sr=4326`, read lon/lat as Web
> Mercator meters. Returned a plausible non-answer rather than an error.

> **USGS 3DEP `identify` / EPQS elevation.** Timed out 3 of 4 attempts. Keep off
> the critical path.

That first one is the failure this tool is shaped by. A service that ignores a
parameter and answers anyway cannot be caught by checking for errors, because
there is no error. It is why `checks.py` exists at all, why the flag services
are asked with an envelope rather than a line and a distance, and why every
returned record is measured against the extent it was supposed to come from.

### What happened when we re-tested it, on 2026-09-13

**Neither behavior reproduced, and that is worth writing down rather than
quietly repeating the note.**

Four attempts at the SH16 corridor midpoint, matching the research's own sample
size:

| Attempt | Result |
|---|---|
| 1 | HTTP 200 in 0.62 s |
| 2 | HTTP 200 in 0.53 s |
| 3 | HTTP 200 in 0.44 s |
| 4 | HTTP 200 in 0.37 s |

Four of four, none over 0.7 seconds, all returning `866.87` feet for
`-98.644635, 29.528488` — a plausible elevation for that spot in San Antonio.

And asked with a **mismatched** coordinate system — the same longitude and
latitude, labeled `wkid=3857` — it did not return a plausible wrong elevation
either. It returned this, as `HTTP 200`, as plain text rather than JSON:

```
Call failed.  [Failed cloud operation: Open, Path: /vsimem/_00001EC8.aux.xml]
```

**So the hazard has changed shape, not disappeared.** It is still an HTTP 200
that is not an answer, and a caller that checks only the status code still gets
nothing useful. But the specific "plausible wrong number" the research recorded
is **not what this service does today**, and the timeouts did not happen at all.

We could not reproduce the original behavior. We are not saying it did not
happen — it is dated, it is recorded, and services change. We are saying what we
saw on 2026-09-13, on four tries, from one machine on one network. Somebody
re-testing from elsewhere may see something different again, and that is rather
the point of writing down the date beside the finding.

**The tool still does not call it.** Elevation is not something a corridor
screening needs, the failure history is on the record whether or not it
reproduces today, and nothing in the output depends on it.

---

## FEMA flood layers

Two separate problems, from the research, **both unverified by us**.

| Source | What the research recorded |
|---|---|
| **FEMA NFHL** | Robots-blocked. Suggested `USA_Flood_Hazard_Reduced_Set` on Esri Living Atlas instead, which caps at 250 records |
| **`FEMA_Flood_Zones` on services9** | Ranks high in a search and holds **Salem, Massachusetts only** |

**Where we looked:** the research notes, and nowhere else. Neither was re-tested
for this page, and neither is called by the tool, so no endpoint here has been
confirmed by us the way every other page's has. Treat both rows as a lead to
follow rather than a finding.

The second one is the more useful lesson anyway, and it is not really about
FEMA. **A service whose name matches what you want, which answers without
erroring, and which holds data for the wrong part of the country, is the single
easiest trap in this whole exercise.** This repo walked into it a second time
with pipelines — see below — after having already written it down.

---

## The ones that are written up elsewhere

Three more services were looked at and set aside, and each belongs on the page
about the service that replaced it:

| Source | Why not | Where |
|---|---|---|
| **`NPMS_Pipelines_2022`** | Named in the specification as the pipeline source. Holds **543 records, every one in Chester County, Pennsylvania.** A Texas query returns zero rows and no error | [the flag services](flag-services.md) |
| **`TxDOT_Control_Sections`** | Answers at layer 0, so it looks like the control service a careless reader expects — and holds numbered highway segments rather than survey monuments | [TxDOT control points](txdot-control-points.md) |
| **NGS Data Explorer, for the corridor query** | Takes a point and a radius or a box, not a corridor; caps at 500; is not an ArcGIS service, so none of this tool's paging, field-list checking or provenance machinery reaches it. **Kept for one job** — the live check in [spec section 3.6](../corridor-screen/spec.md) — because being a different endpoint is exactly what makes that cross-check worth anything | [the NGS datasheets](ngs-datasheets.md) |

---

## What connects all of these

None of them failed loudly. The pipeline service returned 543 real records. 3DEP
returned a real number. `TxDOT_Control_Sections` returns real highway segments
at the layer number everybody guesses.

**A dead service is the easy case.** You see it, you retry, you stop. The
expensive failure is the service that answers — plausibly, promptly, and about
the wrong thing — and the only defense is knowing roughly what the answer should
look like before you ask. A corridor with zero pipelines looked wrong enough to
check the county, and then the state. That is what caught it: not a check in the
code, a person who expected something else.

That is the same judgment a surveyor already applies to a plat that does not
close. It is the part of this that does not automate.
