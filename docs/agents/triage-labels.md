# What the labels mean

The skills talk about five states a work order can be in. This table says what each one is called on this repo.

Right now the names match exactly. That is deliberate — one less thing to hold in your head.

| What the skills call it | What we call it | What it means |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Nobody has looked at this yet |
| `needs-info` | `needs-info` | Waiting on whoever raised it to say more |
| `ready-for-agent` | `ready-for-agent` | Fully specified. An agent can pick it up with nobody watching |
| `ready-for-human` | `ready-for-human` | A person has to do this one |
| `wontfix` | `wontfix` | Decided against. Not happening |

When a skill names one of these states, use the label in the middle column.

**If this repo ever renames them, change the middle column only.** The left column is the skills' own vocabulary, and it is not ours to edit. Rename it and the skills stop finding anything.

## A note on `ready-for-agent`

Some skills apply `ready-for-agent` to everything they create, on the reasoning that a properly written work order is agent-ready by construction.

That is not always true here. "Recruit a surveyor to walk the repo cold" is a job for a person. So is standing up in front of a room for two hours. Labelling those `ready-for-agent` makes the list lie about itself, and a list that lies is worse than no list.

Use `ready-for-human` when a person has to do it. Having two labels is only worth anything if the second one gets used.

## The one that already existed

`wontfix` was on this repo before any of this was set up — GitHub creates it with every new repo. The other four were added by hand.

Worth knowing, because the setup skill writes this vocabulary into a document but does not create the labels themselves. If a label in the middle column does not exist on the repo, `gh issue create --label` fails, and it fails at the moment you are trying to publish a batch of work orders.
