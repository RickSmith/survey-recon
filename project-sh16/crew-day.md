# Crew-day build-up — SH0016-KG DFO 347.7 to 356.367

**This is not an estimate. It is an estimate somebody can argue with.**

Every quantity below is read from `screening.json`. Every rate is an assumption, **not a published standard** — TxDOT publishes no production rates, and this tool has never been near the corridor. Nobody has walked it. The rates carry handles, `A1` through `A11`, so a surveyor can disagree with one of them out loud, by name, rather than disagreeing with the total.

An **RPLS** reads this and decides. The tool decides nothing.

## What went in

| Input | Value | Where it came from |
|---|---|---|
| Corridor length | 8.691 miles | alignment.length_mi |
| Tracts the corridor touches | 524 tracts | parcels[] |
| Tracts carrying something that costs time | 8 tracts | parcels[].flags |
| Published NGS marks in the corridor | 11 marks | control.recovery_risk.marks_in_corridor |
| Of those, recorded MARK NOT FOUND | 11 marks | control.recovery_risk.mark_not_found |
| Distinct TxDOT control monuments | 2 monuments | control.txdot_control.distinct_stations |
| ROW map sheets reaching the corridor | 69 sheets | row_maps.sheet_count |
| Manholes to pop | **not measured** | no service in this run publishes a manhole inventory |
| Culverts to locate | **not measured** | no service in this run publishes a culvert inventory |
| Times traffic control has to be set | **not measured** | derived from the manhole and culvert counts, which are unmeasured |
| Existing ROW width, lane count and traffic | **not measured** | roadway |

**4 of these 11 inputs were never measured**, and they are not zero. Each one below is a question somebody still has to answer, and the arithmetic that needs it is left without a total rather than given a convenient one.

- **Manholes to pop** — No public source screened here publishes manhole locations. A count would have to come from a utility owner, from as-builts, or from somebody driving it.
- **Culverts to locate** — Same: not screened. TxDOT holds drainage inventories that this pass does not call.
- **Times traffic control has to be set** — This is what the two counts above are for. Each manhole or culvert in or beside the travel way is an occupation needing signing and devices. With neither count, this number does not exist and the traffic-control line below has no total.
- **Existing ROW width, lane count and traffic** — existing right-of-way width, lane count and traffic come from Roadway_Inventory_2023, which this pass does not call

## Field hours

**Look for the published NGS marks**

> 11 marks × 0.75 hours per mark = 8.25 hours

- Published NGS marks in the corridor — run control.recovery_risk.marks_in_corridor
- Recovery attempt per published mark — rate A1 (hours_per_mark_recovery_attempt)

All 11 of the 11 marks in this corridor are already recorded MARK NOT FOUND. Somebody has looked for each one and could not find it. Whether to look again is a judgment for the surveyor who signs.

**Set new control**

> 8.691 miles × 0.5 pairs per mile × 3 hours per pair = 13.04 hours

- Corridor length — run alignment.length_mi
- New control pairs to set, per mile — rate A2 (control_pairs_per_mile)
- Hours to set and occupy one control pair — rate A3 (hours_per_control_pair)

On this evidence the control work is setting new rather than recovering existing. That is the largest single judgment in this estimate and it is the surveyor's, not the tool's.

**Recover corners, tract by tract**

> 524 tracts × 0.5 hours per tract = 262.00 hours

- Tracts the corridor touches — run parcels[]
- Corner recovery per tract the corridor touches — rate A4 (hours_per_tract_corner_recovery)

The biggest line on the page, and the first one to argue with.

**Extra time on the flagged tracts**

> 8 tracts × 2 hours per tract = 16.00 hours

- Tracts carrying something that costs time — run parcels[].flags
- Extra time per flagged tract — rate A5 (hours_per_flagged_tract_access)

Field hours only. The days of notice before the crew may go at all are in the flagged parcel table, and they are days rather than hours.

**Set and retrieve traffic control**

> not measured × 1.25 hours per occupation = not measured

- Times traffic control has to be set — run derived from the manhole and culvert counts, which are unmeasured
- Set up and take down traffic control, per occupation — rate A6 (hours_per_road_occupation)
- **No total: Times traffic control has to be set was never measured.**

This line has no total, and that is the finding. Nothing in this run counts manholes or culverts, so nobody knows how many times the crew has to close down and set up. It is not zero. It is unmeasured, and on a job like this it is where the time goes.

**Field hours total: 299.29 hours.**

299.29 hours ÷ 8 hours per crew-day = **38 crew-days**, rounded up.

**That total is a floor.** 1 line above could not be totalled at all, and the hours are missing from this figure rather than being zero in it: *Set and retrieve traffic control*.

## Office hours

**Hand-retrace the ROW map sheets**

> 69 sheets × 1.5 hours per sheet = 103.50 hours

- ROW map sheets reaching the corridor — run row_maps.sheet_count
- Hand retracement per ROW map sheet — rate A7 (hours_per_row_sheet_retracement)

Sheets in this corridor run from 1900 to 2005. Scans of that age are read by eye, and the oldest date may not be a date at all — the bid memo says why.

**Draft the deliverable**

> 8.691 miles × 4 hours per mile = 34.76 hours

- Corridor length — run alignment.length_mi
- Drafting and deliverable, per mile — rate A8 (office_hours_per_mile_drafting)

**Office hours total: 138.26 hours.**

138.26 hours ÷ 8 hours per day = **18 office days**, rounded up.

## The two are not added together

**38 crew-days in the field. 18 days in the office.** They are different things bought from different people, and adding them makes a number that cannot be checked against anything.

A crew-day here is **2 people** for 8 productive hours. Putting a third person on the truck does not divide the hours by three, and this build-up will not pretend it does.

## Traffic control, from the sheet itself

Everything in this section is read from **TCP(S-1)-08A**, pulled by hand and committed at [`project-sh16/manual-pulls/tcp-s-1-08a.pdf`](manual-pulls/tcp-s-1-08a.pdf). Nothing is read across from another standard, which is how this repo got it wrong once already.

**One hour is the line, not twenty minutes.** Work occupying a location up to one hour is short duration. Past the hour, two reliefs lapse: the G20-2a END ROAD WORK sign may no longer be omitted (Note 1), and the channelizing devices on the shoulder taper and tangent section may no longer be omitted (Note 2). That is a sign, a run of cones, and the time to set and retrieve them. It is billable time, not a second vehicle.

**Note 3 is the surveying-specific trap.** Where line-of-sight requirements will not allow the work vehicle to park where it protects the crew, the channelizing devices of Note 2 are required — so the under-an-hour relief does not apply and the devices stand whatever the duration. Sighting down a line is the job, so on a survey this is the ordinary case rather than the exception, and the estimate below charges the setup either way.

**No posted speed puts a shadow truck on this job.** Not found on any of the six TCP(S-*) sheets: 55 mph is an ordinary row in every spacing table. On TCP(S-1) the shadow vehicle with a truck mounted attenuator appears in Note 4 as a permitted substitute for the work vehicle, which is an option rather than a penalty the clock triggers.

**A lane closure is a different sheet, and a different cost.** TCP(S-1) draws only two cases, work off the shoulder and work on the shoulder. Popping a manhole in a travel lane is not one of them: that is TCP(S-2) or TCP(S-3) work, and those sheets *draw* a shadow vehicle with a truck mounted attenuator — two of them on TCP(S-3b), work on centerline. The permission to substitute an ordinary work vehicle is granted for short duration work, so past the hour it lapses. This is the real cost cliff, and it is driven by where the work is rather than by how fast traffic is moving.

**Conventional Roads Only.** Every sheet in the family carries that footnote, and none uses the words freeway or controlled access. Whether this corridor is any of those was not read by this run. Freeway coverage is not found, which is not the same as absent.

The duration line is **1 hour**. Whether this corridor's work crosses it, and how often, depends on the manhole and culvert counts nobody has. That is why the traffic-control line above has no total.

## Every assumption, with its handle

Disagree with a row, not with the total. Each of these is somebody's judgment, and none of them is published by TxDOT or by anybody else.

| | Rate | Value | What to argue with |
|---|---|---|---|
| `A1` | Recovery attempt per published mark | 0.75 hours per mark | A firm that accepts NGS's own MARK NOT FOUND and does not go looking sets this to zero for those marks. That is a defensible call and it is not this tool's to make. |
| `A2` | New control pairs to set, per mile | 0.5 pairs per mile | Spacing is a methodology choice, not a fact. A firm working RTK off a network may set far fewer; a firm running conventional traverse may set more. |
| `A3` | Hours to set and occupy one control pair | 3 hours per pair | Occupation length is the argument here. Shorten the session and this halves; require an OPUS-shareable solution and it grows. |
| `A4` | Corner recovery per tract the corridor touches | 0.5 hours per tract | Start here. This assumes the crew works every tract the corridor clips. On an urban arterial most are small lots whose corners fall out of one setup, and some are already in TxDOT's hands. Halve this number and the field estimate moves more than any other change on the page. |
| `A5` | Extra time per flagged tract | 2 hours per tract | This is a field-hours figure only. The notice period before the crew may go at all is a separate thing entirely, is measured in days rather than hours, and lives in the flagged parcel table beside this file. |
| `A6` | Set up and take down traffic control, per occupation | 1.25 hours per occupation | The quantity, not the rate. This is multiplied by the number of road occupations, and nothing in this run counts them — see the manhole and culvert lines. The rate itself is one crew setting cones on a conventional road. |
| `A7` | Hand retracement per ROW map sheet | 1.5 hours per sheet | Legibility is the whole argument. A clean 1998 sheet is not a 1944 scan, and this single rate covers both. Split it by decade if your reader will bear it. |
| `A8` | Drafting and deliverable, per mile | 4 hours per mile | Per mile is the wrong unit and it is the one the run can supply. Drafting scales with tract count and sheet count far more than with distance. |
| `A9` | Productive field hours in one crew-day | 8 hours per crew-day | Most firms will say this is high. A long haul to a San Antonio corridor, or summer heat, and six is closer. Lowering it raises the day count directly. |
| `A10` | Productive office hours in one day | 8 hours per day | Anybody splitting their week across jobs is not giving this one eight hours a day, and the office day count below assumes they are. |
| `A11` | People in the field crew | 2 people | TCP(S-2c)-10 Note 8 binds a two-person crew on a two-lane road hard — the rodman may only enter the roadway accompanied by a flagger. A flagger is a third person, and none of the rates above carry one. |

The reasoning behind each one is in [`crew_rates.toml`](../corridor-screen/corridor_screen/crew_rates.toml), which is plain text a firm edits without touching any Python. **Replace these with your own rates before quoting anything.**

## What this build-up is not

It is **not a quote**. There is no rate per day here, and no total in dollars.

It is **not a schedule**. Days of work are not days on the calendar: the notice periods that decide when a crew may go at all are in the flagged parcel table, counted in days of two different kinds.

It is **not a measured job**. Nobody has walked this corridor. Every count came from a public map service on the date the run records.

It is a first pass, with the arithmetic left open so somebody who knows the work can correct it. **An RPLS reads it and signs, and remains accountable for every number that reaches a client.**

---

Run `live`, finished 2026-09-13T07:07:07-05:00. Built by corridor-screen 0.1.0 from `screening.json` and `crew_rates.toml`. Nothing here was typed by hand.
