## Approach

Sort by the key, then move the window edge by edge, counting steps; after each question the window is exactly its range.

## Expected output

```text
order: [2, 0, 3, 4, 1]
q2 [1,3): moves 4, distinct 2
q0 [0,4): moves 2, distinct 3
q3 [2,7): moves 5, distinct 3
q4 [4,6): moves 3, distinct 2
q1 [5,8): moves 3, distinct 2
total moves: 17
```

## Why

| question | window before | moves | window values | distinct |
|---|---|---|---|---|
| q2 `[1,3)` | `[0,0)` | right +3, left +1: 4 | `1, 3` | 2 |
| q0 `[0,4)` | `[1,3)` | left -1, right +1: 2 | `3, 1, 3, 2` | 3 |
| q3 `[2,7)` | `[0,4)` | right +3, left +2: 5 | `3, 2, 1, 3, 2` | 3 |
| q4 `[4,6)` | `[2,7)` | left +2, right -1: 3 | `1, 3` | 2 |
| q1 `[5,8)` | `[4,6)` | right +2, left +1: 3 | `3, 2, 2` | 2 |

**After you answer.**

1. In input order the steps are `4, 9, 9, 5, 3`: q0 needs 4 (grow right to 4); q1 `[5,8)` needs 9 (grow right by 4, shrink left by 5); q2 `[1,3)` needs 9 (grow left by 4, shrink right by 5); q3 needs 5 and q4 needs 3. That is 30 steps against 17: the sorted order saves almost half even on 8 elements.
2. Within block 0 the questions are sorted by `r`: 3, 4, 7. So the right edge only grows.
3. Shrinking before growing goes wrong when the new range lies entirely to the right of the window. In input order, going from q0 `[0,4)` to q1 `[5,8)` and shrinking the left edge first would move `cur_l` from 0 to 5 and "remove" position 4, which was never in the window: its count would drop to -1. Growing the right edge to 8 first keeps `cur_l <= cur_r` at every step.

## Another way

Write the moves as distances: a question costs `|l - cur_l| + |r - cur_r|`. Summing these for any order gives the total without simulating the counts.
