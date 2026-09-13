# The Hermes segment runs on a schedule, and keeps the name

[Decision 2 in the plan of record](../plan-of-record.md) reads *"Claude Code as the spine + Hermes (Nous Research) for autonomous work,"* and decision 16 files the right-of-entry letters as *"Hermes beat — the second letter that sends itself."* Both were settled before anything was built.

What got built under [issue #34](https://github.com/RickSmith/survey-recon/issues/34) is a GitHub Actions schedule. `.github/workflows/roe-followup.yml` reads the follow-up clock once a day and writes whatever is due. Nobody starts it. It is genuinely autonomous work, and **it is not Hermes.**

**We keep the cron job, and we keep the name.** "Hermes" stays as the session's label for the 1:48–1:54 block, and the presenter says out loud what is behind it. This record is what stops that being a quiet substitution.

Two things decided it, and the second is the stronger one.

**The autonomy claim does not depend on which model runs the job.** The claim the segment makes is that day 21 arrives whether or not a person is looking. A scheduled workflow makes that claim checkable in public: a run either happened or it did not, and anybody in the room can open it afterward. A model call would have proved the same thing less clearly and with more to go wrong on a hotel network.

**Hermes would put an API key in the attendee path.** `CLAUDE.md` is blunt that the prerequisites are git, a GitHub account and the Claude desktop app, and that *"anything that needs an API key does not belong in the attendee path."* Reaching a hosted Hermes model needs a key; running one locally is a far larger ask than the three prerequisites above. Either route costs an attendee something the rest of the repo has been careful not to cost them.

## Considered options

- **Run the segment on Hermes, as decision 2 says.** Rejected. It buys nothing the room can see, it breaks the dependency rule above, and the build time is time this repo does not have before 8 October 2026. Worth reopening if the going-further material ever needs a real second-agent example — that is the place decision 2 still earns its keep.
- **Rename the block.** Rejected. "Hermes" is in the run of show, the cut line, the deck, the fallback card and the backlog. Renaming buys a reader nothing, costs a churn of edits across all of them, and would quietly delete the fact that a decision changed — which is the one thing this repo's history exists to show.

## Consequences

- **Nothing in this repo may imply a model ran the letters.** `docs/corridor-screen/roe-letters.md` carries the plain statement, and the speaker note on the Hermes slide tells the presenter to say it.
- **Decision 2's Hermes half is undelivered, not withdrawn.** It stands as written. This record narrows it to the one block that named it, and says why.
- **The evidence has to exist for the claim to be made.** A scheduled workflow only runs from the default branch, so the autonomy claim is evidenced only once #34 is merged. Merged before 4 October 2026 and there is a real run summary to open on the day. Merged after, and the presenter says the day has not come round yet rather than implying it has.
