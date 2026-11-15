# Partition into k equal-sum subsets

Write `can_partition_k(nums, k)` that returns `True` if the list of positive integers `nums` can be split into `k` groups (every number in exactly one group, groups non-empty) that all have the **same sum**, and `False` otherwise.

## Example

```python
>>> can_partition_k([4, 3, 2, 3, 5, 2, 1], 4)
True
>>> can_partition_k([1, 2, 3, 4], 3)
False
```

In the first example the groups can be `[5]`, `[1, 4]`, `[2, 3]`, `[2, 3]`, each with sum 5.

## Constraints

- `1 <= k <= len(nums) <= 16`, `1 <= nums[i] <= 10000`.
- One test is a 16-number input with no answer. A search with no pruning tries millions of placements; yours must finish in a few seconds.

## Think about

Put the numbers into `k` buckets one by one, each bucket with capacity `sum(nums) // k`. Three prunings make it fast (chapter section 9):

1. Quick checks: the total must be divisible by `k`, and no number may be larger than one bucket.
2. Place the **largest** numbers first (sort descending): big numbers fail early, high in the tree.
3. If two buckets hold the same sum right now, putting the number in either one leads to the same future. Try only one of them.
