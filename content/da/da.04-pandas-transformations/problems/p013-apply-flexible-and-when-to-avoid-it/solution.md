## Approach

The model answer in `answer.md` goes question by question. The core idea: `apply` hides a Python loop over the
groups, so its cost grows with the number of groups. Most uses have a built-in replacement: an aggregation, a
`transform` with built-in names, or sort + `head`. Rate your answer against the checklist at the end of `answer.md`.

## Complexity

Built-in aggregation and transform: compiled passes over the data, O(n). `apply`: O(n) work plus a Python call and a
new object per group, so roughly O(n + g · c) with a large constant c per group.

## Another way

Explain it through the chapter's measurements: on 5,000 groups, `apply(lambda)` was about 15× slower than the built-in
sum and the lambda z-score about 20× slower than the two built-in transforms (machine-specific numbers, the ratios are
what matters).
