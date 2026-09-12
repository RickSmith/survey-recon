# Sanity checks warn; dead services stop the run

Corridor screening calls public services that fail in two quite different ways. A service can be **dead** — no response, or an HTTP error. Or it can be **wrong** — a plausible answer that is not the answer. The clearest example is in our own research: USGS 3DEP ignored the coordinate-system parameter, read longitude and latitude as Web Mercator metres, and returned a believable elevation for the wrong place. It did not fail. It answered.

We treat the two opposite ways. **A dead service stops the run**, after three automatic retries and an offer to retry, skip or abort. **A tripped sanity check only records a warning**, and the run continues.

That is backwards from the intuition that a wrong answer is more dangerous than no answer. It is deliberate. A dead service is a *fact* — the tool knows it with certainty, so acting on it is safe. A sanity check is a *heuristic*: it guesses that an answer looks wrong. If a heuristic could halt a run, the first false alarm during a live session would teach everyone watching to switch the checks off, and a check that people switch off protects nobody. A warning that always fires and never blocks stays trusted.

It also puts the decision where this repo says it belongs. The tool reports. The licensed surveyor decides whether the answer is good enough to seal.

## Considered options

- **Both fatal.** Rejected. The first false positive kills a run, and the checks lose credibility the moment someone adds a flag to disable them.
- **Both warnings.** Rejected. A dead service means a whole class of data is simply absent. A flagged parcel list that silently omits every school in the corridor is worse than no list, because it looks complete.

## Consequences

- Every sanity-check warning must survive into the output file, next to the data it doubts. A warning nobody reads is the same as no check.
- The output must distinguish `unknown` from `no`. A parcel that could not be checked is never reported as clear.
- A stopped run still writes its output, marked incomplete, listing what finished and what stopped.
