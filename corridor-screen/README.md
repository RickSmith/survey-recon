# corridor-screen

Desktop reconnaissance for a highway corridor. A route and its limits go in. A
parcel list comes out, and every answer the tool received is saved beside it.

**The scope of work is [`docs/corridor-screen/spec.md`](../docs/corridor-screen/spec.md).**
It was settled by grilling, on [issue #5](https://github.com/RickSmith/survey-recon/issues/5).
The one decision that needed its own record is
[ADR 0001 — sanity checks warn, dead services stop the run](../docs/adr/0001-sanity-checks-warn-dead-services-stop.md).
Vocabulary is in [`CONTEXT.md`](../CONTEXT.md), under **Corridor-screening vocabulary**.

---

## What is built so far

The first path through the whole tool, from
[issue #13](https://github.com/RickSmith/survey-recon/issues/13) — the spine,
before any of it gets wide.

| Step | Built |
|---|---|
| Reachability ping on every service | yes |
| Field list confirmed before any query | yes |
| Alignment from a route name and two DFO numbers | yes |
| Corridor buffer, fetched once and cached | yes |
| Parcels from the CoSA BCAD service | yes |
| Every response cached with its provenance record | yes |
| Lead-time column on every parcel | present, and empty |
| Flags — schools, cemeteries, railroads, pipelines | not yet, issues #14–#18 |
| Control, ROW map sheets, roadway facts | not yet, separate work orders |
| SVG renderings | not yet |

## What you need to run it

Python 3.11 or newer. Nothing else — no `pip install`, no libraries. Python
3.11 is the floor because it is the first version that reads TOML on its own,
and TOML is what the provenance records are written in.

## Running it

From this directory:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16
```

| Option | What it does |
|---|---|
| `--route` | The TxDOT route name, exactly as `TxDOT_Roadways` publishes it |
| `--begin-dfo`, `--end-dfo` | The two limits, as Distance From Origin in miles. Either order |
| `--half-width` | How far each side of the centerline counts as inside. Default 300 feet |
| `--mode` | `live`, `cache-first` (default) or `cache-only` |
| `--out` | Where the output file and the cache are written |
| `--yes` | Never ask about a dead service. Stop instead. Use for unattended runs |

**`cache-only` is the mode that makes a run repeatable away from a working
network.** It makes no network calls at all, not even the ping. If a request
was never captured, it says which one and stops rather than guessing.

The cache never expires on its own. `--mode live` is the only refresh, because
a cache that quietly re-fetches on the morning of a session is a hazard rather
than a feature.

## Reading the output

`screening.json` is one file that both a person and a program can read. A run
that stopped part-way writes `screening.incomplete.json` instead, so a blocked
host can never destroy a capture that already worked.

Three parts of it are worth knowing by name.

**The wrong-file check** — the corridor length, both end points and a web map
link, printed before any service is called and recorded in the output. A
misread route does not look like a subtle error. It looks like a
four-thousand-mile corridor on line one.

**The honesty block** — `services`, one entry per service: what was asked, of
what, whether it answered, how many times it had to be asked, which cached file
holds the answer, and what was doubted about it. It is what lets somebody else
decide whether to trust the rest of the file.

**`screened_for`** — the flag types actually checked for each parcel. Nothing
is checked yet, so the list is empty on every row, and no parcel is reported as
clear of anything. A parcel that could not be checked is `unknown`. It is never
`no`.

## The cache

```
project-sh16/cache/
  <service>/
    <name>__<hash>.json        exactly the bytes the server sent
    <name>__<hash>.meta.toml   the request, the capture time, the status
  INDEX.md                     one line per response
```

The response file is never edited. The provenance record — the second file
beside it — carries everything about how the answer was obtained, because the
moment you write that into the response itself, "this is real data the server
really sent" stops being true. That sentence is load-bearing.

`INDEX.md` is the file to point at when you say on stage that the captures were
taken on a particular date.

## The services it calls

Every endpoint was queried live and returned real results. They are named in
one place, [`corridor_screen/sources.py`](corridor_screen/sources.py), together
with the field list each one is expected to publish.

| Purpose | Service | Layer |
|---|---|---|
| Alignment | `TxDOT_Roadways` on TxDOT's ArcGIS Online org | 0 |
| Corridor buffer | Esri's public geometry service | — |
| Parcels | `BCAD_Parcels` via the City of San Antonio | 0 |

**Layer numbers are load-bearing.** TxDOT's control points are layer 67 and its
land parcels are layer 328. A query against layer 0 does not error — it answers
with the wrong data. That is why the tool reads each layer's own field list
before it sends a single query, and refuses to run when the list is not what it
expects.

## The tests

```bash
python -m unittest discover -s tests -t .
```

They use `unittest` from the standard library rather than a test runner that
has to be installed, for the same reason as everything else here.

## On feet

The half-width is in **international feet**, not US survey feet, and the reason
is worth a sentence. The parcel service accepts only that foot — it rejects
`esriSRUnit_SurveyFoot` outright, and answers a US survey foot *code* as if it
were meters, silently. The corridor buffer therefore uses the same foot, so the
drawn corridor is the ribbon the parcels came from. At 300 feet the two differ
by about six ten-thousandths of a foot. The whole finding is written up in
[the geometry service page](../docs/data-sources/arcgis-geometry-service.md).

## A Windows note

Windows refuses to open a file whose path is longer than 260 characters, and
the failure looks like a file-not-found error on a directory that plainly
exists. A project living under something like
`OneDrive - A Fairly Long Firm Name\Documents\Projects\...` reaches that limit
easily. The cache asks Windows for the extended form of every path, so this
works wherever the project happens to sit.
