# Minimum depth

The **minimum depth** is the number of nodes on the shortest path from the root down to a **leaf**. A leaf is a node with no children at all. An empty tree has minimum depth `0`.

A node with only one child is **not** a leaf: its missing child is not the end of a path.

## Example

```python
>>> min_depth(build([3, 9, 20, None, None, 15, 7]))    # 3 -> 9
2
>>> min_depth(build([1, None, 2, None, 3]))            # the only leaf is 3
3
>>> min_depth(build([5]))
1
>>> min_depth(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

Why does `1 + min(min_depth(left), min_depth(right))` give the wrong answer for `[1, None, 2, None, 3]`? What does `min_depth(None) = 0` do to the `min`?
