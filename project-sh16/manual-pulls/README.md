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

| Document | Files | Pulled |
|---|---|---|
| TCP(S-1)-08A — Traffic Control Plan for Surveying Operations | `tcp-s-1-08a.pdf`, `tcp-s-1-08a.dgn` | 2026-09-13 |

`tcp-s-1-08a.dgn` is the same sheet in MicroStation CAD format, which is what
TxDOT draws its standards in. It is here because it is the source TxDOT
publishes, not because anything in this repo reads it.

What the sheet means for crew time is in
[`tcp-s-1-08a.md`](tcp-s-1-08a.md). Read that before quoting the sheet — it
flags a claim elsewhere in this repo that the sheet does not support.

## How to add one

1. Download the file in a browser.
2. Save it in this folder. Use a lowercase name with dashes, no spaces —
   `tcp-s-1-08a.pdf`, not `TCP(S-1)-08A.pdf`. Parentheses in a file name break
   shell commands on some systems, and this repo is run by beginners.
3. Copy the **exact** address you downloaded it from, out of the browser's
   address bar. Not a search result, and never an `onlinemanuals.txdot.gov`
   address — those are superseded.
4. Write the `.meta.toml` beside it. Copy the shape from an existing one.

## The URL trap, again — and a second host

TxDOT moved its manuals. Search engines still return the old
`onlinemanuals.txdot.gov` addresses, and those pages still load, and they are
out of date. Use `txdot.gov`. This repo documents that trap in
`docs/managing-your-agent/the-superseded-manual.md`; do not fall into it while
filing the evidence for it.

There is a **second** old host, and it caught this folder's first pull.
TxDOT's standard-sheet index still answers at
`www.dot.state.tx.us/insdtdot/orgchart/cmd/cserve/standard/toc.htm`, and it
serves working files. `dot.state.tx.us` is not `txdot.gov`.

The fix is not to distrust the download. It is to **check whether the current
host serves the same bytes**, and record the answer:

```bash
curl -sL "https://ftp.txdot.gov/pub/txdot-info/cmd/cserve/standard/traffic/tcps1.pdf" | sha256sum
sha256sum tcp-s-1-08a.pdf
```

Two identical hashes mean the same document, and the `txdot.gov` address can be
cited honestly. `sha256sum` prints a fingerprint of a file's exact contents;
two files with the same fingerprint are the same file. For TCP(S-1)-08A the
hashes matched, and both `.meta.toml` files record that the check was run
rather than assumed.
