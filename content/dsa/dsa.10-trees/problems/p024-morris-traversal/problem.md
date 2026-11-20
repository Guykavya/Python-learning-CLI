# Morris traversal (no stack, no recursion)

Write `morris_inorder(root)` that returns the values in **inorder** using only `O(1)` extra memory besides the output list: no recursion, no stack, no parent pointers, no set of visited nodes. When your function returns, the tree must be **exactly as it was**: the same nodes with the same `left` and `right` pointers.

How can a walk without a stack come back up? The chapter (section 5) only names this trick, so here is the idea. In an inorder walk the node that is visited **just before** a node `cur` that has a left subtree is the **rightmost node of that left subtree**: call it the *predecessor* of `cur`. That node has no right child (it is the rightmost), so its `right` pointer is free. Use it as a temporary **thread** back up to `cur`: set `pred.right = cur`. When the walk, after finishing the left subtree, arrives at `pred`, following `pred.right` takes it back to `cur` without a stack. Then remove the thread.

The loop, with `cur` starting at the root:

1. If `cur.left` is `None`: visit `cur`, then move to `cur.right` (this may follow a thread back up).
2. Otherwise find `pred`: go to `cur.left`, then keep going right while `pred.right` exists **and is not `cur`**.
   - If `pred.right` is `None`: the left subtree is not visited yet. Set the thread `pred.right = cur`, then move to `cur.left`.
   - If `pred.right` is `cur`: the thread was made earlier, so the left subtree is finished. Remove the thread (`pred.right = None`), visit `cur`, then move to `cur.right`.

Stop when `cur` is `None`.

## Example

```python
>>> t = build([4, 2, 6, 1, 3, 5, 7])
>>> morris_inorder(t)
[1, 2, 3, 4, 5, 6, 7]
>>> to_level(t)                     # unchanged afterwards
[4, 2, 6, 1, 3, 5, 7]
>>> morris_inorder(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to 30,000 nodes, any shape (also a chain). `O(n)` time, `O(1)` extra memory besides the output list.

## Think about

Why can the thread never be mistaken for a real right child while you search for `pred`? What would happen to the tree if the function stopped in the middle (an exception) after setting a thread?
