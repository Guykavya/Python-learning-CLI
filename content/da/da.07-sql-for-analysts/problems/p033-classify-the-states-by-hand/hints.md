## Hint 1

Write the users' active months in a small grid (users 1 to 4, months 1 to 4). For each active cell decide new / retained / resurrected from the cell to its left. For each empty cell that has an active cell to its left, the state is churned.

## Hint 2

```text
user 1: active 1 2 3 4         -> new, retained, retained, retained
user 2: active 1 . 3 .         -> new, churned (m2), resurrected (m3), churned (m4)
user 3: active . 2 . 4         -> new (m2), churned (m3), resurrected (m4)
user 4: active . . 3 .         -> new (m3), churned (m4)
per month: count each state; the last line = new + retained + resurrected per month
```
