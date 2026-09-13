# The TCP(S-*) family — what TxDOT actually requires of a survey crew

Six standard sheets, all titled **"Traffic Control Plan for Surveying
Operations,"** all published by TxDOT's Traffic Operations Division. All six are
committed in this folder with a `.meta.toml` beside each.

Every statement below is read off the sheets. Where a sheet is silent, this page
says so rather than filling the gap from a neighboring standard — which is the
mistake being corrected here.

---

## The six sheets

| Sheet | Index | Dated | Cases drawn |
|---|---|---|---|
| **TCP(S-1)-08A** | 211 | 8-08 | (a) work **off** shoulder · (b) work **on** shoulder or paved surface |
| **TCP(S-2)-08A** | 212 | 8-08 | (a) **road closed** under 20 min, off-peak · (b) work **in roadway**, off-peak |
| **TCP(S-2c)-10** | 212A | 1-10 | Single case: **two-lane rural** roadways, as determined by the Engineer |
| **TCP(S-3)-08** | 213 | 8-08 | (a) **right lane closed**, with or without shoulders · (b) work **on centerline** |
| **TCP(S-4)-08A** | 214 | 8-08 | (a) work **off right shoulder of divided roadways** · (b) work **in median of divided roadways** |
| **TCP(S-5)-08** | 215 | 8-08 | (a) work **on right shoulder of divided roadways** · (b) work **on median shoulder of divided roadways** |

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

**On S-2, S-3 and S-5 the hour also changes the vehicle.** Read the shadow
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

**The family splits in two, and you cannot see the split in the notes alone —
you have to look at what the drawing depicts.** Each sheet labels one protective
vehicle in its plan view. That label is the sheet's baseline; the notes then say
what you may swap it for.

| Sheet | The vehicle **drawn** in the plan | Which notes the callout points at |
|---|---|---|
| S-1 | Work Vehicle with high intensity lights | Notes 3 and 4 |
| S-2 | **Shadow Vehicle with TMA** and high intensity lights | Notes 10 & 11 |
| S-2c | *(no vehicle callout; legend shows a Work Vehicle)* | Notes 2 & 3 |
| S-3 | **Shadow Vehicle with TMA** and high intensity lights | Notes 2 & 3 |
| S-4 | Work Vehicle with high intensity lights | Note 4 |
| S-5 | Work Vehicle with high intensity lights | Note 2 |

**The grammar of the notes confirms the drawings, in both directions.**

Where the drawing shows a *work* vehicle, the note offers an **upgrade** — S-1
Note 4 and S-4 Note 4: "A Shadow Vehicle with a Truck Mounted Attenuator … **may
be used in lieu of** the Work Vehicle." Optional, and the crew's own truck is
the baseline.

Where the drawing shows a *shadow* vehicle, the note offers a **downgrade**, and
it is conditional — S-2 Note 10, S-3 Note 2, S-5 Note 2: "**For short duration
work** the Shadow Vehicle with TMA may be **replaced by** another Work Vehicle
with high intensity rotating, flashing or strobe lights." The definite article is
doing real work: *the* Shadow Vehicle is the one already in the drawing.

### So: is a shadow truck ever required?

**On S-1, S-4 and S-2c — no.** The drawn vehicle is an ordinary work vehicle and
the TMA is an option.

**On S-2, S-3 and S-5 — effectively yes, once the work passes one hour.** The
shadow vehicle with TMA is what the sheet draws. The permission to drop to an
ordinary work vehicle is granted only *for short duration work*, which every
sheet defines as up to one hour. Past the hour that permission lapses and the
drawn configuration stands. There is one remaining escape, and it is not
automatic: S-2 Note 11 / S-3 Note 3 / S-5 Note 3 — "Shadow Vehicles with a TMA
are **desirable** when workers or equipment are in the work space. **When
approved by the engineer**, Type III barricades or other channelizing devices
may be substituted for the Shadow Vehicle."

So the honest sentence is: **on the three sheets that put a crew in a travel
lane or on the centerline, passing one hour restores a shadow vehicle with TMA
unless the Engineer approves barricades instead.** Not a certainty. Not a
formality either.

Which sheets are those? S-2 (road closure with flaggers, and work in the
roadway), S-3 (lane closure, and work on centerline), S-5 (right and median
shoulders of divided roadways). Exactly the cases where the crew is exposed.

**There is still no posted speed anywhere in the family that triggers a shadow
vehicle.** That part of the original finding survives. The duration part did
not.

### An inconsistency on S-5, reported not resolved

S-5's plan callout labels a **Work Vehicle**, but the note it points to — Note 2
— is written about replacing "the Shadow Vehicle with TMA," and Note 3 is about
substituting for "the Shadow Vehicle." The drawing and its own notes do not
agree about what is drawn. The most coherent reading is that S-5 depicts the
short-duration case and its notes state the baseline, which is how S-3's
identically worded notes behave. **That is a reading, not something the sheet
says.** Anyone pricing an S-5 job past one hour should ask the Engineer rather
than rely on this paragraph.

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

**Right:** duration really can put a shadow truck on the job. On S-2, S-3 and
S-5 the shadow vehicle with TMA is what the sheet draws, and the permission to
use an ordinary work vehicle instead is granted only for short duration work.
Somebody's instinct about a cost cliff was sound.

**Wrong on every number and on the mechanism.** The line is **one hour**, not 15
or 20 minutes. It is not a speed threshold at all — 55 mph is an ordinary table
row on all six sheets. And what happens at the line is that a *permission
lapses*, leaving the drawn configuration standing, subject to the Engineer's
discretion to accept barricades instead. That is not the same as a rule that
adds a truck, and it does not apply on S-1, S-4 or S-2c at all.

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

1. **The one-hour line, on S-2, S-3 and S-5** — the sheets that put a crew in a
   travel lane, on the centerline, or on a divided-highway shoulder. Past an
   hour, the drawn shadow vehicle with TMA stands unless the Engineer approves
   barricades. That is the cost cliff the original claim was reaching for, at
   the right number and on the right sheets.
2. **TCP(S-1)-08A Note 3** — the line-of-sight rule, which is
   surveying-specific and bites regardless of duration.

### A note on how this page itself went wrong

The first version of this file said flatly that no sheet in the family requires
a shadow truck. That was read entirely out of the **general notes**, whose verbs
are all soft — "desirable," "may be replaced by," "may be substituted." It is
also wrong, and it was caught by a surveyor looking at the **drawings** and
saying that S-2 and S-3 plainly show a shadow vehicle.

On these sheets the drawing is the requirement and the notes are the exceptions
to it. Reading the notes without the plan view inverts the meaning of both. An
agent that can extract text but cannot see a drawing will make this mistake
every time, and will sound confident doing it — which is the point of the
session, arriving unplanned.

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
- Treat the one-hour line as costing only signs and cones. On **S-2, S-3 and
  S-5** it also restores the drawn shadow vehicle with TMA, subject to the
  Engineer's discretion to accept barricades. On S-1, S-4 and S-2c it does not.
- Assume freeway or controlled-access work is covered. **Not found** — every
  sheet is footnoted "Conventional Roads Only."
- Assume the drawn TCP is the whole obligation. S-2c Note 12 says plainly that
  "additional traffic control devices may be required to address local site
  conditions," and most of the relief on these sheets is gated on "as determined
  by the Engineer" or "when approved by the engineer." The Engineer, not the
  sheet, has the last word — and the RPLS still signs.
