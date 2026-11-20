# Validate a BST

Write `is_valid_bst(root)` that returns `True` if the binary tree is a valid binary search tree: for **every** node, all values in its left subtree are **strictly smaller** and all values in its right subtree are **strictly larger**. An empty tree is valid. Duplicate values make a tree invalid.

The values can be any integers, also very large or very small ones (the tests use `-2147483648`, `2147483647` and even `2 ** 70`).

## Example

```python
>>> is_valid_bst(build([4, 2, 6, 1, 3, 5, 7]))
True
>>> is_valid_bst(build([5, 1, 6, None, None, 3, 7]))      # 3 is in the right subtree of 5, but 3 < 5
False
>>> is_valid_bst(build([2, 2, 2]))                        # duplicates
False
>>> is_valid_bst(None)
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few hundred nodes in a chain, or thousands in a bushy tree. `O(n)` time.

## Think about

Chapter section 9 shows the classic wrong idea: compare every node only with its two children. Look at `[5, 1, 6, None, None, 3, 7]`: every node is fine against its parent, and the tree is still invalid. What does a node have to be compared with? Which numbers do you pass down the recursion to remember it? How do you say "no bound yet" without a sentinel number that some tree could reach?
