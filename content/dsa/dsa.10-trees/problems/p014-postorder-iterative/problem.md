# Postorder (iterative)

Write `postorder_iter(root)` that returns the values in **postorder** (left subtree, right subtree, node) with a loop and an explicit stack (or two): no recursion. Return `[]` for an empty tree and do not change the tree.

Postorder is the hardest of the three, because a node may only be visited after **both** of its subtrees are done. The chapter (section 5) shows two ways: reverse a modified preorder, or use one stack and a `last` pointer. Use either one.

The tests include chains of 5,000 nodes, so recursion fails.

## Example

```python
>>> postorder_iter(build([4, 2, 6, 1, 3, 5, 7]))
[1, 3, 2, 5, 7, 6, 4]
>>> postorder_iter(build([1, 2, 3]))
[2, 3, 1]
>>> postorder_iter(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to 5,000 nodes, any shape. `O(n)` time, `O(n)` (two-stack or reversal way) or `O(h)` (one stack) extra memory.

## Think about

Why is "the reverse of a preorder" not postorder? (Try `[1, 2, 3]`.) What small change to the preorder makes the reversal correct?
