# All subsets

Write `subsets(nums)` that returns all subsets (the **power set**) of the list `nums`, whose items are all different. Each subset is a list. The empty subset `[]` and the whole list are included.

The order of the subsets in your result does not matter, and the order inside a subset does not matter either (the tests sort before comparing). Use backtracking (choose, explore, un-choose); `itertools` is not allowed.

## Example

```python
>>> sorted(subsets([1, 2, 3]))
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
>>> subsets([])
[[]]
```

## Constraints

- `0 <= len(nums) <= 12`, all items different.

## Think about

If you append `path` itself to the result instead of a copy, what will all the subsets look like at the end? (Chapter section 5, "The trap: appending the path itself".)
