# Inorder successor

Write `successor(root, key)` that returns the **smallest value in the BST that is strictly larger than `key`**, or `None` if there is none. This is the value that comes right after `key` in the inorder traversal. The `key` does **not** have to be in the tree. Nodes have no parent pointer, and you must not build the inorder list: the tests count the pointer reads on a BST of 4,095 nodes, and one walk from the root down needs only about 13.

## Example

```python
>>> t = make_bst([20, 10, 30, 5, 15, 25, 40])
>>> successor(t, 5), successor(t, 12), successor(t, 15)
(10, 15, 20)
>>> successor(t, 40) is None          # the largest value
True
>>> successor(t, 0), successor(t, 41)
(5, None)
```

`make_bst(keys)` is the tests' helper: it inserts the keys one by one into an empty BST.

## Constraints

- Up to a few thousand nodes. `O(h)` time, `O(1)` extra memory.

## Think about

The chapter (section 9) says: walk down from the root, and every time you go **left**, remember the node you left behind. Why is that node a candidate, and why does a leaf that is a right child find its successor **above** it?
