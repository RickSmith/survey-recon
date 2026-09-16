# Managing your agent

Say you hired a survey technician last month. Sharp, fast, reads everything,
and has never worked in Texas. You would not hand them a job and walk away.
You would tell them exactly what the job is. You would give them one piece of
it at a time. You would look at their work before it went out the door. And
when something came back wrong, you would send it back with a note, and you
would keep the note.

That is the whole of managing an agent. There is nothing else to learn. The
rest of this chapter is what each of those steps looks like when the new hire
is software, and five true stories about the notes that got kept.

## The loop

Every job on this site went through the same four steps, in order, every time.
Even a one-line fix.

**1. Write the work order.** Say what is wanted, what is out of scope, and how
you will know it is done. On this site a work order is a GitHub *issue*, which
is a numbered note anybody can read. The number is how it gets referred to
afterward.

**2. Let the agent work on a copy.** The agent never touches the real thing. It
works on a *branch*, which is a working copy nobody else is affected by. If it
makes a mess, the mess is on the copy.

**3. Read the check print.** When the agent thinks it is done, it hands the copy
back as a *pull request*. That is the check print. You read it, you redline it,
and you either send it back or you approve it.

**4. Sign it.** Approving is called a *merge*. The work goes from the copy into
the real thing. Nobody can do this to their own work here, including the agent.
A person signs, and the signature is on the record with a date.

Five commands carry a job through those steps, and they are in the
[toolkit](../toolkit/index.md). Only one of them changes anything, and it is
the fourth.

## Where the loop earns its keep

The loop is slow on purpose. Every piece of work goes through a work order and
a review, even when it is faster not to. The reason is what happens at step 3.

An agent is confidently wrong the way a new hire is confidently wrong. It will
cite a manual that was replaced two years ago, in a clean sentence, with a
link that looks right. It will accept a number in the wrong unit because the
server did not complain. And once, on this site, the person writing the work
order was the one who was wrong, and the agent repeated it because it was told
to.

None of those got out the door, because somebody read the check print. Every
one of them is written up below, with what it would have cost.

## Five stories from the record

<div class="grid cards" markdown>

-   **[The rule we broke on day one](the-force-push.md)**

    This site has a rule against rewriting its own history. Fifteen minutes
    after it was created, the rule was broken on purpose. Who decided, what it
    cost, and why it is a record and not a precedent.

-   **[The claim we got wrong](the-claim-we-got-wrong.md)**

    Four pages said the licensing board had never spoken about AI. The board
    had, in writing, two years earlier. The agent was told to repeat the claim
    and did. What it costs when the confidently wrong one is the human.

-   **[The manual that was real, and out of date](the-superseded-manual.md)**

    Search still hands out the old address for the TxDOT Survey Manual. The old
    server does not answer, so the agent saw a timeout, not a missing page, and
    cited the old revision anyway. The boring check that catches it.

-   **[The answer that was wrong rather than missing](the-wrong-answer.md)**

    Ask a federal elevation service for feet, in the unit a Texas surveyor
    works in, and it answers in meters. No error. A believable number, three
    and a quarter times too small. Why a wrong answer is worse than a broken
    one.

-   **[The description that outlived its evidence](the-description-that-outlived-its-evidence.md)**

    The glossary kept describing that failure as a run nobody had captured,
    while the captures sat beside it saying otherwise. It reached a slide. What
    a summary is for, and why it is not a source.

</div>

## What to take from the five

Two of the five were the agent being wrong. One was the human being wrong. One
was a description drifting away from the thing it described. And one was a
rule broken on purpose, by a person, with the reason written down at the time.
Four were caught by somebody reading a check print. All five are still on the
record, with the correction or the decision beside them.

That record is the point. A clean history with the mistakes erased would be a
worse teaching example, and a worse audit trail, than one that shows the work
being sent back.

---

## Where this came from

This chapter was planned on
[work order #7](https://github.com/RickSmith/survey-recon/issues/7). Each of
the five stories names its own work order at the end.
