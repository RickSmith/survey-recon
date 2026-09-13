# Captured evidence — the elevation service that answers wrong

These files are what failure beat two is built from. They are committed so the
beat runs with no network, and so every number on
[the wrong answer](../../../docs/managing-your-agent/the-wrong-answer.md) can be
checked against what was actually served.

**Nothing here is edited.** Each file is exactly the bytes that came back.

All ten were fetched on **2026-09-13**, and **every one answered HTTP 200.**
That is the point of the set: not one of them is an error by the only test most
callers apply. The statuses were read off the wire by re-requesting each one;
a saved body carries no headers of its own, so `elevation_trap.CAPTURES` states
them rather than parsing them.

| File | Request | What came back |
|---|---|---|
| `units-feet.json` | `?x=-98.644635&y=29.528488&wkid=4326&units=Feet` | `"value": 866.8668528742528` — a JSON **number**, in feet. Correct |
| `units-us-feet.json` | `?x=-98.644635&y=29.528488&wkid=4326&units=US_Feet` | `"value": "264.221008301"` — a JSON **string**, in meters. No error |
| `units-meters.json` | `?x=-98.644635&y=29.528488&wkid=4326&units=Meters` | `"value": "264.221008301"` — byte-identical to the one above |
| `no-data-gulf.txt` | `?x=-92.0&y=25.0&wkid=4326&units=Feet` | 77 bytes of plain text inside a 200 |
| `wkid-mismatch.txt` | `?x=-98.644635&y=29.528488&wkid=3857&units=Feet` | 77 bytes of plain text inside a 200 |
| `units-lowercase-feet.json` | `...&units=feet` | `866.8668528742528` — a **number**, in feet. This is what rules out case sensitivity as the explanation |
| `units-ft.json` | `...&units=ft` | `"264.221008301"` — meters |
| `units-furlongs.json` | `...&units=Furlongs` | `"264.221008301"` — meters. A unit nobody means seriously, kept because it shows the rule |
| `units-omitted.json` | *(no `units` at all)* | `"264.221008301"` — meters, with no default stated anywhere |
| `sr-4326-ignored.json` | `...&units=Feet&sr=4326` | `866.8668528742528` — identical to `sr=3857` and to sending nothing. `sr` is discarded in silence |
| `sr-3857-ignored.json` | `...&units=Feet&sr=3857` | `866.8668528742528` — the control for the row above |
| `wkid-3857-mercator.json` | `?x=-10981070.536&y=3443084.221&wkid=3857&units=Feet` | `866.8668528742528` — the same point in Web Mercator meters, correctly declared. **`wkid` is honored**, which is what makes the `sr` silence a trap |
| `the-beat.txt` | — | The beat as `--show` renders it, written by `python -m corridor_screen.elevation_trap --write-fallback` and pinned to the code by a test. The fallback for a podium where Python will not start |

The point is `-98.644635, 29.528488` — SH16 at Bandera Road, which is the
corridor the rest of this tool screens.

## Why `units-meters.json` is kept

It looks redundant beside `units-us-feet.json`. It is the control: it proves the
`US_Feet` answer is **the metric answer handed back unchanged**, rather than a
conversion that went wrong somewhere in the middle. The two files are identical.

## Why `wkid-mismatch.txt` is kept

Because it shows what the service does when it *does* apply a parameter. Ask in
degrees while declaring Web Mercator meters and you get plain text, not a wrong
number — so `wkid` is honored. `units` is not. Two parameters, one endpoint,
opposite behavior, and only one of them tells you.

## Do not match on the error text

`no-data-gulf.txt` and `wkid-mismatch.txt` both carry a message, and
[sources we did not use](../../../docs/data-sources/not-used.md) already records
this endpoint returning **two different messages for the same condition on the
same day**. A check that matches the words will stop working. The test is
whether the body parses as JSON at all.

## Stability

The `Feet` and `US_Feet` answers were each requested five times on 2026-09-13
before being captured. Both were identical every time. That is a small sample on
one network on one day, which is all it is — this repo's own
[not-used page](../../../docs/data-sources/not-used.md) records an earlier draft
quoting "none over 0.7 seconds" from four lucky tries, and being wrong the way a
small sample is always wrong.
