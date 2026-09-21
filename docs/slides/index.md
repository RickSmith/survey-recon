# Slides

The deck presented at TSPS 2026. It is written in markdown, lives in this repo,
and is rendered by the same push that publishes this site — so what is on this
page is what was on the screen in the room.

<!--
  These two are plain HTML links rather than markdown ones on purpose.

  The deck is not built by the site builder — Marp builds it, and drops
  deck.html and beyond-the-prompt.pdf into this folder afterwards. The site
  builder checks every markdown link against the files it knows about, and it
  does not know about those two, so it would refuse to build.

  Nothing goes unchecked. .github/workflows/docs.yml confirms both files landed
  before it publishes anything.
-->
<p>
  <a class="md-button md-button--primary" href="deck.html" target="_blank">Open the deck</a>
  <a class="md-button" href="beyond-the-prompt.pdf">Download the PDF</a>
</p>

!!! note "It is a frame, not a talk"
    The deck is **48 slides** — one section break for every block of the two
    hours, and outline slides under each. **0 of them are still placeholders**.
    A placeholder says so on its own face and names the work order that will
    fill it, so that number is how many slides a reader should not trust yet.

    Slides still waiting on a work order: **0**, across **0** blocks of the
    session.

    The skeleton was built under
    [issue #12](https://github.com/RickSmith/survey-recon/issues/12). Ten
    pieces of content have landed. Each is checked against its own source on
    every test run.

    | What landed | Work order | What it is checked against |
    |---|---|---|
    | The cold-open slide | [#81](https://github.com/RickSmith/survey-recon/issues/81) | Its figures, read out of the SH16 run |
    | Act I | [#82](https://github.com/RickSmith/survey-recon/issues/82) | Its counts, tallied off the captured grilling rather than read out of its prose |
    | Act II | [#83](https://github.com/RickSmith/survey-recon/issues/83) | Every figure, read out of the SH16 run. The three figures #80 retired are checked for by name |
    | The money slide | [#32](https://github.com/RickSmith/survey-recon/issues/32) | Its figures, read out of the crew-day build-up |
    | The datum gap | [#33](https://github.com/RickSmith/survey-recon/issues/33) | Its counts, read out of the SH16 run |
    | The concept slides | [#31](https://github.com/RickSmith/survey-recon/issues/31) | The translation table in `CONTEXT.md` |
    | Hermes | [#34](https://github.com/RickSmith/survey-recon/issues/34) | Its day 21, derived from the lead-time table rather than written on the slide |
    | Act III | [#84](https://github.com/RickSmith/survey-recon/issues/84) | Each of its three slides, read back out of the document it frames |
    | The review, seal and three failures | [#85](https://github.com/RickSmith/survey-recon/issues/85) | Every figure and date on those five slides, read back out of the committed captures the beats were built from |
    | The close | [#86](https://github.com/RickSmith/survey-recon/issues/86) | The form, and the pages those three slides send a room to, and offering a way in that can be **typed** |

    The short link and the QR code are
    [#10](https://github.com/RickSmith/survey-recon/issues/10) and
    [#38](https://github.com/RickSmith/survey-recon/issues/38), and neither
    exists yet.

    **#85 and #86 landed within an hour of each other**, and the last two rows
    of that table went in together. Every slide in the deck now carries its own
    content, and every one is read back against a committed source on every
    test run.

!!! info "What building the frame turned up"
    On **13 September 2026**, when the skeleton landed, four work orders
    existed for slide content: #31 through #34. They covered 12 of the 34
    unfinished slides. The other **22**, across six of the eleven blocks, had
    nobody writing them: the cold open, Act I, most of Act II, all of Act III,
    the failure beat and the close.

    None of it was visible until there was a slide to hang each block on. Those
    slides said `no work order yet` rather than pointing at an issue nobody had
    written. That is the same rule as everywhere else here: **not found**, never
    the stronger claim. Issues #81 through #86 were opened the same day and
    closed the gap.

## How it is put together

| File | What it is |
|---|---|
| `docs/slides/beyond-the-prompt.md` | The deck itself. Plain markdown. `---` starts a new slide |
| `docs/slides/themes/tsps.css` | Type sizes and colors. The canvas is 1920 x 1080 and nothing is smaller than 28pt |
| `docs/slides/img/` | The pictures beside the bullets, and the green motif behind every section break. Plain SVG, nothing on them under 56 px on a 600-wide panel, which is 29pt once Marp fits the panel into a quarter of the slide |
| `docs/scenarios/sh16/img/*-slide.svg` | The two maps that fill a whole slide, both in Act II: the corridor and the control on it. Drawn from the SH16 run by the same command as the page maps, with bigger type and no side panel |
| `.github/workflows/slides.yml` | Renders the deck to HTML and PDF every time the repo is pushed |
| `corridor-screen/tests/test_deck.py` | Holds the deck to the run of show. See below |
| `corridor-screen/tests/test_cold_open.py` | Holds the cold-open slide to the SH16 run — and stops it announcing a figure the terminal has not reached yet |
| `corridor-screen/tests/test_act_one.py` | Holds Act I to the captured grilling, counting its rows rather than reading its prose — and stops a slide calling a transcript a recording |
| `corridor-screen/tests/test_act_two.py` | Holds Act II to the SH16 run, and checks by name for the three stale figures #80 retired |
| `corridor-screen/tests/test_act_three.py` | Holds each Act III slide to the document it frames — the bid memo, the flagged parcel table and the crew-day build-up |
| `corridor-screen/tests/test_beat_slides.py` | Holds the five review-and-failure slides to the captured evidence behind each beat — and refuses one word the evidence does not support |
| `corridor-screen/tests/test_close.py` | Holds the three closing slides to the form and the pages they send a room to — and refuses a QR code or a short link until somebody has made one |
| `corridor-screen/tests/test_money_slide.py` | Holds the money slide to the crew-day build-up its figures come from |
| `corridor-screen/tests/test_datum_gap.py` | Holds the datum-gap slide to the research note and the SH16 run |
| `corridor-screen/tests/test_concept_slides.py` | Holds the concept slides to the translation table, and to what they ported |
| `corridor-screen/tests/test_interjections.py` | Counts Seneca's interjections, keeps them one to a block, and refuses one that talks down to the room |

## Where the clock lives

Every slide carries a speaker note, and every note opens the same way:

```
0:30–0:46 · 16 min · Act I — The grilling
```

Those timings are read from the run of show in
[the plan of record](../plan-of-record.md) §5 — not typed in twice. A block
whose time or length changes there fails the deck's own tests until the deck
agrees with it.

**The clock is never on the slide.** A time printed on a projector is a promise
to three hundred people that the session is where it says it is, and the first
live demo that runs long turns every slide into an accusation.

## The questions the room is already asking

The deck carries **6 audience-proxy interjections**, written into the speaker
notes. Each one is a question a firm owner in the room is already thinking and
will not raise a hand to ask, said out loud by Seneca so the answer gets given
to everybody. The form is the same every time:

```
**Seneca (audience proxy), <where on the slide>:** "<the question, in the
room's own words>"

**Answer:** <what goes back, and which committed file it stands on>
```

The shape is written out above rather than a real one quoted, because a real
one quoted here is a second copy of a line, and the copy is what drifts.

They are **one to a block, spread across the two hours** — the cold open, Act I,
the stretch, Act II, Act III and the seal slide. One block cannot carry two,
and the session does not go an hour without the room having a voice.

**One of them is genuinely skeptical**, and its own note says so. It asks what
the agent actually saved, in hours, on this job, and the answer is that nobody
measured it — the same rule the money slide's note sets for the presenter. A
skeptical question the presenter is glad to hear is a cue rather than
skepticism, and a room of principals can tell the difference from the back.

Scripted so they land. Rehearsed so they do not sound scripted — which means
rehearsing them in the run-through against the clock, not reading them off a
page on the day.

## Making a cut

Every block of the session opens with a **section break** — a dark green slide
carrying the block's name. The one exception is the cold open, which opens on
the title slide, because that is what is really on the screen for those eight
minutes while the agent runs.

That is what makes a cut cheap: cutting a block is deleting from one break to
the next, which anybody can do the night before without reading the slides.

The three **Acts** carry a heavy rule over the title, so they read from the back
of the room as bigger pieces than the five-minute stretch break.

The three things on [the cut line](../plan-of-record.md#cut-line-in-order) are
marked in the speaker notes of the exact slide they would take out, as
`Cut 1 of 3`, `Cut 2 of 3` and `Cut 3 of 3`. The four things the plan says never
to cut are not marked, and the tests refuse to let them be.

## How this deck is kept honest

`corridor-screen/tests/test_deck.py` reads the deck on every test run and holds
it to all of this:

- every block covered, in order, in one unbroken run each
- the clock in every note and on no slide
- a break at the head of every block, and the Acts marked as Acts
- the cut line marked, and nothing the plan protects marked
- every file a speaker note sends a presenter to committed
- every claim with legal weight carrying its source **on the slide**
- nothing in the theme under 28pt
- no slide asking for more room than 1920 x 1080 has

Every count in the boxes above is checked against the deck as well, because a
number written in prose beside a thing is a number that rots.

The money slide gets a second file of its own,
`corridor-screen/tests/test_money_slide.py`, for the same reason. Every figure
on it is read back out of the crew-day build-up in `project-sh16/` and
compared: the day counts, the hours, the rate handles, and **every number
anywhere on the block**. The one exception is a number sitting on a line that
carries its own source. The build-up is
regenerated whenever the tool runs; a slide is not. That block is read out loud
to a room that prices this work for a living.

```bash
cd corridor-screen && python -m unittest tests.test_deck
```

## Previewing it on your own machine

You do not need any of this to read the deck — the links above always work. But
if you want to change a slide and watch it update, see
[the README](https://github.com/RickSmith/survey-recon#previewing-locally).
