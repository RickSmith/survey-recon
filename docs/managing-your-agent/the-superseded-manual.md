# The manual that was real, and out of date

Ask a search engine for the TxDOT Survey Manual. The link you are handed is on
`onlinemanuals.txdot.gov`.

**The manual is not there any more.** It is at `txdot.gov/manuals/row/ess/`, and
the two are not the same document.

This is the first of the two failures the session shows on purpose. It is not a
story about a broken link. A broken link is easy — you click it, nothing loads,
you look elsewhere. This one is worse than that, and the reason is the whole
point.

## What each address serves

Checked on **2026-09-13**. Both pages are captured and committed, so the table
below can be read against the evidence rather than taken on trust.

| | The address search gives you | The address the manual is at |
|---|---|---|
| Host | `onlinemanuals.txdot.gov` | `www.txdot.gov` |
| Manual | TxDOT Survey Manual, **March 2025** | TxDOT Survey Manual, **April 2026** |
| Manual Notice | **2025-1** | **2026-1** |
| Answering today | **no** — see below | yes, HTTP 200 |

A surveyor quoting a section out of the first one is quoting a revision that was
replaced.

## The old host is not dead, and that matters

It would be easier if it were. A dead host gives an agent a clear answer.

`onlinemanuals.txdot.gov` is still **in DNS** — the internet's phone book, which
turns a name into the number a computer actually dials. The name is in the book.
Nobody answers the phone: no connection on port 80 or port 443, three attempts,
twelve seconds each, on 2026-09-13.

So what an agent actually sees is a **timeout**. Not a 404 that says "this is
gone." A timeout, which looks exactly like bad Wi-Fi, and which any sensible
retry loop will try again in a few seconds.

!!! warning "This is why the page says *not answering* rather than *dead*"
    We could not reach it from here. That is not the same as proving nobody
    can. This repo writes "not found" rather than "does not exist," and says
    where it looked — the rule is in
    [CLAUDE.md](https://github.com/RickSmith/survey-recon/blob/main/CLAUDE.md),
    and it applies to our own findings first.

## So where does the wrong citation come from?

If the old host answers nothing, how does an agent end up quoting March 2025?

Two ways, and both are ordinary.

**It cites the link without opening it.** The URL is on `txdot.gov`. It appears
high in search results. It has the right words in it. An agent under time
pressure writes the citation from the search result. So does a person under time
pressure. Nothing was fetched, so nothing failed.

**It finds an archived copy.** The Internet Archive has the old manual, and
so do mirrors and quoted excerpts all over the web. Those load instantly and
read as authoritative, because they *are* authoritative. They are just old.

Either way the agent ends up with a real TxDOT manual, real section numbers, and
a revision no longer in force.

> **It did not invent anything: it followed the link search gave it, read a real
> TxDOT manual, and cited a revision that had been replaced.**

That is the beat. It did not lie. It found the wrong document and believed it —
which is exactly what a new hire does, and exactly why the licensed human is the
one who signs.

## There were two old addresses, not one

Worth knowing if you go looking. The older path meta-refreshed to the newer one:

```
onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm
   ↓ (a 186-byte page whose only content is "Redirecting to new URL...")
onlinemanuals.txdot.gov/TxDOTOnlineManuals/TxDOTManuals/ess/index.htm
   ↓
   nothing answers here today
```

Both are captured. The check below does not need to know about two paths. It
matches the **host**, whatever follows it. The redirect stub is kept anyway. It
is the evidence for this diagram, and it is the thing that explains why two
different old addresses are still circulating.

## Run it yourself

The beat reproduces on demand, and **reads only from disk** — it cannot be taken
away from you by a hotel network:

```bash
python -m corridor_screen.manual_links --show
```

## The boring half, which is the useful one

CLAUDE.md has said from early on: *use `txdot.gov/manuals/row/ess/...` URLs,
never `onlinemanuals.txdot.gov`.* A rule like that is true right up until
somebody is in a hurry.

So there is now something that runs it:

```bash
python -m corridor_screen.manual_links --check .
```

It exits non-zero if any page or module in this repo cites a superseded URL, and
it prints the `txdot.gov` address to use instead. **It runs in the test suite**,
so `python -m unittest discover -s tests -t .` catches one.

!!! note "It fails the build now. It did not when this page was written"
    An earlier draft said "fails the build." That was not true then, and it is
    exactly the shape of claim this page exists to warn about: a sentence that
    reads as a guarantee and is not one. GitHub Actions ran two workflows at
    the time, the docs site and the slides, and neither ran a Python test.

    A later work order added a workflow that runs the tests on every pull
    request, so the claim is true now. It is recorded here rather than quietly
    corrected, because the gap between the two drafts is the lesson.

**How it tells a citation from a warning.** Several pages here name the old
address on purpose, to warn about it, and this page is one of them. So the check
looks only for a full, clickable address, with `http://` or `https://` in front
of it. A hostname in a sentence is a warning. A full address is a claim.

That is the only clever part. Everything else is a pattern and a list of files,
which is the point:

> **The rule that catches an error is usually boring and was written for
> something else.**

## What this cost, and what it is worth

Finding this took four fetches and a look at an archive index. It is not clever
work. It is the work of checking a link before citing it — the thing the rule in
CLAUDE.md was already asking for, now done by something that does not get tired
at 4pm on a Friday.

**You still sign it.** The check catches a superseded address. It cannot tell
you whether the section you quoted says what you think it says.

---

## Where this came from

The failure was reproduced and written up under
[work order #25](https://github.com/RickSmith/survey-recon/issues/25). The
workflow that made "fails the build" true is
[#78](https://github.com/RickSmith/survey-recon/issues/78).
