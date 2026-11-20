## Approach

Count with a formula instead of drawing the tree. For the naive version `C(0) = C(1) = 1` and `C(n) = 1 + C(n - 1) + C(n - 2)`. For the memo version, separate **misses** (the body does the real work and stores a new key) from **hits** (the body counts, finds the key, returns at once).

## Expected output

```text
naive 0 0 1
naive 1 1 1
naive 2 1 3
naive 3 2 5
naive 4 3 9
naive 5 5 15
naive 6 8 25
memo 8 11 7
again 8 1 7
next 13 3 8
```

## Why

| n | `fib(n)` | `C(n) = 1 + C(n-1) + C(n-2)` |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 2 | 1 | 1 + 1 + 1 = 3 |
| 3 | 2 | 1 + 3 + 1 = 5 |
| 4 | 3 | 1 + 5 + 3 = 9 |
| 5 | 5 | 1 + 9 + 5 = 15 |
| 6 | 8 | 1 + 15 + 9 = 25 |

`fib_memo(6)` on an empty notebook: misses for `6, 5, 4, 3, 2, 1, 0` (7 calls, 7 keys stored), and hits for the right-hand calls `fib_memo(1)` (asked by 3), `fib_memo(2)` (by 4), `fib_memo(3)` (by 5), `fib_memo(4)` (by 6): 4 calls. Total 11, notebook size 7.

`again`: one call, a hit. `next`: `fib_memo(7)` is a miss (1), it asks `fib_memo(6)` (hit) and `fib_memo(5)` (hit): 3 calls, and key 7 is added: 8 keys.

Answers to the questions: `2 * F(7) - 1 = 2 * 13 - 1 = 25`, yes. For `n >= 2` there are `n + 1` misses (keys `0..n`) and `n - 2` hits (the right-hand calls of `n, n-1, ..., 3`), so `2n - 1` calls: for `n = 25` that is 49, as in chapter section 1.

## Another way

Draw the naive tree for `fib(4)` (9 nodes) and colour every repeated subtree. Then draw the memo version as a chain with one extra short arrow per node. The 25 versus 11 gap grows fast: for `n = 25` it is 242785 versus 49.
