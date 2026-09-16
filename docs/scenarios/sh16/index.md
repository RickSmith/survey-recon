# The worked example: SH16, Bexar County

You have been asked to price a right-of-way survey. TxDOT wants to widen
Bandera Road, which is State Highway 16, from Loop 410 out to Old Bandera Road.
Just under nine miles, both sides. Preliminary design, so the mapping has to
be right before anybody draws a new line.

Before you can put a number on it you need to know four things. What control is
out there, and whether any of it can still be found. How many tracts you cross,
and who owns them. Which of those tracts will cost you time before a crew can
set foot on it. And how many days the crew and the office really need.

That is a week of somebody's time, pulling maps and making calls, before the
first stake goes in. This page is what happened when an agent did the desk half
of that week in twenty-one seconds, and what a licensed surveyor still has to
do with the result.

Everything below comes from public records. No client data was used, and none
ever will be.

---

## What the agent was told

Not "survey Bandera Road." A scope. The route by TxDOT's own name, `SH0016-KG`,
and the two mile markers that bound it, 347.7 to 356.367. A ribbon three
hundred feet either side of the centerline. A fixed list of public map services
to ask, in a fixed order, and a rule for what to do when one of them does not
answer.

That scope was argued out in an interview before any code was written, and it
is written down in full as [the specification](../../corridor-screen/spec.md).
The interview is the part of this session most worth copying. An agent given a
vague job does a vague job, quickly.

![How the screening works: one line in, fourteen services asked, one file out, three documents, one surveyor](img/how-it-works.svg)

## The morning it ran

On 13 September 2026 at six minutes past seven, the tool asked TxDOT for the
centerline, and TxDOT answered. It drew the ribbon. Then it asked thirteen more
public services, one after another, what was inside that ribbon. Every one of
them answered. The run finished at seven minutes past.

Every answer was saved to disk with the date it came back and the exact
question that produced it. That matters more than it sounds. The conference
network is not to be trusted, and a public server can go quiet for a day, which
one of these did the following week. When the results are shown on stage they
are read back from those saved answers, and the page says so out loud. The code
is real. The answers are from the thirteenth.

## Where the job is

![The corridor map: SH16 from Loop 410 to Old Bandera Rd, with the 524 tracts and the 8 flagged ones numbered](img/corridor-map.svg)

The ribbon touches **524 tracts**. That number comes from the Bexar County
Appraisal District's own parcel map, and it is a count, not an acreage. How
much of each tract the widening takes was not measured, and the memo says so
rather than adding up a column of nothing.

Eight of the 524 carry something that costs time before a crew can go on. Seven
have a school on them or next door. One has a cemetery.

The cemetery is the easy one. Texas law requires fourteen days of written
notice to the surrounding landowner before entering a cemetery, and the tool
found the section and the link, [Tex. Health & Safety Code §
711.041(c)(2)](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm). So
that tract reads *14 calendar days*.

The schools are the hard one, and they are hard in a way worth understanding.
There is no published number of days for getting a survey crew onto school
district land. The tool looked in the Education Code, in the TxDOT Survey
Manual, and in TxDOT's right-of-way procedures. It found a background-check rule
and no notice period. So those seven tracts read *wait not found*, not *no
wait*. Somebody has to call the district, and the call is what turns an unknown
into a date.

A blank, a dash, or a zero in that column would have read as *clear*. That is
the first thing to notice about how this tool is built. When it does not know,
it says it does not know, and it says where it looked.

Two of the fourteen services came back with nothing at all. No railroad crosses
this ribbon. No mapped pipeline runs through it. The tool reports those as *we
looked and found none*, which is a different answer from *we did not look*.

## What control is out there

![The control map: 11 NGS marks with their PIDs and conditions, and 2 TxDOT monuments](img/control-map.svg)

The National Geodetic Survey publishes eleven marks inside the ribbon. **Every
one of the eleven is recorded MARK NOT FOUND.** Somebody went looking for each
of them, between 1995 and 2002, and came back without it.

A tool that reported "11 marks in the corridor" and stopped would have you
pricing the recovery of eleven monuments that three decades of looking could
not turn up. This one reads the condition off each datasheet and puts it on
the map beside the mark.

MARK NOT FOUND is a report with a date on it, not a verdict. The mark may be
under a foot of fill. But on this evidence the control work on this job is
setting new, not recovering old, and that is the single largest judgment in
the estimate. It is the surveyor's judgment. The tool lays out the evidence and
stops.

TxDOT publishes two of its own monuments in the ribbon, both reported in good
condition, with descriptions a crew can drive to. They are on the same map.

## The record drawings

Sixty-nine right-of-way map sheets reach this corridor. Fifteen of them are
SH16's own, dated 1944 to 1998. The other fifty-four belong to the roads that
cross it, Loop 410, Loop 1604, FM 471 and FM 1560, because the right of way
where two roads meet is drawn on the crossing road's sheets. A crew retracing an
interchange will need them.

The oldest sheet in the set is dated 1 January 1900. That may not be a date at
all. The same value appears on 368 of the 20,276 sheets the service publishes,
and the service never publishes an empty date, so it looks like a stand-in for
*nobody wrote it down*. The tool could not confirm that, so it reports the range
the data gives, names the sheet, and tells you to check the drawing before you
quote the age of the records.

The drawings themselves are not online. They come through TxDOT's Real Property
Asset Map or by open records request, and the sheet names to ask for are in
the run's output.

## How far help is

![The crew safety map: the nearest hospital, ambulance, fire and police, with straight-line distances](img/crew-safety-map.svg)

The nearest hospital is the Audie L. Murphy VA, two miles from the Loop 410 end
of the corridor. It is also **eight miles from the other end**. A party chief
working the Old Bandera Road end who read only the first number would be wrong
by six miles.

So every place on the crew safety sheet carries three distances: to the nearest
point on the road, and to each end. And every one is labeled a straight line,
because a straight line does not know about the creek with no crossing or the
freeway with no turnaround, and an ambulance does.

## What it could not see

This is the part of the output to read first, and the tool puts it first in
the memo. Every item here is a question a person still has to answer.

- **Gated access and livestock.** No public source publishes either. A tract is
  not clear of a locked gate because this screening does not mention one.
- **The existing right-of-way width, the lane count, and the traffic.** The
  service that holds them was not called on this run. The ribbon width used
  here is the one in the scope, not the one TxDOT holds.
- **How much of each tract is taken.** Counted, not measured.
- **Whether TxDOT already owns a tract.** Not checked. Some of the 524 may be
  in state hands already.
- **Manholes, culverts, and how many times traffic control has to go out.**
  Nothing in the public record counts them, and they are where the field time
  goes on a road like this.
- **Right of entry, on every tract.** Deliberately unknown. Texas has no
  automatic right of entry for a surveyor, and nothing in a parcel map creates
  one. Nothing in this screening is permission to enter anywhere.

## The estimate

![The crew-day sheet: inputs on the left, the lines of arithmetic on the right, and the totals](img/crew-day-sheet.svg)

The build-up came out at **38 crew-days in the field** with two people to a
crew, and **18 days in the office**. The two are never added together. They are
bought from different people.

Both numbers are floors. Two lines of the field arithmetic have no total at
all, because the things they multiply were never counted. Those hours are
missing from the 38, not zero in it.

Every rate carries a handle, `A1` through `A12`, so you can disagree with one of
them out loud. The biggest line is corner recovery, rate `A4`, at half an hour
on each of 524 tracts. Halve it and the field figure moves more than any other
change you could make. That is the point of showing the arithmetic. A total is
something you accept or reject. A line is something you argue with.

The rates are not a published standard. TxDOT publishes none. They are stated
assumptions in a plain text file a firm can edit, and each one says where it
came from.

## What a surveyor does with all this

Reads it. Decides whether eleven missing marks mean setting new control or one
more day of looking. Calls the school districts. Orders the fifteen SH16 sheets
and asks about the interchanges. Drives the corridor, because nobody has. Then
prices the job, signs it, and owns it.

The tool wrote a specimen right-of-entry letter for the cemetery tract, from
public records, with the fourteen-day notice and its citation on it. It was not
mailed and it was not signed. A licensed surveyor does both, and remains
accountable for it. That is not a limitation of the tool. It is the whole
arrangement.

## The one thing that was live

Everything above replays from the saved answers. One call does not. When the
tool is run for a room, it asks the National Geodetic Survey, right then, for
every mark within two miles of the middle of the corridor, and compares the
answer with what the run captured.

On 13 September it got thirteen marks back. Five of them are in the captured
run as well, and all five say the same thing live as they said in the capture,
MARK NOT FOUND. That is a cross-check between two different NGS services, not
a recording agreeing with itself.

The day after, the same service answered with an empty list, and an hour later
it refused the call. The next day it was back, and its answer had not changed
by a byte. Public servers have bad days. That is why the rest of this
page replays from disk, and why the live moment is a separate command that can
fail without touching anything else.

## See for yourself

The whole screening replays with no network at all:

```bash
python -m corridor_screen --route SH0016-KG --begin-dfo 347.7 --end-dfo 356.367 --out ../project-sh16 --mode cache-only
```

A live run and a replay of the capture were compared. They differ in
seventy-four places, every one of them the run's own account of itself:
timestamps, its mode, and how long each service took to answer. Every parcel,
every flag, every mark and every sheet is identical.

The files the run produced are in the project folder:

| File | What it is |
|---|---|
| [`bid-memo.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/bid-memo.md) | The memo a principal reads before pricing. What is not known comes first |
| [`flagged-parcels.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/flagged-parcels.md) | The eight tracts, sorted so the one needing a phone call soonest is first |
| [`crew-day.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/crew-day.md) | The build-up, every line of arithmetic and where each number came from |
| [`roe/roe-letter-1.md`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/roe/roe-letter-1.md) | The specimen right-of-entry letter |
| [`screening.json`](https://github.com/RickSmith/survey-recon/blob/main/project-sh16/screening.json) | Everything the run found, in one file the three documents above are written from |
| [`cache/`](https://github.com/RickSmith/survey-recon/tree/main/project-sh16/cache) | Every answer every service gave, with its date and the exact request beside it |

The detailed account of the run, service by service, with every surprise it
turned up, is on [What the capture found](capture-note.md).

---

## Where this came from

The scope was settled in an interview on 12 September 2026, recorded on
[work order #5](https://github.com/RickSmith/survey-recon/issues/5). The run
and its capture are [#20](https://github.com/RickSmith/survey-recon/issues/20).
The three documents are [#22](https://github.com/RickSmith/survey-recon/issues/22),
[#23](https://github.com/RickSmith/survey-recon/issues/23) and
[#24](https://github.com/RickSmith/survey-recon/issues/24). The two days the
live call failed are [#128](https://github.com/RickSmith/survey-recon/issues/128).
The drawings are [#154](https://github.com/RickSmith/survey-recon/issues/154).
