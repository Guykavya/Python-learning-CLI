# Build a tree from preorder and inorder

The preorder and the inorder traversal of a binary tree **with distinct values** together determine the tree (chapter section 11). Write `build_from_pre_in(preorder_vals, inorder_vals)` that builds that tree and returns its root. Two empty lists give `None`. Use `TreeNode`. Do not change the two lists you are given.

## Example

```python
>>> t = build_from_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
>>> to_level(t)
[3, 9, 20, None, None, 15, 7]
>>> to_level(build_from_pre_in([1, 2], [2, 1]))          # 2 is the left child
[1, 2]
>>> to_level(build_from_pre_in([1, 2], [1, 2]))          # 2 is the right child
[1, None, 2]
>>> build_from_pre_in([], []) is None
True
```

`to_level` is the tests' helper (the chapter's `to_level_list`): the tree as a level-order list with `None` for gaps.

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. `O(n)` time is the goal (a dictionary from value to inorder index); the tests do not time you, but they check the result by walking the new tree again.

## Think about

Which value is the root? Where is it in the inorder list, and what does everything to its left and to its right belong to? Why must the left subtree be built **before** the right one when you read the preorder from the front?
