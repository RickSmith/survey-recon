# What the labels mean

The five commands talk about five states a work order can be in. This file says
what each one is called at «FIRM NAME».

Right now the names match the skills' own names exactly. That is deliberate — one
less thing to hold in your head.

| What the skills call it | What we call it | What it means |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Nobody has looked at this yet |
| `needs-info` | `needs-info` | Waiting on whoever raised it to say more |
| `ready-for-agent` | `ready-for-agent` | Fully specified. An agent can pick it up with nobody watching |
| `ready-for-human` | `ready-for-human` | A person has to do this one |
| `wontfix` | `wontfix` | Decided against. Not happening |

When a skill names one of these states, use the label in the middle column.

**If you rename them, change the middle column only.** The left column is the
skills' own vocabulary and it is not yours to edit. Rename that and the skills
stop finding anything.

## Create the labels before you need them

Writing a label into this file does not create it on the project. If a label in
the middle column does not exist, `gh issue create --label` fails — and it fails
at the moment you are trying to publish a batch of work orders.

GitHub creates `wontfix` with every new project. Add the other four once:

```bash
gh label create needs-triage --description "Nobody has looked at this yet"
```

```bash
gh label create needs-info --description "Waiting on whoever raised it"
```

```bash
gh label create ready-for-agent --description "Fully specified, ready for an agent"
```

```bash
gh label create ready-for-human --description "A person has to do this one"
```

## A note on `ready-for-agent`

Some skills apply `ready-for-agent` to everything they create, on the reasoning
that a properly written work order is agent-ready by construction.

That is not always true. "Walk the site and photograph the access" is a job for a
person. So is "call the landowner." Labelling those `ready-for-agent` makes the
list lie about itself, and **a list that lies is worse than no list.**

Use `ready-for-human` when a person has to do it. Having two labels is only worth
anything if the second one gets used.
