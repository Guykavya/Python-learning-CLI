## Approach

**The reduction.** Every smash replaces `x` and `y` by `y - x`. Unroll the whole game and the last stone is a sum of all the original weights, each with a `+` or `-`: the stones split into a plus-group `A` and a minus-group `B`, and the result is `sum(A) - sum(B)`. Conversely, for any split into two groups you can reach `|sum(A) - sum(B)|`: smash a stone of the heavier group against a stone of the lighter group, and the leftover piece stays in its group. So:

> smallest last stone = smallest `|sum(A) - sum(B)|` over all ways to split the stones in two groups.

That is the **minimum subset difference** problem. If one group sums to `s <= total / 2`, the difference is `total - 2s`, so we want the **largest reachable `s` not above `total // 2`**. Subset sum (chapter section 12) tells us every reachable `s` at once.

```python
def last_stone_weight_ii(stones):
    total = sum(stones)
    half = total // 2
    f = [False] * (half + 1)
    f[0] = True
    for x in stones:
        for s in range(half, x - 1, -1):     # downwards: each stone once
            if f[s - x]:
                f[s] = True
    for s in range(half, -1, -1):            # largest reachable sum <= half
        if f[s]:
            return total - 2 * s
    return total                             # never reached: f[0] is True
```

`[2, 7, 4, 1, 8, 1]`: total 23, half 11. 11 is reachable (`2 + 8 + 1`), so the answer is `23 - 22 = 1`.

## Complexity

`O(n * total)` time, `O(total)` space: at most `100 * 5,000` steps.

## Another way

Use the bitset of chapter section 12: `bits = 1`, `bits |= bits << x` for each stone, then scan `s` from `half` down for the first set bit. Or keep a Python `set` of reachable sums and grow it stone by stone (`sums |= {s + x for s in sums}`); simple, and still bounded by `total + 1` different sums.

The game itself is a fine **brute force** for very small inputs (a memo on the sorted tuple of remaining stones), and the tests use it to check the reduction. It is exponential in the number of stones.
