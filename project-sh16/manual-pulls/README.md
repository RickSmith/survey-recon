# Pulled by hand

Some TxDOT documents cannot be fetched by a program. The host refuses the
request, or the file sits behind a page that only a browser can work through.
Those documents get downloaded by a person and committed here.

## Why this is not the cache

`project-sh16/cache/` holds the responses the corridor tool received while it
ran, and the tool rewrites `cache/INDEX.md` on every run. A file a person
dropped in there by hand would appear in that index nowhere, and could be
written over. So hand-pulled documents live in this folder instead.

## The provenance rule is the same rule

Provenance is the record of where a document came from and when — the chain of
custody you would want on any record you plan to rely on. The cache keeps that
record in a `.meta.toml` file beside every response. A `.toml` file is plain
text, one `name = value` per line, readable in any editor.

A person doing the fetching does not make provenance matter less. So **every
file in this folder has a `.meta.toml` beside it, with the same name.**

## What is here

| Document | File | Pulled |
|---|---|---|
| TCP(S-1)-08A — Operations for Surveying | `tcp-s-1-08a.pdf` | *not yet pulled* |

## How to add one

1. Download the file in a browser.
2. Save it in this folder. Use a lowercase name with dashes, no spaces —
   `tcp-s-1-08a.pdf`, not `TCP(S-1)-08A.pdf`. Parentheses in a file name break
   shell commands on some systems, and this repo is run by beginners.
3. Copy the **exact** address you downloaded it from, out of the browser's
   address bar. Not a search result, and never an `onlinemanuals.txdot.gov`
   address — those are superseded.
4. Write the `.meta.toml` beside it. Copy the shape from an existing one.

## The URL trap, again

TxDOT moved its manuals. Search engines still return the old
`onlinemanuals.txdot.gov` addresses, and those pages still load, and they are
out of date. Use `txdot.gov`. This repo documents that trap in
`docs/managing-your-agent/the-superseded-manual.md`; do not fall into it while
filing the evidence for it.
