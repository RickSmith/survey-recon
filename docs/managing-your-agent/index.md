# Managing your agent

!!! note "Placeholder"
    This chapter is a stub. It gets written under
    [issue #7](https://github.com/RickSmith/survey-recon/issues/7).

The supervision loop: write the work order, let the agent work on a copy, read
the check print, send it back or sign it. This chapter walks through the five
commands that carry it, and then shows **this repo's own pull requests** as the
worked example — including the ones that got sent back.

## Here already

- **[The rule we broke on day one](the-force-push.md)** — this repo has a rule
  against altering its own history. Fifteen minutes in, we broke it on purpose.
  What happened, what it cost, and who made the call.
- **[The claim we got wrong](the-claim-we-got-wrong.md)** — four pages of this
  repo stated that TBPELS had not spoken directly to AI. The board had approved a
  written opinion on it two years earlier, and the work order handed to the agent
  told it to repeat the claim anyway. What it costs when the confidently wrong
  one is the human.
- **[The manual that was real, and out of date](the-superseded-manual.md)** —
  search still hands out the old address for the TxDOT Survey Manual. The old
  host does not answer, so an agent sees a timeout rather than a 404, and cites
  the revision anyway. Failure beat one, and the boring check that catches it.
- **[The answer that was wrong rather than missing](the-wrong-answer.md)** — ask
  the USGS elevation service in `US_Feet`, the unit a Texas surveyor works in,
  and it answers in meters. No error, valid JSON, a believable number three and
  a quarter times too small. Failure beat two, and why a wrong answer is worse
  than a broken one.
