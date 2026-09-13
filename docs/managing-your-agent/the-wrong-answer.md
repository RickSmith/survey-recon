# The answer that was wrong rather than missing

Ask the USGS elevation service for the height of SH16 at Bandera Road. Ask it
twice. Change one word.

```
...&units=Feet      →  866.8668528742528
...&units=US_Feet   →  "264.221008301"
```

866.8668528742528 divided by 264.221008301 is **3.28084** — feet per meter. It
is the same ground. The second answer is in meters.

**No error was raised.** HTTP 200. Valid JSON. A number that is a perfectly
ordinary elevation for San Antonio, three and a quarter times too small.

This is failure beat two, written under
[issue #26](https://github.com/RickSmith/survey-recon/issues/26).

## `US_Feet` is not a typo

That is the part that should worry you.

It is not a programmer fat-fingering `Feet`. **It is what you call the unit you
work in.** It is the US survey foot — the one EPSG numbers `9003`, and the one TxDOT's
Survey Manual requires in deliverables
([TxDOT Survey Manual, Ch. 3, Control Points](https://www.txdot.gov/manuals/row/ess/index.html)).

A surveyor asking for elevations in the unit of their own profession gets
meters, and is told nothing.

!!! warning "This repo already has this exact trap somewhere else"
    `9003` is also the code that
    [the geometry service](../data-sources/arcgis-geometry-service.md) accepts
    and answers differently — it took the US survey foot and handed back a
    corridor with **2,132 parcels where the right unit returned 658**. Same
    code, same silence, different service.

    Two independent services, both accepting the surveyor's own unit, both
    answering in something else without saying so. That is not one bug. It is a
    shape.

## There is no field to check

This is why reading the answer more carefully does not help.

```json
{"location":{"x":-98.644635,"y":29.528488,
             "spatialReference":{"wkid":4326,"latestWkid":4326}},
 "locationId":0,"value":"264.221008301","rasterId":61823,"resolution":1}
```

The `spatialReference` block tells you the **coordinate** system. Nothing tells
you the **unit of the answer**. There is no field you failed to read. There is
no field.

The only thing that differs is the JSON type — a number for `Feet`, a string for
everything else. That is not a warning. It is a coincidence you would have to
already suspect in order to notice.

## The same service can fail loudly, and that version is safer

Ask about a point in the Gulf of Mexico:

```
HTTP 200
Call failed.  [Failed cloud operation: Open, Path: /vsimem/_000011B4.aux.xml]
```

Still a 200. But it is **not JSON**, so `json.loads` raises, and whoever wrote
the caller finds out inside a second.

!!! note "Do not match on that message"
    Those are the exact bytes of `captures/silent-nodata/no-data-gulf.txt`, and
    **the text varies between runs.** An earlier draft of this page quoted
    `_00002B0B.aux.xml` — a real response, from a live call made while
    researching this, but not the one committed here. Quoting something other
    than the evidence is the failure this page is about, so it is recorded
    rather than quietly corrected.

    [Sources we did not use](../data-sources/not-used.md) records the same
    endpoint answering `Invalid or missing input parameters.` for the same
    condition on the same day. The check that keeps working is whether the body
    parses as JSON at all.

Put the two side by side and the beat is the comparison:

| | What happens | Who notices |
|---|---|---|
| **Gulf of Mexico** | 200 carrying plain text | Anything that parses it. Immediately |
| **`units=US_Feet`** | 200 carrying valid JSON and a real number | Only somebody who knows this county |

> **The broken answer is caught by anything that reads it, and the plausible one
> is caught only by somebody who already knew what this ground is.**

That last clause was not in the first draft of this page, and finding out why is
the best thing in it.

**264.22 feet is below the floor of Bexar County**, which runs roughly 400 to
2,000. So a range check catches this — *if* the range is this county's. A range
check against the Earth, which is what you write when you do not know where the
job is, sails straight past it.

The first version of the code behind this page had a single check written
`0 < feet < 5000`, above a comment saying Bexar runs 400 to 2,000. The two did
not agree, and the wider bound was quietly doing the work — the function had
been calibrated, without anyone deciding to, so the answer came out the way the
argument wanted. The review caught it.

There are now two functions, `survives_a_generic_check` and
`survives_a_local_check`, and the honest claim is the narrower one:

> General care does not catch it. Knowing your own ground does.

Which is this repo's whole argument, arrived at from the wrong end.

## What the ticket expected, and what is actually there

Worth recording, because it is the repo's own rule about dated research.

[Issue #26](https://github.com/RickSmith/survey-recon/issues/26) describes the
service ignoring **the coordinate-system parameter**. It still does. And an
earlier draft of this page said it did not — because it tested the wrong
parameter.

**There are two spellings, and only one of them does anything.** Checked
2026-09-13, all captured:

| Sent | Answer |
|---|---|
| `sr=4326` | `866.8668528742528` |
| `sr=3857` | `866.8668528742528` |
| no coordinate system at all | `866.8668528742528` |
| `wkid=3857` with Web Mercator meters | correct elevation |

`sr` is the parameter this repo's original research named, and it is discarded
in silence — sending `4326`, sending `3857`, and sending nothing are the same
request. `wkid` is honored.

So one letter separates a parameter that works from one thrown away without
comment, and **nothing in the response tells you which you used.** That is worse
than the ticket describes, not different from it.

!!! note "The correction is kept, not tidied away"
    [Sources we did not use](../data-sources/not-used.md) had the `sr` half
    right the whole time — "`sr=4326` is silently ignored, which is the original
    hazard, still here." The draft of this page that contradicted it was wrong,
    and testing `wkid` and concluding something about `sr` is exactly the shape
    of error these pages exist to teach.

## Run it yourself

Reproduces on demand, and **reads only from disk** — a hotel network cannot take
it away from you:

```bash
python -m corridor_screen.elevation_trap --show
```

Twelve responses are committed in `corridor-screen/captures/silent-nodata/`, with
the exact request each came from. **Every one of them answered HTTP 200** — that
is the point of the set. Not one is an error by the only test most code applies.

## What to do about it

Nothing clever, and nothing this repo can do for you.

**Ask twice.** A second request in a unit you are sure of, and a ratio you check
yourself. If the two answers differ by 3.28, you have found it.

**And check against your own county, not against the planet.** That is the check
that caught this one, and it is not a programming skill. It is knowing that
Bandera Road does not sit at 264 feet.

**And do not use this service on anything that matters.** The corridor tool does
not call it at all — elevation is not something a corridor screening needs, and
the failure history is on the record either way. That decision is in
[ADR 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md), which was
written around this service before any of the above was found.

**You still sign it.** A check can tell you two numbers disagree. It cannot tell
you which one belongs in the deliverable.
