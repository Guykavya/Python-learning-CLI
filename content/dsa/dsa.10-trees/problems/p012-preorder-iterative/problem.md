# Preorder (iterative)

Write `preorder_iter(root)` that returns the values of the tree in **preorder** (node, left subtree, right subtree) using a loop and an **explicit stack**: no recursion. Return `[]` for an empty tree. Do not change the tree.

The tests also use skewed trees with 5,000 nodes. A recursive function needs 5,000 nested calls and fails with `RecursionError` there (chapter section 5), so the stack must be yours.

## Example

```python
>>> preorder_iter(build([4, 2, 6, 1, 3, 5, 7]))
[4, 2, 1, 3, 6, 5, 7]
>>> preorder_iter(build([1, None, 2, 3]))
[1, 2, 3]
>>> preorder_iter(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to 5,000 nodes, any shape. `O(n)` time, `O(h)` extra memory for the stack.

## Think about

A stack gives back the **last** thing you pushed. You want to visit the left child first. Which child do you push first?
