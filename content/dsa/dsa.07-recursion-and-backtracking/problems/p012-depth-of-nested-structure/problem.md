# Depth of a nested structure

Write `depth(xs)` that returns how deeply the list `xs` is nested:

- a list with no lists inside has depth **1** (this includes the empty list `[]`);
- otherwise the depth is 1 plus the largest depth among the inner lists.

Only `list` objects count as levels; strings, tuples and numbers are plain values.

## Example

```python
>>> depth([])
1
>>> depth([1, 2, 3])
1
>>> depth([1, [2, [3]], 4])
3
>>> depth([[], [[]]])
3
```

## Constraints

- The depth is at most 100. Do not change `xs`.

## Think about

`[[], [[]]]` has two inner lists: `[]` with depth 1 and `[[]]` with depth 2. Which one decides the answer?
