# Esri ArcGIS geometry service

A centerline is a line. A job is a strip of ground either side of it. This
service is the calculator that turns the one into the other: it takes the
centerline and the half-width and hands back the ribbon as a shape.

**Endpoint**

```
https://utility.arcgisonline.com/arcgis/rest/services/Geometry/GeometryServer/buffer
```

Public, no key, no account. Queried live on 2026-09-12 and it returned real
results.

---

## Why this service is here at all

It is the only outside service in the corridor tool that is not a source of
data. It is a calculator.

Buffering a line is the one job in corridor screening that normally needs a
geometry library installed. The alternative was to add a dependency, and the
repo's rule is that attendees need git, a GitHub account and the Claude desktop
app — nothing else. So the arithmetic is handed to a service that already does
it, and the tool still installs nothing.

The parcel query does its **own** buffering, from the same line and the same
distance, which is how [the spec](../corridor-screen/spec.md) section 4 has it.
This service is asked once, separately, for a polygon we can draw, stamp into
the output and hand to somebody later.

## What we send

| Parameter | Value | Why |
|---|---|---|
| `geometries` | the alignment, as an Esri polyline in WGS 84 | |
| `inSR`, `outSR`, `bufferSR` | `4326` | longitude and latitude in, longitude and latitude out |
| `distances` | the half-width | stated by the user, never derived |
| `unit` | `9002` | the international foot — see below |
| `unionResults` | `true` | one corridor, not one polygon per segment |
| `geodesic` | `true` | measured on the ellipsoid rather than on a flat map |

## What comes back

One `geometries` array. Each entry has `rings`. A corridor with a break in it
comes back as more than one ring, and those rings are separate pieces of
corridor, not a polygon with a hole in it.

---

## Quirks

### The unit code that answers wrong instead of erroring

This is the important one, and it is not about this service — it is about the
**parcel** query, which has to be asked for the same foot so that the drawn
corridor is the ribbon the parcels came from.

Tested live on 2026-09-12 against `BCAD_Parcels`, same line, same 300 ft
distance, only the `units` value changed:

| `units` value | Parcels returned |
|---|---|
| `esriSRUnit_Foot` | **658** |
| `esriSRUnit_SurveyFoot` | rejected — `'units' parameter is invalid` |
| `9003` | **2132** |

`9003` is the EPSG code for the US survey foot. The query endpoint accepts it
without complaint and answers with more than three times as many parcels —
almost exactly the ratio of feet to meters. It appears to treat an unrecognized
unit as meters and say nothing about it.

The rejected value is the good case: you find out immediately. The accepted one
is the case this repo keeps warning about. A 300-foot corridor that quietly
became a 300-meter corridor still produces a parcel list, still draws, still
looks like an answer, and would put roughly three times the tracts into a bid.

**So the tool uses the international foot on both endpoints**, because it is the
only unit the two agree on. TxDOT's Survey Manual does require US survey feet in
deliverables ([Ch. 3, Control Points](https://www.txdot.gov/manuals/row/ess/index.html)),
and screening is not a deliverable; at a 300-foot half-width the two feet differ
by about six ten-thousandths of a foot.

### It is a shared public utility

`utility.arcgisonline.com` is Esri's own, offered without a key. It has been
reliable in testing, but it is not TxDOT and not a county — nobody has promised
us anything about it. The corridor polygon is cached like every other response,
so a run replayed from cache never needs it.

---

## Where it is named in the code

[`corridor-screen/corridor_screen/sources.py`](https://github.com/RickSmith/survey-recon/blob/main/corridor-screen/corridor_screen/sources.py),
as `GEOMETRY`. The unit codes and the finding above are recorded beside the
buffer call in `corridor.py`.

---

## Where this came from

This service was worked out under [work order #21](https://github.com/RickSmith/survey-recon/issues/21).
