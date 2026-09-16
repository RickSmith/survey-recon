# The claim we got wrong

This repo told people, on four pages, that TBPELS had not spoken directly to AI.

**That was wrong.** The board approved a written opinion on AI on 14 November
2024. It had been public for nearly two years when we wrote the opposite.

Here is how it happened, what caught it, and what was changed. It is kept for
the same reason [the force push](the-force-push.md) is kept: a record that
leaves out the unflattering parts is not a record.

## What we said

The sentence appeared in four places, in slightly different words:

| File | What it said |
|---|---|
| `README.md` | "TBPELS has not spoken directly to AI, but responsibility doctrine already covers it" |
| `docs/index.md` | The same sentence |
| `docs/plan-of-record.md` | "TBPELS hasn't spoken directly to AI; responsibility doctrine already covers it" — written into the slide notes as a punchline for owners |
| `toolkit/CLAUDE.md` | "As of «DATE», we have not found guidance from TBPELS addressing AI specifically" |

Three of those four state it as fact. The fourth, the agent handbook we ship to
firms, says "we have not found" — which was the honest form, and which is the
only one of the four that was not actually false.

## What is true

**TBPELS Policy Advisory Opinion 71, *The Use of Artificial Intelligence (AI)
Software By Licensees*, approved in public session on 14 November 2024.**

<https://pels.texas.gov/nm/2024/pao-71-response.pdf>

It is two pages. It says AI software is a tool, that nothing bans it, and it sets
three caveats about oversight, competence and client confidentiality. It names
the board rules that already apply. Its conclusion is that no new opinion was
needed, because the existing rules cover it.

It is listed as number 71 on the board's public index at
<https://pels.texas.gov/policy.htm>, between an opinion on limiting liability and
one on foreign-based engineering firms.

The full quotation and what it means for a firm is on
[The seal and responsible charge](../governance/seal-and-responsible-charge.md).

## How it happened

The claim came from the September 2026 research pass, and it was never checked
against the board's own site. It was plausible, it fitted the story we wanted to
tell, and nobody typed it into a search box next to the word "TBPELS."

It survived four rewrites because each rewrite copied it from the last one.

It was caught on **2026-09-12**, by an agent writing the governance pages. The
work order it was working from told it, in writing, to state the claim. The agent looked
the claim up before writing it down, found PAO 71, and stopped.

## The uncomfortable part

The work order was wrong. A licensed human wrote it. The agent was told, in
writing, to publish a false statement of law to an audience of licensed
professionals. It did not publish it. The only reason is that it checked a
citation it had been handed rather than repeating it.

This session's thesis is that the agent is the one that gets confidently wrong
and the human is the one who catches it. That is usually the direction. **It is
not the only direction**, and a firm that builds its checking only in that
direction has built half of it.

## What actually saved it

Not cleverness. A rule, written down in this repo's own handbook before any of
this happened:

> **Never invent a TxDOT requirement.** Cite the manual section and its URL, or say
> you could not confirm it

The claim about TBPELS had no citation. Following the rule meant going to find
one, and the search that was supposed to confirm the claim disproved it instead.

**The rule that catches an error is usually boring and was written for something
else.** This one was written about TxDOT manuals.

## What was changed

On 2026-09-12:

- The false sentence was removed from `README.md`, `docs/index.md` and
  `docs/plan-of-record.md`, and replaced with what PAO 71 actually says
- `toolkit/CLAUDE.md` — the handbook firms take home — was corrected, and now
  points at PAO 71 rather than leaving the firm to fill in a blank
- The governance pages were written against the real opinion
- This page was added

**No history was rewritten.** The commits that carried the false claim are still
there, still readable. The correction is a new entry, which is how a field book
works.

## What we are still not saying

We are not saying PAO 71 settles every question. It does not.

It does not address whether AI output must be disclosed on a sealed document. It
does not address how Tex. Occ. Code § 1071.351(d) applies to work no person
prepared. Those remain **not found**, and they are written up as not found on
[The seal and responsible charge](../governance/seal-and-responsible-charge.md).

The difference between this page and the sentence it replaced is that "not found"
now means somebody looked.

---

## Where this came from

The claim was caught and corrected under
[work order #7](https://github.com/RickSmith/survey-recon/issues/7), the one
that was telling the agent to repeat it.
