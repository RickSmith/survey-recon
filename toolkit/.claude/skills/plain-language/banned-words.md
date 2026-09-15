# The word list

Fifty-five words and phrases that turn up far more often in machine writing than
in anybody's field notes. Each row gives a plainer word to use instead.

This table is the one place the list is written down.
`corridor-screen/tests/test_plain_language.py` reads the first column out of it
and checks the pages in `docs/` against it. Adding a row here adds a rule.
Deleting a row drops one.

The list is a blunt instrument and it is meant to be. It finds nothing in this
repo today, which is the point: it costs nothing to keep and it stops the drift
later. When it does fire on a word you used correctly, the plainer word in the
second column is usually shorter anyway.

The first twenty-one are the strongest signals. The next nineteen are words
people do use, which machines reach for far too often. The last fifteen are
joining words that arrive in clusters.

| Word or phrase | Use instead |
|---|---|
| delve | dig into, look at |
| tapestry | mix, combination |
| landscape | space, field |
| pivotal | important, key |
| underscore | show, highlight |
| testament | proof, evidence |
| intricate | complicated, detailed |
| intricacies | details |
| meticulous | careful, thorough |
| meticulously | carefully |
| nuanced | subtle |
| multifaceted | many-sided |
| embark | start, begin |
| spearhead | lead, drive |
| bolster | support, strengthen |
| bolstered | supported, strengthened |
| garner | get, earn |
| interplay | relationship |
| realm | area, field |
| labyrinth | maze, mess |
| symphony | mix, blend |
| crucial | important, key |
| vibrant | lively, active |
| foster | encourage, grow |
| enhance | improve |
| leverage | use |
| navigate | deal with, handle |
| resonate | connect, land |
| illuminate | show, explain |
| showcase | show, display |
| enduring | lasting, long-term |
| robust | strong, solid |
| holistic | whole, complete |
| comprehensive | full, complete |
| innovative | new, fresh |
| dynamic | active, changing |
| seamless | smooth, easy |
| seamlessly | smoothly, easily |
| cutting-edge | latest, newest |
| game-changer | big deal, breakthrough |
| Furthermore | Also, And |
| Moreover | And |
| Additionally | Also, And |
| Consequently | So |
| Nevertheless | Still, But |
| Subsequently | Then, After that |
| Notably | Worth mentioning |
| Indeed | (usually just delete it) |
| Nonetheless | But, Still |
| Hence | So |
| Thus | So |
| In conclusion | (just conclude) |
| In summary | (just summarize) |
| It's worth noting that | (delete it and state the thing) |
| It's important to understand that | (delete it and state the thing) |

## Where the list came from

Taken from the AI patterns dictionary in
[`lguz/humanize-writing-skill`](https://github.com/lguz/humanize-writing-skill),
MIT licensed, © 2026 Luis Guzman. Read at commit
[`4b7c37f`](https://github.com/lguz/humanize-writing-skill/commit/4b7c37fa5148fd499e18498fcc91bb10ed801733)
on 2026-09-15.

The rows are the same words. The second column is shortened, and the three tiers
are one table here so that a test can read the list from a single place. That
dictionary in turn credits Wikipedia's "Signs of AI writing" page, GPTZero's
vocabulary research, and several editing forums.
