## Approach

The "ends exactly here" state of section 5 (maximum subarray):

- Sort by the first value. A pair that can precede `(c, d)` has `b < c`, hence `a < c`, so it sorts earlier. Pairs with the same first value can never be in one chain, so ties do not matter.
- **State:** `f[i]` = the longest chain that ends with `pairs[i]`.
- **Transition:** `f[i] = 1 + max(f[j])` over `j < i` with `pairs[j][1] < pairs[i][0]`; just `1` if there is none.
- **Answer:** `max(f)`, because the best chain may end with any pair; `0` for no pairs.

```python
def longest_chain(pairs):
    pairs = sorted(pairs)                 # by first value: a predecessor always comes earlier
    n = len(pairs)
    f = [1] * n                           # f[i] = longest chain that ENDS with pairs[i]
    for i in range(n):
        for j in range(i):
            if pairs[j][1] < pairs[i][0] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f) if f else 0
```

Trace `[(5,24), (39,60), (15,28), (27,40), (50,90)]`. Sorted: `(5,24) (15,28) (27,40) (39,60) (50,90)`. `f = [1, 1, 2, 2, 3]`: `(27,40)` follows `(5,24)`; `(39,60)` follows `(5,24)` or `(15,28)`; `(50,90)` follows `(27,40)` (24 < 27, then 40 < 50). Answer 3.

A deeper look: here `f[-1]` always equals `max(f)`. The last sorted pair has the largest start, so it can follow every pair that the last pair of the best chain follows: swap that last pair for it and the chain keeps its length. Do not rely on that kind of luck: in most "ends at `i`" DPs (maximum subarray, LIS) the answer really is `max(f)`, so write `max(f)` by habit.

## Complexity

`O(n^2)` time (plus `O(n log n)` for the sort), `O(n)` space.

## Another way

This is the activity selection of dsa.13 in disguise: sort by the **second** value and greedily take every pair that starts after the last taken end. That is `O(n log n)` and the tests use it as an independent check on big inputs. The DP is slower, but it needs no exchange argument, and it still works when the pairs have **weights** and you want the heaviest chain (`f[i] = w[i] + max f[j]`), where the greedy fails.
