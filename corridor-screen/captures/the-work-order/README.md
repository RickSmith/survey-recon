# Captured evidence — the work order that was wrong

These files are what failure beat three is built from. Beat three is the one
where the error is **ours**, not the agent's: [issue #7](https://github.com/RickSmith/survey-recon/issues/7)
instructed the agent in writing to publish a false statement of law, and the
agent went looking for the citation this repo's own rules demand, could not find
one, and stopped.

They are committed so the beat runs with no network. The plan of record says
beat three is the one that must not be cut for time, and until these files
existed it was the only beat that needed GitHub to be reachable from the podium.

The account the beat is told from is
[the claim we got wrong](../../../docs/managing-your-agent/the-claim-we-got-wrong.md).
What PAO 71 actually says, quoted at length, is on
[the seal and responsible charge](../../../docs/governance/seal-and-responsible-charge.md) —
so the opinion itself does not need a network either.

| File | What it is | Where it came from |
|---|---|---|
| `issue-7.json` | The work order, exactly as the GitHub API returns it — body, state, labels, dates | `gh api repos/RickSmith/survey-recon/issues/7` on 2026-09-13 |
| `issue-7-comments.json` | The correction comment, same API, same day | `gh api repos/RickSmith/survey-recon/issues/7/comments` on 2026-09-13 |
| `issue-7.txt` | The same two things as `gh` renders them for a terminal. The file to open at a podium | `gh issue view 7` and `gh issue view 7 --comments`, on 2026-09-13 |

**The two JSON files are exactly the bytes the API returned.** `issue-7.txt` is
not: it is the output of the two commands above, one after the other, with the
command line printed above each so a reader can tell which is which and re-run
them. Nothing inside either block was touched.

## What to point at on stage

Two lines, in this order.

**The work order, acceptance criterion 4** — in `issue-7.txt` under
`## Acceptance criteria`, and in `issue-7.json` under `body`:

> It states plainly that TBPELS has not spoken directly to AI, and that
> responsibility doctrine already covers it

**The comment that answered it**, in the second half of `issue-7.txt`:

> **Correction: acceptance criterion 4 is factually wrong. Please do not restore it.**

That is the whole beat. A licensed human wrote the first line. The agent wrote
the second, and then did not write the page it had been told to write.

## Why the issue was captured and the opinion was not

PAO 71 is a two-page PDF on the board's own site, and this repo quotes the part
that matters in full on the governance page linked above. A copy of the PDF
would be a second copy of something already readable offline.

The issue is the opposite case. It lives on GitHub and nowhere else, it is the
thing being pointed at, and a repo that is about to tell a room *"check this
yourself"* should not depend on the venue's Wi-Fi to show its own evidence.

## The dates are the point

The work order was written on 2026-09-12. PAO 71 was approved on **14 November
2024** — public for nearly two years by then. Both dates are in the files rather
than in this paragraph: `created_at` in `issue-7.json`, and the date quoted in
the comment.
