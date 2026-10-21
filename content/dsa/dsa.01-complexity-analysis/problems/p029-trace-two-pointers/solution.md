## Walkthrough, first part

| i | a[i] | j before | j after | values j moved past | inner | pairs added | pairs |
|---|---|---|---|---|---|---|---|
| 0 | 1 | 0 | 3 | 1, 2, 4 | 3 | 2 | 2 |
| 1 | 2 | 3 | 3 | none (7 - 2 = 5) | 3 | 1 | 3 |
| 2 | 4 | 3 | 4 | 7 | 4 | 1 | 4 |
| 3 | 7 | 4 | 5 | 8 | 5 | 1 | 5 |
| 4 | 8 | 5 | 6 | 11 | 6 | 1 | 6 |
| 5 | 11 | 6 | 6 | none (15 - 11 = 4) | 6 | 0 | 6 |
| 6 | 15 | 6 | 8 | 15, 16 | 8 | 1 | 7 |
| 7 | 16 | 8 | 8 | none (end) | 8 | 0 | 7 |

The pairs are (1, 2), (1, 4), (2, 4), (4, 7), (7, 8), (8, 11), (15, 16).

## Second part

For each `i`, the loop counts `j = i, i + 1, ...` while the difference is below 4: 3, 2, 2, 2, 2, 1, 2, 1. Total 15.

Output:

```
inner 8
pairs 7
inner with reset 15
```

## Key idea

1. In the first part `j` only moves forward and stops at `n`, so across the **whole** program the `while` body runs at
   most `n` times. The `for` loop adds `n` more steps. Total O(n), even though a loop sits inside a loop. This is an
   amortised argument: one `i` may move `j` a lot, but the total movement is bounded.
2. The second part restarts `j` at `i`, so its cost depends on the data. If `k` is larger than every difference (say
   all values are equal, or `k = 10^9`), every `i` scans to the end: `n + (n - 1) + ... + 1`, O(n^2).

This "two pointers that only move forward" pattern is the heart of many O(n) algorithms in dsa.03.
