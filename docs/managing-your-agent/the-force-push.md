# The rule we broke on day one

This repo has a rule about its own history. `CLAUDE.md`, the handbook the agent
works from, states it plainly:

> Do not squash commits or rewrite history

It was broken once, on purpose, fifteen minutes after the repo existed. Here is
what happened, who decided, and what it cost. It is written down because a
record nobody can check is not worth showing anybody, and because the shape of
it is the whole session in miniature.

## First, what a force push is

A **commit** is a field book entry. You write down what you did, you date it, and
you move on. The entries stack up in order, and the order is the record.

A **force push** replaces what is on GitHub with what is on your machine, and
throws away whatever was there before. In field book terms: you tear out a page,
write a new one, and put it back. The old page is gone. Nothing on the new page
says a page was ever removed.

That last part is the problem. A field book you can quietly re-paginate is not a
field book. It is a draft.

## What happened

**2026-09-12, 18:58:26 UTC.** The `survey-recon` repo was created on GitHub. The
MIT license box was ticked during setup, so GitHub made the first entry itself:

- Commit `11e4dc2`, *"Initial commit"*
- One file in it: `LICENSE`

**2026-09-12, 19:13:15 UTC.** Fifteen minutes later, on Rick's machine, the real
starting material was committed:

- Commit `30c8d40`, *"Seed the repo: plan of record, research, context, first work order"*
- Ten files, including its own `LICENSE`

**Then the two would not join.** The commit on GitHub and the commit on the
machine had no ancestor in common — neither one grew out of the other. Git calls
that **unrelated histories**, and it refused the push rather than guess.

Two ways out were put to Rick:

1. **Merge the two histories.** Keep both first entries, joined by a third.
2. **Force push.** Replace GitHub's entry with the one on the machine.

The rule conflict was named out loud before he chose. He chose the force push,
knowing it broke the rule he had written that morning.

**The result, still true today:** `30c8d40` is the only root of `main`. `11e4dc2`
is no longer on any branch.

## What was actually lost

One file. `LICENSE`. The same MIT license text that `30c8d40` already carried.

The two versions differed by exactly one line:

| Commit | Line 3 of `LICENSE` |
|---|---|
| `11e4dc2` (discarded) | `Copyright (c) 2026 Rick Smith` |
| `30c8d40` (kept) | `Copyright (c) 2026 Richard A. Smith Jr.` |

Nothing else was in that commit. No work was lost, no decision, no research.

We are not going to dress this up as a near miss. The damage was one line of
boilerplate, and the name that survived is the more correct one.

## So why write it down at all

Because of when it happened, not what it cost.

The argument this whole repo makes is that its history is honest enough to put on
a projector. Fifteen minutes in, the rule that makes that true got set aside for
convenience. If that goes unrecorded, every other claim on this site gets a little
cheaper — and correctly so.

There is also something worth noticing in the shape of it:

- **The agent stopped and asked.** It did not force push and mention it later. It
  laid out both options and named the rule it was about to break.
- **A licensed human chose.** Knowingly, with the conflict in front of him.

That is the whole session in one small incident. The agent can be careful, fast,
and right about the options. It still does not get to decide. Somebody signs.

## Check it yourself

You do not have to take this page's word for any of it. GitHub still serves the
discarded commit if you ask for it by name:

**<https://github.com/RickSmith/survey-recon/commit/11e4dc22f7f748b6bceb2171f101e273ad908171>**

Open it. One file, `LICENSE`, and a different copyright line. That is all that
was there.

One caveat, stated so nobody is surprised later: a commit that is not on any
branch is loose, and GitHub is free to collect it eventually. If that link ever
stops working, this page is the record. That is the point of writing it down.

## What we did not do

We did not undo it. `30c8d40` stays the root of `main`.

Reaching back to repair a rewrite with another rewrite would be the same mistake
wearing a better excuse. The entry stays as written, and this page sits beside it
explaining what happened.
