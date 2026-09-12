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

!!! note "Placeholder"
    Right now the deck is one title slide and one content slide — just enough to
    prove the pipeline works end to end. The real deck gets built under
    [issue #12](https://github.com/RickSmith/survey-recon/issues/12).

## How it is put together

| File | What it is |
|---|---|
| `docs/slides/beyond-the-prompt.md` | The deck itself. Plain markdown. `---` starts a new slide |
| `docs/slides/themes/tsps.css` | Type sizes and colours. The canvas is 1920 x 1080 and nothing is smaller than 28pt |
| `.github/workflows/slides.yml` | Renders the deck to HTML and PDF every time the repo is pushed |

## Previewing it on your own machine

You do not need any of this to read the deck — the links above always work. But
if you want to change a slide and watch it update, see
[the README](https://github.com/RickSmith/survey-recon#previewing-locally).
