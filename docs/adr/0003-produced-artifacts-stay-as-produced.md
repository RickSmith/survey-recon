# Produced artifacts stay as produced

Issue #133 set a plain-language standard for the pages in `docs/` and issue #134
built a test that counts it. Two pages are held out of that standard for good,
and one of them is the worst-written file in the repo.

| File | What it says about itself |
|---|---|
| `docs/corridor-screen/spec.md` | "settled 2026-09-12, from the grilling on issue #5" |
| `docs/txdot-research.md` | "Research compiled 2026-09-12" |

Both are the agent's own output, produced live on a dated run. They are not
documentation somebody wrote about the tool. They are the evidence that the
session happened and that it produced what it claims to have produced.

`spec.md` runs 9,547 words and it is dense, long-sentenced and hard going. A
reader who has just read the plain-language skill will open it, see every fault
the skill names, and ask why it was skipped. That question is what this record
answers.

**Rewriting a produced artifact to read better makes the demo a lie.** The whole
point of showing that file on stage is that the audience is looking at what the
agent actually wrote, on a date, from a conversation they can also read. Edit it
for style and it becomes a thing a human polished afterwards. The claim "this is
what came out" would no longer be true, and nothing on the page would say so.

Three tests already read these two files: `test_datum_gap.py`, `test_deck.py`
and `test_manual_links.py`. They check that the claims in them match the run and
the manuals. That is the right kind of check for a produced artifact. Whether it
reads well is not a question that applies to it.

## The difference between exempt and allowlisted

The plain-language test carries a list of pages not swept yet. That list is a
debt. Each child work order of #133 deletes its own lines, and when the list is
empty the list goes too.

These two files are not on it, and must never be. An exemption is a decision
that stands. A test in `test_plain_language.py` fails if either one turns up on
the allowlist, because a child work order would then delete the line in good
faith and the exemption would quietly be gone.

Three more paths are exempt for their own reasons, none of them this one:

- `docs/agents/` — rewritten under #40 and read by software, not by a person
- `docs/slides/beyond-the-prompt.md` — slide bullets, already short and plain
- `CONTEXT.md` and `CLAUDE.md` — a glossary and a list of rules for an agent.
  Neither is a page a surveyor reads. They are not scanned at all

## Considered options

- **Rewrite `spec.md` and mark it as edited.** Rejected. A note saying "tidied
  up on a later date" is honest, and it still leaves the audience unable to tell
  which sentences the agent wrote. The value of the file is that nobody touched
  it.
- **Drop both files from the site.** Rejected for the same reason in reverse.
  They are worth showing. A reader who wants to know what an agent produces
  unsupervised should be able to go and look at nine thousand words of it.

## Consequences

- `spec.md` stays the worst-written file in the repo, on a public site, next to
  a skill that says not to write like that. That is the cost and it is accepted.
- Both files keep the dated line that says what they are. A produced artifact
  that does not say it was produced is just a badly written page.
- If either file is ever edited for anything other than a correction of fact,
  this record is wrong and should be replaced rather than ignored.
