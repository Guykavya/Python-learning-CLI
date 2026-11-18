## Approach

Fill the boxes left to right; for each amount list `f[a - c] + 1` for the coins that fit, in coin order. Keep the first strict minimum in `last`.

## Expected output

```text
a=1 tried=[1] f[a]=1 last=1
a=2 tried=[2] f[a]=2 last=1
a=3 tried=[3, 1] f[a]=1 last=3
a=4 tried=[2, 2, 1] f[a]=1 last=4
a=5 tried=[2, 3, 2] f[a]=2 last=1
a=6 tried=[3, 2, 3] f[a]=2 last=3
table: [0, 1, 2, 1, 1, 2, 2]
coins used: [3, 3]
answer: 2
```

## Why

| a | coin 1: `f[a-1]+1` | coin 3: `f[a-3]+1` | coin 4: `f[a-4]+1` | `f[a]` | `last[a]` |
|---|---|---|---|---|---|
| 1 | f[0]+1 = 1 | | | 1 | 1 |
| 2 | f[1]+1 = 2 | | | 2 | 1 |
| 3 | f[2]+1 = 3 | f[0]+1 = 1 | | 1 | 3 |
| 4 | f[3]+1 = 2 | f[1]+1 = 2 | f[0]+1 = 1 | 1 | 4 |
| 5 | f[4]+1 = 2 | f[2]+1 = 3 | f[1]+1 = 2 | 2 | 1 |
| 6 | f[5]+1 = 3 | f[3]+1 = 2 | f[2]+1 = 3 | 2 | 3 |

At `a = 5` coin 1 and coin 4 both give 2. Coin 1 came first and set `f[5] = 2`; coin 4's `2 < 2` is False, so `last[5]` stays 1 (both `4 + 1` and `1 + 4` are optimal).

The walk back: `last[6] = 3`, go to 3; `last[3] = 3`, go to 0. Coins `[3, 3]`, two of them, which matches `f[6] = 2`.

**After you answer.** Greedy takes 4, then 1, then 1: three coins, one more than the DP. With `<=` the last tying coin would win: only `last[5]` changes (to 4), and `coins used` is still `[3, 3]` because the walk from 6 never visits 5.

## Another way

Think of the amounts as nodes 0..6 and each coin as an edge `a - c -> a`. `f[a]` is the shortest path (in edges) from 0 to `a`, and `last` is the BFS parent pointer from dsa.10. The walk back is the usual "follow the parents" loop.
