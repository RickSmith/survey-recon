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

The spine, from [issue #13](https://github.com/RickSmith/survey-recon/issues/13),
and the flags that hang off it, from
[issue #17](https://github.com/RickSmith/survey-recon/issues/17).

| Step | Built |
|---|---|
| Reachability ping on every service | yes |
| Field list confirmed before any query | yes |
| Alignment from a route name and two DFO numbers | yes |
| Corridor buffer, fetched once and cached | yes |
| Parcels from the CoSA BCAD service | yes |
| Every response cached with its provenance record | yes |
| Flags — schools, cemeteries, railroads, pipelines | yes |
| Lead time on every flag, with its citation | yes |
| The longest wait on a parcel, without arithmetic | yes |
| NGS marks in the corridor, carrying their condition | yes |
| TxDOT control points, ROW map sheets, roadway facts | not yet, separate work orders |
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
| `--sanity-margin-ft` | How far outside the ribbon any part of a parcel may sit before the run doubts it. Default 500 |
| `--adjacent-distance-ft` | How close a feature must be to a parcel to earn an `adjacent` flag. Default 100 |
| `--corridor-flag-parcels` | How many parcels one feature must cross before it is also recorded against the run. Default 5 |
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

Four parts of it are worth knowing by name.

**The wrong-file check** — the corridor length, both end points and a web map
link, printed before any service is called and recorded in the output. A
misread route does not look like a subtle error. It looks like a
four-thousand-mile corridor on line one.

**The honesty block** — `services`, one entry per service: what was asked, of
what, whether it answered, how many times it had to be asked, which cached file
holds the answer, and what was doubted about it. It is what lets somebody else
decide whether to trust the rest of the file.

**`screened_for`** — the flag types actually checked for each parcel. It is
built from the services that actually answered, never from the list of types the
tool knows about. A flag service that was blocked today leaves its type off this
list, and no parcel is then reported as clear of it. A parcel that could not be
checked is `unknown`. It is never `no`.

**`control`** — the NGS marks inside the corridor, each carrying its PID and the
condition it was last left in, and `recovery_risk` counting the ones stamped
`MARK NOT FOUND`. A run that never reached the service writes a `not-screened`
block naming why, rather than an empty list — because "no marks here" and
"nobody looked" are different answers and only one of them is good news.

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
| Schools | USGS `structures` on `carto.nationalmap.gov` | **23** |
| Cemeteries | USGS `structures`, same server | **2** |
| Railroads | USGS `transportation`, same server | **38** |
| Pipelines | **TPMS**, Railroad Commission of Texas | 0 |
| NGS marks | `NGS_Datasheets_Feature_Service` on `services2.arcgis.com` | 1 |

The four flag services each have a quirk worth knowing, and two of them return
a plausible wrong answer rather than an error. They are written up in
[the flag services page](../docs/data-sources/flag-services.md).

The NGS datasheets service has a quieter one: the condition field is called
`LAST_COND` there and `condition` on NGS's other API, and asking for the wrong
name returns nothing and raises nothing. It is written up on
[the NGS datasheets page](../docs/data-sources/ngs-datasheets.md).

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

## How a parcel is checked against the corridor

The service is asked which parcels **intersect** the ribbon, and the sanity
check tests that answer the same way it was asked: does **any part** of the
parcel come near the corridor. Not its center point — a 189-acre tract clipped
by a 600-foot ribbon has its frontage on the pavement and its center a quarter
mile away, and that is the parcel an estimator most needs to see.

The distance is measured from the centerline, against the half-width plus
`--sanity-margin-ft`, which defaults to 500. At the default half-width that
means a parcel is doubted only when every part of it is more than 800 ft from
the centerline. It is slack for a filter that is working, not a second corridor.

Set the margin to `0` and the check agrees with the CoSA service's own spatial
filter on all 530 records the SH16 corridor returns. Two independent pieces of
geometry, same answer.

## How an NGS mark is checked against the corridor

Differently, and on purpose. A mark is a **point**: it is within the half-width
of the centerline or it is not. No margin and no neighbor distance. A parcel is
an area and can be clipped by a ribbon; a point cannot.

That strict test is what builds the list rather than what doubts it. The tool
asks the service about a box around the corridor, then measures every mark
itself and keeps the ones inside — so the honesty block reports "31 returned, 11
in the corridor", the same pair of numbers the flag services report.

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

## Flags, and the lead times they carry

A **flag** is something on a parcel that costs time. A **lead time** is the
delay before you can enter — not how long the work takes, but how long you wait
for permission before it can start.

Four types are screened: **school, cemetery, railroad, pipeline.**

**`on` and `adjacent` are recorded separately and never merged.** A feature
inside the parcel is `on` it. The same feature within `--adjacent-distance-ft`
is `adjacent`, and carries the measured distance. A party chief needs to know
about both. An estimator must not count both.

**Every lead time carries its citation.** The numbers live in
[`corridor_screen/lead_times.toml`](corridor_screen/lead_times.toml), which is
checked-in data rather than code, and the loader refuses to read a row with no
source and no link. A lead time with no citation is a rumor with a number on it.

| Flag | Lead time | Where it comes from |
|---|---|---|
| Railroad | **45 calendar days** (published range 30–45) | Union Pacific's own procedures page. Corporate procedure, not statute |
| Cemetery | **14 calendar days** | Tex. Health & Safety Code § 711.041(c)(2) |
| Pipeline | **2 working days** (48 hr floor) | Tex. Util. Code § 251.151(a) |
| School | **not found** | § 22.0834 is background checks, not a notice period |

**Every number says which days it counts.** Two working days and two calendar
days are different promises — § 251.151(a) excludes weekends and legal holidays,
§ 711.041 does not — and the tool will not convert one into the other, because
that would mean inventing a calendar it cannot check. So `lead_time_basis` rides
on every flag, `max_lead_time_basis` on every parcel row, and the table's loader
refuses a number that does not say.

The full wording, the limits on each number and the account of where we looked
are in [Lead times and their sources](../docs/corridor-screen/lead-times.md).

**Two numbers sit side by side on every parcel row**, and both are needed:

- `max_lead_time_days` — the longest confirmed wait, so nobody has to do
  arithmetic to find the parcel that drives the schedule. `lead_time_driver`
  names which flag set it and `max_lead_time_basis` says which days it counts
- `lead_time_not_found` — the flag types on that parcel whose lead time could
  not be confirmed

A parcel with a cemetery and a school shows **14 days** *and* `school` in the
not-found list. Fourteen is the longest number anybody can stand behind, and it
is not the whole answer.

## What SH16 returns

Run on 2026-09-12 at the default 300 ft half-width:

| Flag | Returned | On a corridor parcel |
|---|---|---|
| School | 39 | 6 |
| Cemetery | 6 | 1 |
| Railroad | 0 | 0 |
| Pipeline | 0 | 0 |

Eight of 524 parcels carry a flag. The longest wait is **14 calendar days**, on
the Episcopal Church parcel at 11093 Bandera Rd, which carries a columbarium.

**Zero railroads is a checked answer, not an empty one.** The same USGS layer
returns 412 records across Bexar County. There is simply no track within 300 ft
of this stretch of Bandera Road.

Both numbers are in the honesty block — `record_count` and `records_used` — so a
reader sees "39 returned, 6 used" rather than a bare 6. The flag services are
asked about a box drawn around every parcel in the corridor, which is wider than
the ribbon, so the 33 unused schools are a normal answer to the question that was
asked. Hiding them would make the 6 look like the whole world.

### The control

| | |
|---|---|
| NGS marks returned | 31 |
| Inside the 300 ft corridor | **11** |
| Of those, `MARK NOT FOUND` | **11** |
| Of those, condition unknown | 0 |

**Every NGS mark within 300 feet of this centerline is one NGS could not find.**
The last recovery attempts run from 1995 to 2002. Each row carries a
`datasheet_url` straight to that mark's full NGS record, because `MARK NOT FOUND`
starts a decision rather than ending one. A run that reported "11 marks
in the corridor" and stopped there would have an estimator pricing recovery on
eleven marks that three decades of looking could not turn up. That is the whole
reason `condition` is carried through and never dropped.

Two of the twenty marks outside the ribbon are `GOOD`. They are real, and they
are close — they are simply further from the centerline than the stated
half-width. Hunting control is a good reason to run again with a wider
`--half-width`, which is what the number is settable for.

**TxDOT primary control is a separate work order**, issue #15. The output names
`txdot_points` as `not-screened` rather than leaving it out, so a missing block
never reads as an empty one.
