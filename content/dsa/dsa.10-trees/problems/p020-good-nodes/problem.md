# Good nodes

On the path from the root down to a node, call a node **good** if no node **before** it on that path (no ancestor) has a larger value. The root is always good. A node with the same value as the largest ancestor is good too (nobody is larger).

Write `count_good_nodes(root)` that returns how many nodes of the tree are good. An empty tree gives `0`. Values may be negative.

## Example

```python
>>> count_good_nodes(build([3, 1, 4, 3, None, 1, 5]))
4
>>> count_good_nodes(build([3, 3, None, 4, 2]))
3
>>> count_good_nodes(build([-1, -5, -3]))          # only the root is good: -5 and -3 are smaller than -1
1
>>> count_good_nodes(None)
0
```

In the first tree the good nodes are `3` (the root), `4`, the `3` below the `1` (it equals the maximum `3` so far), and `5`. The two `1`s are not good.

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

What does a node need to know from above to decide whether it is good? That is information traveling **down** (chapter section 3), not up: so it becomes a parameter. What should its initial value be so that the root is always good, even when its value is negative?
