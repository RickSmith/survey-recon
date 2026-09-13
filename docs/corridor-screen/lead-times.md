# Lead times, and where each number comes from

**A lead time is the delay before you can enter.** Not how long the work takes —
how long you wait for permission before the work can start. It is the difference
between a parcel you can shoot next Tuesday and one you cannot shoot until next
month.

This page is the citation list for every number the corridor tool prints. The
numbers live in `corridor-screen/corridor_screen/lead_times.toml`, which is
checked-in data rather than code, so the person who is accountable for a number
can change it without touching Python and the change shows a readable diff.

Every URL below was opened and read on **2026-09-12**, and the quoted language is
what the page said on that date.

---

## The rule this table is held to

**A lead time with no citation is a rumor with a number on it.** The loader
refuses to read a row that has no source and no link, the same way the tool
refuses to run against a layer whose field list is wrong. It is a configuration
mistake, and it costs nothing to catch before the run rather than after.

A row with no confirmed figure must begin with the words **"Not found"** and
must say where it looked. That is checked too. Anything softer than "not found"
reads as "no delay," and those are not the same statement.

---

## Confirmed, and statutory

### Cemetery — 14 days

[Tex. Health & Safety Code § 711.041(c)(2)](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm)

The surrounding landowner may set the routes and the hours. Outside those hours,
a person must give written notice *"not later than the 14th day before the date
the person wishes to visit the cemetery."*

Two limits, and **the surveyor judges both, not the tool**:

- The section grants access *"for purposes usually associated with cemetery
  visits."* Whether entering to run a survey is one of those is a legal question,
  not a geometric one.
- Subsection (d) says the section does not apply to an unverified cemetery.

A separate clock runs the other way. Discovering a cemetery nobody had recorded
means filing notice with the county clerk **within 10 days** —
[§ 711.011(a)](https://statutes.capitol.texas.gov/Docs/HS/htm/HS.711.htm).

### Pipeline — 48 hours, which is two **working** days

[Tex. Util. Code § 251.151(a)](https://statutes.capitol.texas.gov/Docs/UT/htm/UT.251.htm)

Notice to a notification center — Texas 811 — *"not earlier than the 14th day
before the date the excavation is to begin or later than the 48th hour before
the time the excavation is to begin, excluding Saturdays, Sundays, and legal
holidays."*

So 48 hours is a **floor**, not a booking, and the weekend and holiday exclusion
can make it longer on the calendar than it is on paper. The tool records two
working days, **and records that they are working days.**

That last part matters. Two working days and two calendar days are different
promises, and the tool will not convert one into the other — doing so would mean
inventing a calendar of weekends and Texas legal holidays that it does not have
and could not check. So every number carries a `lead_time_basis` saying which
days it counts, the loader refuses a confirmed row that does not say, and the
parcel row repeats it as `max_lead_time_basis`. A reader who sees "2 working
days" knows to add the weekend. A reader who sees a bare "2" does not.

**The number may not apply at all.** § 251.002 defines excavation as mechanized
equipment used *"to remove or otherwise disturb soil to a depth of 16 or more
inches."* A hand-driven monument may fall outside the chapter entirely. The tool
records the floor. The surveyor judges the case.

---

## Confirmed, but procedure rather than statute

### Railroad — 30 to 45 days

[Union Pacific, Right of Entry / Temporary Use of Railroad Property — Procedures](https://www.up.com/real-estate/tempuse/procedures)

In Union Pacific's own words on that page: *"The normal turn-around time for
processing applications is now running between 30-45 days."* The same page states
a non-refundable application fee of **$1,545** and warns that incomplete
applications halt processing. Railroad Protective Liability insurance and
flagging are separate requirements.

**The tool plans on 45, not 30.** A bid cannot promise the good end of somebody
else's queue. Both ends of the range are carried in the output, so a reader can
see the range the tool chose from rather than only the choice.

**This is one railroad's procedure.** The Bexar County rail lines the USGS layer
returns belong to Union Pacific, BNSF and San Antonio Central. BNSF and the short
lines publish their own procedures and were not read.

---

## Not found

### School — no number of days

[Tex. Educ. Code § 22.0834](https://statutes.capitol.texas.gov/Docs/ED/htm/ED.22.htm)
is real and it is relevant, but **it is not a notice period**. It requires a
criminal history review of a contractor's employees where they have continuing
duties related to the contracted services *and* direct contact with students.

Subsection (a-1)(3) exempts public work separated from students by a secure
barrier fence *"not less than six feet in height"*, where the contracting entity
adopts a policy banning employees from interacting with students. So a survey
behind a proper barrier with an enforced no-contact policy may need no background
check at all.

That is a condition of entry. It is not a number of days, and this table will not
turn one into the other.

**Where we looked:** § 22.0834 itself; the TxDOT Survey Manual (ESS, rev. April
2026), which does not address school access; and TxDOT ROW Preliminary Procedures
Ch. 4. District board approval runs on a board's own meeting cycle and badging
follows approval — both real, neither published as a figure.

**What the tool does with it.** A parcel whose only flag is a school shows no
`max_lead_time_days`, and `lead_time_not_found` on that row says `school`. It is
not reported as clear. It is reported as unmeasured, which is a different thing,
and it is the same distinction as `unknown` against `no`.

### Church, federal or tribal, gated or agricultural

Rows exist for all three so the gap is visible rather than absent. None is
screened by this tool.

| Row | Why there is no number |
|---|---|
| Church | No Texas statute setting a notice period was found. Authority rests with a board that commonly meets monthly |
| Federal or tribal | Special-use permits and tribal council plus BIA consent are the routes. No published turn-around was confirmed. **Assume months; do not quote a number** |
| Gated or agricultural | No notice period exists to look for, and no public source publishes gate locations or livestock. This is the not-screenable gap in [spec section 12](spec.md) |

---

## What the tool does with all of this

Every flag on a parcel carries its own lead time and its own citation. The parcel
row then carries two things beside each other:

- **`max_lead_time_days`** — the longest confirmed wait, so nobody has to do
  arithmetic to find the parcel that drives the schedule. `lead_time_driver`
  names which flag set it, and `max_lead_time_basis` says which days it counts.
- **`lead_time_not_found`** — the flag types on that parcel whose lead time could
  not be confirmed.

Both are needed. A parcel with a cemetery and a school shows 14 days **and**
`school` in the not-found list, because 14 is the longest number anybody can
stand behind and it is not the whole answer.

The citations travel inside `screening.json` too, under `run.lead_times`, so
somebody holding only the output file can check a number against its source
without this repo beside them. A lead time is worth exactly what its citation is
worth.
