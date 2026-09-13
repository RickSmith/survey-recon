---
marp: true
theme: tsps
paginate: true
title: Beyond the Prompt
description: TSPS 2026 convention session on supervising an AI agent for survey work
---

<!-- _class: title -->

# Beyond the Prompt

## Getting Started with Agentic AI for Geomatics Tools and Workflows

**Rick Smith** — Conrad Blucher Institute, Texas A&M–Corpus Christi
**Seneca Holland**

TSPS 2026 Convention · October 8, 2026

<!--
0:00–0:08 · 8 min · Cold open

This slide stays up while the agent runs. Hand it the SH16 job first, in front
of the room, then turn around and introduce yourselves while it works.

Say the caching line here, not later: the responses were captured on the 12th
and 13th of September so the session is not at the mercy of hotel Wi-Fi, the
code is live code, and anybody can run it themselves.

Fallback if the command will not start: docs/presenting/fallbacks.md, row one.
-->

---

# The job we just handed it

- The corridor: SH16, Loop 410 to Gibeaut Rd, Bexar County
- 8.69 miles of a TxDOT right of way, scoped from public records only
- What we asked for: what is out there, and what it costs in crew days
- What it does next: reads, asks, and shows its work

> **To be written** — #81

<!--
0:00–0:08 · 8 min · Cold open

One slide only. The terminal is the thing on screen for this block; this is
what goes up beside it, or behind it, while the run finishes.

Do not explain the tool yet. The whole point of the cold open is that the room
watches something real happen before anybody has defined a single term.
-->

---

<!-- _class: divider -->

# What is an agent

## From a prediction engine to something that does work

<!--
0:08–0:20 · 12 min · What is an agent

Twelve minutes, three slides. Prediction, then the three shapes of the tool,
then the loop. Nothing here is about survey work yet, which is deliberate: the
room needs the mechanism before it will believe the demo.
-->

---

# It predicts the next word

- What a language model is actually doing, in one plain sentence
- Why that makes it fluent, fast, and sometimes confidently wrong
- The survey parallel: a very well-read new hire who has never been on site

> **To be written** — #31

<!--
0:08–0:20 · 12 min · What is an agent

Keep this to one idea. The room does not need the architecture; it needs to
know why a wrong answer arrives in the same confident voice as a right one.
-->

---

# Chatbot, copilot, agent

- Chatbot: you ask, it answers, nothing happens afterward
- Copilot: it suggests while you work, and you accept or reject
- Agent: it plans, acts, checks its own work, and repeats
- What changes at each step is not intelligence, it is what it may touch

> **To be written** — #31

<!--
0:08–0:20 · 12 min · What is an agent

The distinction that matters to a principal is the last bullet. A chatbot
cannot cost you anything. An agent can, because it acts.
-->

---

# The loop

- Read the assignment, plan the work, do a piece of it
- Check the result, correct, go round again
- It stops when the work is done or when it is stuck
- A human decides what "done" means, before the loop starts

> **To be written** — #31

<!--
0:08–0:20 · 12 min · What is an agent

This is the slide the rest of the session refers back to. Draw the loop rather
than list it if a drawing can be made to work at 1920 x 1080.
-->

---

<!-- _class: divider -->

# Vocabulary of managing one

## Four words, each with a survey equivalent

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Ten minutes, five slides. Markdown, the repo and git, issues, context, tokens.

Every one of these is introduced by its survey equivalent first. The
translation table is in CONTEXT.md at the root of the repo, and it is the
authority for the words used here.
-->

---

# Markdown

- Plain text a person can read and a machine can also read
- No proprietary format, no version that will not open in nine years
- The survey parallel: a field book, not a CAD file
- Everything in this session is written in it, including these slides

> **To be written** — #31

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Show this file on screen for ten seconds. Seeing the slide and the source
side by side does more than a paragraph of explanation.
-->

---

# The repo, and git

- A repo is the job folder. Git is the field book that never loses a page
- A branch is a working copy nobody else is affected by
- A commit is a field book entry, with a date and a name on it
- Nothing is ever overwritten, so nothing is ever quietly lost

> **To be written** — #31

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Do not teach git commands. This room is deciding whether to point somebody at
this, not typing it themselves. Terms only, and the survey word first.
-->

---

# Issues, and pull requests

- An issue is a work order: what to do, and how you will know it is done
- A pull request is the check print you redline before anything is final
- Merging is signing and sealing
- Nothing reaches the job without somebody licensed looking at it

> **To be written** — #31

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

This is the slide that sets up the whole accountability argument at the end.
Land the last bullet slowly.
-->

---

# Context

- The agent only knows what is in front of it right now
- A handbook in the repo is read every time; a conversation is not
- The survey parallel: written office standards against hallway advice
- Where the rules live decides whether they are followed

> **To be written** — #31

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Beat 3 at 1:36 is the payoff for this slide. The rule that caught our own
error was written in CLAUDE.md months before, for a different purpose.
-->

---

# Tokens

- The unit the tool reads and writes in, and the unit it bills in
- Roughly three quarters of a word, which is all the precision needed here
- Why a long document costs more to work on than a short one

> **To be written** — #31

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Cut 3 of 3. This slide goes to a footnote in the repo if the session is
running long. Keep it to one slide so the cut is a single deletion.
-->

---

<!-- _class: divider act -->

# Act I — The grilling

## The agent interviews you before it touches anything

<!--
0:30–0:46 · 16 min · Act I — The grilling

Sixteen minutes, five slides, and the hinge of the whole session. Most of this
block is live: /grill-with-docs, then /to-spec, then /to-tickets, with the real
issues appearing on the projector at the end.

The slides are scaffolding around a live demo. Keep them out of the way.

Fallback: corridor-screen/captures/the-grilling/README.md is Act I on one
screen. Nineteen questions, what was recommended, what Rick answered.
-->

---

# What the grilling is

- You describe a job. The agent asks until it understands the scope
- It is allowed to disagree with you, and it does
- The survey parallel: the scoping call you wish every client would sit through
- Nineteen questions, on the real SH16 job, in one sitting

> **To be written** — #82

<!--
0:30–0:46 · 16 min · Act I — The grilling

Set up the live run here, then stop talking. The room learns more from
watching the questions arrive than from any description of them.
-->

---

# Live: the interview

- Run it against the SH16 scope, on the projector, at full size
- Let the silences sit. The questions are the content
- Watch for the moment it asks something the room had not thought of

> **To be written** — #82

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block. This slide is a holding card; switch away from it immediately.

If the live run will not start, open the captured transcript instead and say
plainly that it is a transcript of a real run and not a recording.
-->

---

# Live: from answers to a scope of work

- The interview becomes a written scope you can read and argue with
- Every decision is on the page, including the ones you did not make
- Nothing is assumed silently, which is the whole value of it

> **To be written** — #82

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block. Show the spec document, scroll it once, slowly. Do not read it out.
-->

---

# Live: from a scope to work orders

- The scope breaks into numbered work orders, each small enough to check
- They land on GitHub, publicly, while the room watches
- Thirty-five of them, on the real job, in under two minutes

> **To be written** — #82

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block, and the one that gets the audible reaction. Have the issues page
open in a second window so you can switch to it the moment they appear.
-->

---

# Why this is the hinge

- The work you do before the agent starts is the work that decides the outcome
- A vague assignment produces confident, plausible, wrong work
- This is not new. It is how you already supervise a party chief
- Everything after this slide is the agent executing a scope you approved

> **To be written** — #82

<!--
0:30–0:46 · 16 min · Act I — The grilling

If only one slide from this block survives a cut, it is this one. Say the
third bullet in their words, not in software words.
-->

---

<!-- _class: divider -->

# The money slide

## Rework is the argument. Speed is not.

<!--
0:46–0:52 · 6 min · The money slide

Six minutes, two slides, moved up to here on purpose: owners need the money
frame before they will invest attention in another 45 minutes of demo.

Billable hours, never subscription pricing. The numbers come from the crew-day
build-up in project-sh16/, not from invention.
-->

---

# The billable-hour math

- What the desktop recon on this corridor costs in hours today
- What it cost with the agent doing the reading, and who checked it
- Every number traced to the crew-day build-up in the repo
- No subscription pricing. Nobody in this room buys software by the seat

> **To be written** — #32

<!--
0:46–0:52 · 6 min · The money slide

Numbers must come from project-sh16/crew-day.md and carry their handles, A1
through A12, so anybody who wants to argue with one can find it.
-->

---

# Rework, not speed

- TxDOT: there is no acceptable failure rate for any TxDOT survey
- A non-compliant survey cannot be invoiced
- For an owner, that is not a quality sentence. It is a money sentence
- Speed is the smaller half of the argument. Lead with this one

Survey Manual (ESS) rev. April 2026, Ch. 4 · txdot.gov/manuals/row/ess

> **To be written** — #32

<!--
0:46–0:52 · 6 min · The money slide

"Cannot be invoiced" needs its citation on the slide, with the manual section
and its URL. Use txdot.gov/manuals/row/ess/ - never onlinemanuals.txdot.gov.
-->

---

<!-- _class: divider -->

# Stretch + questions

## Five minutes. Stand up.

<!--
0:52–0:57 · 5 min · Stretch + questions

One slide, and nothing else. This is a holding card for the break.

Take questions from the floor. If the room is quiet, Seneca has the
audience-proxy interjections for exactly this moment - see #35.

Nothing is on screen to lose here, so there is no fallback to reach for.
-->

---

<!-- _class: divider act -->

# Act II — Find the control

## What is already on the ground, and what is not

<!--
0:57–1:18 · 21 min · Act II — Find the control

Twenty-one minutes, six slides, mostly output on screen. NGS marks and their
conditions, TxDOT control points, ROW map sheets, the datum gap, and the one
genuinely live call.

Fallback: docs/scenarios/sh16/capture-note.md reads the findings out in the
order you need them, and project-sh16/screening.json is the run itself.
-->

---

# What we asked it to find

- Every published survey mark inside the corridor, and its last condition
- Every TxDOT primary control point, and whether it still exists
- Every right-of-way map sheet the corridor touches, and its date
- All of it from public sources. No client data, ever

> **To be written** — #83

<!--
0:57–1:18 · 21 min · Act II — Find the control

The last bullet is a governance point disguised as a technical one. Say it
plainly: nothing belonging to a client went anywhere near this.
-->

---

# The NGS marks

- What came back for this corridor, and how many were usable
- MARK NOT FOUND is a report with a date on it, not a verdict
- A mark somebody looked for and could not find is control you may have to set
- Counted separately from the marks reported present, and here is why

> **To be written** — #83

<!--
0:57–1:18 · 21 min · Act II — Find the control

The distinction in bullets two and three is the one an estimator gets wrong.
A count of marks reads as control you have.
-->

---

# The TxDOT control points

- What the state publishes about its own monuments on this route
- Monument destroyed is a stronger claim than MARK NOT FOUND. Both cost a trip
- Condition unknown is neither. Nobody looked, so nobody knows
- Two records can name one monument, so a record count is not a monument count

> **To be written** — #83

<!--
0:57–1:18 · 21 min · Act II — Find the control

Distinct stations against record count is the detail that makes a surveyor
trust the rest of the output. Do not skip it for time.
-->

---

# The right-of-way map sheets

- The historical record drawings the corridor crosses, and their dates
- A corridor figure and a county figure answer different questions
- Sheets from the 1940s and sheets from the 1990s are not the same document
- What the tool reports, and what still has to be ordered by hand

> **To be written** — #83

<!--
0:57–1:18 · 21 min · Act II — Find the control

docs/data-sources/row-map-sheets.md works the corridor-against-county
difference through properly. Take the numbers from there.
-->

---

# The datum gap

- What datum do you certify to, and what does your report say
- TxDOT's April 2026 Survey Manual does not mention the 2022 replacements
- State that precisely, with the manual's date. No blame, and no pretending
- It is a scope and liability question, not a geodesy lecture

> **To be written** — #33

<!--
0:57–1:18 · 21 min · Act II — Find the control

This is the slide most likely to be quoted afterward, so it has to be exactly
right. Open question, stated plainly, no settled answer implied.
-->

---

# The one genuinely live call

- Everything so far came off the disk, captured in September, and we said so
- This one goes out to the network now, in front of you
- If it fails, that is also true, and we will say that too
- One live moment is what proves the rest is not a movie

> **To be written** — #83

<!--
0:57–1:18 · 21 min · Act II — Find the control

NGS /radial was the most reliable endpoint tested. If it does not answer, say
so and move on - losing it costs the live moment and nothing else.
-->

---

<!-- _class: divider act -->

# Act III — The estimate package

## Three documents a principal can actually use

<!--
1:18–1:36 · 18 min · Act III — The estimate package

Eighteen minutes, three slides. Bid memo, flagged parcel table with statutory
lead times, crew-day build-up.

All three are committed under project-sh16/, so every one of them has a
fallback that is just a file on the laptop.
-->

---

# The bid memo

- What a principal reads before pricing the job, in one page
- Written by the tool, from the run, with its sources beside every claim
- It says what it could not check, which is the part that earns trust

> **To be written** — #84

<!--
1:18–1:36 · 18 min · Act III — The estimate package

Open project-sh16/bid-memo.md on screen. Scroll to the honesty block and stop
there for a moment.
-->

---

# The flagged parcel table

- Every tract with something on it that costs time
- Sorted so the one needing a phone call soonest is at the top
- Statutory lead times, each with a citation you can check
- Unknown is never written as no. One of those sends a crew to a locked gate
- Gated access and livestock cannot be screened, and the output says so

> **To be written** — #84

<!--
1:18–1:36 · 18 min · Act III — The estimate package

project-sh16/flagged-parcels.svg is the projector drawing, and
project-sh16/flagged-parcels.md carries the table. The last two bullets are
the ones a party chief cares about.
-->

---

# The crew-day build-up

- The hours estimate shown as arguable math, not as a single number
- Every rate has a handle, so anybody can point at the one they disagree with
- An estimate you can argue with is an estimate you can defend

> **To be written** — #84

<!--
1:18–1:36 · 18 min · Act III — The estimate package

Cut 2 of 3. If time is short, show project-sh16/crew-day.md as a finished
output instead of building it live. The finished file makes the same point.
-->

---

<!-- _class: divider -->

# Review, seal — and the three failures

## An hour of it working. Now the part that matters.

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Twelve minutes, five slides, placed after an hour of the agent succeeding
because that is when a failure lands.

If the session is behind by 1:36, cut beat 2. It is the most technical of the
three and the least about accountability. Beat 3 is never cut.
-->

---

# Where the work got sent back

- This repo was built the way this session tells you to work
- Here are the issues, the check prints, and the places it got redlined
- Including one that was approved and should not have been
- Not a demo. A record, and it is public

> **To be written** — #85

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Fallbacks: docs/managing-your-agent/the-force-push.md and
docs/managing-your-agent/the-claim-we-got-wrong.md tell this from the repo
rather than from GitHub.
-->

---

# Beat 1 — the superseded manual

- Search still points at a TxDOT address that no longer serves the manual
- The agent found the wrong document, believed it, and cited a dead revision
- It did not lie. It did what a new hire does with a stale binder
- The defense: fetch the URL you are about to cite, and check what comes back

> **To be written** — #85

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Fallback: python -m corridor_screen.manual_links --show, from the
corridor-screen folder. It needs no network.
-->

---

# Beat 2 — the silent `NoData`

- `NoData` is a service saying "no height recorded for that point"
- One question, asked twice, one word apart
- It ignored the coordinate system, landed in the ocean, and said `NoData`
- No error, and the web's code for "here is your answer" on both
- It did not fail. It answered. That is worse

> **To be written** — #85

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Not on the cut line, and the block it sits in is never cut. The plan's own
timing warning is narrower than that: if the run is behind at 1:36, drop
this one beat -- the most technical of the three and the least about
accountability -- and keep the block.

Fallback: python -m corridor_screen.elevation_trap --show
-->

---

# Beat 3 — the error in our own work order

- Our own work order told the agent to publish a false statement of law
- A licensed human wrote it. It was already on four pages of this repo
- The agent went looking for the citation our own rules demand, and stopped
- If your checking only runs one direction, you have built half of it

> **To be written** — #85

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Never cut. Needs about three minutes: the room has to see the work order
before it sees the catch.

Fallback: corridor-screen/captures/the-work-order/issue-7.txt has both halves,
in order. The rule that caught it was written for something else entirely.
-->

---

# You seal it. You own it.

- TBPELS has spoken directly to AI. Its answer is the existing doctrine
- AI is a tool. The licensee is responsible for what they sign and seal
- Responsible charge is direct supervision's standard, not a looser one
- Personally review and approve decisions before they are acted on

PAO 71, 14 Nov 2024 · pels.texas.gov · 22 Tex. Admin. Code § 131.2(11), (38)

> **To be written** — #85

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Every claim on this slide needs its citation: PAO 71 of 14 November 2024, and
22 TAC 131.2. docs/governance/seal-and-responsible-charge.md carries both, and
needs no network.
-->

---

<!-- _class: divider -->

# Hermes

## The second letter that sends itself

<!--
1:48–1:54 · 6 min · Hermes

Cut 1 of 3. Six minutes, two slides, and first on the cut line - so this whole
section from this break to the next one comes out in a single deletion.

Build it so it survives being reduced to a recorded teaser. See #34.
-->

---

# The letter nobody remembers to send

- Right of entry is not a statutory right in Texas. You have to ask
- A denied RPLS *may seek* a court order; an LSLS *is entitled to* one
- Day 21 comes out of the lead-time math, not out of a hard-coded number
- Nothing in it touches client data

Tex. Occ. Code §§ 1071.3585 and 1071.358 · lead times in the repo, each cited

> **To be written** — #34

<!--
1:48–1:54 · 6 min · Hermes

If the live demo is cut, play the recording and say plainly that it is a
recording. Its own work order asks for one.
-->

---

<!-- _class: divider -->

# Accountability · Monday morning · the live issue

## What to do when you get back to the office

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

Six minutes, three slides, and the close. Never cut.

The last slide opens one real GitHub issue live, which teaches issues,
instruments adoption, and picks the next worked example, all at once.
-->

---

# The pattern, said out loud

- Corridor, then public data, then a flagged list, then lead times
- That works for a ranch boundary and an ALTA as well as it works for a highway
- Nothing in it is specific to TxDOT except the services it calls
- Name the pattern before you show the next example

> **To be written** — #86

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

Say the pattern out loud before the live issue goes up. The room has to hear
the general shape before it will offer its own examples.
-->

---

# Monday morning

- Point one person in your firm at the repo. Not the whole office
- Write your firm's AI-use policy before anybody needs it, not after
- Decide what client data never leaves the office, in writing
- Nothing changes about who signs and who carries the liability

> **To be written** — #86

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

docs/for-principals/ is the one page to hand somebody. Hold up the handout
here if it is printed.
-->

---

# Introduce yourself

- One issue, opened live, on the projector
- Tell us who you are and what you would automate
- The replies pick the next worked example
- The short link and the QR code are on the handout

> **To be written** — #86

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

The form is .github/ISSUE_TEMPLATE/introduce-yourself.yml.

It cannot collect a reply without GitHub, so if the network is gone, put the
form on screen and ask the room to do it from their seats.

The short link and QR code are #10, then #38. Check they exist before the day.
-->
