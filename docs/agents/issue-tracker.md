# Where the work orders live

Work orders for this repo are GitHub issues. `CONTEXT.md` translates *issue* as *work order*, and that is exactly what one is: a single job, written down, before anybody starts it.

Everything below is how an agent reads and writes them. It all goes through `gh`, GitHub's own command line tool. Run inside a clone, `gh` works out which repo it is in by itself, from `git remote -v`. You never tell it.

## The everyday commands

| To do this | Run |
| --- | --- |
| Open a work order | `gh issue create --title "..." --body "..."` |
| Read one, with its comments | `gh issue view <number> --comments` |
| Comment on one | `gh issue comment <number> --body "..."` |
| Add or remove a label | `gh issue edit <number> --add-label "..."` / `--remove-label "..."` |
| Close one | `gh issue close <number> --comment "..."` |

For a body longer than a line or two, write it to a file first and pass `--body-file`. Quoting a long message directly on the command line will bite you eventually.

To list them:

```
gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'
```

Narrow it with `--label` and `--state`.

## Two phrases the skills use

The skills are written to work on any repo, so they say general things like "publish to the issue tracker." Here is what those mean here.

- **"Publish to the issue tracker"** — create a GitHub issue.
- **"Fetch the relevant ticket"** — run `gh issue view <number> --comments`.

## Pull requests as a way of asking for work

**PRs as a request surface: no.**

That line is a switch, and `/triage` reads it. Leave it at `no` unless this repo starts treating pull requests from outsiders as feature requests.

A pull request is the check print you redline. Flip this to `yes` and those redlines join the same queue as work orders, running through the same labels and the same states, using the `gh pr` versions of the commands above:

- Read one: `gh pr view <number> --comments`, and `gh pr diff <number>` for the changes themselves
- List the outside ones: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`, then keep only those whose `authorAssociation` is `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR` or `NONE`. Drop `OWNER`, `MEMBER` and `COLLABORATOR` — those are us
- Comment, label, close: `gh pr comment`, `gh pr edit --add-label` / `--remove-label`, `gh pr close`

One trap worth knowing. GitHub numbers issues and pull requests out of the same pot, so a bare `#42` might be either one. Resolve it with `gh pr view 42`, and fall back to `gh issue view 42` when that comes back empty.

## Wayfinding

`/wayfinder` runs a large piece of work as a **map** — one issue holding the notes, the decisions so far, and the fog — with **child** issues hanging off it as individual jobs. Think of the map as the project file and the children as the jobs on it.

**The map** is an issue labeled `wayfinder:map`. Create it with `gh issue create --label wayfinder:map`.

**A child** is an issue linked to the map as a GitHub sub-issue, through `gh api` on the sub-issues endpoint. Where sub-issues are not switched on, put the child in a task list in the map body instead, and put `Part of #<map>` at the top of the child. Label it `wayfinder:<type>` — one of `research`, `prototype`, `grilling` or `task`. Once somebody takes it, assign it to them.

**Blocking** uses GitHub's native issue dependencies. Prefer these: they show up in the web page, so a human can see what is waiting on what without reading any body text.

```
gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>
```

`<blocker-db-id>` is the blocker's numeric **database id**. It is not the `#number` you see on the page, and it is not the `node_id`. Read it with:

```
gh api repos/<owner>/<repo>/issues/<n> --jq .id
```

Pass the wrong one and the call either fails or quietly links the wrong issue.

GitHub then reports `issue_dependencies_summary.blocked_by` — a count of blockers still open. That count is the live gate. Where dependencies are not available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. Either way the rule is the same: a job is unblocked when every one of its blockers is closed.

**Finding what is actually workable.** List the map's open children. Drop any with an open blocker — `issue_dependencies_summary.blocked_by > 0`, or an open issue named in the `Blocked by` line. Drop any that already has somebody assigned. First one left in map order wins.

**Taking it**: `gh issue edit <n> --add-assignee @me`. That is the first thing written in a session, so two people never start the same job.

**Finishing it**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then add a pointer to the answer in the map's decisions-so-far. The map is only useful if it stays current.
