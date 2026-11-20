# Level order

Write `level_order(root)` that returns the values level by level: a list of lists. The first list is the root, the second the nodes of depth 1 from left to right, and so on. For an empty tree return `[]` (an empty list, not `[[]]`).

## Example

```python
>>> level_order(build([3, 9, 20, None, None, 15, 7]))
[[3], [9, 20], [15, 7]]
>>> level_order(build([1, None, 2, 3]))
[[1], [2], [3]]
>>> level_order(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time, `O(w)` extra memory (`w` is the width of the widest level).

## Think about

How do you know where one level ends and the next begins? (Chapter section 6: read `len(queue)` **before** you start the level.)
