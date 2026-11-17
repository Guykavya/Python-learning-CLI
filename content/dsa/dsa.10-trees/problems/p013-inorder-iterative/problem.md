# Inorder (iterative)

Write `inorder_iter(root)` that returns the values in **inorder** (left subtree, node, right subtree) with a loop and an explicit stack: no recursion. Return `[]` for an empty tree and do not change the tree.

The tests include chains of 5,000 nodes, so a recursive function fails with `RecursionError`.

## Example

```python
>>> inorder_iter(build([4, 2, 6, 1, 3, 5, 7]))
[1, 2, 3, 4, 5, 6, 7]
>>> inorder_iter(build([1, None, 2, 3]))
[1, 3, 2]
>>> inorder_iter(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to 5,000 nodes, any shape. `O(n)` time, `O(h)` extra memory.

## Think about

At every moment, what does the stack hold? (Chapter section 5: the ancestors that are still waiting for their turn.) When do you push, when do you pop, and where do you go after a visit?
