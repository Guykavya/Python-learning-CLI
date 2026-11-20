## Hint 1

Walk down as in a search. A smaller key goes into the left subtree, a larger key into the right one, an equal key is ignored. When you reach an empty place (`None`), what is the answer of "insert into an empty tree"?

## Hint 2

The recursive version returns the (possibly new) root of each subtree and reattaches it: `root.left = insert(root.left, key)`. Without the assignment the new node is created and lost. For an equal key return the same `root`, so that the caller's pointer stays valid.

## Hint 3

```
def insert(root, key):
    if root is None:
        return TreeNode(key)
    if key < root.val:
        root.left = insert(root.left, key)
    elif key > root.val:
        root.right = insert(root.right, key)
    return root                       # also for an equal key
```
