## Approach

The boolean subset-sum array becomes a **count** (chapter section 12). `f[s]` = how many subsets of the numbers processed so far have sum `s`. When `x` arrives, the subsets that **skip** `x` keep their sums (`f[s]` stays) and the subsets that **take** `x` are the old subsets with sum `s - x`. So `f[s] += f[s - x]`, and the loop goes downwards so that `f[s - x]` is the count from before `x`.

```python
def count_subsets(nums, target):
    f = [0] * (target + 1)
    f[0] = 1                             # the empty subset
    for x in nums:
        for s in range(target, x - 1, -1):   # downwards: each number once
            f[s] += f[s - x]
    return f[target]
```

**Zeros.** For `x = 0` the range is `target` down to `0`, and `f[s] += f[s - 0]` doubles every count. That is exactly right: every subset can now include the zero or not. `[0, 0, 1]` with target 1 gives 4.

**Empty input.** The loop never runs and `f[target]` is 1 for target 0 (the empty subset), 0 otherwise.

## Complexity

`O(n * target)` time, `O(target)` space.

## Another way

Top-down: `ways(i, s)` = subsets of `nums[i:]` with sum `s`; `ways(i, s) = ways(i + 1, s) + (ways(i + 1, s - nums[i]) if nums[i] <= s)`, with base `ways(n, s) = 1 if s == 0 else 0`. With `functools.cache` it has `n * (target + 1)` states. Note the base case is at **`i == n`** only: a version that returns 1 as soon as `s == 0` forgets the zeros later in the list. Without the cache it is `2**n`.
