# BST delete

Write `delete(root, key)` that removes `key` from the binary search tree and **returns the new root** (the root changes when you delete it). If the key is not in the tree, the tree stays as it is. Chapter section 9 has three cases:

1. **A leaf:** remove it.
2. **One child:** the child (with its whole subtree) takes the place of the node.
3. **Two children:** copy the value of the **inorder successor** (the smallest value of the **right** subtree) into the node, then delete that successor node from the right subtree. Use the successor, not the predecessor: the tests compare the exact shape.

Change the tree in place; do not build a new one.

## Example

```python
>>> root = make_bst([5, 3, 8, 1, 4, 7, 9, 2])       # [5, 3, 8, 1, 4, 7, 9, None, 2]
>>> root = delete(root, 4)                          # a leaf
>>> to_level(root)
[5, 3, 8, 1, None, 7, 9, None, 2]
>>> root = delete(root, 1)                          # one child: 2 moves up
>>> to_level(root)
[5, 3, 8, 2, None, 7, 9]
>>> root = delete(root, 5)                          # two children: 7 (the successor) goes to the root
>>> to_level(root)
[7, 3, 8, 2, None, None, 9]
>>> to_level(delete(root, 42))                      # not in the tree
[7, 3, 8, 2, None, None, 9]
```

`make_bst(keys)` is the tests' helper: it inserts the keys one by one. `to_level` is the chapter's `to_level_list` (a level-order list with `None` for gaps).

## Constraints

- Up to a few hundred nodes, so recursion is fine. The values are distinct. The tests also compare thousands of random operations with a Python `set`.

## Think about

Why must the result of the recursive call be assigned back (`root.left = delete(root.left, key)`)? In the two-children case, why does deleting the successor node always fall into case 1 or 2?
