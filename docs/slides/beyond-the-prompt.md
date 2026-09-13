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

- **SH16, Loop 410 to Old Bandera Rd** — 8.69 miles, Bexar County
- 300 ft each side of the centerline. We chose that and can modify if needed
- Asked for: what is out there, and what it costs in crew days
- 14 public map services. No client file was opened

This will be real code and real data (we might use previously captured if the internet acts up). You will be able to run this yourself using the GitHub repository: corridor-screen/README.md

<!--
0:00–0:08 · 8 min · Cold open

One slide only. The terminal is the thing on screen for this block; this is
what goes up beside it, or behind it, while the run finishes.

Do not explain the tool yet. The whole point of the cold open is that the room
watches something real happen before anybody has defined a single term. No
slide in this block says what an agent is, and the next block is where that
starts.

The plan is to run it live. The cache is the backup, not the plan -- the
committed SH16 run really did call all fourteen services on 13 September.
Say that plainly if the network makes you switch: "this is running off
answers we captured on the 12th and 13th." Undisclosed caching, if the room
notices it, costs you the room. The last line on the slide is what keeps that
honest whichever way the demo goes.

What it does next -- it reads, it asks, and it shows its work -- is worth
saying out loud and did not fit on the slide. The terminal is demonstrating
all three anyway.

No count on this slide is a result. 8.69 miles and 300 ft are what went in;
524 tracts is what comes back, and it comes back on the terminal beside you.
Do not say it before the run does.

"300 ft each side" is the half-width, and the point of the bullet is that a
person chose it. Somebody will ask why not 200 or 500. The answer is that it
is stated rather than derived, so it can be argued with -- and it can be
changed and the run done again, which is the bullet's own promise.

Fallback: docs/presenting/fallbacks.md, row one. The whole run replays off the
disk with --mode cache-only and makes no network call at all. Do not retype
that line; copy it from corridor-screen/README.md under "If the network is
down".
-->

---

<!-- _class: divider -->

# What is an agent

## From a prediction engine to something that does work

<!--
0:08–0:20 · 12 min · What is an agent

Twelve minutes, four slides. Prediction, then the three shapes of the tool,
then the loop, then where it breaks. Nothing here is about survey work yet,
which is deliberate: the room needs the mechanism before it will believe the
demo.

**The fourth slide is where it breaks**, and it belongs here rather than at the
end: a room that has watched something impressive and *then* hears the caveats
has already stopped listening to them. Nothing in this block is on the cut
line — §7 drops Hermes, the build-up and the token slide, in that order.
-->

---

# It predicts the next word

- It predicts the next word. Then the next one. That is the whole mechanism
- Run that at scale — books, code, manuals, and yes, survey documentation
- **The survey parallel: a traverse.** One trivial operation, repeated enough
- Skills nobody wrote in — grammar, arithmetic, code — appeared as it got bigger
- Which is why a wrong answer arrives in the same voice as a right one

<!--
0:08–0:20 · 12 min · What is an agent

Keep this fast. This room has heard of ChatGPT and does not need the
architecture.

Land the traverse analogy and move. A trivially simple operation, repeated at
scale, produces something powerful — that is a sentence this room already
believes about their own work.

Flag the catch here rather than at the end: prediction has no idea when it is
wrong. Beat 1 at 1:36 is where that lands.
-->

---

# Chatbot, copilot, agent

- **Chatbot** — you ask, it answers. You do all the work
- **Copilot** — it drafts, you drive every step and accept or reject each one
- **Agent** — you state the outcome; it plans, acts, checks, and goes again
- The shift is from writing *about* the work to actually doing the work
- What changes is not intelligence. It is what the tool may touch

<!--
0:08–0:20 · 12 min · What is an agent

The survey version, if the room wants one: chatbot is "how do I buffer a
parcel layer?" Copilot writes the buffer while you watch every line. Agent is
"here is the parcel data, produce the buffer and flag what is odd" — and it
goes and does it, fixing its own errors on the way.

The distinction that matters to a principal is the last bullet. A chatbot
cannot cost you anything. An agent can, because it acts.
-->

---

# The loop

- **Goal** — you state the outcome
- **Reason** — it plans the next step
- **Act** — it calls a tool: writes code, reads a file, queries a map service
- **Observe** — it reads the result, adjusts, and goes round again
- It runs until the work is done, until it is stuck, or until it asks
- **You decide what "done" means, before the loop starts**

<!--
0:08–0:20 · 12 min · What is an agent

This is the most important slide in the block. **The capability is not a
smarter model. It is the loop.** It writes code, runs it, reads the error,
fixes it, runs it again — and that self-correction is what the room is about
to watch happen live.

What the loop runs on, if anybody asks: a model, tools, the context it can
see, and guardrails — what it may touch and what it has to ask about first.
The guardrail example that lands: this one asks before it deletes anything or
spends money.

A human decides what "done" means, before the loop starts. That is Act I.
-->

---

# Where it breaks

- **Confidently wrong.** It invents things, and it believes stale things it finds
- **Fooled by what it reads.** Give it least access, not the run of the yard
- **Data.** What you type goes to a company's computers. Treat it as email
- **Accountability is yours.** *The agent did it* is not a defense

**PAO 71** — TBPELS, 14 Nov 2024 · pels.texas.gov/nm/2024/pao-71-response.pdf

<!--
0:08–0:20 · 12 min · What is an agent

This slide is not on the cut line — §7 of the plan of record drops Hermes, the
crew-day build-up and the token slide, in that order, and none of them is this
one. It is what separates a briefing from a sales pitch, and this room can
smell the difference.

**PAO 71 is not a new rule.** The board said the rules it already has cover
AI, and named four of them. Full text and the rule numbers are in
docs/governance/seal-and-responsible-charge.md.

"Least access" in their words: a key to one gate rather than the whole yard.
Give it what the job needs and nothing else.

**Cost is off this slide on purpose** — retries and long documents are billed,
and the money slide at 0:46 does that argument properly. Say it here only if
somebody asks.

Say the last bullet their way — you seal it, you own it. The close at 1:54 is
where it gets said properly.
-->

---

<!-- _class: divider -->

# Vocabulary of managing one

## Every word here has a survey equivalent

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Ten minutes, five slides. Markdown, the repo and git, issues, context, tokens.

Every one of these is introduced by its survey equivalent first. The
translation table is in CONTEXT.md at the root of the repo, and it is the
authority for the words used here.
-->

---

# Markdown

- **Markdown is plain text with a few marks** — not a CAD file, no proprietary
  format, and no version that will not open in nine years
- The marks do the formatting: `#` makes a heading, `**this**` goes bold
- Everything in this session is written in it, including these slides

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Show this file on screen for ten seconds. Seeing the slide and the source side
by side does more than a paragraph of explanation.

Why it matters rather than what it is: an agent reads and writes markdown
natively, so the instructions you give it and the work it hands back are the
same kind of file. Plain text on any machine, no software to buy.
-->

---

# The repo, and git

- A **repo** is the job folder. **Git** is the field book that never loses a page
- A **branch** is a working copy nobody else is affected by
- A **commit** is a field book entry, with a date and a name on it
- Nothing is overwritten by accident, so nothing is quietly lost

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Do not teach git commands. This room is deciding whether to point somebody at
this, not typing it themselves. Terms only, and the survey word first.

The line that lands: every change to this session's own repo is a field book
entry with a name and a date on it, and you are about to see the messy ones.
-->

---

# Issues, and pull requests

- An **issue** is a work order: what to do, and how you know it is done
- A **pull request** is the check print you redline before anything is final
- **Merging** is signing and sealing
- Nothing reaches the job without somebody licensed looking at it

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

This is the slide that sets up the whole accountability argument at the end.
Land the last bullet slowly.

Every word on this slide has a survey word beside it on purpose — the
translation table in CONTEXT.md at the root of the repo is where they are
settled, and it is the authority, not this slide.
-->

---

# Context

- The **context window** is what is spread on the desk right now. Anything off
  the desk might as well not exist
- Every word it writes, it **re-reads** that whole window first
- A handbook committed in the repo is on the desk every time. A conversation is not
- **The survey parallel:** written office standards against hallway advice

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Beat 3 at 1:36 is the payoff for this slide. The rule that caught our own
error was written in CLAUDE.md months before, for a different purpose — it was
in the window every time, so it was applied every time.

The failure mode worth naming if there is time: a window that is full has to
drop something, and what gets dropped is usually the oldest part of the
conversation. Which is why the rules belong in a file, not in a chat.
-->

---

# Tokens

- A **token** is a crew-hour for the machine — what the tool counts and bills
  *you* in. Never the unit you bill a client in
- About **4 characters**, or three quarters of a word
- *"Understanding AI is fascinating!"* is **7 tokens**, not four words
- Which is why a long document costs more to work on than a short one

<!--
0:20–0:30 · 10 min · Vocabulary of managing one

Cut 3 of 3. This slide goes to a footnote in the repo if the session is
running long. Keep it to one slide so the cut is a single deletion.

The example is the whole slide. It splits as Understand · ing · AI · is ·
fascin · ating · ! — seven pieces for four words, because long words break up
and the space before a word travels with it.

**Say "about".** How a sentence splits depends on the model doing the
splitting, and the seven above is one model's answer, not a law. Four
characters is the rule of thumb worth remembering.

**Do not let the room hear "so I bill my client in tokens."** They do not. The
money slide at 0:46 is in crew-hours and stays in crew-hours. A token is what
the tool costs *you*, which is the smaller of the two numbers by a distance.
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
- **The survey parallel:** the scoping call you wish clients would sit through
- On SH16 it asked **19 questions**, in three rounds, in one sitting
- You answered every one. Nothing was assumed on your behalf

The real run — corridor-screen/captures/the-grilling/README.md

<!--
0:30–0:46 · 16 min · Act I — The grilling

Set up the live run here, then stop talking. The room learns more from
watching the questions arrive than from any description of them.

"It is allowed to disagree with you" is the bullet to say slowly. This room
has bought software that does what it is told and produces confident rubbish.
An agent that pushes back is the unfamiliar part.

Do not promise 19 questions live. That is what it asked on 12 September, on
this job, and it is on the slide as a past fact. A live run asks what it
asks.
-->

---

# Live: the interview

- Run it against the SH16 scope, on the projector, at full size
- Let the silences sit. The questions are the content
- Watch for the one it asks that nobody in the room had thought of

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block. This slide is a holding card; switch away from it immediately.
Three bullets, and they are for you rather than for them.

If the live run will not start, open
corridor-screen/captures/the-grilling/README.md and say plainly that it is a
**transcript, not a recording**. There is no video of that session and there
never was. The README is the whole block on one screen; the full run is
corridor-screen/captures/the-grilling/the-grilling.md beside it.
-->

---

# Live: from answers to a scope of work

- The interview becomes a written scope you can read and argue with
- Every decision is on the page, including the ones you did not make
- Nothing is assumed silently, which is the whole value of it

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block. Show the spec document, scroll it once, slowly. Do not read it out.

The scope of work it writes is docs/corridor-screen/spec.md, and it is
committed — so if /to-spec will not run, open the file that run produced and
say that is what it produced.

The sentence for this slide, if you need one while it scrolls: this is the
check print. You redline it now, on a page, instead of finding it in the
field.
-->

---

# Live: from a scope to work orders

- The scope breaks into numbered work orders, each small enough to check
- They land on GitHub, publicly, while the room watches
- Last time: **35 work orders in 89 seconds**, numbered 5 to 39

GitHub stamped these — corridor-screen/captures/the-grilling/the-tickets.md

<!--
0:30–0:46 · 16 min · Act I — The grilling

Live block, and the one that gets the audible reaction. Have the issues page
open in a second window so you can switch to it the moment they appear.

**35 in 89 seconds is a past fact, not a promise.** Those times are the ones
GitHub stamped -- 20:32:08 to 20:33:37 on 12 September -- and they are the part
of that file nothing later can edit. A live run produces what it produces.

Two things about the capture, if anybody asks. The tickets file is the result
of a /to-tickets run, **not a recording of one**, and the grilling beside it
never ran that command at all. And row one of it is issue #5, "Specify the
corridor-screening tool" -- which is the work order the grilling was run
against, hours later. The tickets came first. The stage runs them the other
way round because that is the order the ideas go in, not the order that
Saturday went.
-->

---

# Why this is the hinge

- The work you do before the agent starts decides the outcome
- A vague assignment produces confident, plausible, wrong work
- **This is not new.** It is how you already supervise a party chief
- **13 of the 19 answers** were "your recommendation" — delegation, working
- **5 answers changed the shape of the tool.** That is what you are for

corridor-screen/captures/the-grilling/README.md

<!--
0:30–0:46 · 16 min · Act I — The grilling

If only one slide from this block survives a cut, it is this one. Say the
third bullet in their words, not in software words.

**The last two bullets are the argument.** Thirteen "your recommendation"
answers is not laziness -- it is what delegation looks like when it is
working, and this room delegates for a living. The five that changed the tool
are the ones nobody else in the building could have given: which file formats
a firm actually owns, what to do when a source is down, that you look at the
drawing before you trust the numbers, that parcel data differs county to
county, and that scope has to be cut somewhere.

The two counts overlap by one. Q14 says "your recommendation" and then adds a
condition, so it is in both. Thirteen and five do not add to eighteen, and
somebody will check.

**Q18 is the one to dwell on if you have the time.** The agent had designed a
general, swappable parcel-source config. Rick cut it -- never mind for this,
stick to Bexar County. An agent will happily build the general case nobody
asked for, and the person paying for it is the one who stops that.
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

- **38 crew-days** in the field — 299.29 hours at 8 to the day, 2 people to a crew
- **18 days** in the office — 138.26 hours. The two are never added together
- Largest line: corner recovery, rate `A4` — 524 tracts at 0.5 hours = 262.00
- Argue with `A4`. Do not argue with the total
- 2 lines have no total at all, so 38 is a floor rather than an estimate

<!--
0:46–0:52 · 6 min · The money slide

Every figure here is read out of project-sh16/crew-day.md, and the tests fail
if this slide and that file ever disagree. Nothing on it was typed from memory.

Say the handles out loud. A4 is the one this room will want to argue with —
half an hour on every tract the corridor clips, whether it is a ranch or a
quarter-acre lot — and letting them argue with it is the whole point of
showing the arithmetic.

Do not price the agent here. Nothing in this repo has measured what it saves,
and a number invented on this slide is the one they will quote back at you.

Hours, never a price per seat or per month. Nobody in this room buys software
that way, and quoting it in those units loses them.

299.29 and 138.26 are crew-hours, not person-hours. If somebody in the second
row starts halving them, that is why.

An RPLS directed this run and checked every figure on it. Say so if you are
asked; the accountability close at 1:54 is where it gets said properly.

Fallback: project-sh16/crew-day.md is the build-up itself, with every step.
-->

---

# Rework, not speed

- **"There is no acceptable failure rate for any TxDOT survey"**
- A non-compliant survey **cannot be invoiced**
- Not a sentence about quality. A sentence about money
- Hours you have already paid a crew for, and cannot bill to anybody
- Speed is the smaller half of this argument

Survey Manual (ESS) rev. April 2026, Ch. 4 · txdot.gov/manuals/row/ess

<!--
0:46–0:52 · 6 min · The money slide

Read the quote off the slide rather than paraphrasing it. This is the sentence
an owner repeats to their accountant, and the citation is on the slide so the
back of the room can check it while you are saying it.

If the room wants to talk about speed, bring it back to the unbillable hours.
An agent that reads every standard before the crew rolls is aimed at rework;
the time it saves is real and is the smaller argument.

Never onlinemanuals.txdot.gov — that host is the failure beat later on.

Fallback: docs/for-principals/index.md makes this argument and carries the same
citation, on one page written for this room.
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
- Fourteen services. Every one answered, and the run finished complete
- All of it from public sources. **No client data, ever**

<!--
0:57–1:18 · 21 min · Act II — Find the control

The last bullet is a governance point disguised as a technical one. Say it
plainly: nothing belonging to a client went anywhere near this.

"Every one answered" is worth a beat. Fourteen public services, no sanity
check tripped, and the run finished `complete` rather than `incomplete`. That
is not the normal outcome and the tool is built for the other one -- a dead
service stops the run and a doubtful answer records a warning, which is
ADR 0001.

The three findings come next in the order an estimator needs them: what
control is published, whether it is still there, and what the record drawings
are. Do not reorder them for variety.
-->

---

# The NGS marks

- **11 marks in the corridor. All 11 read `MARK NOT FOUND`**
- That is a report with a date on it, not a verdict
- Somebody looked and did not find it. You may have to set it
- **11 is not 11 pieces of control you have.** It is 11 you may set
- Nothing here was *condition unknown* — nobody-looked is a third answer

project-sh16/screening.json

<!--
0:57–1:18 · 21 min · Act II — Find the control

The distinction in bullets two and three is the one an estimator gets wrong.
A count of marks reads as control you have.

**All eleven is the number that lands.** Not several, not most -- every
published NGS mark inside this corridor was last reported as not found. An
estimate built on "eleven marks are out there" is an estimate for recovering
control that may not be there to recover.

The word to be careful with is "destroyed", and it is not the word NGS used.
`MARK NOT FOUND` says somebody looked on a date and did not find it. It may
still be under six inches of caliche. TxDOT publishes a *destroyed* for its
own monuments, which is the stronger claim, and that is the next slide.

Zero `condition unknown` here, and say that rather than skipping it. It is
the third answer -- nobody looked at all -- and a corridor where it is not
zero is a corridor with a gap nobody has measured.
-->

---

# The TxDOT control points

- **4 records in the corridor. They name 2 distinct monuments**
- A crew drives to the monument. An estimator must not count it twice
- All 4 published `Good`. **None carries a recovery date**
- None destroyed and none unknown here — but *good* on what day?
- *Monument destroyed* is a stronger claim than `MARK NOT FOUND`
- *Condition unknown* is neither. Nobody looked, so nobody knows

project-sh16/screening.json

<!--
0:57–1:18 · 21 min · Act II — Find the control

Distinct stations against record count is the detail that makes a surveyor
trust the rest of the output. Do not skip it for time.

Four records, two monuments, and the tool reports both numbers rather than
picking one. The service holds two records for 274 of its 492 stations, so
this is the ordinary case and not a quirk of this corridor. Do not call that
a statewide figure -- this service is the **San Antonio District's** control,
and docs/data-sources/txdot-control-points.md is blunt that no statewide
TxDOT primary control service was found.

**The third bullet is the one to land.** All four read `Good` and not one of
them carries a recovery date -- `last_recovered` is empty on every record. The
NGS marks on the slide before this are the opposite: a harder word, with a
date attached. An undated `Good` is a weaker thing to build a bid on than a
dated `MARK NOT FOUND`, and this room will get that immediately.

**Bullets five and six describe words, not findings.** Neither destroyed nor
condition unknown turned up here. Say so, because a room that hears the
definitions will assume they were found. They are on the slide because they
are three different statements about a monument and only one of them means
you have it.

The contrast with the previous slide is the point of the pair: eleven NGS
marks nobody could find, and two TxDOT monuments called good by nobody on no
date. Same corridor, two agencies -- and only the query happened on one day.
-->

---

# The right-of-way map sheets

- **69 sheets reach this corridor. 15 of them are SH16's own**
- The other 54 belong to the crossing routes at the interchanges
- SH16's 15 date **1944 to 1998** — fifty-four years of drawing
- Across all of Bexar County SH16 has **27**, 1937–1998. Both are right
- **Say which question you are answering.** Corridor, or county

docs/data-sources/row-map-sheets.md

<!--
0:57–1:18 · 21 min · Act II — Find the control

docs/data-sources/row-map-sheets.md works the corridor-against-county
difference through properly. Take the numbers from there.

**69 and 27 are both true and they answer different questions.** 69 is what
reaches this corridor, because the right of way at an interchange is drawn on
the crossing route's sheets -- IH0410 contributes 24, Loop 1604 nineteen,
FM0471 eight, FM1560 three. 27 is SH16 across the whole county, over three
control sections, 15 + 8 + 4. Quote one, say which, and do not let the room
hear the other as a correction.

This row of the run of show was wrong until 2026-09-13 and said 27 as if it
were the corridor figure. The account is issue #80. If somebody has an older
handout, that is why.

The tool reports sheet numbers and dates. **It does not fetch the drawings.**
Those come from the Real Property Asset Map, and anything not there is an Open
Records Request. Say that plainly -- it is a real gap and it costs real days.
-->

---

# The datum gap

- **April 2026** Survey Manual: no realization, no epoch, no geoid model
- No reference in it to **NATRF2022**, **NAPGD2022** or **SPCS2022**
- Its control service: geoid `N/A` on 4 records, 2 monuments here; `GEOID03` just outside
- *"TxDOT will not accept any datum transformations for control"*

**So what do you certify to?** Name realization, epoch and geoid in your report

Survey Manual (ESS) rev. April 2026, Ch. 3 · txdot.gov/manuals/row/ess

<!--
0:57–1:18 · 21 min · Act II — Find the control

This is the slide most likely to be quoted afterward, out of a photograph taken
from the fourth row by somebody who was not here. So say the sentence on the
slide and stop.

**It is a gap, not a mistake.** Nobody in this room gets to be smug about it,
and a slide that sounded smug would cost you every contractor in the audience.

**Four records, two monuments.** Say both numbers. The slide before this one
just made that exact point, and a record count heard as a monument count
doubles the control an estimator thinks is already set.

**GEOID03 is the part the room will react to**, so let them. Say what is
there and nothing more: the same service, the same response, two records
outside this corridor, naming a geoid model where this corridor's records
name none. Whether that is right is not ours to say from a podium.

The rest of what a report can say, beyond the line on the slide — a firm's
choice, not a rule anybody has written:

  - where the published values came from, and on what date
  - that no transformation was performed, which the manual does require

Sources: docs/txdot-research.md has the finding and how it was read;
docs/data-sources/txdot-control-points.md has the N/A geoid in the live data;
the GEOID03 records are in project-sh16/cache/txdot-primary-control-points.
-->

---

# The one genuinely live call

- Everything so far came off the disk, captured in September, and we said so
- This one goes out to the network now, in front of you
- Last time: **5 marks in both, and all 5 conditions agreed**
- If it fails, that is also true, and we will say that too
- One live moment is what proves the rest is not a movie

<!--
0:57–1:18 · 21 min · Act II — Find the control

NGS /radial was the most reliable endpoint tested. If it does not answer, say
so and move on - losing it costs the live moment and nothing else.

**It is a cross-check, not a recording agreeing with itself.** The live call
asks NGS today; the capture is what NGS said on 13 September. Five marks
appear in both and all five conditions matched -- MARK NOT FOUND on every one.
That is the claim worth making: the cache is not stale in the way that would
matter.

Five is what it found last time, not a promise. It is a live call.

It is a separate command rather than a mode, on purpose, so the worst a dead
network can do is cost this moment. The screening run is unaffected either
way, and the command says so itself when there is no network.
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

- One page a principal reads before pricing. Written by the tool, from the run
- **What it could not check comes first**, ahead of anything it found
- Gated access and livestock: **no public source publishes either one**
- Right of entry unknown on every tract, deliberately. Refused, an RPLS *may seek* a court order — Tex. Occ. Code § 1071.3585
- Not a survey. Not a title search. **An RPLS reads it and decides**

project-sh16/bid-memo.md

<!--
1:18–1:36 · 18 min · Act III — The estimate package

Open project-sh16/bid-memo.md on screen and scroll to *What is not known, and
why*. That section sits above the findings in the file, not below them, and
that ordering is the whole slide. Say so out loud -- a memo that leads with
what it could not check is a memo a principal can price against.

**Two different things earn the trust here, and they are worth keeping apart.**
*What is not known, and why* is the gaps section, and what makes it work is
where it sits. The **honesty block** is the other one, and CONTEXT.md reserves
that term for something narrower: the record of every service called, whether
it answered, when its answer was captured and what was doubted about it, which
is what *What was done* and the screening file beside the memo carry. Do not
call the gaps section the honesty block on stage. A room holding CONTEXT.md
will hear it, and this deck is the thing teaching them the word.

Four gaps are worth naming off the screen, because each one costs somebody a
phone call: gated access and livestock, which nothing public publishes; the
existing right-of-way width, which was not read; how much of each tract the
corridor takes, which was counted but never measured as an acreage; and whether
TxDOT already owns a tract, which was not checked at all.

**Right of entry is the one with a statute behind it**, so the citation is on
the slide rather than only here. An RPLS refused permission *may seek* a court
order, Tex. Occ. Code § 1071.3585; an LSLS acting officially *is entitled to*
one, Tex. Occ. Code § 1071.358. Two different verbs, two different licenses,
and two sections a digit apart. No parcel polygon establishes either, and
nothing in this screening is permission to enter.

Do not let the room hear this as a disclaimer page. It is the findings section
of an estimate, written by something that knows the difference between
*not found* and *not there*.

Fallback: the memo is committed at project-sh16/bid-memo.md, so the fallback
for this slide is opening the file on the laptop.
-->

---

# The flagged parcel table

- **8 of 524 tracts** cost time. Soonest phone call at the top
- `unknown` is never written as `no`. One of those finds a locked gate
- School, **not found** — 7 of the 8. Unmeasured, so it sorts first
- Cemetery, **14 calendar days** — Tex. Health & Safety Code § 711.041(c)(2)
- Gated access and livestock **cannot be screened**. The run says so

project-sh16/flagged-parcels.md · project-sh16/screening.json

<!--
1:18–1:36 · 18 min · Act III — The estimate package

project-sh16/flagged-parcels.svg is the projector drawing and
project-sh16/flagged-parcels.md carries the table. Put the drawing up and read
the table off it.

**Sorted by wait, not by parcel number.** The tract needing a phone call
soonest is the first row. An estimator reads the top of this table and starts
dialing, which is the only ordering that does any work.

**The unmeasured rows sort above the measured one**, and that is worth saying
out loud because it looks backwards for a second. A tract whose wait nobody has
measured needs the call *before* a tract whose wait is a known fourteen days --
the call is what turns the unknown into a date. Sorting the unknowns to the
bottom would read, correctly enough for a room at a glance, as "these are the
easy ones."

**The two words to keep apart are unknown and no.** One of them sends a crew to
a locked gate. Where a wait says *not found*, this repo looked for a published
notice period and did not find one -- docs/corridor-screen/lead-times.md records
exactly where it looked, which is what makes it a finding rather than a shrug.
It is not a shorter wait. It is an unmeasured one, and somebody has to make the
call that turns it into a date.

The school row is the honest one and it is seven of the eight. Looked in:
Tex. Educ. Code § 22.0834, which sets background-check conditions and no notice
period; the TxDOT Survey Manual (ESS) rev. April 2026,
txdot.gov/manuals/row/ess, which does not address school access; and TxDOT ROW
Preliminary Procedures Ch. 4. District board approval runs on a board's own
meeting cycle and badging follows approval -- both real, neither published as a
figure.

**Calendar days and working days are different promises** and this table never
converts one into the other. The cemetery figure is fourteen calendar days.

**The last bullet is the party chief's, and it names the run rather than the
table**, because the table is not where it is written. Nothing public publishes
gate locations or livestock, so the run records both under `not_screenable`
with the reason beside each, and project-sh16/bid-memo.md reads them out in
prose. The table lists tracts that were flagged; a thing nothing can flag was
never going to appear in it. Say "the run says so" and open the memo if the
room wants to see the sentence.

Fallback: all three files are committed under project-sh16/, so the drawing, the
table and the run are on the laptop whatever the network does.
-->

---

# The crew-day build-up

- The hours as arguable math, not one number to take or leave
- Every rate has a **handle**, `A1` to `A12`. Argue with a row, not a total
- **5 of the 12 inputs were never measured.** No total, not a zero
- Twelve rates, all plain text. Replace them before you quote a client
- An estimate you can argue with is an estimate you can defend

project-sh16/crew-day.md · these rates are published by nobody

<!--
1:18–1:36 · 18 min · Act III — The estimate package

Cut 2 of 3. If time is short, show project-sh16/crew-day.md as a finished
output instead of building it live. The finished file makes the same point.

**A handle is a short name stamped on one rate** so a room can disagree with
that rate out loud, by name, instead of disagreeing with the total. It is a
note number on a sheet: you say *note 8*, not *the drawing*. `A1` through `A12`
are in the build-up's own rate table, each beside the sentence saying what to
argue with.

Say plainly that none of the twelve is published by TxDOT or by anybody else.
The standard sheets say what goes on the road, not how long it takes to put it
there. These are this repo's assumptions and they are meant to be replaced --
corridor-screen/corridor_screen/crew_rates.toml is plain text a firm edits
without touching any Python, which is what the fourth bullet is promising.

**This slide deliberately says nothing the money slide already said.** At 0:46
this room was given the day counts, `A4` by name, and the half-hour-per-tract
figure behind it. Do not read any of that out again -- eighteen minutes is what
the run of show gives this block, and saying the same three things twice is how
it stops fitting. Have A4 ready for when somebody raises it, which somebody
will: halve it and the field estimate moves more than any other single change
on the page. Some of those tracts may already be in TxDOT's hands, too.

**The five unmeasured inputs are the point of the slide, not a caveat on it.**
Manholes, culverts, how many times traffic control gets set, how much of the
retracement falls on the centerline, and the existing right-of-way width. Two
whole lines of the build-up therefore carry no total at all, and those hours are
missing from the figures rather than being zero in them. The figures are a
floor.

Fallback: this is the slide to drop first inside the block. The build-up is
committed at project-sh16/crew-day.md, and project-sh16/crew-day.txt is the same
thing as the console prints it, in one screen.
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

- Every change here began as a work order and ended in a human review
- **Nothing was squashed.** The history is untidy because it is real
- The rule against rewriting it was broken **once**, knowingly, on day one
- The agent named the rule and laid out both options. A licensed human chose
- Not a demo. A record, and it is public

docs/managing-your-agent/

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Two pages, in this order, and neither one needs GitHub.

**docs/managing-your-agent/the-force-push.md first.** Fifteen minutes after this
repo existed, its own rule against rewriting history was set aside. What it cost
was one line of a license file, and the copyright name that survived is the more
correct of the two. What makes it worth a room's time is the shape: the agent
stopped, laid out both options, and named the rule it was about to break. Rick
chose, with the conflict in front of him.

**Say the word "once" out loud.** It has happened one time, on purpose, and that
page is a record rather than a precedent. A room that hears "we bend it when it
suits us" has heard the opposite of the point.

Then docs/managing-your-agent/the-claim-we-got-wrong.md, and only far enough to
say it is there. It is beat 3, twelve minutes from now, and telling it here
spends the surprise.

Fallback: this slide is already its own fallback. Both pages are committed, so
open them from the laptop and never open GitHub at all.
-->

---

# Beat 1 — the superseded manual

- Search still hands out a TxDOT address that TxDOT retired
- The old host answers nothing. **A timeout reads as weather**
- So it followed the link, read a real manual, cited **March 2025**
- The revision in force is **April 2026** — txdot.gov/manuals/row/ess
- It did not lie. It did what a new hire does with a stale binder

corridor-screen/captures/superseded-manual/ · captured 2026-09-13

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

Run `python -m corridor_screen.manual_links --show` from the corridor-screen
folder. It prints both addresses, what each one serves, and the evidence file
behind each. No network.

**The detail that makes this a beat rather than a broken link**: the retired
address is still published, and nothing answered on it at all — six attempts,
twelve seconds apiece, over both a plain and a secure connection. So a caller
waits and gets nothing back, which reads as a bad network rather than as a
retired document. A "page not found" would have told the agent something.
Silence told it nothing, so it used what the search gave it.

The defense is boring, and being boring is the point: fetch the URL you are
about to cite and read what comes back. This repo runs that check over its own
files on every test run, which is why the retired host is named in `CLAUDE.md`
rather than left to memory.

Fallback: corridor-screen/captures/superseded-manual/the-beat.txt is the same
beat as plain text, for a podium where Python will not start.
-->

---

# Beat 2 — wrong, not missing

- One question, asked twice, one word apart. Same point on Bandera Rd
- `units=Feet` → **866.87**. `units=US_Feet` → **264.22**
- Same ground. The second answer is in **meters** — 3.28084 ft per meter
- `US_Feet` is not a typo. It is the unit a Texas surveyor works in
- **No error either time.** Nothing in the reply says which unit

corridor-screen/captures/silent-nodata/ · captured 2026-09-13

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

**This is the beat to drop if the run is behind at 1:36.** The plan of record
says so: the most technical of the three and the least about accountability. The
block itself is never cut — only this one beat inside it.

Run `python -m corridor_screen.elevation_trap --show` from the corridor-screen
folder.

Two things to say while the numbers are up. First, `US_Feet` is the US survey
foot, EPSG 9003 — the unit TxDOT's Survey Manual asks for in deliverables,
txdot.gov/manuals/row/ess. The surveyor asking in the unit of their own
profession is the one who gets meters back.

Second, the same service can fail loudly, and that version is the safe one. A
point out in the Gulf answers with a line of plain English rather than the
structured reply a program knows how to read — so anything reading it breaks
inside a second, loudly, in front of somebody. The believable answer is the
dangerous one.

**What separates them is where the range check is drawn.** 264 ft is below the
floor of Bexar County, which runs roughly 400 to 2,000, so a check against this
county catches it and a check against the whole Earth sails straight past.
Nobody writes a county range check unless they already know where the job is.

Fallback: corridor-screen/captures/silent-nodata/the-beat.txt.
-->

---

# Beat 3 — the error in our own work order

- Our own work order told the agent to publish a false statement of law
- A licensed human wrote it. It was live on **four pages** of this repo
- **The same work order carried the rule that refused it** — criterion 5
- The agent went to find the citation, found **PAO 71**, and stopped
- Approved **14 Nov 2024** — public for nearly two years. pels.texas.gov

corridor-screen/captures/the-work-order/issue-7.txt · captured 2026-09-13

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

**Never cut.** It needs about three minutes, because the room has to see the
work order before it sees the catch. Two lines, in this order, and do not
summarize either one.

Open corridor-screen/captures/the-work-order/issue-7.txt. Acceptance criterion 4
is in the first half: "It states plainly that TBPELS has not spoken directly to
AI." A licensed human wrote that, in a work order, to be published. Read it out.

Then the comment in the second half: "Correction: acceptance criterion 4 is
factually wrong. Please do not restore it."

**Then say which rule caught it**, because that is the part a firm can copy.
Criterion 5 of the same issue — no invented requirement anywhere, every rule
cites its source or says it could not be confirmed — is the one the comment
credits. It came from the handbook rule in `CLAUDE.md`, written about TxDOT
manuals and about nothing like this.

The rule that catches an error is usually boring and was written for something
else. That is the argument for writing the handbook before you need it.

The account is docs/managing-your-agent/the-claim-we-got-wrong.md. The opinion
is quoted in full on docs/governance/seal-and-responsible-charge.md.

Fallback: corridor-screen/captures/the-work-order/issue-7.txt is the whole beat,
both halves in order, and it is the file to open first whatever the network is
doing. This is the beat that must not be cut, so it never depends on GitHub.
-->

---

# You seal it. You own it.

- TBPELS has spoken directly to AI, in writing, since 2024
- **AI is a tool. No rule bans it directly.** You answer for what you seal
- **Responsible charge is a synonym for direct supervision**
- Review and approve decisions **before they are acted on**
- Check the work as though you had done it yourself. You did

PAO 71, 14 Nov 2024 · pels.texas.gov · 22 Tex. Admin. Code § 131.2(11), (38)

<!--
1:36–1:48 · 12 min · Review, seal — and the three failures

The claim in this deck most likely to be photographed and forwarded, which is
why every citation on it is on the slide rather than only here.

**This repo said the opposite on four pages until 12 September 2026.** Say so.
If it is not said here it is not said anywhere, and beat 3 two slides back was
that correction landing.

What PAO 71 says, in the board's own words: AI software is a tool, neither the
Practice Acts nor the board rules directly ban it, and licensees are ultimately
responsible for any work product they sign and seal. It sets three caveats —
oversight and review, competence, and client data — and names the surveying
rules behind each. Its conclusion is that no new opinion was needed.

**The sentence to slow down on is the definition.** 22 Tex. Admin. Code
§ 131.2(11) says direct supervision entails that the surveyor personally makes
the decisions, or personally reviews and approves proposed decisions prior to
their implementation. An agent that ran unsupervised and handed over a finished
product did not have its decisions approved before it made them. That is the
whole argument for small assignments with a check print at the end of each.

Fallback: docs/governance/seal-and-responsible-charge.md quotes all of it and
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

- Right of entry is not a statutory right **in Texas**. You have to ask
- A denied RPLS *may seek* a court order; an LSLS *is entitled to* one
- TxDOT ships **two** templates. Non-response is the ordinary case

**Day 21 is derived, not typed.** 45 calendar days in `lead_times.toml`, cited
to Union Pacific — halved, 22 — rounded to whole weeks, **21**.

Tex. Occ. Code §§ 1071.3585 and 1071.358 · nothing in it touches client data

<!--
1:48–1:54 · 6 min · Hermes

Live: `python -m corridor_screen.roe --show` from the corridor-screen folder.
It reads from disk and makes no network call.

"With no human action" is a real claim, so point at the thing that makes it
one: .github/workflows/roe-followup.yml reads the same clock daily on a
schedule. If request 2 turned up in a run summary on 4 October and nobody
started it, open the run. That is the evidence; the command is the rehearsal.

If the live demo is cut, play the recording and say plainly that it is a
recording -- corridor-screen/captures/the-letter-that-sends-itself/the-demo.txt.
Its own work order asked for one.

The question from the room is "there is no railroad on that corridor." Correct.
The interval is how long a letter may sit before you ask again, which is firm
policy, so it comes from the longest wait the firm plans against anywhere. The
demo prints that sentence on screen.

Do not claim it mails anything. It writes a file. An RPLS signs and sends.
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

- **Corridor → public data → flagged list → lead times**. Four steps
- A ranch boundary and an ALTA fit that shape as well as a highway does
- Only the services change. Swap the parcel source and the four steps hold
- **Every step says what it could not check**, or the list prices nothing
- Say it out loud before you go looking for your own

corridor-screen/README.md · project-sh16/bid-memo.md

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

Say the pattern out loud before the live issue goes up, not after. The room has
to hear the general shape before it will offer its own examples, and the last
slide of the session is where it offers them.

**Four steps, and the fourth is the one people drop.** Corridor, then public
data, then a flagged list, then lead times. Stop at the third and you have a
list of tracts with nothing but a schedule-shaped hole beside it -- nobody
prices from that, and nobody schedules a crew from it either.

**The fourth bullet is the thesis of the whole session, so do not rush it.**
What makes this usable is not that it finds things. It is that it writes down
what it could not check: gated access and livestock, which nothing public
publishes, and the waits recorded as *not found* rather than as zero.

Nothing in the shape belongs to TxDOT. What a different job changes is the
services -- a parcel source, a control source, a flag source, and a lead-time
table the firm keeps and can argue with. Say that plainly when somebody asks
whether it works on anything but a highway, because somebody will.

Fallback: nothing live here. corridor-screen/README.md walks the same four
steps in its own words, on the laptop, with no network.
-->

---

# Monday morning

- **Point one person at the repo. Not the office.** Somebody fussy about sources
- **Write the firm's AI-use policy before anybody needs it**, not after
- Mark each rule as a board rule, as board guidance, or as firm choice
- **Decide in writing what client data never leaves the office**
- *Would I email this outside the firm?* is the whole test
- Who signs does not change — 22 Tex. Admin. Code § 138.33(b)

docs/for-principals/index.md · docs/governance/ai-use-policy.md

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

**This slide is for the people who buy the tool and carry the risk, not for
the people who would use it.** Nothing on it is a keystroke. If the room hears
an operator's slide here, they will wait for a demo that is not coming and the
session ends on the wrong note.

docs/for-principals/index.md is the page to hand somebody who was not in the
room -- four minutes, no command line. Hold it up here if it is printed.

**The first bullet is the one that gets argued with.** One person, not the
office: not necessarily your most technical person, because the skill being
asked for is supervision, which the firm already teaches. Somebody fussy about
sources, who has the standing to tell a confident answer that it is wrong.

**The third bullet is the whole point of the template** and it is worth saying
slowly. docs/governance/ai-use-policy.md marks every line as a board rule, as
board guidance, or as firm choice, so nobody in a firm can present a preference
as a requirement. A room that takes home one idea should take home that one.

The question on the fourth bullet is the entire checklist on
docs/governance/what-never-leaves.md. Ask it out loud and let it sit.

**Do not re-argue PAO 71 here.** That slide ran at 1:36 with its citation, and
this block has six minutes and three jobs. The last bullet is a callback, not
an argument -- say it once and move to the form.

Fallback: nothing live here either. All three pages are committed, so the
fallback is opening a file.
-->

---

# Introduce yourself

- One work order, opened live, on this screen. An **issue** is a work order
- Who you are, and the one job you would hand to an agent tomorrow
- Only that last box is required. The replies pick the next worked example
- **It is public. Treat it as permanent.** No client names, no job numbers
- github.com/RickSmith/survey-recon → Issues → New → *Introduce yourself*

No network in the room? Photograph this slide and do it tonight

<!--
1:54–2:00 · 6 min · Accountability · Monday morning · the live issue

The form is .github/ISSUE_TEMPLATE/introduce-yourself.yml. Open it live and
fill the first box in yourself, so the room watches somebody do it once.

**Three jobs at once, and say which one you are doing.** It teaches issues to a
room that met the word ninety minutes ago. It measures how many people actually
try this rather than how many nodded. And the replies pick what gets built
next, which is the only honest reason to ask anybody for anything at 1:59.

**The route on the slide is typed, not scanned, and that is deliberate.** The
short link is #10 and the QR code is #38. Neither exists yet, so nothing on
this slide leans on either -- when they land, add the code and leave the typed
route on, because a phone that will not focus in a dark ballroom is the
ordinary case rather than the unlucky one.

**Say the public-and-permanent line out loud rather than letting them read
it.** Everything here is public and stays public. The form asks them to tick a
box confirming they kept client-identifying work out of it, and that box is the
one thing on the form besides the question itself that they cannot skip.

Fallback: it cannot collect a single reply without GitHub, and that is a fact
about the ask rather than a failure of it. With the network gone, put
.github/ISSUE_TEMPLATE/introduce-yourself.yml on screen, read the question out,
and ask the room to do it from their seats that evening. The slide says so on
its face, because nobody out there sees this note.
-->
