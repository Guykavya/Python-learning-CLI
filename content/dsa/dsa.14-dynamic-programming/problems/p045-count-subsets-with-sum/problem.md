# Count subsets with sum

Write `count_subsets(nums, target)` that returns **how many subsets** of `nums` have sum exactly `target` (chapter section 12, "Counting subsets with a given sum"). Subsets are chosen by **position**: two equal numbers at different positions are different items, and the empty subset counts (it has sum 0).

## Example

```python
>>> count_subsets([1, 2, 3, 3], 6)    # {1,2,3a}, {1,2,3b}, {3a,3b}
3
>>> count_subsets([0, 0, 1], 1)       # {1}, {0a,1}, {0b,1}, {0a,0b,1}
4
>>> count_subsets([2, 4], 0)          # only the empty subset
1
>>> count_subsets([0, 0], 0)          # {}, {0a}, {0b}, {0a,0b}
4
>>> count_subsets([5], 3)
0
```

## Constraints

- `0 <= len(nums) <= 200`, `0 <= nums[i] <= 50`, `0 <= target <= 1000`.
- Return the exact count (Python integers do not overflow; the answer can be huge).
- Time `O(n * target)`. Listing every subset does not finish for `n = 200`.

## Think about

How is this different from the boolean subset sum? What does the update `f[s] += f[s - x]` mean in words? What does it do when `x = 0`?
