# Build a tree from postorder and inorder

The inorder and the postorder traversal of a binary tree **with distinct values** also determine the tree. Write `build_from_in_post(inorder_vals, postorder_vals)` (the inorder list comes **first**, as in the chapter) that builds the tree and returns its root. Two empty lists give `None`. Use `TreeNode`. Do not change the two lists you are given.

## Example

```python
>>> t = build_from_in_post([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])
>>> to_level(t)
[3, 9, 20, None, None, 15, 7]
>>> to_level(build_from_in_post([2, 1], [2, 1]))         # 2 is the left child of 1
[1, 2]
>>> to_level(build_from_in_post([1, 2], [2, 1]))         # 2 is the right child of 1
[1, None, 2]
>>> build_from_in_post([], []) is None
True
```

`to_level` is the tests' helper (the chapter's `to_level_list`): the tree as a level-order list with `None` for gaps.

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. `O(n)` time is the goal.

## Think about

In a postorder list the **root comes last**. Read the list from the end: after the root, which subtree's items come next, the left one or the right one? In which order must you therefore build the two subtrees?
