# Documents pulled outside a tool run

Published documents — standard sheets, manuals, memos — that this repo needs to
quote and therefore keeps a copy of. They are not responses the corridor tool
received, so they do not belong in the cache.

The folder is named `manual-pulls` because the first one genuinely was pulled by
hand. Read **"Blocked" was not true** below before repeating that assumption
about the next document.

## Why this is not the cache

`project-sh16/cache/` holds the responses the corridor tool received while it
ran, and the tool rewrites `cache/INDEX.md` on every run. A file placed there by
hand would appear in that index nowhere, and could be written over. So documents
kept for reference live in this folder instead.

## The provenance rule is the same rule

Provenance is the record of where a document came from and when — the chain of
custody you would want on any record you plan to rely on. The cache keeps that
record in a `.meta.toml` file beside every response. A `.toml` file is plain
text, one `name = value` per line, readable in any editor.

Who did the fetching does not change how much provenance matters. So **every
file in this folder has a `.meta.toml` beside it, with the same name**, naming
the URL, the date, the byte count and the SHA-256.

## What is here

All six TxDOT standard sheets titled **"Traffic Control Plan for Surveying
Operations,"** plus the memo that introduced the newest one.

| Document | Index | Files |
|---|---|---|
| TCP(S-1)-08A | 211 | `tcp-s-1-08a.pdf`, `tcp-s-1-08a.dgn` |
| TCP(S-2)-08A | 212 | `tcp-s-2-08a.pdf`, `tcp-s-2-08a.dgn` |
| TCP(S-2c)-10 | 212A | `tcp-s-2c-10.pdf`, `tcp-s-2c-10.dgn` |
| TCP(S-3)-08 | 213 | `tcp-s-3-08.pdf`, `tcp-s-3-08.dgn` |
| TCP(S-4)-08A | 214 | `tcp-s-4-08a.pdf`, `tcp-s-4-08a.dgn` |
| TCP(S-5)-08 | 215 | `tcp-s-5-08.pdf`, `tcp-s-5-08.dgn` |
| TxDOT memo, 11 Jan 2010, introducing TCP(S-2c)-10 | — | `tcp-s-2c-10-memo.pdf` |

Each `.dgn` is the same sheet in MicroStation CAD format, which is what TxDOT
draws its standards in. They are here because they are the source TxDOT
publishes, not because anything in this repo reads them.

**Read the summaries before quoting any sheet:**

- [`tcp-s-family.md`](tcp-s-family.md) — what all six require, and the answer to
  whether a shadow truck is ever forced by the clock. It is not.
- [`tcp-s-1-08a.md`](tcp-s-1-08a.md) — the crew-time reading of S-1 on its own.

## "Blocked" was not true

Issue [#11](https://github.com/RickSmith/survey-recon/issues/11) said the host
blocked automated fetching, so pulling these was a human job. That was written
down as a fact and believed for weeks. It is not one.

Every file above answers **HTTP 200 to a plain `curl`** at
`https://ftp.txdot.gov/pub/txdot-info/cmd/cserve/standard/traffic/`. All twelve
sheet files and the memo were fetched that way on 2026-09-13. So was the index
page.

What is genuinely awkward is the **naming**: the server calls the files
`tcps1.pdf`, `tcps2c.dgn` and so on, which nothing tells you from outside. You
have to read the index to learn them. "Hard to discover" had been recorded as
"impossible to fetch," and nobody rechecked.

## The soft-404 that cost this folder an error

A **soft-404** is a not-found answer wearing a success status code: the server
says HTTP 200, and the body is an error page. Nothing in the status code warns
you, so a program stores the error page as if it were the document.

`www.dot.state.tx.us/insdtdot/orgchart/cmd/cserve/standard/toc.htm` is the
standard-sheet index, and it works. But it **does not host the files** — its
links point out to `ftp.dot.state.tx.us/pub/txdot-info/...`. Request a PDF from
the `www.dot.state.tx.us/insdtdot/...` path directly and you get **HTTP 200 with
5,104 bytes of "Page Not Found" HTML.**

The first version of `tcp-s-1-08a.pdf.meta.toml`, committed in
[#68](https://github.com/RickSmith/survey-recon/pull/68), recorded exactly that
dead URL as the document's origin. It was inferred from the index address and
never fetched. The correction is recorded in that file rather than quietly
edited away.

**Two hosts serve these files and both are real mirrors:**
`ftp.txdot.gov/pub/txdot-info/...` and `ftp.dot.state.tx.us/pub/txdot-info/...`.
Every file here was fetched from both and hashed; all thirteen matched. Cite the
`txdot.gov` one.

## How to add a document

1. Get the file. Try `curl` first — see above, "blocked" is often wrong.
2. Save it here with a lowercase, dashed name: `tcp-s-1-08a.pdf`, not
   `TCP(S-1)-08A.pdf`. Parentheses in a file name break shell commands on some
   systems, and this repo is run by beginners.
3. Write the `.meta.toml` beside it. Copy the shape from an existing one.
4. **Verify the URL you are about to cite.** Do not infer it.

## Verifying, which is the whole point

`sha256sum` prints a fingerprint of a file's exact contents. Two files with the
same fingerprint are the same file. This loop re-fetches every recorded URL and
checks it against what is committed:

```bash
cd project-sh16/manual-pulls && for m in *.meta.toml; do f=$(python -c "import tomllib,sys;print(tomllib.load(open(sys.argv[1],'rb'))['file'])" "$m"); u=$(python -c "import tomllib,sys;print(tomllib.load(open(sys.argv[1],'rb'))['source_url'])" "$m"); a=$(sha256sum "$f" | cut -d' ' -f1); b=$(curl -sL "$u" | sha256sum | cut -d' ' -f1); [ "$a" = "$b" ] && echo "OK   $f" || echo "FAIL $f"; done
```

Thirteen `OK` lines is a pass. That loop is what caught the dead URL described
above — a claim nobody had tested until something tested all of them.
