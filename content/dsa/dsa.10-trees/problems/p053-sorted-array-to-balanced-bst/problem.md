# Sorted array to a balanced BST

Write `sorted_to_bst(values)` that takes a list of **distinct integers in increasing order** and returns the root of a binary search tree that holds exactly these values and has the **smallest possible height**: at every node the heights of the two subtrees differ by at most 1. An empty list gives `None`. Use `TreeNode`. Do not change the list.

Many shapes are correct (for an even number of values you can lean left or right), so the tests check the **properties**: the inorder traversal equals the list, the tree is a BST, every node is balanced, and the height is the smallest possible (`n.bit_length()` for `n` values).

## Example

```python
>>> t = sorted_to_bst([1, 2, 3, 4, 5, 6, 7])
>>> to_level(t)
[4, 2, 6, 1, 3, 5, 7]
>>> sorted_to_bst([]) is None
True
>>> t = sorted_to_bst([10, 20])
>>> t.val in (10, 20) and (t.left is None) != (t.right is None)
True
```

`to_level` is the tests' helper (the chapter's `to_level_list`): the tree as a level-order list with `None` for gaps.

## Constraints

- Up to a few thousand values. `O(n)` time.

## Think about

Chapter section 11: which value becomes the root so that the two halves are as equal as possible? What are the left and right subtrees? Why does this build a **valid BST**, not only a balanced tree?
