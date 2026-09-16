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
| ROW map sheets over the corridor, and how far back they go | yes |
| The crew safety sheet — nearest hospital, EMS and police | yes |
| The whole tool replaying offline, checked against the live run | yes |
| One genuinely live call, cross-checked against the capture | yes |
| The bid memo — the document a principal reads before pricing | yes |
| The flagged parcel table, with its projector drawing | yes |
| The crew-day build-up, with every rate open to argument | yes |
| TxDOT primary control points, on layer 67 | yes |
| Roadway facts — ROW_MIN, lanes, traffic | not yet, a separate work order |
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
| `--safety-search-miles` | How far around the corridor to look for the nearest hospital, EMS and police. Default 25. Raise it on a rural corridor |
| `--mode` | `live`, `cache-first` (default) or `cache-only` |
| `--out` | Where the output file and the cache are written |
| `--yes` | Never ask about a dead service. Stop instead. Use for unattended runs |

## If the network is down

**Mid-session, open [the fallback card](../docs/presenting/fallbacks.md)
instead of this page.** It is one page, in clock order, covering the whole
two hours rather than this tool alone.

**This is the line to run.** From this directory, nothing else needed:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only
```

It makes **no network calls at all**, not even the reachability ping. Every
answer comes off the disk, from the capture committed in this repo. You should
see `ping  ... skipped` on every service, and the run should finish with
`parcels     524`.

If a request was never captured, it names that exact request and stops. It
never guesses and it never quietly returns a shorter list.

The cache never expires on its own. `--mode live` is the only refresh, because
a cache that quietly re-fetches on the morning of a session is a hazard rather
than a feature.

### Why you can trust the cached numbers

Because it is checked, not asserted. A live run and a cache-only run of SH16
were compared on 2026-09-13 and differed in exactly **74 places, every one of
them the run's own account of itself** — when it started and finished, its run
id, its mode, and five fields on each of the fourteen services saying whether
each host was pinged, how many times it was asked, and whether the answer came
off the disk. Every parcel, flag, lead time, survey mark, ROW sheet and the
whole crew safety sheet were identical.

The comparison is a command you can run:

```bash
python -m corridor_screen.replay one-run/screening.json another-run/screening.json
```

It prints what differs, then prints what it allowed to differ and why. It
finishes successfully only when every finding matches.

**What to compare against what.** It answers one question: did a replay find
what the live run found. So compare a live run against a replay **of that same
capture** — the two runs either side of one `--mode live`. Comparing a fresh
live run against a replay of an older capture will report differences, and it
should: the two ran against the services on different days, and `captured_at`
says so on every service. That is the field working, not the check failing.

The same comparison runs in the test suite against the committed capture, **with
the network taken away** — not politely asked for, actually removed, at the
level below every library that could reach for it. See `tests/test_offline.py`.
That test is the one that would catch a stray live call before a session rather
than during one.

## The renderings

The screening run fetches once; separate commands read that one file and write
what a person actually reads. All three are built:

```bash
python -m corridor_screen.bid_memo --out ../project-sh16
```

It writes `bid-memo.md` — the document a principal reads before pricing. It
prices nothing and decides nothing. What it does carefully is keep **what is not
known** in its own section near the front, ahead of the findings that depend on
it, rather than as a footnote under a total.

It will not print a number the run did not measure. `acres_in_corridor` is not
implemented, so the memo says the take was not measured rather than summing a
column of nothing into "0.0 acres".

The second is the flagged parcel table:

```bash
python -m corridor_screen.parcel_table --out ../project-sh16
```

It writes **two** files from the same data. `flagged-parcels.md` is the one a
reader keeps and a pull request can diff. `flagged-parcels.svg` is the one that
goes on a projector. **SVG is a drawing stored as text rather than as pixels** —
it redraws itself at whatever size it is shown at, the way a vector plot stays
sharp where a scan goes blocky. [Spec section
9](../docs/corridor-screen/spec.md) picked it for exactly that: it "stays sharp
on a projector at any size," commits to git as text, and needs nothing
installed.

**The interesting column is the one with no number in it.** On SH16, seven of
the eight flagged tracts carry a school, and no published notice period was
found for one — see [lead times](../docs/corridor-screen/lead-times.md), which
records where it looked. That column never prints a blank, a dash or a zero. It
prints `not found — school`, because an unmeasured wait and no wait are not the
same statement, and the difference is worth more on a projector than anywhere
else.

The drawing shows twelve rows. A corridor with more says how many it did not
show rather than quietly ending at twelve; the Markdown carries all of them.

The third is the crew-day build-up:

```bash
python -m corridor_screen.crew_day --out ../project-sh16
```

It writes `crew-day.md`, the build-up itself, and `crew-day.txt`, the same
thing as a plain text fallback for a podium where Python will not start. Both
are written every run, so the capture [#27](https://github.com/RickSmith/survey-recon/issues/27)
audits is recorded as the work happens rather than when somebody remembers a
flag.

**The output is not a number.** It is eleven labeled inputs, seven lines of
arithmetic and two totals, because a room of firm owners is going to argue with
it and that is the only thing that makes it worth anything. Every rate carries
a handle — `A1` to `A11` — so a surveyor can disagree with one row out loud
rather than disagreeing with the total.

**Every rate is an assumption and says so.** TxDOT publishes no production
rates: the standard sheets say what goes on the road, not how long it takes to
put it there. They live in
[`corridor_screen/crew_rates.toml`](corridor_screen/crew_rates.toml), which is
plain text a firm edits without touching Python, and the loader refuses a row
whose `source` names TxDOT unless it carries a URL somebody opened and the date
they opened it.

**The traffic-control line has no total, and that is the finding.** Nothing in
this run counts manholes or culverts, so nobody knows how many times the crew
has to set up and take down. That is not zero, and on a job like this it is
where the time goes. The rest of the traffic control is read from
`TCP(S-1)-08A` itself: the duration line is **one hour**, and **no posted speed
anywhere in the six-sheet family puts a shadow truck on the job.**

## The drawings

Surveyors read drawings, and until this command the job came with a JSON file.
It draws the run:

```bash
python -m corridor_screen.drawings --out ../project-sh16 --copy-to ../docs/scenarios/sh16/img
```

It writes five SVG files into `project-sh16/drawings/`, and the same five again
wherever `--copy-to` points, which is where the site can show them.

| Drawing | What it shows |
|---|---|
| `corridor-map.svg` | The centerline, the 300-foot ribbon, all 524 tracts, and the 8 flagged ones numbered |
| `control-map.svg` | The 11 NGS marks, each with its PID and `MARK NOT FOUND`, and the 2 TxDOT monuments |
| `crew-safety-map.svg` | The nearest hospital, ambulance, fire and police, with a straight line to the nearer end of the corridor |
| `how-it-works.svg` | The tool in one picture: a line in, fourteen services asked, one file out, three documents, one surveyor |
| `crew-day-sheet.svg` | The build-up laid out as a sheet, with the two lines that have no total shown as having no total |

**Nothing on a drawing is drawn by hand.** Every shape comes from the cached
service responses the run names, and every number is read from
`screening.json`. The tests read the numbers back out of the SVG and compare.

**The copies under `docs/` are held to the sources.** A test fails if a copy
differs from its source by one byte, and another fails if re-drawing the
committed run does not reproduce the committed files. So after any change to
this command or to the run, run it again with `--copy-to` and commit what it
wrote. The site never shows an older drawing than the run it describes.

The maps have no basemap and no street names beyond the two ends of the
corridor, because the tool never had any. That is a limit and it is stated on
each map. The bid memo carries a link to the ground.

## The check that keeps a citation honest

```bash
python -m corridor_screen.manual_links --show
```

Failure beat one of the session, and it runs entirely from files committed in
`captures/superseded-manual/` — so a hotel network cannot take it away from you.

Search still hands out `onlinemanuals.txdot.gov` links for the TxDOT Survey
Manual. **That host is still listed in DNS — the internet's phone book — and
answers nothing**, so an agent sees a timeout rather than a 404, which looks
exactly like bad Wi-Fi and invites a retry. The manual moved, and the two are
not the same document: the old address last served **March 2025, Manual Notice
2025-1**, and the one in force is **April 2026, Manual Notice 2026-1**.

The other half is the one that earns its keep every day:

```bash
python -m corridor_screen.manual_links --check .
```

It fails if any page or module here cites a superseded address, and prints the
`txdot.gov` one to use instead. CLAUDE.md has forbidden those URLs from early
on; this is what makes that rule something other than a sentence nobody runs.
It is in the test suite. The full account is on
[the superseded manual](../docs/managing-your-agent/the-superseded-manual.md).

## The beat about the answer you cannot check

```bash
python -m corridor_screen.elevation_trap --show
```

Failure beat two, running entirely from files committed in
`captures/silent-nodata/` — so a hotel network cannot take it away.

Ask the USGS elevation service for the height of SH16 at Bandera Road, twice,
one word apart. `units=Feet` gives **866.8668528742528**. `units=US_Feet` gives
**"264.221008301"**. The ratio is 3.28084, which is feet per meter: it is the
same ground, answered in meters, with no error and **no field anywhere in the
response saying which unit it is**.

`US_Feet` is not a typo. It is the US survey foot — what EPSG numbers `9003`,
and what [the geometry service](../docs/data-sources/arcgis-geometry-service.md)
also accepts and silently treats as meters, returning 2,132 parcels where the
right unit returned 658. Two services, same silence.

The same endpoint *can* fail loudly — a point in the Gulf of Mexico returns a
200 carrying plain text, which breaks any parser and gets noticed in a second.
That comparison is the beat: the broken answer is caught by anything that reads
it, and the plausible one is caught by nothing. The full account is
[the wrong answer](../docs/managing-your-agent/the-wrong-answer.md).

## The letter that sends itself

```bash
python -m corridor_screen.roe --show
```

Not a failure beat — nothing in it is wrong. It is the Hermes segment, and it
runs from files committed in this repo, so a hotel network cannot take it away
either.

**Right of entry is not a statutory right in Texas.** You ask, and the owner may
say nothing at all. TxDOT ships **two** letter templates for that reason. The
second one is the work firms forget, and this writes it on a clock nobody has
to remember.

**Day 21 is derived, not typed.** No published right-of-entry turn-around was
found in any TxDOT manual this repo read, so there is no number to quote.
Instead: the longest confirmed wait in
[`lead_times.toml`](corridor_screen/lead_times.toml) counted in calendar days is
the railroad's **45**; halve it so the second letter gets the window the first
one had, **22**; round down to whole weeks because a letter moves in weeks,
**21**. Put 60 in the railroad row and the follow-up moves to day 28. The full
argument is on
[the right-of-entry letters page](../docs/corridor-screen/roe-letters.md).

To write whatever is due today:

```bash
python -m corridor_screen.roe --write ../project-sh16/roe
```

Before 2026-10-04 that writes one letter and says the second is not due. On or
after it, two — and nobody had to remember. It mails nothing, signs nothing and
carries no address. An **RPLS** does all three.

**Nobody has to run it either.** `.github/workflows/roe-followup.yml` reads the
same clock every day on a schedule and puts whatever is due into the run
summary. It commits nothing and needs no secret. That workflow is the evidence
behind "with no human action"; the command above is the rehearsal of it.

## The one call that stays live

Everything above replays from disk. This one goes out to NGS while you watch:

```bash
python -m corridor_screen.live_check --out ../project-sh16
```

It is worth making because **it asks a different NGS endpoint than the screening
run uses** — the Data Explorer API with a point and a radius, against the
datasheets feature service with a corridor. Different service, different query,
different spellings of the same fields. So when the two agree about a mark, that
is a cross-check rather than a recording agreeing with itself.

Run on 2026-09-13 against the committed capture: 5 marks appear in both, and
**all 5 conditions agree** — `MARK NOT FOUND` on every one.

A mark in one and not the other is ordinary, and never reported as a
disagreement: a circle around the midpoint and a 300-foot ribbon are different
questions. A condition that *has* changed is printed loudly and is not an error
— it means NGS updated a record since the capture, which is the tool being right
about how old its data is.

**If there is no network,** it says so and says the screening run is unaffected.
That is why it is a separate command and not a mode: the worst a dead network
can do is cost the live moment.

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
| TxDOT control | `Primary_Control_Points`, the San Antonio district's | **67** |
| ROW map sheets | `ROW_Maps_CL_2017` on `maps.dot.state.tx.us` | 0 |
| Hospitals · Ambulance · Fire and EMS · Police | USGS `structures`, same server as the flags | **14 · 15 · 16 · 18** |

The four flag services each have a quirk worth knowing, and two of them return
a plausible wrong answer rather than an error. They are written up in
[the flag services page](../docs/data-sources/flag-services.md).

The NGS datasheets service has a quieter one: the condition field is called
`LAST_COND` there and `condition` on NGS's other API, and asking for the wrong
name returns nothing and raises nothing. It is written up on
[the NGS datasheets page](../docs/data-sources/ngs-datasheets.md).

The ROW map service has the loudest one in the tool. Its dates arrive as
milliseconds rather than text, so every sheet older than 1970 is a **negative**
number — and on Windows the obvious way to read one raises an error instead of
returning a wrong date, on exactly the oldest sheets. It is written up on
[the ROW map sheets page](../docs/data-sources/row-map-sheets.md), together with
why this corridor reports 15 SH16 sheets where the county reports 27.

The crew safety layers sit on the same USGS server as the flags and carry a
quirk of their own: **every layer on that server exists twice**, once under a
`Labels` group and once under a `Features` group, so hospitals are layer 14 and
also layer 49. Both copies answered identically when checked, which is the only
reason it does not bite. That, and the reason every distance on that sheet is
labeled a straight line rather than a drive, are on
[the crew safety page](../docs/data-sources/crew-safety.md).

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
