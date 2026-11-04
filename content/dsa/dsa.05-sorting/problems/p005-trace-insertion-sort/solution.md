## Approach

Simulate round by round. The sorted prefix grows by one element per round; the key travels left past every larger element.

## Expected output

```text
i = 1 key = 3 [3, 4, 2, 10, 12, 1] shifts so far 1
i = 2 key = 2 [2, 3, 4, 10, 12, 1] shifts so far 3
i = 3 key = 10 [2, 3, 4, 10, 12, 1] shifts so far 3
i = 4 key = 12 [2, 3, 4, 10, 12, 1] shifts so far 3
i = 5 key = 1 [1, 2, 3, 4, 10, 12] shifts so far 8
[1, 2, 3, 4, 10, 12]
```

## Why

Shifts per round: 1, 2, 0, 0, 5, total 8. That equals the inversion count of `[4, 3, 2, 10, 12, 1]`. Rounds with key 10 and 12 cost nothing because they were already in the right place, which is why insertion sort is fast on nearly sorted data.
