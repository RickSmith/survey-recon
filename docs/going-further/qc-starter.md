# A QC starter

!!! danger "Read this before you use it"
    **This is a starting point. It is not a compliance system.**

    It does not certify anything, it does not satisfy any TxDOT or TBPELS
    requirement, and it has never been run against a sealed deliverable. It
    checks one narrow thing: **is this draft in a fit state to be reviewed
    yet?**

    Nothing on this page moves any liability off the person who signs. If you
    were looking for the page that settles who is accountable, that is
    [the seal and responsible charge](../governance/seal-and-responsible-charge.md).

---

## The one job it does

Your firm's real check already exists. It is
[section 5 of the AI-use policy](../governance/ai-use-policy.md): a named RPLS
reads the work against its sources, follows the numbers back, and decides
whether they would have reached the same conclusion.

**That check is expensive, because it is a licensed person's attention.** This
page is the cheap step in front of it.

It catches the drafts that waste that attention — the one with a number and no
source, the one whose "could not confirm" quietly disappeared between versions,
the one that does not say what it never looked at. **A draft that fails this
list is not ready for a reviewer. A draft that passes it is not approved** — it
is only ready to be read.

| | Who does it | What it answers |
|---|---|---|
| **This list** | The agent, on its own output | Is this fit to hand to a person yet? |
| **[Policy §5](../governance/ai-use-policy.md)** | A named RPLS | Is this right, and would I have said the same? |
| **The seal** | The same RPLS | Am I taking responsibility for it? |

Only the third one has legal weight. This page has none.

---

## Print this part

<div markdown="1" style="border:2px solid currentColor; padding:1.2em; border-radius:4px;">

# Before this draft goes to a reviewer

Ten questions. Any "no" sends it back **before** it costs a licensed person an
hour.

## The numbers

- [ ] **Every number with money or legal consequence has a source beside it.**
      A fee, a notice period, an accuracy tolerance, a lead time. Beside the
      number, not in a list at the end
- [ ] **Every number carries its unit.** Feet or meters, grid or surface,
      calendar days or business days. A number with no unit is a total station
      left on the wrong setting: the reading is real, and you cannot tell what
      it is
- [ ] **The arithmetic is shown, not just the answer.** A reviewer has to be
      able to disagree with one row rather than the total

## The sources

- [ ] **Every link in the document was actually opened.** Not "looks right" —
      opened. A dead address can answer cheerfully, and an out-of-date manual
      is worse than a missing one
- [ ] **Nothing is cited from a superseded source.** Retired manual addresses
      and old rule chapter numbers are still all over the internet
- [ ] **Captured data says when it was captured.** If it came out of a saved
      copy rather than off the live service, the document says so and gives the
      date

## The gaps

- [ ] **"Unknown" is written as unknown. It is never written as "no."** One of
      those two words sends a crew to a locked gate
- [ ] **"Not found" is written as not found, never "does not exist"** — and it
      says where the search went
- [ ] **The document names what it did not check.** A source that was skipped,
      a flag no public data can see, a question left open. **Silence reads as
      clear, and it is not**

## The person

- [ ] **One named person is going to read this end to end.** Not "the office."
      A name. If nobody is named, it is not ready to send

---

**If it has to leave the office before the reviewer is finished**, it goes out
as a preliminary document under 22 Tex. Admin. Code § 138.33(e) — unsigned,
unsealed, carrying that rule's exact caveat text. **That is a release, not an
approval.**

</div>

---

## If you want the agent to run it

Save the block below as `.claude/skills/qc-check/SKILL.md` in your own project,
next to the five commands you copied. Then type `/qc-check` after the agent
hands you something.

**It is text on this page rather than a sixth folder in the toolkit, and that is
deliberate.** The kit's five commands are Matt Pocock's, vendored unchanged and
accounted for. This one is ours, it is untested, and it does not belong sitting
among them looking like it has the same standing.

The agent checking its own homework is worth exactly what that sounds like —
**some.** The list aims at the mechanical misses: a missing unit, a link nothing
ever fetched, a gap the document does not admit to. **How often it actually
catches them here is untested.** What it certainly cannot catch is a number that
is plausible and wrong. That is what the person is for.

```markdown
---
name: qc-check
description: Check a draft against the fitness-to-review list before a person reads it. Use after producing any document, estimate, memo or table that a licensed professional will review.
---

# Check this draft is fit to review

You are checking a document you just produced, before a licensed
professional spends their time on it. You are NOT approving it. You are
deciding whether it is worth their hour yet.

Go through every item. For each one, quote the part of the document that
satisfies it, or say plainly that it fails.

## The numbers

1. Does every number with money or legal consequence carry a source beside
   it — not in a list at the end?
2. Does every number carry its unit? Feet or meters, grid or surface,
   calendar days or business days.
3. Is the arithmetic shown, so a reader can argue with one row instead of
   the total?

## The sources

4. Was every link in the document actually fetched? If you did not fetch
   it, say so — do not assume it resolves.
5. Is anything cited from a source known to be superseded?
6. Where data came from a saved copy rather than a live service, does the
   document say so and give the capture date?

## The gaps

7. Is anything that could not be checked written as `unknown`, never as
   `no`?
8. Is anything that could not be confirmed written as "not found", with an
   account of where you looked — never as "does not exist"?
9. Does the document name what it did not check?

## The person

10. Is there one named person who will read it end to end?

## How to report

Print a table: the item, PASS or FAIL, and the evidence or the reason.

Then state one of two verdicts, and nothing softer:

- **NOT READY** — list every FAIL and stop. Do not fix them silently.
- **READY TO REVIEW** — and say, in one sentence, that this means ready to
  be read, not approved.

Never write "approved", "signed off", "verified" or "complete". You cannot
do any of those. A person does.
```

!!! warning "Change it. It is yours, and it is not finished"
    Ten items is a first version, written against what went wrong while
    building this repo. Your firm's drafts go wrong in your firm's own ways.

    Add the checks that catch **your** rework. Delete the ones that never fire.
    A checklist nobody edits is a checklist nobody reads.

---

## What this is not, one more time

- **Not a compliance check.** It tests nothing against TxDOT specifications,
  TBPELS rules, or any standard of care
- **Not a substitute for the review in
  [policy §5](../governance/ai-use-policy.md)**, which is the one that decides
  whether the work is right
- **Not evidence of supervision.** A passing report is the agent's opinion of
  the agent's work
- **Not tested on a real deliverable.** It is a starting point, which is the
  most this repo claims for it

The session settled early that QC and compliance are
[out of scope](../plan-of-record.md), with a starter in the repo only. This is
that starter, and that is all it is.
