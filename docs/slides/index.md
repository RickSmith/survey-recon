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
    The deck is **46 slides** — one section break for every block of the two
    hours, and outline slides under each. **11 of them are still placeholders**,
    and each of those says so on its face and names the work order that will
    fill it.

    Slides still waiting on a work order: **0**, across **0** blocks of the
    session.

    The skeleton was built under
    [issue #12](https://github.com/RickSmith/survey-recon/issues/12). Seven
    pieces of content have landed, each checked against its own source on every
    test run: the cold-open slide under
    [#81](https://github.com/RickSmith/survey-recon/issues/81), its figures
    read out of the SH16 run; Act I under
    [#82](https://github.com/RickSmith/survey-recon/issues/82), its counts
    tallied off the captured grilling rather than read out of its prose; Act II
    under [#83](https://github.com/RickSmith/survey-recon/issues/83), every
    figure read out of the SH16 run and the three figures #80 retired checked
    for by name; the money slide under
    [#32](https://github.com/RickSmith/survey-recon/issues/32), its figures read
    out of the crew-day build-up; the datum gap under
    [#33](https://github.com/RickSmith/survey-recon/issues/33), its counts read
    out of the SH16 run; the concept slides under
    [#31](https://github.com/RickSmith/survey-recon/issues/31), held to the
    translation table in `CONTEXT.md`; and Hermes under
    [#34](https://github.com/RickSmith/survey-recon/issues/34), whose day 21 is
    derived from the lead-time table rather than written on the slide. The rest
    lands under [#84](https://github.com/RickSmith/survey-recon/issues/84)
    through [#86](https://github.com/RickSmith/survey-recon/issues/86) (Act III,
    the failure beat and the close).

!!! info "What building the frame turned up"
    On **13 September 2026**, when the skeleton landed, the four work orders
    that existed for slide content — #31 through #34 — covered 12 of the 34
    unfinished slides. The other **22**, across six of the eleven blocks, had
    nobody writing them: the cold open, Act I, most of Act II, all of Act III,
    the failure beat and the close.

    None of it was visible until there was a slide to hang each block on. Those
    slides said `no work order yet` rather than pointing at an issue nobody had
    written — the same rule as everywhere else here: **not found**, never the
    stronger claim. #81 through #86 were opened the same day and closed the gap.

## How it is put together

| File | What it is |
|---|---|
| `docs/slides/beyond-the-prompt.md` | The deck itself. Plain markdown. `---` starts a new slide |
| `docs/slides/themes/tsps.css` | Type sizes and colors. The canvas is 1920 x 1080 and nothing is smaller than 28pt |
| `.github/workflows/slides.yml` | Renders the deck to HTML and PDF every time the repo is pushed |
| `corridor-screen/tests/test_deck.py` | Holds the deck to the run of show. See below |
| `corridor-screen/tests/test_cold_open.py` | Holds the cold-open slide to the SH16 run — and stops it announcing a figure the terminal has not reached yet |
| `corridor-screen/tests/test_act_one.py` | Holds Act I to the captured grilling, counting its rows rather than reading its prose — and stops a slide calling a transcript a recording |
| `corridor-screen/tests/test_act_two.py` | Holds Act II to the SH16 run, and checks by name for the three stale figures #80 retired |
| `corridor-screen/tests/test_money_slide.py` | Holds the money slide to the crew-day build-up its figures come from |
| `corridor-screen/tests/test_datum_gap.py` | Holds the datum-gap slide to the research note and the SH16 run |
| `corridor-screen/tests/test_concept_slides.py` | Holds the concept slides to the translation table, and to what they ported |

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
it to all of this — every block covered, in order, in one unbroken run each;
the clock in every note and on no slide; a break at the head of every block and
the Acts marked as Acts; the cut line marked and nothing the plan protects
marked; every file a speaker note sends a presenter to committed; every claim
with legal weight carrying its source **on the slide**; nothing in the theme
under 28pt; and no slide asking for more room than 1920 x 1080 has.

Every count in the boxes above is checked against the deck as well, because a
number written in prose beside a thing is a number that rots.

The money slide gets a second file of its own,
`corridor-screen/tests/test_money_slide.py`, for the same reason. Every figure
on it is read back out of the crew-day build-up in `project-sh16/` and compared
— the day counts, the hours, the rate handles, and **every number anywhere on
the block** unless it sits on a line carrying its own source. The build-up is
regenerated whenever the tool runs; a slide is not. That block is read out loud
to a room that prices this work for a living.

```bash
cd corridor-screen && python -m unittest tests.test_deck
```

## Previewing it on your own machine

You do not need any of this to read the deck — the links above always work. But
if you want to change a slide and watch it update, see
[the README](https://github.com/RickSmith/survey-recon#previewing-locally).
