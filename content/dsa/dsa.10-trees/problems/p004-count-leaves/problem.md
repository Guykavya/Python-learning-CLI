# Count leaves

A **leaf** is a node with no children at all (no left and no right child). Write `count_leaves(root)` that returns the number of leaves in the tree. An empty tree has 0 leaves.

## Example

```python
>>> count_leaves(build([4, 2, 6, 1, 3, 5, 7]))
4
>>> count_leaves(build([1, 2]))       # the root has one child, so it is not a leaf; only 2 is
1
>>> count_leaves(build([5]))          # a single node is a leaf
1
>>> count_leaves(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

Why does this function need **two** base cases, while `size` needed one? What would the function return for every tree if you wrote only the `None` case?
