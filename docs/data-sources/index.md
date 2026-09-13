# Data sources

!!! note "Placeholder"
    This page is a stub. It gets written under
    [issue #21](https://github.com/RickSmith/survey-recon/issues/21).

Every public service this repo queries gets its own page here: the endpoint, the
fields it returns, and its quirks — including the ones that return a plausible
wrong answer instead of an error.

Verified research notes live in
[TxDOT research](../txdot-research.md) until this chapter is written.

## Written so far

- [Esri ArcGIS geometry service](arcgis-geometry-service.md) — builds the corridor
  polygon. Written under [issue #13](https://github.com/RickSmith/survey-recon/issues/13)
  because the corridor tool started calling it, and it appears in no earlier
  research note. It carries the unit-code trap: a value the parcel query accepts
  and answers wrong.
- [The flag services](flag-services.md) — schools, cemeteries, railroads and
  pipelines. Written under [issue #17](https://github.com/RickSmith/survey-recon/issues/17).
  It carries two traps worth the reading time: a USGS layer that buffers a long
  polyline into the wrong county without erroring, and a pipeline service named
  in the spec that turns out to hold Pennsylvania data only.
- [The NGS datasheets service](ngs-datasheets.md) — the survey marks along the
  corridor, and the condition each was last left in. Written under
  [issue #14](https://github.com/RickSmith/survey-recon/issues/14). Its trap is
  the quiet kind: the condition field is called `LAST_COND` here and `condition`
  on NGS's other API, and asking for the wrong name returns nothing and raises
  nothing.
