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
work in.** It is the US survey foot — the one EPSG numbers `9003`, the one the
TxDOT survey specification is written in, the one on your data collector.

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
Call failed.  [Failed cloud operation: Open, Path: /vsimem/_00002B0B.aux.xml]
```

Still a 200. But it is **not JSON**, so `json.loads` raises, and whoever wrote
the caller finds out inside a second.

Put the two side by side and the beat is the comparison:

| | What happens | Who notices |
|---|---|---|
| **Gulf of Mexico** | 200 carrying plain text | Anything that parses it. Immediately |
| **`units=US_Feet`** | 200 carrying valid JSON and a real number | **Nobody** |

> **The broken answer is caught by anything that reads it, and the plausible one
> is caught by nothing until somebody has sealed it.**

That is the whole argument for beat two. An error message is a service doing you
a favor. This is the other thing.

## What the ticket expected, and what is actually there

Worth recording, because it is the repo's own rule about dated research.

[Issue #26](https://github.com/RickSmith/survey-recon/issues/26) describes the
service ignoring **the coordinate-system parameter** and reading longitude and
latitude as Web Mercator meters. Checked on 2026-09-13, that is not what this
endpoint does now — `wkid` is honored. Ask in Web Mercator meters with
`wkid=3857` and the right elevation comes back; ask in degrees while claiming
`3857` and you get plain text rather than a wrong number.

**The hazard did not go away. It moved** — from the coordinate system to the
units. Same failure, different clothes: a parameter accepted, quietly not
applied, and answered around.

[Sources we did not use](../data-sources/not-used.md) already records this
endpoint changing shape once between the original research and a re-test, and
says so rather than quietly updating the note. This is the second time.

## Run it yourself

Reproduces on demand, and **reads only from disk** — a hotel network cannot take
it away from you:

```bash
python -m corridor_screen.elevation_trap --show
```

Five responses are committed in `corridor-screen/captures/silent-nodata/`, with
the exact request each came from. **Every one of them answered HTTP 200** — that
is the point of the set. Not one is an error by the only test most code applies.

## What to do about it

Nothing clever, and nothing this repo can do for you.

**Ask twice.** The only thing that separates 866.87 from 264.22 is a second
request in a unit you are sure of, and a ratio you check yourself. That is what
`elevation_trap.value_of` does, and it is the entire defense.

**And do not use this service on anything that matters.** The corridor tool does
not call it at all — elevation is not something a corridor screening needs, and
the failure history is on the record either way. That decision is in
[ADR 0001](../adr/0001-sanity-checks-warn-dead-services-stop.md), which was
written around this service before any of the above was found.

**You still sign it.** A check can tell you two numbers disagree. It cannot tell
you which one belongs in the deliverable.
