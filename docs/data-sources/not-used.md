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

!!! warning "Those two paragraphs are quotations, not findings"
    They are what [the research](../txdot-research.md) recorded on 2026-09-12,
    and they are quoted here because they are why this service was looked at.
    **Neither reproduced.** The rest of this section is what we saw ourselves.

    In particular, **no response this repo holds contains the token `NoData`** —
    not one of those committed in `corridor-screen/captures/silent-nodata/`,
    and the Gulf of Mexico point that would deserve one answers plain text
    instead. The account of that description reaching the glossary and then a
    slide is
    [the description that outlived its evidence](../managing-your-agent/the-description-that-outlived-its-evidence.md).

That first one is the failure this tool is shaped by. A service that ignores a
parameter and answers anyway cannot be caught by checking for errors, because
there is no error. It is why `checks.py` exists at all, why the flag services
are asked with an envelope rather than a line and a distance, and why every
returned record is measured against the extent it was supposed to come from.

### What happened when we re-tested it, on 2026-09-13

**Read the caveat before the numbers: this was not an exact replication.** The
research recorded `sr=4326` being ignored. Today's `v1` endpoint does not take
`sr` at all — it takes `wkid` — so we could not repeat the original request
against the original endpoint. What follows is what this endpoint does now.

**It answered every time, and the times varied a lot.** Ten attempts across two
machines on the same day: six between 0.40 s and 1.29 s, one at 3.20 s and one
at **16.35 s**. Every one returned HTTP 200 and `866.87` feet for
`-98.644635, 29.528488` — a plausible elevation for that spot in San Antonio.

So we did **not** reproduce "timed out 3 of 4 attempts." We also did not find a
service you would want on a critical path: a sixteen-second response is a
sixteen-second response, and an earlier draft of this page quoted "none over
0.7 seconds" from four lucky tries. That sentence was wrong the way a small
sample is always wrong.

**`sr=4326` is silently ignored — which is the original hazard, still here.**

```
?x=-98.644635&y=29.528488&units=Feet&sr=4326   → 866.87 ft
?x=-98.644635&y=29.528488&units=Feet            → 866.87 ft   (identical)
```

Passing the parameter the research named changes nothing, and the service does
not say so. That is the same shape of failure the research recorded: a parameter
accepted, ignored, and answered around.

**A wrong `wkid` gives an HTTP 200 that is not an answer** — plain text, not
JSON:

```
?x=-98.644635&y=29.528488&units=Feet&wkid=3857   → Invalid or missing input parameters.
```

A caller checking only the status code gets a 200 and a body that will not
parse. Note that **the exact text varies between runs**: an earlier attempt the
same day returned `Call failed.  [Failed cloud operation: Open, Path:
/vsimem/_00000376.aux.xml]` instead. Do not match on the message.

### The unit is not honored either, and that one hands you a number

Found on 2026-09-13 under
[issue #26](https://github.com/RickSmith/survey-recon/issues/26), and it is a
worse trap than either of the two above because it answers.

Same point, same second, one word different:

| `units` value | `value` in the response | JSON type | Actually |
|---|---|---|---|
| `Feet` | `866.8668528742528` | number | feet |
| `Meters` | `"264.221008301"` | string | meters |
| `US_Feet` | `"264.221008301"` | string | **meters** |
| `ft` | `"264.221008301"` | string | **meters** |
| `Furlongs` | `"264.221008301"` | string | **meters** |
| *(omitted)* | `"264.221008301"` | string | **meters** |

866.8668528742528 / 264.221008301 = 3.28084, which is feet per meter. Every
unrecognized value returns the metric answer, unchanged, with no error.

**Every row above is a committed response**, at
`corridor-screen/captures/silent-nodata/`, with the exact request beside it.

**It is not case sensitivity.** Lowercase `feet` returns 866.87, the same as
`Feet` (`units-lowercase-feet.json`). The service has a short list of words it knows, and everything else —
including the surveyor's own unit — falls through to meters. Knowing that
matters, because "just match the capitalization" is the wrong lesson and would
leave you exposed.

**`US_Feet` is the one that matters.** It is not a typo — it is the US survey
foot, what EPSG numbers `9003` and what TxDOT's Survey Manual requires in
deliverables ([TxDOT Survey Manual, Ch. 3, Control Points](https://www.txdot.gov/manuals/row/ess/index.html)). A surveyor asking in the unit of their own profession gets meters.

**There is no field to check.** The response carries a `spatialReference` for
the *coordinate* system and nothing at all for the unit of the answer. The only
thing that differs is the JSON type, which is a coincidence rather than a
warning.

This is the **same mechanism** as the `9003` trap on
[the geometry service](arcgis-geometry-service.md), which "appears to treat an
unrecognized unit as meters and say nothing about it." Two independent services,
two different vendors, the same silence, both triggered by the surveyor's own
unit. Both were caught by asking twice rather than by reading the answer harder.

**And `wkid` is honored, which is what makes the `sr` silence above a trap.**
Ask in Web Mercator meters with `wkid=3857` correctly declared and the right
elevation comes back (`wkid-3857-mercator.json`). So this endpoint has two names
for the coordinate system: one applied, one discarded without comment, and
nothing in the answer saying which you used.

Requested five times each on 2026-09-13; `Feet` and `US_Feet` were identical
every time. The responses are committed at
`corridor-screen/captures/silent-nodata/`, and
`python -m corridor_screen.elevation_trap --show` replays the comparison offline.

### What we are and are not saying

We are saying what this endpoint did on 2026-09-13, from two machines, on one
network, on ten attempts. We are **not** saying the research was wrong: it is
dated, it named a different parameter, services change, and a slow network
somewhere else will see the timeouts we did not.

The hazard has not gone anywhere. It has changed shape — from "a plausible wrong
number" to "a 200 that will not parse" and "a parameter quietly ignored" — and
both of those still defeat a caller that only checks the status code.

What we are also saying, plainly, is that **we could not confirm the `NoData`**.
We looked in every response committed for this beat and in the research page that
is the claim's only source, and it is not in either. That is *not found* rather
than *it never happened*, and the difference is that somebody looked.

**The tool still does not call it.** Elevation is not something a corridor
screening needs, the failure history is on the record whether or not any
particular part of it reproduces today, and nothing in the output depends on it.

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
