## Approach

Search for the node and reattach the result at every level (`root.left = delete(root.left, key)`). At the node: with at most one child, the answer is that child (or `None`), which lifts the child's whole subtree one level. With two children the node cannot be replaced by a child, so its **value** is replaced by the inorder successor's value, the smallest value in the right subtree. That successor is the leftmost node of the right subtree, so it has no left child, and deleting it from the right subtree is case 1 or 2.

## Code

```python
def delete(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:                                         # this is the node to delete
        if root.left is None:                     # a leaf, or only a right child
            return root.right
        if root.right is None:                    # only a left child
            return root.left
        successor = root.right                    # two children: the smallest value of the right subtree
        while successor.left is not None:
            successor = successor.left
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root
```

## Complexity

`O(h)` time: one walk down to the node, and one more walk down to the successor. `O(h)` memory for the recursion.

## Another way

Use the **predecessor** (the largest value of the left subtree) instead of the successor: it is just as correct and gives a different shape. An iterative version keeps the `parent` of the node and the parent of the successor, and rewires the parent's pointer by hand; it avoids recursion, which is needed for the chains in the `BST` class at the end of this module.
