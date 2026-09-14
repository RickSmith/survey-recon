# Going further

Every page before this one was written to need three things: **git, a GitHub
account, and the Claude desktop app.** That was a promise, and it was kept.

**This page breaks it on purpose.** The things kept out of the main path get to
exist here, and each one says what it costs before it says what it does.

!!! warning "Nothing on this page is required"
    The [take-home toolkit](../toolkit/index.md) is finished without any of it.
    If you never open this page again, nothing you took home stops working.

    Come back when the five commands feel ordinary. Not before.

---

## What you already have

The kit ships nine of Matt Pocock's skills — the five you type, and four they
call while they run. That is
[written out in the skills README](https://github.com/RickSmith/survey-recon/blob/main/toolkit/.claude/skills/README.md),
with the reasoning for each.

The set it was taken from has **twenty-five**. This section is the other sixteen.

---

## 1. The rest of Matt Pocock's set

Sixteen skills, as version 1.2.3 documents them. The one-line summaries are
ours, shortened from
[the upstream reference list](https://github.com/mattpocock/skills#reference).

### The ones you would type

| Command | What it does | Worth your time? |
|---|---|---|
| `/wait-what` | Fire it the moment an answer does not make sense. It re-explains, in your own glossary's words | **Yes. If you only take one, take this one** |
| `/handoff` | Squeezes a long conversation into a note, so a fresh session can carry on | Yes. The agent forgets between sessions. This is the field book entry that survives |
| `/to-questionnaire` | Turns a decision you cannot make alone into a short form for the one person who can | Yes. It is a request for information, in the shape you already send one |
| `/ask-matt` | Asks what you are trying to do, then names which of his skills fits | Yes, if you forget which command is which |
| `/triage` | Moves work orders through a set of states, one owner at a time | Later. It needs enough work orders to be worth sorting |
| `/wayfinder` | Plans a job too big for one sitting, as a map of decisions to settle one at a time | Later. This is a multi-month job's tool |
| `/teach` | Teaches you something across several sittings, keeping notes between them | Maybe. It is a study tool, not a work tool |
| `/grill-me` | The interview, without the glossary and decision-record writing | No. You have `/grill-with-docs`, which is that plus more |
| `/improve-codebase-architecture` | Surveys software you already have, and reports what could be tidied | No. It assumes a codebase, and you are not keeping one |
| `/setup-matt-pocock-skills` | Interviews you and writes the setup files | **No. The kit ships those files already written.** The skills README says what to do if it ever gets mentioned |

### The ones the agent reaches for on its own

You can type these, and mostly you will not have to: upstream's reference list
marks them **model-invoked**, meaning the agent opens one itself when the job
fits. The four already in your kit work the same way.

| Skill | What it does | Worth having? |
|---|---|---|
| `research` | Chases a question through primary sources and writes up what it found, with citations | Yes — **and open every citation.** See the warning below |
| `diagnosing-bugs` | A disciplined loop for "it is broken and nobody knows why" | Yes, if you ever keep a tool running |
| `resolving-merge-conflicts` | Works through two people's edits to the same file, one piece at a time | Yes, once more than one person edits your repo |
| `wizard` | Writes a step-by-step script that walks a **person** through what only a person can do | Yes. Closest thing in the set to a field procedure |
| `prototype` | Builds a throwaway to answer "would this even feel right?" | Maybe. Useful before you commit to a shape |
| `writing-for-agents` | How to write a document an agent will read | Yes, once you start editing your own `CLAUDE.md` |

!!! danger "Any skill can write a citation, and a citation can be confidently wrong"
    This repo has the receipt, from its own work rather than from this skill. A
    superseded TxDOT manual address was quoted, with a date, out of a manual
    that has not been at that address for years — and the address does not
    answer at all, so what an agent sees is a timeout that looks like bad
    Wi-Fi:
    [the manual that was real, and out of date](../managing-your-agent/the-superseded-manual.md).

    Use `research`. Then open every link it hands you. **A citation you did not
    open is a citation you are taking on faith,** and your seal goes on the
    document, not the agent's.

### Two ways to get them

**Route A — install the set as a plugin.** A **plugin** is a bundle of skills
the app fetches and keeps up to date for you, instead of you holding the files.
[Upstream's own installation notes](https://github.com/mattpocock/skills#installation-30-second-setup)
say the set is listed in the app's official catalog, so there is nothing to add
first. Typed into the Claude desktop app:

```
/plugin install mattpocock-skills
```

That costs **no new prerequisite.** You already have the app. Upstream describes
what arrives as read-only, updating when he ships a change — you are
subscribing, not keeping a copy.

**We have not walked a first-time reader through this route.** The
[Day 0 setup](../day-0/index.md) pages are screenshot-checked; this is one line
off somebody else's README.

**Route B — the `npx` route.** This is the one the toolkit was built to avoid:

```
npx skills@latest add mattpocock/skills
```

It writes editable copies into your own project, and `npx skills update` pulls
his later changes when you ask for them. That is the reason somebody would
prefer it: **the files are yours, and you may change them.**

The price is real. `npx` comes with **Node.js**, which is a separate program to
install, which needs a terminal, which in a lot of firms needs somebody with
administrator rights.

!!! warning "Neither route is required for anything in the main path"
    The five commands are already on your disk, as plain markdown you copied.
    They do not need the plugin, they do not need `npx`, they do not need
    Node.js, and they never did.

    This section is for the person in your firm who is comfortable installing
    things. It is not a step anybody else has to take.

!!! note "Take either route and you now have nine skills twice"
    Upstream says it plainly: installing both ways "leaves you with every skill
    twice." You copied nine of them into `.claude/skills/`, so either route
    hands you a second copy of those nine.

    You can see it in the names. A skill that arrived as a plugin reads
    `/mattpocock-skills:grill-with-docs`. The one you copied is plain
    `/grill-with-docs`. That prefix is what the
    [Day 0 screenshot note](../day-0/index.md) is about — there it explains a
    picture; here it is how you tell two copies apart.

    **Pick one.** Either delete the nine copied folders and live on the plugin's
    updates, or skip the plugin and keep the copies you can edit. Running both
    is how two revisions of the same procedure end up in the same truck.

---

## 2. Hermes, and what it is actually for

**This repo has never run Hermes.** Nothing in this section was tested by us. It
is a description of somebody else's tool, read off their own documentation, and
it is here because the session says the name out loud.

### Two different things share the name

| | What it is | Where |
|---|---|---|
| **Hermes 4** | A family of language models from Nous Research. **Open weights** — the model itself is a file you can download, not only a service you call | [Model card](https://huggingface.co/NousResearch/Hermes-4-405B) |
| **Hermes Agent** | A program that runs on a server you control, remembers across sessions, and writes its own procedures as it goes | [Project](https://hermes-agent.nousresearch.com/) · [source and license](https://github.com/NousResearch/hermes-agent) |

The model card describes the 405B version as built on Meta's Llama-3.1-405B and
carrying the Llama 3 license, with 70B and 14B versions alongside it. Those
numbers are model sizes, and bigger means more hardware to run it. **The license
is not the same for every size.** Read the card for the size you mean rather
than this table. The Agent is separate work, published under the MIT license —
the same permissive license as the five commands in your kit.

### What it is good for

- **Work that carries on when nobody is at the keyboard.** That is the whole
  point of it, and it is a real point
- **Running on hardware you control.** Its
  [own documentation](https://hermes-agent.nousresearch.com/docs/) describes
  running it on a cheap rented server, or on your own machine
- **Holding the weights.** With an open-weight model, the thing answering you is
  a file you have. Nobody can retire it out from under you. For a firm that has
  watched software go away, that is not nothing
- **Filling in forms and calling services.** The model card advertises **tool
  calling** and **structured output** — being able to call a service and to
  answer in a fixed shape rather than in prose. That is the difference between
  a model that writes you a paragraph about a parcel and one that can go and
  ask about it

### What it is not

- **It is not a lighter lift than what you already have.** Its
  [setup documentation](https://hermes-agent.nousresearch.com/docs/) asks for
  credentials through Nous Portal, or your own key for another provider. **An
  API key does not belong in the attendee path**, which is why this sits on this
  page and not in the kit
- **It is not supervision.** An agent working while you sleep produces work you
  did not watch being produced. The Texas rule asks you to review and approve
  proposed decisions **before they are acted on** — see
  [the seal and responsible charge](../governance/seal-and-responsible-charge.md).
  The more autonomous the tool, the harder that sentence gets. The rule does not
  bend to meet it
- **It is not something to try on a live job.** A server you keep running is a
  server somebody has to look after

### What this repo built instead, and why

The session's Hermes block — the right-of-entry letter that sends itself on day
21 — **is a scheduled GitHub Actions job, and it is not Hermes.** The presenter
says so on stage, and it is written down twice: in
[ADR 0002](../adr/0002-the-hermes-segment-runs-on-a-schedule.md) and on
[the right-of-entry letters page](../corridor-screen/roe-letters.md).

The short version: the claim that block makes is *day 21 arrives whether or not
a person is looking.* A public run summary anybody can open proves that better
than a model call would, and it costs an attendee nothing.

ADR 0002 names this page as the place a real second-agent example could still
earn its keep. **It has not been built.** Said here rather than left as a gap
somebody finds later.

---

## 3. A QC starter

Deciding whether an agent's output is fit to review is a different job from
reviewing it. The [QC starter](qc-starter.md) is one page for that first job.

It is a starting point, and it is **not** a compliance system. That page says so
in larger type than this one does.

---

## What is deliberately not here

- **A way to make the agent sign anything.** There is no such thing. Where that
  is settled is [Governance](../governance/index.md)
- **A hosted service, a subscription, or a vendor to call.** This repo has
  tested none, so it recommends none
- **A second worked example.** The session names one on stage. Building it is
  your Monday, not ours

---

**If you take one thing off this page:** get `/wait-what`, by either route
above, and type it the next time an answer does not make sense. It is not in
your kit, so it costs you one of the two installs — and it is the cheapest
thing on this page to be wrong about.
