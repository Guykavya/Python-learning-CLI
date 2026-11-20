## Approach

Chapter section 12, "Subset sum". A 0/1 knapsack whose value is yes/no.

- **State:** `f[s]` = True if some subset of the numbers processed so far sums to `s`.
- **Transition:** for a number `x`, `f[s] = f[s] or f[s - x]` ("make `s` without `x`, or make `s - x` and add `x`").
- **Base:** `f[0] = True`, the empty subset.
- **Order:** `s` from high to low, so `f[s - x]` still describes the subsets **without** `x`.

```python
def subset_sum(nums, target):
    f = [False] * (target + 1)
    f[0] = True                              # the empty subset
    for x in nums:
        for s in range(target, x - 1, -1):   # downwards: each number once
            if f[s - x]:
                f[s] = True
    return f[target]
```

For `[3, 4, 5]` and target 9, the reachable sums grow like this:

| after | reachable sums |
|---|---|
| start | 0 |
| 3 | 0, 3 |
| 4 | 0, 3, 4, 7 |
| 5 | 0, 3, 4, 5, 7, 8, 9 |

9 = 4 + 5 is reachable.

## The bonus: a whole row in one integer

```python
def subset_sum_bits(nums, target):
    bits = 1                                 # bit s set = sum s reachable; only 0 at first
    mask = (1 << (target + 1)) - 1           # sums above target are never needed
    for x in nums:
        bits = (bits | (bits << x)) & mask
    return (bits >> target) & 1 == 1
```

`bits << x` shifts every set bit `s` to `s + x`: "every reachable sum, plus `x`". The OR keeps the old sums (without `x`). Because the shift reads the **old** `bits` as a whole, each number is used once, with no loop direction to get wrong. The work is the same `n * target` bit operations, but they happen inside CPython's big-integer code, many bits per machine word, instead of one Python step per cell. That is why it handles `n = 2000`, `target = 10**5` easily while the list version (2 * 10**8 Python steps) would take a minute or more.

## Complexity

List version: `O(n * target)` time, `O(target)` memory. Bit version: `O(n * target / w)` machine operations, where `w` is the number of bits CPython handles per step (30), plus the overhead of creating a new integer each time.

## Another way

A set of reachable sums: `reach = {0}`, then `reach |= {s + x for s in reach if s + x <= target}` for each `x`. It is easy to read and fine when few sums are reachable, but it has a Python-level step per reachable sum, so it is not faster than the list in the worst case.
