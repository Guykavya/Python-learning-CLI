# Find the duplicate number

`nums` has `n + 1` integers, each between `1` and `n` (inclusive). So at least one value appears twice (pigeonhole). Exactly one value is repeated, possibly more than twice. Write `find_duplicate(nums)` that returns it.

Rules:

- do **not** modify `nums` (no sorting, no marking with negative signs);
- `O(1)` extra memory (no set, no counting list, no sorted copy). The tests measure it.

Treat the array as a linked list (chapter section 7, "A cycle hidden in an array"): index `i` is a node and `nums[i]` is its `next`. Index `0` is the head. Then the duplicate value is the **start of a cycle**, and problem 19's two phases find it.

## Example

```python
>>> find_duplicate([1, 3, 4, 2, 2])
2
>>> find_duplicate([3, 1, 3, 4, 2])
3
>>> find_duplicate([2, 2, 2, 2, 2])
2
```

For `[1, 3, 4, 2, 2]`: `0 -> 1 -> 3 -> 2 -> 4 -> 2 -> 4 -> ...`. Index `2` is entered from index `3` and from index `4`: two arrows into one node, the start of the cycle.

## Constraints

- `1 <= n <= 10**5`, `len(nums) == n + 1`, `1 <= nums[i] <= n`.

## Think about

Why can the walk never leave the array? Why is index `0` never inside the cycle? Why do two equal values mean two arrows into the same node?
