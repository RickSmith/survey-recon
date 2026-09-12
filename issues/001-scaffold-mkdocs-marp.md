# Issue #1 — Scaffold the docs site and slide pipeline

*Written by hand. The first work order in this repo came from a person, and it should be obvious that it did.*

---

## Why

Everything else depends on this. The repo has two publishing jobs — a documentation site attendees read, and the slides presented from the stage — and both are built from markdown that lives in this repo. Until that pipeline works, no content can be verified as it will actually appear.

This also has to be boring and reliable by September 17, because from then on the interesting work assumes it.

## What

Stand up two GitHub Actions workflows publishing from the same repo.

**1. Documentation site — MkDocs Material → GitHub Pages**
- `mkdocs.yml` with the nav skeleton from `docs/plan-of-record.md` §6
- Stub pages for every section so the nav is navigable end to end, each with a one-line placeholder
- Material theme, search enabled, light/dark toggle
- `.github/workflows/docs.yml` — build and deploy on push to `main`

**2. Slides — Marp → HTML and PDF**
- `docs/slides/` holding Marp markdown
- One title slide and one content slide, enough to prove the pipeline
- `.github/workflows/slides.yml` — render to HTML and PDF, publish alongside the docs site
- Type must be legible from the back of a conference room. Test at 1920×1080, minimum 28pt body

## Acceptance criteria

- [ ] A push to `main` publishes the docs site with no manual step
- [ ] Every nav entry resolves — no 404s, no dead links
- [ ] Slides render to both HTML and PDF in CI
- [ ] The published site is reachable and its URL is written into `README.md`
- [ ] `README.md` explains how to preview both locally
- [ ] A first-time visitor can find Day 0 setup within one click of the landing page

## Out of scope

Real content. This issue is the pipeline only. Stub pages are correct here; writing them properly is other issues' work.

## Notes

- Attendees must never need Node. If Marp requires it in CI that is fine — CI is ours, not theirs. Nothing in the attendee path may depend on it
- Keep `mkdocs.yml` readable. Surveyors will open it, and it is their first look at what a config file even is
- Watch the site URL length. `<user>.github.io/survey-recon` is a mouthful from the back row, and a short link plus QR is an open question in `docs/plan-of-record.md` §8
