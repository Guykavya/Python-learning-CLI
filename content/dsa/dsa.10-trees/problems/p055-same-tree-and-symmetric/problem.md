# Same tree? Symmetric tree?

Write two functions (chapter section 12):

- `same_tree(a, b)` returns `True` if the trees `a` and `b` have the **same shape and the same values** at every position. Two empty trees are the same; an empty tree and a non-empty one are not.
- `is_symmetric(root)` returns `True` if the tree is a **mirror image of itself**: its left subtree is the mirror image of its right subtree (compare the left side of one with the right side of the other). An empty tree is symmetric.

Do not change the trees.

## Example

```python
>>> same_tree(build([1, 2, 3]), build([1, 2, 3]))
True
>>> same_tree(build([1, 2]), build([1, None, 2]))      # same values, different shape
False
>>> same_tree(None, None), same_tree(None, build([1]))
(True, False)
>>> is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))
True
>>> is_symmetric(build([1, 2, 2, None, 3, None, 3]))
False
>>> is_symmetric(None)
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

Both functions ask the same kind of question about **two** trees at once: what do you return when both are empty, when only one is, and when both exist? For the mirror, which child of `a` is compared with which child of `b`?
