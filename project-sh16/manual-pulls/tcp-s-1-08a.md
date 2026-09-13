# TCP(S-1)-08A — what it does to crew time

Read with the sheet open: [`tcp-s-1-08a.pdf`](tcp-s-1-08a.pdf). Provenance is in
[`tcp-s-1-08a.pdf.meta.toml`](tcp-s-1-08a.pdf.meta.toml). Every statement below
is on the sheet; nothing here is inferred from a different standard.

## The effect on crew time, in one paragraph

TCP(S-1)-08A puts the duration line for a survey crew at **one hour**. Work that
occupies a location up to one hour is *short duration*; work that holds a
location for more than one hour inside a single daylight period is *short term
stationary*. Staying under the hour buys two reliefs, and only two: the G20-2a
"END ROAD WORK" sign may be omitted (Note 1), and the channelizing devices on
the shoulder taper and tangent section may be omitted (Note 2). Cross the hour
and both come back — a sign, a run of cones, and the time to set and retrieve
them. That is billable time, not a second vehicle. What actually adds a vehicle
is **Note 3**: if line-of-sight requirements for the surveying operation will
not allow the work vehicle to be parked where it protects the crew, the Note 2
channelizing devices are required *regardless of duration*. That is the
surveying-specific trap, because sighting down a line is the job. The shadow
vehicle with a truck-mounted attenuator (TMA) appears in **Note 4** as a
permitted **substitute** for the work vehicle — an option, not a penalty the
clock triggers.

## The rest of what the sheet says

- Two cases are drawn: **TCP(S-1a) work off shoulder** and **TCP(S-1b) work on
  shoulder or paved surface**.
- Advance sign spacing: **3X where the posted speed is 50 mph or less, 1500 ft
  where it is over 50 mph.** `X` comes from the sheet's own spacing table.
- Note 5 — the CW20-1D "ROAD WORK AHEAD" sign may be substituted for the
  CW21-6D "SURVEY CREW AHEAD" sign.
- Note 6 — the plan may also be used for shoulder and off-shoulder work on
  **multilane undivided** roadways.
- Note 7 — the "SURVEY CREW AHEAD" sign at a low-volume intersecting side road
  is *desirable but not required* when working **less than 15 minutes** in the
  area of that side road, **as determined by the Engineer**. This is the only
  15-minute figure on the sheet, and it governs one sign at a side road. It is
  not a crew-configuration threshold.
- Note 8 — cones may be placed at the edge of pavement next to the work space
  to enhance safety. *May*, not *shall*.
- The sheet carries TxDOT's own banner: **"WHENEVER POSSIBLE, SURVEY PARTIES
  SHOULD AVOID, BY THE USE OF OFFSET LINES, ANY UNNECCESSARY PERIODS OF TIME ON
  THE ROAD SURFACE."** The misspelling of *unnecessary* is TxDOT's and is
  reproduced here as printed. The sheet's one revision, dated 8-18-08, is
  recorded as "Corrected misspelling," which evidently did not catch this one.

## What this sheet does not cover

The spacing table is footnoted **"Conventional Roads Only."** TCP(S-1)-08A does
not speak to divided highways or controlled-access facilities. Five further
sheets in the same family exist — TCP(S-2)-08A, TCP(S-2c)-10, TCP(S-3)-08,
TCP(S-4)-08A and TCP(S-5)-08 — and are **not in this repo yet**. Until they
are, say "not found on TCP(S-1)" rather than "TxDOT does not require it."

## A claim in this repo that this sheet does not support

`docs/txdot-research.md` currently carries this, and says plainly that it was
read across from the mobile-operations standard **TCP(3-1)** because TCP(S-1)
could not be fetched at the time:

> mobile TCPs apply on conventional roads ≤45 mph for work stopping up to ~15
> minutes. Beyond either threshold, a stationary TCP is required — shadow
> vehicle with TMA, arrow board, signing, radios.

and the soundbite drawn from it:

> **A 20-minute shot on a 55-mph highway converts a two-person crew into a crew
> plus shadow truck.**

**TCP(S-1)-08A does not say that.** On this sheet the duration line is one hour,
not fifteen or twenty minutes; the consequence of crossing it is signs and
cones, not a truck; and the TMA shadow vehicle is an alternative to the work
vehicle rather than an addition to the crew.

That is **not the same as saying the claim is wrong.** TCP(S-1) is conventional
roads only, and a 55-mph highway may well be a divided facility covered by one
of the five sheets listed above. The honest statement today is that the claim is
**unsupported by the surveying standard now in hand, and unresolved** until the
rest of the family is pulled. It should not be repeated on stage in its current
form. Correcting `docs/txdot-research.md` is its own issue, not this one.
