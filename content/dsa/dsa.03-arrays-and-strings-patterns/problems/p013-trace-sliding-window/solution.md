## Walkthrough

| r | enters a[r] | leaves a[r-3] | window after | sum | best |
|---|---|---|---|---|---|
| start | | | [4, 2, -1] | 5 | 5 |
| 3 | 3 | 4 | [2, -1, 3] | 5 + 3 - 4 = 4 | 5 |
| 4 | 5 | 2 | [-1, 3, 5] | 4 + 5 - 2 = 7 | 7 |
| 5 | -6 | -1 | [3, 5, -6] | 7 + (-6) - (-1) = 2 | 7 |
| 6 | 1 | 3 | [5, -6, 1] | 2 + 1 - 3 = 0 | 7 |

Check each sum directly: `2 - 1 + 3 = 4`, `-1 + 3 + 5 = 7`, `3 + 5 - 6 = 2`, `5 - 6 + 1 = 0`. They match.

## Output

```
start [4, 2, -1] 5
add 3 remove 4 window [2, -1, 3] sum 4 best 5
add 5 remove 2 window [-1, 3, 5] sum 7 best 7
add -6 remove -1 window [3, 5, -6] sum 2 best 7
add 1 remove 3 window [5, -6, 1] sum 0 best 7
best 7
```

## Key ideas

- An array of `n` elements has `n - k + 1` windows of size `k`: here 5 (one `start` line and four `add` lines).
- Each slide costs two operations, whatever `k` is. That is the whole point of the window.
- The best window is in the middle, so `best` must be tracked; the final `s` is not the answer.
