# Height of a tree

Write `height(root)` that returns the height of the tree, **counted in nodes**: the number of nodes on the longest path from the root down to a leaf. This is the convention of the chapter (section 1):

- an empty tree (`None`) has height `0`,
- a single node has height `1`,
- a root with two leaf children has height `2`.

(Some books count edges, so a single node has height 0 and an empty tree has height -1. Here we do not.)

## Example

```python
>>> height(build([4, 2, 6, 1, 3, 5, 7]))
3
>>> height(build([1, None, 2, None, 3]))
3
>>> height(build([9]))
1
>>> height(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes; the tests keep the depth below the recursion limit. `O(n)` time.

## Think about

Why does the answer for a node use `max` of the two subtrees and not their sum?
