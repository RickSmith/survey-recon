# What to read before you start

A new hire reads the project file before driving to site. Same rule here.

## Read these first, every session

- **`CONTEXT.md`** at the top of the job folder. The shared vocabulary. If you
  catch yourself guessing what a word means, that word belongs in there
- **`CLAUDE.md`**, beside it. How work gets done here, and who signs
- **`docs/agents/issue-tracker.md`** — where work orders live, and the commands
  for reading and writing them
- **`docs/agents/triage-labels.md`** — the five states a work order can be in
- **`docs/adr/`**, when it exists. An **ADR** is an architecture decision record:
  one short file saying that a decision was made, what it was, and why. It is a
  field book entry for a decision instead of for a measurement. Read the ones
  touching whatever you are about to change

**The two `docs/agents/` files are not optional.** `/to-spec`, `/to-tickets` and
`/code-review` each check that somebody handed them that vocabulary, and stop if
nobody did. Reading them at the start of the session is what keeps that from
happening.

If `CONTEXT.md` or `docs/adr/` is missing, **carry on quietly.** Do not point out
that they are absent, and do not offer to create them up front.
`/grill-with-docs` writes them when a term or a decision actually gets settled,
which is the only moment anyone knows what to put in one.

## Where they live

One glossary, one decision folder, both at the top of the job folder:

```
/
├── CLAUDE.md
├── CONTEXT.md
├── docs/
│   ├── agents/
│   │   ├── domain.md          ← this file
│   │   ├── issue-tracker.md
│   │   └── triage-labels.md
│   └── adr/
│       ├── 0001-....md
│       └── 0002-....md
└── ...
```

Start here. A bigger project can be split into several glossaries later, and you
will know when, because somebody will have got lost.

## Use the words in the glossary

When you name something — a work order title, a heading, a file name, a note on a
change — use the word `CONTEXT.md` uses. Do not drift to a synonym you happen to
prefer.

This matters more here than in most trades, because the readers are licensed
professionals. Calling a monument a "marker", or recovery "finding it again",
reads as somebody who has not done the work. Once a reader clocks that, they stop
trusting the rest of the page, and they are right to.

If the idea you need is not in the glossary yet, work out which of two things is
happening:

- You are inventing language this firm does not use. Reconsider
- There is a real gap. Add the word, and say that you added it

## Say so when you contradict a decision

If what you are about to do goes against a recorded decision, say so out loud
rather than quietly working around it:

> Contradicts ADR-0003 (we do not use county parcel geometry for boundary work)
> — but worth reopening because…

Overriding a decision is allowed. Overriding one silently is not.
