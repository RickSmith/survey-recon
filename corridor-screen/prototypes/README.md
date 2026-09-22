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
