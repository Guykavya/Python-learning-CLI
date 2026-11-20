# Zigzag level order

Write `zigzag(root)` that returns the levels like `level_order`, but the direction **alternates**: the first level (the root) goes left to right, the second right to left, the third left to right again, and so on. An empty tree gives `[]`.

## Example

```python
>>> zigzag(build([1, 2, 3, 4, 5, 6, 7]))
[[1], [3, 2], [4, 5, 6, 7]]
>>> zigzag(build([3, 9, 20, None, None, 15, 7]))
[[3], [20, 9], [15, 7]]
>>> zigzag(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

Do you need to change the order in which nodes enter the queue, or only the order in which a finished level is written down? Which is simpler and safer?
