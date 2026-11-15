## Approach

Include/exclude recursion on an index, carrying the remaining target. A remaining target of 0 is a success right away (leave out every undecided item). Combining the two branches with `or` returns as soon as one of them succeeds, so the rest of the tree is never visited.
With negative numbers you may **not** prune on `remaining < 0`: a later negative number could bring it back to 0.

## Code

```python
def has_subset_sum(nums, target):
    def go(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums):
            return False
        return go(i + 1, remaining - nums[i]) or go(i + 1, remaining)

    return go(0, target)
```

## Complexity

`O(2^n)` calls in the worst case (when the answer is `False`), depth `n`. When an answer exists it is often found after very few calls.

## Another way

Keep the set of all reachable sums: start with `{0}` and for each number add `s + x` for every `s`. That is `O(n * number of distinct sums)`, very fast when the numbers are small.
