## Walkthrough

First list:

| x | cur + x | x alone | new cur | best |
|---|---|---|---|---|
| 2 | (first) | 2 | 2 | 2 |
| -3 | -1 | -3 | -1 | 2 |
| 4 | 3 | 4 | 4 (fresh) | 4 |
| -1 | 3 | -1 | 3 | 4 |
| 2 | 5 | 2 | 5 | 5 |
| -5 | 0 | -5 | 0 | 5 |
| 3 | 3 | 3 | 3 (tie) | 5 |

The answer 5 comes from the run that started fresh at 4 and ended at 2: `4 -1 2`.

Second list:

| x | cur + x | x alone | new cur | best |
|---|---|---|---|---|
| -4 | (first) | -4 | -4 | -4 |
| -2 | -6 | -2 | -2 (fresh) | -2 |
| -7 | -9 | -7 | -7 (fresh) | -2 |

## Output

```
-- [2, -3, 4, -1, 2, -5, 3]
2 2 2
-3 -1 2
4 4 4
-1 3 4
2 5 5
-5 0 5
3 3 5
answer 5
-- [-4, -2, -7]
-4 -4 -4
-2 -2 -2
-7 -7 -2
answer -2
```

## Key ideas

- `cur` starts fresh exactly when the old `cur` is negative: then `cur + x < x`.
- `best` never goes down. `cur` can.
- With all negatives, every step starts fresh and the answer is the largest element. Starting at `a[0]` (not 0) makes
  that work.
