## Approach

Include/exclude recursion that **returns a count**: the count of a node is the sum of the counts of its two children. Because every number is positive, a remaining target of 0 means exactly one completion (leave out the rest), and a negative remaining target means none.

## Code

```python
def count_subsets(nums, target):
    def go(i, remaining):
        if remaining == 0:
            return 1
        if remaining < 0 or i == len(nums):
            return 0
        return go(i + 1, remaining - nums[i]) + go(i + 1, remaining)

    return go(0, target)
```

## Complexity

At most `2^(n+1)` calls, `O(2^n)` time and depth `n`. Pruning cuts many branches but does not change the worst case.

## Another way

Many branches reach the **same** state `(i, remaining)`. Memoising on that pair (or a table `ways[s]` filled item by item) gives `O(n * target)` time: that is dynamic programming (chapter section 17).

```python
def count_subsets(nums, target):
    ways = [1] + [0] * target
    for x in nums:
        for s in range(target, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[target]
```
