## Approach

Insertion is a search that ends in an empty place. The recursive function answers "what is the tree after inserting `key` into the tree that starts here?": for `None` it is a single new node; otherwise the key goes into the left or right subtree, and the result is reattached with an assignment (`root.left = insert(root.left, key)`). An equal key leaves the tree unchanged. The function always returns its own `root`, so the caller can write `root = insert(root, key)` even for the first key.

## Code

```python
def insert(root, key):
    if root is None:
        return TreeNode(key)                 # found the empty place
    if key < root.val:
        root.left = insert(root.left, key)   # reattach: the subtree may be new
    elif key > root.val:
        root.right = insert(root.right, key)
    return root                              # also for an equal key: already there
```

## Complexity

`O(h)` time (one step per level) and `O(h)` memory for the recursion. A balanced tree has `h` about `log n`; inserting sorted keys one after another gives a chain with `h = n`.

## Another way

An iterative version keeps a `parent` pointer while walking down and attaches the new node to it at the end (it handles an empty tree with a special case). It needs no recursion, which matters for chains of thousands of nodes (the `BST` class at the end of this module needs that).
