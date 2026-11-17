# Floor and ceiling in a BST

Write two functions on a binary search tree of distinct values:

- `floor(root, key)` returns the **largest value that is `<= key`**, or `None` if every value is larger than `key`.
- `ceiling(root, key)` returns the **smallest value that is `>= key`**, or `None` if every value is smaller than `key`.

If `key` is in the tree, both return `key`. The `key` does not have to be in the tree. Do not change the tree. Use the BST order: the tests count the pointer reads on a BST of 4,095 nodes.

## Example

```python
>>> t = make_bst([20, 10, 30, 5, 15, 25, 40])
>>> floor(t, 12), ceiling(t, 12)
(10, 15)
>>> floor(t, 5), ceiling(t, 5)
(5, 5)
>>> floor(t, 41), ceiling(t, 41)
(40, None)
>>> floor(t, 0), ceiling(t, 0)
(None, 5)
```

`make_bst(keys)` is the tests' helper: it inserts the keys one by one into an empty BST.

## Constraints

- Up to a few thousand nodes. `O(h)` time, `O(1)` extra memory.

## Think about

While you walk down to look for `key`, which nodes are *candidates*? When you go right at a node, what do you know about that node for the floor? When you go left, what do you know for the ceiling?
