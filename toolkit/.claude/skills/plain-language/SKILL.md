---
name: plain-language
description: Plain language for the pages in docs/. Use when writing a doc page, editing one, reviewing a doc change, or fixing a sentence the plain-language test failed.
---

# Plain language

The readers of `docs/` are licensed surveyors. Most of them write very little
software. They are reading these pages to decide whether to trust a tool with
work they will put a seal on.

Write the way a good field note is written. One fact per sentence. The actor
named. Nothing in it that a reader has to hold in their head while they look for
the verb.

This skill is the standard. Three of its rules are counted by
`corridor-screen/tests/test_plain_language.py`, which runs on every pull
request. Four more are yours to catch, because no test can.

## The three rules a test counts

Apply all three to every sentence you write or edit in `docs/`.

| Rule | The number |
|---|---|
| Sentence length | 40 words or fewer |
| Em dashes in one sentence | 1 at most |
| Words from the list | none |

**40 words.** Past that a reader has to start again from the beginning. Aim far
under it. The limit is where the test fails, not where the writing gets bad.

**One em dash.** An em dash is `—`, the long one. One in a sentence sets off an
aside. Two turn the sentence inside out, because the reader now has to hold the
first half open while the middle runs. Use a comma, a period, or a pair of
parentheses.

**The word list.** Fifty-five words and phrases, in
[`banned-words.md`](banned-words.md) beside this file, each with a plainer word
to use instead. Read that file when you need a replacement or when the test
names a word you want to argue about.

A true hit on a plain English word is rare, and it is still worth fixing. This
repo had exactly one, on `docs/data-sources/txdot-roadways.md`, where a page
named the `_` character in English:

```
On every SH16 segment read on 2026-09-13 its value is a single underscore.
```

Naming the character itself is shorter and clearer: *its value is a single `_`
character*. Work order #135 made that change on 2026-09-15, so the list now
fires nowhere in this repo.

**Put a bad example inside a code fence.** A **code fence** is a block wrapped in
three backticks, the way the quotation above is. Markdown shows it exactly as
typed, and the check skips it. Without the fence, quoting a fault commits it.

## What the test cannot see

The check reads paragraphs. It skips code fences, tables, headings, list items
and raw HTML, because a rule about word count applied to a command line would
fail a page for quoting a command correctly.

**A long bullet therefore passes.** Eighty words in a bullet are not counted;
the same eighty words in a paragraph fail. That is a limit of the counter and
not a loophole in the standard. The three rules apply to every sentence you
write, wherever it sits. A green test means nothing was caught, not that the
page is done.

## The four faults no test counts

These are the ones a reviewer catches. Each has a name so you can name it in a
review comment.

**The flip.** "Not because the tool failed, but because nobody read the
warning." The flip builds drama by first saying a thing that is not so. Say what
happened. "Nobody read the warning."

**Self-reference.** "This section explains how the cache works." A page that
narrates itself spends the reader's attention on the page instead of the
subject. Delete the sentence and start with the cache.

**The stack.** Two or more semicolons in one sentence. A semicolon joins two
complete thoughts, so a stack of them is a paragraph wearing one period. Break
it into sentences. The worst sentence in this repo runs 219 words and holds ten
semicolons.

**The setup.** "So what does that mean for a boundary retracement? It means the
tool cannot tell you." A question you answer yourself is a delay. Make the
point: "The tool cannot tell you."

## How to fix a long sentence

Find the joint. A long sentence is almost always two or three facts held
together by a dash, a semicolon, or the word *and*. Cut at the joint and give
each fact its own period.

Here is a real one, from `docs/data-sources/bcad-parcels.md`. It is 41 words
long and it holds two em dashes, so it breaks two of the three counted rules at
once:

```
2278 is NAD 83 Texas South Central, the State Plane zone Bexar County falls
in — the zone covers a good deal more of Texas than this one county — and it
is in the units a Texas surveyor works in.
```

Three facts are in there. The number names a zone. The zone is bigger than the
county. The zone reports in the units a Texas surveyor works in. The dashes were
doing the work three periods should do:

```
2278 is NAD 83 Texas South Central. That is the State Plane zone Bexar County
falls in, and it reports in the units a Texas surveyor works in. The zone
covers a good deal more of Texas than this one county.
```

Eight words, then twenty-one, then fifteen. No em dashes. Nothing was dropped
and no claim changed.

**Changing what a sentence says is a different job from changing how it reads.**
If the fix needs a fact you cannot confirm, stop and say so in the pull request.
The page above is owned by work order #135, not by this file.

## What this standard does not cover

Two pages in `docs/` are the agent's own dated output, kept as evidence that the
demo happened. They stay as they are. So do the three pages in `docs/agents/`,
which are read by software, and the slide bullets in
`docs/slides/beyond-the-prompt.md`, which are already short.
[ADR 0003](../../../../docs/adr/0003-produced-artifacts-stay-as-produced.md)
records why.

`CONTEXT.md` is a glossary and stays dense. `CLAUDE.md` is a list of rules for
an agent. Neither is a page a surveyor reads, and neither is checked.

## Where this came from

| | |
|---|---|
| The standard | [Federal Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/), `plainlanguage.gov` |
| The word list and the fault names | [`lguz/humanize-writing-skill`](https://github.com/lguz/humanize-writing-skill), MIT licensed, © 2026 Luis Guzman |
| Exact commit read | [`4b7c37f`](https://github.com/lguz/humanize-writing-skill/commit/4b7c37fa5148fd499e18498fcc91bb10ed801733) |
| Captured | 2026-09-15 |

The Federal Plain Language Guidelines are free and public, so a reader of this
repo can go and read the source. That is why they were chosen over ASD-STE100,
whose word list costs money and bans words a surveyor uses every day.

The humanize-writing skill is cited rather than copied. Its list of structural
patterns names *Parallel Negation* and *Em Dash Overuse*, which are the flip and
the em dash count above. It arrived at those two faults on its own, and
measuring this repo found the same two. That agreement is why the list is worth
citing.

It was not copied because of its third pass, *Add Human Texture*, which asks a
writer to pick a voice and to make less predictable word choices. That is good
advice for a post, and the skill has a section of rules for LinkedIn. A
procedure a surveyor acts on should be dull and predictable.

**Thank you to Luis Guzman**, whose dictionary is the source of the word list in
the file beside this one.
