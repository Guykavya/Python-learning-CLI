# Count subsets with a given sum

Write `count_subsets(nums, target)` that returns **how many** subsets of `nums` add up to `target`. All numbers are positive. Subsets are counted by **position**: `[1, 1]` with target 1 has two subsets (the first 1 or the second 1).

The empty subset has sum 0; since all numbers are positive, it is the only subset with sum 0.

## Example

```python
>>> count_subsets([1, 2, 3, 4, 5], 5)
3
>>> count_subsets([1, 1], 1)
2
>>> count_subsets([2, 4], 0)
1
```

The three subsets in the first example are `[5]`, `[1, 4]` and `[2, 3]`.

## Constraints

- `0 <= len(nums) <= 20`, `1 <= nums[i] <= 1000`, `0 <= target <= 20000`.
- Twenty items have about a million subsets; plain include/exclude recursion takes a second or two. Pruning (chapter section 9) makes it much faster.

## Think about

Since every number is positive: what can you conclude when the remaining target is already 0? When it is negative?
