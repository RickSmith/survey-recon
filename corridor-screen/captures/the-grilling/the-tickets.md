# The work orders, and the 89 seconds they took

The last move of Act I is `/to-tickets`, and this is what it did.

**Thirty-five work orders, numbered 5 to 39, created between 20:32:08 and
20:33:37 on 12 September 2026.** Eighty-nine seconds. The whole schedule of this
project, written down, before anybody built anything.

The times below are the ones GitHub stamped. They are the part of this file that
is pinned to that minute and cannot be edited by anything that happened later.

| # | Created | State today | Label today | Work order |
|---:|---|---|---|---|
| 5 | 20:32:08 | closed | ready-for-human | Specify the corridor-screening tool |
| 6 | 20:32:11 | closed | ready-for-agent | Build the take-home toolkit |
| 7 | 20:32:13 | closed | ready-for-agent | Write the governance pages |
| 8 | 20:32:14 | closed | ready-for-agent | Add the two issue templates |
| 9 | 20:32:17 | open | ready-for-human | Recruit one RPLS to walk the repo cold |
| 10 | 20:32:21 | open | ready-for-human | Decide the short link and generate the QR code |
| 11 | 20:32:23 | closed | ready-for-human | Pull TCP(S-1)-08A by hand |
| 12 | 20:32:25 | open | ready-for-agent | Build the Marp deck skeleton |
| 13 | 20:32:30 | closed | ready-for-agent | Tracer bullet: corridor in, flagged parcel list out |
| 14 | 20:32:33 | closed | ready-for-agent | Add NGS marks, carrying their condition |
| 15 | 20:32:35 | closed | ready-for-agent | Add TxDOT primary control points |
| 16 | 20:32:36 | closed | ready-for-agent | Add ROW map sheet count and date range |
| 17 | 20:32:37 | closed | ready-for-agent | Fill the lead-time column with real flags |
| 18 | 20:32:42 | closed | ready-for-agent | Add the crew safety sheet |
| 19 | 20:32:44 | closed | ready-for-agent | Make the whole tool run offline from cache |
| 20 | 20:32:48 | closed | ready-for-agent | Run SH16 end to end and commit the demo cache |
| 21 | 20:32:50 | closed | ready-for-agent | Document every data source |
| 22 | 20:32:53 | closed | ready-for-agent | Build the bid memo |
| 23 | 20:32:55 | closed | ready-for-agent | Build the flagged parcel table |
| 24 | 20:32:56 | closed | ready-for-human | Build the crew-day build-up, with the math shown |
| 25 | 20:32:59 | closed | ready-for-agent | Script failure beat 1: the superseded manual |
| 26 | 20:33:01 | closed | ready-for-agent | Script failure beat 2: the silent NoData |
| 27 | 20:33:03 | closed | ready-for-agent | Verify the fallback capture set is complete |
| 28 | 20:33:07 | open | ready-for-agent | Write the Day 0 setup guide |
| 29 | 20:33:11 | open | ready-for-agent | Write the going-further page |
| 30 | 20:33:13 | open | ready-for-agent | Write the one-page principals brief |
| 31 | 20:33:16 | open | ready-for-agent | Port the concept slides from the brain-dump deck |
| 32 | 20:33:17 | open | ready-for-agent | Build the money slide |
| 33 | 20:33:19 | open | ready-for-agent | Build the datum-gap slide |
| 34 | 20:33:21 | open | ready-for-agent | Build the Hermes demo: the letter that sends itself |
| 35 | 20:33:24 | open | ready-for-agent | Write Seneca's audience-proxy interjections |
| 36 | 20:33:27 | open | ready-for-human | Run the full two-hour dry run |
| 37 | 20:33:30 | open | ready-for-human | Re-record the fallbacks after the cuts |
| 38 | 20:33:33 | open | ready-for-human | Print the handout with the QR code |
| 39 | 20:33:37 | open | ready-for-human | Tag the teaching-moment PRs and freeze the repo |

## Two things to say out loud with this on screen

**Nine of the thirty-five say `ready-for-human`.** The list does not pretend an
agent can do everything. Recruiting a surveyor, standing in front of a room,
printing a handout, deciding what to cut — those went to a person the moment
they were written, and they are still with a person now.

**Number 27 is on this list.** It is the work order that asked whether the
session had a fallback for every step, which is the work order this file exists
because of. The list audits itself.

## What is true about this file, and what is not

**The times and the numbers are the real thing.** They are what GitHub recorded
when the batch was written, and nothing since can move them.

**The titles, states and labels are today's.** This was captured with
`gh issue list --state all` on 2026-09-13, so it shows where each work order
stands now — closed, open, who it is waiting on — rather than how it read the
minute it was created. GitHub does not keep the original title, so nobody can
produce that view, and this file does not claim to.

**The bodies are not here.** Thirty-five acceptance-criteria blocks is a
document, not a fallback. What Act I shows the room is that the work got written
down, in order, in a minute and a half. The one body worth reading on stage is
[the work order that was wrong](../the-work-order/issue-7.txt), and it has its
own capture for its own beat.

`the-tickets.json` beside this file is exactly what that command returned,
unedited — all 49 issues open and closed, not only the 35 above.

Every row in the table is checked against that JSON by
`corridor-screen/tests/test_fallbacks.py`. The first draft of this file had one
label wrong, and that is the test that caught it.
