# The TCP(S-*) family — what TxDOT actually requires of a survey crew

Six standard sheets, all titled **"Traffic Control Plan for Surveying
Operations,"** all published by TxDOT's Traffic Operations Division. All six are
committed in this folder with a `.meta.toml` beside each.

Every statement below is read off the sheets — **including the drawings**, which
were rendered and looked at, not just text-extracted. That distinction is not
pedantic here: reading only the notes produced the opposite answer. See
*How this page got it wrong twice* at the end.

---

## The six sheets

| Sheet | Index | Case | What it covers | **Protective vehicle drawn** |
|---|---|---|---|---|
| **TCP(S-1)-08A** | 211 | a | Work **off** shoulder or paved surface | 1 Work Vehicle |
| | | b | Work **on** shoulder | 1 Work Vehicle |
| **TCP(S-2)-08A** | 212 | a | **Road closed** under 20 min, off-peak, with or without shoulders | **None** — flaggers instead |
| | | b | Work **in roadway**, off-peak, with or without shoulders | **1 Shadow Vehicle with TMA** |
| **TCP(S-2c)-10** | 212A | — | A **two-lane rural intersection**, as determined by the Engineer | 1 Work Vehicle |
| **TCP(S-3)-08** | 213 | a | **Right lane closed**, with or without shoulders | **1 Shadow Vehicle with TMA** |
| | | b | Work **on centerline** | **2 Shadow Vehicles with TMA** |
| **TCP(S-4)-08A** | 214 | a | Work **off right shoulder** of divided roadways | 1 Work Vehicle |
| | | b | Work **in median** of divided roadways | 2 Work Vehicles (1 where a median barrier protects a side — Note 2) |
| **TCP(S-5)-08** | 215 | a | Work **on right shoulder** of divided roadways | 1 Work Vehicle *(but see the S-5 contradiction below)* |
| | | b | Work **on median shoulder** of divided roadways | 1 Work Vehicle *(same caveat)* |

**How to tell them apart on the page.** The legend gives the Truck Mounted
Attenuator (TMA) its own symbol — a small solid black chevron. On S-2b and on
both S-3 cases the drawn truck carries that chevron on the end facing traffic.
On S-1, S-2c, S-4 and S-5 the truck is drawn plain. The symbol, not the note
wording, is what distinguishes a shadow vehicle from an ordinary work truck.

`tcp-s-2c-10-memo.pdf` is the 11 January 2010 memorandum from Carol T. Rawson,
P.E., then Interim Director of the Traffic Operations Division, to all District
Engineers, announcing TCP(S-2c)-10 as an **additional** surveying TCP usable
immediately in construction, maintenance, and maintenance force operations. It
is a TxDOT scan; the text layer has OCR errors, so read the page image for
anything load-bearing.

**Divided roadways are covered.** S-4 and S-5 are about nothing else. The idea
that the family stops at undivided two-lane roads is wrong, and
[`tcp-s-1-08a.md`](tcp-s-1-08a.md) has been corrected accordingly.

**Freeways are not covered.** Every one of the six carries the footnote
**"Conventional Roads Only"** on its sign-spacing table. No sheet in the family
uses the words *freeway* or *controlled access*. A divided conventional highway
is inside the family; an Interstate is **not found** here. Look elsewhere before
concluding TxDOT is silent.

---

## What every sheet agrees on

**The duration bands.** All six print the same five-band bar — MOBILE, SHORT
DURATION, SHORT TERM STATIONARY, INTERMEDIATE TERM STATIONARY, LONG TERM
STATIONARY — and all six define the middle two identically:

> **SHORT DURATION** — work that occupies a location up to 1 hour.
> **SHORT TERM STATIONARY** — daytime work that occupies a location for more
> than 1 hour within a single daylight period.

**Only TCP(S-2c)-10 defines MOBILE**, and this is the sentence that matters
later on this page:

> **MOBILE** — work that moves continously or intermittently (stopping up to
> approximately 15 minutes).

*(The misspelling of "continuously" is TxDOT's, reproduced as printed.)*

**The one-hour line buys relief on every sheet — but it buys different things
on different sheets, and that difference is the whole cost story.** On every
sheet the G20-2a "END ROAD WORK" sign may be omitted for short duration work,
and on S-1 the shoulder taper and tangent channelizing devices may be omitted
too. Signs and cones: setup and teardown time.

**On TCP(S-2b) and TCP(S-3) the hour also changes the vehicle.** Read the shadow
vehicle section below before pricing anything from this page.

**The surveying-specific catch.** TCP(S-1)-08A Note 3: "If line-of-sight
requirements for surveying operations will preclude the placement of the Work
Vehicle to protect workers, the channelizing devices mentioned in Note 2 are
required." Note 2 is the one that lets those devices be omitted for work under
an hour. So Note 3 withdraws Note 2's relief — meaning the devices stand
whatever the duration. **That last sentence is a reading of the two notes
together, not a phrase printed on the sheet.**

A survey crew is in that case routinely, because sighting down a line is the
job. TCP(S-2)-08A Note 9 and TCP(S-2c)-10 Note 6 push from the other direction:
the surveying instrument **should not** / **shall not** be located on the paved
surface.

**The banner, on five of the six:** "WHENEVER POSSIBLE, SURVEY PARTIES SHOULD
AVOID, BY THE USE OF OFFSET LINES, ANY UNNECCESSARY PERIODS OF TIME ON THE ROAD
SURFACE." *(TxDOT's spelling of "unnecessary," reproduced as printed.)*

---

## Posted speed — what each sheet actually keys to

Everything on these sheets scales with **posted speed**, and 55 mph is the
number the repo's claim turns on, so it gets its own treatment here.

| Table | On which sheets | Speed range |
|---|---|---|
| Taper lengths, device spacing, minimum sign spacing, longitudinal buffer | **All six** | **30 to 75 mph** |
| Stopping Sight Distance | **S-2 and S-2c only** | **20 to 80 mph** |

**55 mph is an ordinary row on every one of the six.** Nothing happens at it. On
S-4, for instance, the 55 mph row reads: taper 550 / 605 / 660 ft for a 10, 11
or 12 ft offset; channelizing devices at 55 ft on a taper and 110–140 ft on a
tangent; minimum sign spacing 500 ft; longitudinal buffer space 295 ft. It is a
row of dimensions, not a threshold, and the rows above and below it look the
same in kind.

**There is exactly one speed break in the family**, and it is on S-1 only:
advance signs go at **3X where the posted speed is 50 mph or less, and 1500 ft
where it is over 50 mph** — `X` being that sheet's own minimum sign spacing. So
a 55 mph job under S-1 does buy longer advance signing than a 45 mph one. Longer
signing, not a different crew.

S-4 and S-5 do not key advance signing to speed at all. They fix it in feet:
signs at **2600 ft required**, a further sign at **1000 ft optional at the
Engineer's discretion** (S-4 Note 6), with 1600 ft also drawn on S-5.

The other speed figure anywhere in the family is TCP(S-3)-08 Note 7's 45 mph,
and it governs one sign — see the table further down.

---

## The shadow vehicle, which is the money question

A truck-mounted attenuator (TMA) is the crash cushion on the back of a shadow
truck. A shadow truck plus operator is the single largest step-change in a
survey crew's day rate, so whether a sheet *requires* one is the question that
decides an estimate.

**You cannot see the answer in the notes. You have to look at the drawing.**
Every sheet's notes use the same soft verbs — *desirable*, *may be replaced by*,
*may be substituted*. What actually differs between sheets is **which vehicle is
drawn in the plan view**, and whether it carries the legend's solid black TMA
chevron.

### A shadow vehicle with TMA is drawn on exactly two sheets

**TCP(S-2b)** — work in the roadway. One shadow vehicle with TMA, callout "(See
Notes 10 & 11)". Note that **TCP(S-2a)**, the road-closure case on the same
sheet, draws **no protective vehicle at all** — it uses flaggers and a closure
of under 20 minutes. The notes are scoped accordingly: notes 7–9 are headed
"TCP(S-2a)", notes 10–12 "TCP(S-2B)".

**TCP(S-3)** — both cases, callout "(See Notes 2 & 3)". S-3a, right lane closed,
draws one. **S-3b, work on centerline, draws two** — one at each end of the work
space, 30 ft minimum clearance to each, because traffic passes on both sides.
That is the most expensive configuration in the family and it is the one a
retracement crew chaining a centerline will land on.

Everywhere else the drawn truck is plain: S-1 (both cases), S-2c, S-4a, and
S-5 (both cases). **S-4b draws two** of them — work in a median has traffic on
both sides too — reducible to one where an existing median barrier protects a
direction (S-4 Note 2).

### What the notes then do

Where the drawing shows a **work** vehicle, the note offers an **upgrade**:
"A Shadow Vehicle with a Truck Mounted Attenuator … **may be used in lieu of**
the Work Vehicle" (S-1 Note 4, S-4 Note 4). Optional. The crew's own truck is
the baseline.

Where the drawing shows a **shadow** vehicle, the note offers a **conditional
downgrade**: "**For short duration work** *the* Shadow Vehicle with TMA may be
**replaced by** another Work Vehicle with high intensity rotating, flashing or
strobe lights" (S-2 Note 10, S-3 Note 2). The definite article is doing real
work — *the* Shadow Vehicle is the one already in the drawing.

### So: is a shadow vehicle ever forced?

**On TCP(S-2b) and TCP(S-3), yes — once the work passes one hour.** It is what
those sheets draw, and the permission to use an ordinary truck instead is
granted only *for short duration work*, defined on every sheet as up to one
hour. Past the hour the permission lapses and the drawn configuration stands.

One escape remains and it is not automatic — S-2 Note 11 / S-3 Note 3: "Shadow
Vehicles with a TMA are **desirable** when workers or equipment are in the work
space. **When approved by the engineer**, Type III barricades or other
channelizing devices may be substituted for the Shadow Vehicle."

**On S-1, S-2a, S-2c and S-4, no.** The drawn vehicle is an ordinary work truck
and the TMA is an option throughout.

**There is no posted speed anywhere in the family that forces anything.** That
part of the earlier finding survives unchanged.

So the accurate sentence is: **a survey crew working in a travel lane or on the
centerline for more than an hour is looking at a shadow vehicle with a TMA —
two of them on the centerline — unless the Engineer approves barricades
instead.** On a shoulder, off the pavement, or at a two-lane rural intersection,
it is not.

### TCP(S-5) contradicts itself, and this page does not resolve it

S-5's plan callout reads "**Work Vehicle** with high intensity … lights. (See
Note 2)", and the truck drawn beside it carries **no TMA chevron** — the symbol
is plainly the legend's Heavy Work Vehicle. But S-5's own Notes 2 and 3 are
written about "**the** Shadow Vehicle with TMA," wording carried over verbatim
from S-3, where a shadow vehicle *is* drawn.

Either the drawing depicts the short-duration case and the notes state a
baseline the drawing never shows, or the notes were copied and never reconciled.
**The sheet does not say which, and neither will this page.** Anyone pricing an
S-5 job past one hour should put the question to the Engineer rather than pick a
reading. An earlier version of this file picked one; that was a mistake.

All of the above is a finding about these six sheets. It is not a finding about
TxDOT contract provisions, district practice, or what a given Area Engineer will
accept on a given job — none of which are in scope here, and all of which can be
stricter.

---

## The claim this repo has been making

`docs/txdot-research.md` carries this, honestly labeled there as read across
from the mobile-operations standard **TCP(3-1)** because the surveying sheets
could not be fetched at the time:

> mobile TCPs apply on conventional roads ≤45 mph for work stopping up to ~15
> minutes. Beyond either threshold, a **stationary** TCP is required — shadow
> vehicle with TMA, arrow board, signing, radios.
>
> **A 20-minute shot on a 55-mph highway converts a two-person crew into a crew
> plus shadow truck.**

**Half right, and the half that is right is the half that costs money.**

**Right:** duration really can put a shadow truck on the job. On **TCP(S-2b)**
and **TCP(S-3)** the shadow vehicle with TMA is what the sheet draws, and the
permission to use an ordinary work vehicle instead is granted only for short
duration work. On S-3b it is **two** shadow vehicles. Somebody's instinct about
a cost cliff was sound.

**Wrong on every number and on the mechanism.** The line is **one hour**, not 15
or 20 minutes. It is not a speed threshold at all — 55 mph is an ordinary table
row on all six sheets. And what happens at the line is that a *permission
lapses*, leaving the drawn configuration standing, subject to the Engineer's
discretion to accept barricades instead. That is not the same as a rule that
adds a truck, and it does not apply on S-1, S-2a, S-2c or S-4 at all — those draw an ordinary
work truck.

The interesting part is *why* the numbers are wrong, because nobody made them
up. **All three are real. Each governs something else.**

| Number | Where it really comes from | What it actually governs |
|---|---|---|
| **~15 minutes** | TCP(S-2c)-10, MOBILE definition | The boundary between *mobile* and *short duration* work. A **classification**, with no requirement attached to crossing it |
| **20 minutes** | TCP(S-2)-08A Note 7 | "Road closures shall be less than 20 minutes. Closures less than 5 minutes are desirable." A cap on **how long you may close a road** with flaggers. Nothing to do with shadow trucks |
| **45 mph** | TCP(S-3)-08 Note 7 | One CW20-5L "LEFT LANE CLOSED" sign per direction may be omitted below 45 mph **and** under 2000 ADT — average daily traffic, the count of vehicles past a point in a day. It governs **one sign** |

Three true facts from three different sheets, welded into a fourth claim that
none of them makes. That is the failure mode worth putting on stage: not
fabrication, but **synthesis across sources that each looked authoritative**.
Every number survives spot-checking. The sentence built from them does not.

**The honest replacement** has two parts:

1. **The one-hour line, on TCP(S-2b) and TCP(S-3)** — work in a travel lane and
   work on the centerline. Past an hour the drawn shadow vehicle with TMA
   stands unless the Engineer approves barricades, and on S-3b that is **two**
   shadow vehicles. That is the cost cliff the original claim was reaching for,
   at the right number and on the right sheets.
2. **TCP(S-1)-08A Note 3** — the line-of-sight rule, which is
   surveying-specific and bites regardless of duration.

### How this page got it wrong twice

**First pass.** This file said flatly that no sheet in the family requires a
shadow truck. That was read entirely out of the **general notes**, whose verbs
are all soft — "desirable," "may be replaced by," "may be substituted." Two
independent reviewers checked the quotations and passed them, because the
quotations were accurate. The conclusion drawn from them was not.

A surveyor looked at the plans and said, in one line, that S-2 and S-3 show
shadow vehicles.

**Second pass.** The correction was made from **text positions** — where each
label sits on the page — without rendering the drawings. That got S-2 and S-3
right but produced three further errors: it credited S-5 with a shadow vehicle
it does not draw, missed that S-3b draws **two**, missed that S-2a draws
**none**, and swapped the captions of S-1a and S-1b.

**Third pass.** `poppler` was installed, the sheets were rendered, and the
drawings were looked at. Only then did the TMA chevron — a separate legend
symbol, present on some trucks and absent on others — become visible at all.

**The lesson, which is better than the one it replaces.** On a CAD standard
sheet the **drawing states the requirement** and the notes are exceptions to it.
Identical note wording means opposite things depending on what is drawn. Text
extraction flattens the legend, the notes and the plan view into one stream and
destroys exactly the distinction that decides the cost. An agent that reads text
but cannot see a picture will get this wrong, and will sound confident doing it.
The fix is not a cleverer prompt. It is rendering the page and looking — and,
failing that, saying out loud that the reading is text-only.

Correcting the research doc is
[#70](https://github.com/RickSmith/survey-recon/issues/70), not this file's job.

---

## What a crew-day estimator may and may not take from this

**May:**

- One hour is the duration line that changes the sign and device set, on every
  sheet in the family.
- Crossing it costs setup and teardown of a sign and a run of channelizing
  devices — time, on a conventional road.
- Line of sight, not duration, is what most often forces channelizing devices
  on a survey job (S-1 Note 3).
- Divided-roadway work has its own sheets, S-4 and S-5, with longer advance
  signing: the signs shown at 2600 ft are **required** and the 1000 ft sign is
  optional at the Engineer's discretion — both halves are **S-4 Note 6**.
- Two-lane rural work under S-2c binds the crew in ways the other sheets do
  not, and the verbs differ — TxDOT's own, not paraphrased:
  the rodman **may only** enter the roadway accompanied by a flagger and as
  traffic allows (Note 8); the crew and flaggers **shall** wear high-visibility
  apparel meeting ANSI 107-2007 Class 2 or Class 3 (Note 11); flaggers and crew
  **should** use two-way radios "or other means of communication" (Note 10).
  Note 10 is advisory and names an alternative. Note 11 is not. Price them
  differently.

**May not:**

- Assert that any **posted speed** triggers a required shadow truck. **Not found
  on any of the six sheets** — 55 mph is an ordinary table row on all of them.
- Treat the one-hour line as costing only signs and cones. On **TCP(S-2b) and
  TCP(S-3)** it also restores the drawn shadow vehicle with TMA — two of them on
  S-3b — subject to the Engineer's discretion to accept barricades. On S-1,
  S-2a, S-2c and S-4 it does not.
- Read S-5 either way. Its drawing and its notes disagree; **ask the Engineer.**
- Assume freeway or controlled-access work is covered. **Not found** — every
  sheet is footnoted "Conventional Roads Only."
- Assume the drawn TCP is the whole obligation. S-2c Note 12 says plainly that
  "additional traffic control devices may be required to address local site
  conditions," and most of the relief on these sheets is gated on "as determined
  by the Engineer" or "when approved by the engineer." The Engineer, not the
  sheet, has the last word — and the RPLS still signs.
