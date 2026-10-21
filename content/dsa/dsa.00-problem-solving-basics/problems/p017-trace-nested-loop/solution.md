## Walkthrough

One row per run of the inner loop body. `count` is reset to 0 each time `i` changes.

| i | j | count after | i * j | total after | printed |
|---|---|---|---|---|---|
| 1 | 0 | 1 | 0 | 0 | `1 0` |
| 1 | (inner done) | 1 | | 0 | `row 1 count 1` |
| 2 | 0 | 1 | 0 | 0 | `2 0` |
| 2 | 1 | 2 | 2 | 2 | `2 1` |
| 2 | (inner done) | 2 | | 2 | `row 2 count 2` |
| 3 | 0 | 1 | 0 | 2 | `3 0` |
| 3 | 1 | 2 | 3 | 5 | `3 1` |
| 3 | 2 | 3 | 6 | 11 | `3 2` |
| 3 | (inner done) | 3 | | 11 | `row 3 count 3` |
| (outer done) | | | | 11 | `total 11` |

So the output is:

```
1 0
row 1 count 1
2 0
2 1
row 2 count 2
3 0
3 1
3 2
row 3 count 3
total 11
```

## Key idea

In a nested loop the inner loop runs **completely** for every single value of the outer
variable. When the inner range depends on the outer variable (`range(i)`), the inner loop
runs a different number of times in each round: 1, then 2, then 3, for 6 inner runs in total.
A variable set to 0 inside the outer loop (`count`) restarts every round; a variable set
before both loops (`total`) keeps growing across all rounds.
