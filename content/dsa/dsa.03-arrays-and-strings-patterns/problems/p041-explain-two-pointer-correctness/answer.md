**1. Too small.** If `a[i] + a[j] < target`, then for every `k` with `i < k <= j` we have `a[k] <= a[j]`
(the array is sorted), so `a[i] + a[k] <= a[i] + a[j] < target`. The largest partner still in play is not
enough, so no partner in play is enough. `a[i]` belongs to no remaining pair and can be thrown away: `i += 1`.

**2. Too big.** If `a[i] + a[j] > target`, then every `k` with `i <= k < j` has `a[k] >= a[i]`, so
`a[k] + a[j] >= a[i] + a[j] > target`. Even the smallest partner is too big, so `a[j]` belongs to no remaining
pair: `j -= 1`.

**3. Invariant.** "If some pair `(p, q)` with `p < q` and `a[p] + a[q] = target` exists, then `i <= p` and
`q <= j`." It is true at the start (`i = 0`, `j = n - 1`). Step 1 moves `i` only when `a[i]` is in no remaining
pair, so `i` never moves past `p`: when `i == p`, the sum is `a[p] + a[j] >= a[p] + a[q] = target`, so the
"too small" branch cannot run. In the same way `j` never moves below `q`. Each pass shrinks the gap `j - i` by 1,
so the loop must end, and it can only end at `i == j` if no solution existed: with a solution, the pointers
are trapped at `i <= p < q <= j` and the loop stops at a pair with the right sum.

**4. Example.** `a = [1, 3, 4, 6, 8, 11]`, `target = 10`:

```
0 5 12 j-1
0 4 9 i+1
1 4 11 j-1
1 3 9 i+1
2 3 10 found
```

It returns `(2, 3)`, the values 4 and 6. The pair `(0, 1)` (1 + 3 = 4) was never checked: at the second step
`1 + 8 = 9 < 10` proved that 1 is too small even with 8, so it is too small with 3 as well.

**5. Breaks.** Unsorted `[1, 9, 5, 4]`, `target = 9` (the pair 5 + 4): `1 + 4 = 5 < 9`, `i += 1`;
`9 + 4 = 13 > 9`, `j -= 1`; `9 + 5 = 14 > 9`, `j -= 1`; now `i == j`, stop. The pair is missed, because `a[j]` is no
longer "the largest value in play", so the "too small" step threw away 1 for a wrong reason and the "too big"
steps threw away 4 and then 5. Duplicates change nothing: the proof only used `<=`, so
`[2, 2, 3]`, `target = 4` gives `2 + 3 = 5 > 4`, `j -= 1`, then `2 + 2 = 4` found.

**6. Cost.** Every pass either returns or moves one pointer inward, and the gap `j - i` starts at `n - 1`, so
there are at most `n - 1` passes: O(n). If the array is unsorted, sorting first costs O(n log n), which then
dominates. (A hash set gives O(n) without sorting, but uses O(n) extra memory.)

**Common traps.** Saying "it works because the array is sorted" without saying **which** comparison the
sorting guarantees. Forgetting that the argument is about pairs still in play, not about all pairs.
