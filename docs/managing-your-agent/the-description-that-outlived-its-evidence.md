# The description that outlived its evidence

This repo's own glossary described a run nobody captured.

It said the USGS elevation service ignored the coordinate system, read longitude
and latitude as Web Mercator meters, landed somewhere in the Atlantic, and
answered `NoData`. **Three claims, and the evidence in this repo supports none
of them.** The captures were committed on 2026-09-13. The glossary was not read
against them.

This page is the account of that, kept for the same reason
[the claim we got wrong](the-claim-we-got-wrong.md) and
[the force push](the-force-push.md) are kept. The correction is a new entry, not
a quiet rewrite.

## What the captures actually say

Every file below is committed in `corridor-screen/captures/silent-nodata/`, and
every one of them answered **HTTP 200**.

| Claim in the glossary | What the evidence shows |
|---|---|
| The coordinate system was ignored **in a way that moved the point** | Half true, and the half that matters is false. `sr` **is** discarded in silence — `sr=4326`, `sr=3857` and no `sr` at all are the same request. But the answer stays **correct** every time (`sr-4326-ignored.json`, `sr-3857-ignored.json`), and `wkid` is honored: the same point sent as Web Mercator meters with `wkid=3857` answers the same elevation (`wkid-3857-mercator.json`). Nothing moved the point |
| It landed in the Atlantic | **Not found.** No capture in this repo shows a response for any point but SH16 at Bandera Road and one in the Gulf of Mexico. There is no Atlantic request, and nothing that would produce one |
| It answered `NoData` | **Not found.** The token is in no response this repo holds. The Gulf of Mexico point — the one a `NoData` would properly belong to — answers plain text inside a 200 — `Call failed.  [Failed cloud operation: Open, Path: /vsimem/_000011B4.aux.xml]`, which is the exact body of `no-data-gulf.txt` and **not** a message to match on, because the text varies between runs. Not JSON, and not a `NoData` |

## What the service really does

The hazard is real. It moved from the position to the **unit**.

```
...&units=Feet      →  866.8668528742528     a JSON number, in feet
...&units=US_Feet   →  "264.221008301"       a JSON string, in meters
```

Same ground, 3.28084 apart, which is feet per meter. No error either time, and
**no field anywhere in the reply says which unit it is.** `US_Feet` is not a
typo — it is the US survey foot, what EPSG numbers `9003` and what TxDOT's
Survey Manual requires in deliverables
([TxDOT Survey Manual, Ch. 3, Control Points](https://www.txdot.gov/manuals/row/ess/index.html)).

The full write-up is
[The answer that was wrong rather than missing](the-wrong-answer.md), which has
been correct since [issue #26](https://github.com/RickSmith/survey-recon/issues/26).

## How it survived

The description came from the September 2026 research pass, which recorded
*"3DEP silently returned `NoData`. Ignored `sr=4326`, read lon/lat as Web
Mercator meters."* That line is still on
[the research page](../txdot-research.md), where it belongs — it is what the
research said, and the research is a dated record rather than a claim this repo
makes today.

**What went wrong is what happened to it next.** The line was copied into
`CONTEXT.md` as a settled fact, and `docs/plan-of-record.md` took its wording
for the run of show. Then the beat was actually run, on 2026-09-13 under issue
#26, and the captures came back saying something else. The write-up was
corrected. The glossary was not, because nothing pointed from one to the other.

So the repo held the corrected account and the wrong one at the same time. Both
`d905bac` and `01dbc29` are dated 2026-09-13. They are the captures and the
corrected write-up. The glossary entry sitting beside them went on saying
something else, in the file every other page is told to trust.

## The part that should worry you

It reached a slide.

The skeleton beat 2 slide for [issue #85](https://github.com/RickSmith/survey-recon/issues/85)
was written out of the glossary rather than out of the captures, and it
inherited all three errors word for word. **That is a slide about being
confidently wrong, being confidently wrong, on a projector, to a room of people
who can check it from their seats.**

It was caught by a test — `corridor-screen/tests/test_beat_slides.py`, which
reads every figure on those slides back out of the committed captures and
refuses the one word the evidence does not support, by name.

!!! note "A glossary is not a source"
    The failure here is not that somebody wrote something wrong. It is that a
    **summary** was treated as evidence by the next person to need it, three
    documents downstream of the thing that was actually measured.

    `CONTEXT.md` exists so no page has to explain a term twice. That is a good
    reason for it to exist and a bad reason to cite it. **Cite the capture.**

## What was changed

On 2026-09-13, under
[issue #104](https://github.com/RickSmith/survey-recon/issues/104):

- The `NoData` entry in `CONTEXT.md` was rewritten against the captures.
  `NoData` is still defined, because it is still a real thing an elevation
  service returns. What was dropped is this service having returned one here
- `docs/plan-of-record.md` §5 beat 2 was rewritten, and its timing warning now
  names the beat the way the slide is headed — *wrong, not missing*
- [Sources we looked at and did not use](../data-sources/not-used.md) and
  [the research page](../txdot-research.md) were marked where they read as this
  repo's own finding rather than as a quotation of the research
- This page was added
- `test_beat_slides.py` grew the check that was missing: the plan of record and
  the glossary are now held to the deck, the same way the fallback card already
  was

**The folder is still called `silent-nodata`.** So is the title of issue #26.
Renaming committed evidence to match a corrected story is its own kind of
tidying-up, and the point of keeping the old name is that somebody reading the
history can see where the description came from.

## What we are still not saying

We are not saying the September research was wrong.

It is dated. It named a parameter, `sr`, that the current `v1` endpoint does not
take at all. So the original request cannot be repeated against the original
endpoint. A service that behaved one way on 2026-09-12 and another way on
2026-09-13 is an ordinary thing for a service to be.

**What we could not confirm is the `NoData` itself.** We looked in every
response committed in `corridor-screen/captures/silent-nodata/` and in the
research page the description came from, and it is not in either. That is
*not found* rather than *it never happened*, and the difference is that somebody
looked.

What we are saying is narrower, and it is the whole point: **this repo's rule is
"cite it or say you could not confirm it," and an uncited claim sat in its
glossary anyway. The glossary is the one file every other page is told to
trust.**
