# Captured evidence — the superseded TxDOT manual

These files are what failure beat one is built from. They are committed so the
beat runs with no network, and so every claim on
[the superseded manual](../../../docs/managing-your-agent/the-superseded-manual.md)
can be checked against what was actually served rather than taken on trust.

**Nothing here is edited.** Each file is exactly the bytes that came back.

| File | What it is | Where it came from |
|---|---|---|
| `legacy-ess-index-archived-2025-06-18.html` | TxDOT Survey Manual, **March 2025**, Manual Notice **2025-1** | Internet Archive capture `20250618021450` of `onlinemanuals.txdot.gov/TxDOTOnlineManuals/TxDOTManuals/ess/index.htm` — the last archived copy carrying real manual content |
| `current-ess-index.html` | TxDOT Survey Manual, **April 2026**, Manual Notice **2026-1** | Fetched live from `https://www.txdot.gov/manuals/row/ess/index.html` on 2026-09-13 |
| `legacy-old-path-archived-2025-03-08.html` | 186 bytes of meta-refresh, pointing at the other legacy path | Internet Archive capture `20250308044703` of `onlinemanuals.txdot.gov/txdotmanuals/ess/index.htm` |
| `the-beat.txt` | The beat as `--show` renders it | Written by `python -m corridor_screen.manual_links --write-fallback`, and pinned to the code by a test. The fallback for a podium where Python will not start |

The archive is used for the legacy pages because the host no longer answers.
There is no way to re-fetch what it used to serve.

**What the old host did on 2026-09-13**, recorded here rather than in the module
because an address has a shelf life and this file is dated:

| | |
|---|---|
| `onlinemanuals.txdot.gov` resolved to | `168.44.238.246` |
| Port 80 | no connection, 3 attempts, 12 s each |
| Port 443 | no connection, 3 attempts, 12 s each |

The name is still published. Nothing answers on it. Those are two different
findings and the page keeps them apart.

**Why the encoding is worth a note.** The legacy page declares
`charset=ISO-8859-1` in its own head. Read as UTF-8 it does not fail; it just
comes out wrong above byte 127. `manual_links.capture_text` reads the charset the
page declares rather than assuming, and there is a test on it.

These files hold legacy URLs because that is what they served. That is evidence,
not a citation, which is why `manual_links.check_repo` does not scan this directory.
