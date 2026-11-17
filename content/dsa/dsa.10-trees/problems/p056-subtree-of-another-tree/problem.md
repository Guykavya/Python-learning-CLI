# Subtree of another tree

Write `is_subtree(root, sub)` that returns `True` if some node of the tree `root` is the start of a subtree that is **exactly the same** as the tree `sub`: the same shape and the same values, **all the way down to the leaves** of that part of `root`. A tree that only matches the *top* of a bigger subtree does not count. The empty tree `sub` is a subtree of every tree, including the empty tree. An empty `root` has no subtree that is not empty.

## Example

```python
>>> is_subtree(build([3, 4, 5, 1, 2]), build([4, 1, 2]))
True
>>> is_subtree(build([3, 4, 5, 1, 2, None, None, None, None, 0]), build([4, 1, 2]))   # 2 has a child 0 here
False
>>> is_subtree(build([12]), build([2]))
False
>>> is_subtree(build([1, 2]), None), is_subtree(None, build([1]))
(True, False)
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n * m)` time is fine (`n` nodes in `root`, `m` in `sub`).

## Think about

Chapter section 12: try `same_tree` at every node. What do you return if `sub` is empty? If `root` is empty and `sub` is not? Why is a tree with a **longer** branch below a matching node not a match?
