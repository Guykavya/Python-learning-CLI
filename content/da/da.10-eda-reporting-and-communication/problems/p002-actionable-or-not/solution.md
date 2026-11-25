## Approach

1. Number, "from"/"to", owner, ISO date, two limitations: nothing to report.
2. Every check fails: no digit, no comparison word, empty owner, "soon" is not a date, no limitations.
3. Has a number (1.7) but no comparison word ("by" is not in the list); the date is written in words, which this pattern does not accept; only one limitation.
4. No digit; "than" is a comparison; the rest is fine.

## Code

```text
1 []
2 ['no number', 'no comparison', 'no owner', 'no date', 'fewer than two limitations']
3 ['no comparison', 'no date', 'fewer than two limitations']
4 ['no number']
```

## Complexity

Not applicable (a trace problem).

## Another way

The chapter's full linter accepts both `31 January 2025` and `2025-01-31`: the third finding's "no date" is a limit of this short linter. Linters must be tuned on real drafts.
