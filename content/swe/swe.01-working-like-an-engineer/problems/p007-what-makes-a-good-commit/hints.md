## Hint 1

For each of the three situations ask: what do I need to be **true about every single commit** for this tool to work well?

## Hint 2

`revert` creates the opposite of one commit. If that commit also contains a formatting change and a typo fix, what else gets undone? `bisect` runs your tests on a commit in the middle of the history. What if the tests fail there for an unrelated reason?

## Hint 3

Structure: one sentence per situation (what goes wrong in A, what works in B), then the rules: one logical change per commit, every commit builds and passes tests, a message that says what and why, no generated or personal files.
