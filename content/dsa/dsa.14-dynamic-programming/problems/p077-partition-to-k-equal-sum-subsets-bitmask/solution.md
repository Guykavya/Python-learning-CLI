## Approach

Fill the `k` groups one after another. The key observation is the one from chapter section 19, "Assigning tasks": remove every piece of information that can be computed from the rest.

- The set `mask` of placed numbers fixes their sum `S`.
- All finished groups hold exactly `target`, so the current group holds `S % target`, and the number of finished groups is `S // target`.

So the state is just `mask`, and `2**n` states replace the `k**n` ways to give each number a group.

- **State:** `fill[mask]` = how full the current group is, or `-1` if the numbers in `mask` cannot be placed this way.
- **Transition:** add a number `i` not in `mask`, if it fits: `fill[mask | 1 << i] = (fill[mask] + nums[i]) % target`. When a group reaches `target` exactly, `% target` turns it into 0: a new empty group starts.
- **Base:** `fill[0] = 0`.
- **Answer:** `fill[full] == 0`.

```python
def can_split(nums, k):
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    if max(nums) > target:
        return False
    n = len(nums)
    fill = [-1] * (1 << n)          # fill[mask]: how full the current group is; -1 = unreachable
    fill[0] = 0
    for mask in range(1 << n):
        here = fill[mask]
        if here == -1:
            continue
        for i in range(n):
            if not mask >> i & 1 and here + nums[i] <= target:
                fill[mask | (1 << i)] = (here + nums[i]) % target
    return fill[(1 << n) - 1] == 0
```

Why storing one fill value per mask is safe: any two ways of reaching the same `mask` placed the same numbers, so they have the same sum and therefore the same fill. There is nothing to choose between, and overwriting is harmless.

`[2, 2, 2, 2, 3, 4, 5]` with `k = 4` (target 5): the 5 makes a group alone, and 3 and 4 each need a partner of 2 or 1. 3 + 2 works, but 4 needs a 1, which does not exist. Every way to fill the masks gets stuck, so the full mask is never reached.

## Complexity

`O(2**n * n)` time and `O(2**n)` memory: about a million steps for `n = 16`. Backtracking (dsa.07) is `O(k**n)` in the worst case, about 4.3 billion assignments for `n = 16`, `k = 4`, unless it prunes well.

## Another way

Backtracking with strong pruning: sort `nums` in decreasing order, put each number into a group, skip a group whose current sum equals that of a group already tried (they are interchangeable), and stop as soon as one group would overflow. It is often fast in practice, but its worst case is still exponential in a worse way, and the "same sum" pruning is easy to get wrong. The mask DP's running time does not depend on the numbers at all.
