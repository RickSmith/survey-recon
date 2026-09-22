# Prototypes — throwaway code, kept as a record

Nothing in this folder ships. Nothing in this folder is merged into `main`.

A prototype here is code written to answer one question and then thrown away.
It is kept because the answer is worth more with the thing that produced it
sitting beside it. When a decision comes out of one, the decision gets written
properly somewhere else, and the prototype stays here as the record of what was
tried.

There are no tests on this code, and there is no error handling in it beyond
what makes it run.

---

## `job_page_prototype.py` — the job page, three ways

**The question**, from
[issue #194](https://github.com/RickSmith/survey-recon/issues/194): what
sections does the job page have, in what order, and what happens when a
principal clicks one of the eight flagged tracts?

**The plan**, in one line: three variants of the job page, switchable via
`?variant=`, in one self-contained HTML file built from the committed SH16 run.

### The answer, settled by Rick on 2026-09-22

**B wins, except for what B does with the memo.**

| | What the job page does |
|---|---|
| What a principal sees first | The numbers, then the eight flagged tracts. Not the map |
| Clicking a flagged tract | The row expands where it sits |
| Toggling a layer | The whole page. Switch off control and the control section goes with it |
| Crew safety | One number among the others, with no heading of its own |
| The bid memo | **On the page.** This is the one place the answer is not B's |

The memo is the exception because of finding 6 below: B links the memo out,
and a link is the part of B that does not survive. Finding 5 measured what
carrying it costs instead — 4 printed pages.

**Nothing is built from this.** [#188](https://github.com/RickSmith/survey-recon/issues/188)
freezes the repo before the session on 8 October 2026 and says the map is
planning only. The decision is recorded; the code stays on this branch.

### How to run it

```
python corridor-screen/prototypes/job_page_prototype.py
```

It writes `corridor-screen/prototypes/job-page-prototype.html`. Open that file
by double-clicking it. There is no server, nothing is installed, and it works
with the Wi-Fi off — which is what the real page has to do, so the prototype
does it too.

Switch variants with the bar floating at the bottom of the page, or with the
left and right arrow keys, or by editing the address:

| | |
|---|---|
| `?variant=A` | The map is the page |
| `?variant=B` | The list is the page |
| `?variant=C` | The page is questions |

The bar is deliberately ugly so nobody mistakes it for part of the design.

### What the three variants disagree about

They are not three color schemes. Each one answers the five open questions
differently, and the answers do not mix:

| Question | A — the map is the page | B — the list is the page | C — the page is questions |
|---|---|---|---|
| What a principal sees first | The map, full width | Seven numbers, then the eight tracts | A question, in words, with a one-line answer |
| Clicking a flagged tract | Opens its card below the map and scrolls to it | Expands the row where it sits, and marks the small map | Opens a panel over the page, one tract at a time |
| Toggling a layer | The map only | The whole page — switch off control and the control section goes with it | Neither. There are no switches |
| The bid memo | All of it, at the bottom | None of it. Links out instead | All of it — the page is the memo with the map in it |
| Crew safety | Its own section, low down | One number in the strip, which opens | Its own question, asked last |

### Why this is a page of its own

`/prototype` says to prefer hosting variants inside a real page, because a
throwaway page on its own is a vacuum where every variant looks fine. The
nearest real page here is the SH16 scenario page, and it was considered and
turned down: it is a site page built by mkdocs for somebody browsing the repo,
and [#188](https://github.com/RickSmith/survey-recon/issues/188) is blunt that
the job page is a single file emailed to a principal who runs nothing. Hosting
the variants in the scenario page would put them inside the one frame the real
thing never has.

The vacuum is answered a different way instead. The page carries the whole SH16
run at full density — every tract on the map, all eight flagged tracts told in
full, the memo entire — so no variant gets to look good by being empty.

### Where the numbers come from

The same place the drawings get them: the committed run in
`project-sh16/screening.json` and the cached service responses beside it.
Nothing on the page is typed in by hand.

A prototype that invents its own numbers teaches the wrong thing about how
crowded a real page gets, and this repo does not invent numbers anywhere else.

### What reacting to it found

Written down here as well as on the ticket, because the ticket is where the
decision goes and this is where the evidence is.

1. **The eight tracts are not eight decisions.** Seven of the eight are
   flagged for a school, and four of the eight belong to Northside ISD. Seven
   of the eight rows read *no published wait — school*. A list that says the
   same thing seven times in a row is one phone call, not eight, and variant B
   spends its best space saying it.
2. **Four of the eight sit on top of each other.** Over 8.691 miles in a
   browser-shaped frame, four flagged tracts land within about 38 pixels of
   each other. The first draft drew three of the numbers underneath the
   others, where they could be neither read nor clicked. Moving the numbers
   apart and drawing a leader line back to the tract is not decoration — click
   a tract on the map does not work without it.
3. **A panel over the page does not print.** A and B printed all eight tracts
   with no extra work. C printed none of them, because the rule that keeps the
   panel shut on screen keeps it shut on paper. It took a print rule written by
   hand. That is one real cost of the overlay, measured rather than guessed.
4. **The map wastes about half the width it is given.** The corridor runs
   northwest to southeast, so a landscape frame leaves wide empty margins on
   both sides. Whether the browser frame should be landscape at all is a
   question this prototype raised and did not settle.
5. **The memo is cheap.** Printed, variant A is 13 pages and the memo — all
   four of its sections — is 4 of them. Variant B carries no memo at all and
   still prints 11. So the reason to link the memo out is not its size, and any
   argument for a link has to be made on some other ground.
6. **A link out has nowhere to point.** Variant B is the one that links the
   memo instead of carrying it, and the link is the part that does not work.
   A path relative to the repo dies the moment the file is emailed. The only
   address that survives is this public repo on the open internet, which is
   both the wrong thing for a real client's memo and dead with the Wi-Fi off.
   The variant is built with those links so the cost is visible rather than
   argued about.
7. **The whole file is 374 KB**, with the map present once and moved into the
   active variant by JavaScript rather than copied three times. The real page
   carries one variant, so this over-states the real page and it is already
   inside the half a megabyte #188 guessed at.

### `measure_churn.py` — what the page costs git

```
python corridor-screen/prototypes/measure_churn.py
```

Written for [#192](https://github.com/RickSmith/survey-recon/issues/192), which
asked whether half a megabyte per run belongs in git and argued against on the
grounds that "each regeneration is a large diff nobody reads." That is a claim
about a number and nobody had the number.

It builds the page carrying one variant — which is what a real run writes —
then builds it again with one thing changed, and counts the lines between them.
On 2026-09-22:

| Change | Lines the page moves |
|---|---|
| A re-run, same data | **4** |
| A tract loses its flag | **91** |

The page is 1,270 lines and 318 KB, of which the map is 280 KB — 88% of it.

Four, because the generators here write one element per line, so a re-run only
moves the footer stamp. Ninety-one when a tract changes, which is the artifact
doing its job. The second number is the control: a measurement that only ever
shows small diffs has not proved anything until it also shows a big one.

So #192's case against was not true of this repo, and the ticket settled on
**commit it**.

### `measure_geometry_cost.py` — what one fat file would cost

```
python corridor-screen/prototypes/measure_geometry_cost.py
```

Written for [#193](https://github.com/RickSmith/survey-recon/issues/193), which
asked where the job page reads its data from. One live answer was that
`screening.json` should grow to carry everything the page needs, so the page
reads one file rather than two. Nobody had the size.

On 2026-09-22:

| | Bytes |
|---|---|
| `screening.json` today | 473,838 |
| The geometry, written the way the file is written | 1,020,433 |
| **`screening.json` if it carried the geometry** | **1,494,271 — 3.2x** |
| The cache, which stays either way | 4,129,838 |

`screening.json` carries no geometry today. A parcel record has no geometry
field, and the corridor names a cache key instead of holding its own ring.

The last row is what decided it. `CLAUDE.md` requires every API response to be
cached, so the cache folder stays whatever this ticket says. Growing
`screening.json` does not replace it — it commits a second copy of data already
on disk, at triple the size.

So #193 settled on the page reading **`screening.json` plus the cache**, which
is the shape `drawings.load()` already uses.

### `audit_print_contrast.py` — does the map survive a mono printer?

```
python corridor-screen/prototypes/audit_print_contrast.py
```

Written for [#195](https://github.com/RickSmith/survey-recon/issues/195), which
asked what a reader on paper loses. A principal is as likely to print the page
as to click it, and an office printer is as likely to be monochrome as not.

**The rule it holds:** two things a reader has to tell apart must not differ
only by fill color. It is about *pairs* — the flagged tract against the
ordinary one, the inside of the corridor against the outside. It does not
forbid fills: the four markers are an x, a triangle, a square and a cross, and
a shape is a shape whatever the ink.

On 2026-09-22 both pairs pass, and both pass **by their outline**:

| Pair | By fill | By outline |
|---|---|---|
| Flagged tract vs ordinary tract | 1.13:1 | **3.41:1** |
| Inside the corridor vs outside | 1.02:1 | **3.71:1** |

Below about 1.5:1 two colors are the same gray. So on paper the fills are
decoration and the strokes carry everything — **which holds by luck, because
nobody chose those strokes for a printer.** The rule is what stops somebody
later drawing a flag as a fill alone and never finding out.

### `read_the_floor.py` — proof the markup floor can be stood on

```
python corridor-screen/prototypes/read_the_floor.py
```

Written for [#196](https://github.com/RickSmith/survey-recon/issues/196), which
took three layers of checking for the job page. Two need a browser in a
container. The third — the floor — is meant to run on a bare Python with
nothing installed, reading the page back with `html.parser`.

That was the one claim in #196's answer nobody had run.
[#190](https://github.com/RickSmith/survey-recon/issues/190) had already found
that `xml.etree` **cannot** parse the page, so "just parse it" was not a safe
assumption to leave lying around. This parses it — 380,875 characters, standard
library only.

It checks facts about the file and only those: eight flagged tracts each
carrying an id so something can click them, all eight told in full in every
variant, every row with a detail behind it, the run reference present.

**What it deliberately cannot see is anything a stylesheet decides.** All three
defects #195 found were CSS, and this file passes every one of them. That is
not a gap in the floor — it is the reason the other two layers exist.

### How it was checked

Rendered and printed with headless Edge, which
[#190](https://github.com/RickSmith/survey-recon/issues/190) found ships with
Windows and needs nothing installed:

```
msedge --headless=new --disable-gpu --window-size=1400,1150 --screenshot=out.png "file:///...job-page-prototype.html?variant=A"
```

```
msedge --headless=new --disable-gpu --print-to-pdf=out.pdf --no-pdf-header-footer "file:///...job-page-prototype.html?variant=A"
```

The printing check is the one that matters most, because the page's PDF is its
own print stylesheet and nothing else. Printed, A is 13 pages, B is 11 and C is
14, and **all three print all eight tracts**. One of them did not until it was
made to.
