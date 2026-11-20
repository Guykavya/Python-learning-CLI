## Hint 1

Round 1 starts with `[0, -, -, -, -, -]`. The first three edges start at 3, 2 and 1, which are still infinite: skip them. Then `(0, 1, 4)` gives `dist[1] = 4`, `(0, 2, 9)` gives `dist[2] = 9`, `(1, 3, 5)` uses the **new** `dist[1] = 4` at once. Continue with the last two edges.

## Hint 2

The last edge of round 1, `(4, 1, -2)`, lowers `dist[1]` from 4 to `1 - 2 = -1`. But the edges that leave vertex 1 were already used in this round with the old value. They will use `-1` only in round 2. That is why the rounds are needed.
