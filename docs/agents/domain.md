# What to read before you start

A new hire reads the project file before driving to site. Same rule here.

## Read these first, every time

- **`CONTEXT.md`** at the repo root. The shared vocabulary — surveying, geodetic, TxDOT and project terms. If you catch yourself guessing what a word means, that word belongs in there.
- **`docs/adr/`**, when it exists. An **ADR** is an architecture decision record: one short file saying that a decision got made, what it was, and why. It is a field book entry for a decision instead of for a measurement. Read the ones touching whatever you are about to change.

If either is missing, **carry on quietly.** Do not point out that they are absent, and do not offer to create them up front. `/domain-modeling` writes them when a term or a decision actually gets settled — which is the only moment anyone knows what to put in one.

## Where they live

This repo is single-context: one glossary, one decision folder, both at the root.

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-....md
│   └── 0002-....md
└── ...
```

A much larger repo can be split into several contexts, each with its own glossary. You would know, because a `CONTEXT-MAP.md` would sit at the root pointing at each one. In that case, read every `CONTEXT.md` relevant to what you are doing, and check `src/<context>/docs/adr/` as well as the root `docs/adr/` — a decision can be scoped to one context rather than to the whole repo.

That is not this repo. Adding that structure here would be cost with nothing bought.

## Use the words in the glossary

When you name something — in a work order title, a proposal, a test name, a commit message — use the word `CONTEXT.md` uses. Do not drift to a synonym you happen to prefer.

This matters more here than in most repos, because the readers are licensed surveyors. Calling a monument a "marker", or recovery "finding it again", reads as somebody who has not done the work. Once a reader clocks that, they stop trusting the rest of the page, and they are right to.

If the idea you need is not in the glossary yet, stop and work out which of two things is happening:

- You are inventing language this project does not use. Reconsider.
- There is a real gap. That is a note for `/domain-modeling`.

## Say so when you contradict a decision

If what you are about to do goes against a recorded decision, say so out loud rather than quietly working around it:

> Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…

Overriding a decision is allowed. Overriding one silently is not.

This repo's own history gets shown on stage. A decision that was reversed without a word is exactly the thing that history is meant to make visible.
