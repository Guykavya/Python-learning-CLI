## Hint 1

Find the node first, as in a search: smaller keys are on the left, larger on the right, and the function returns the (possibly new) root of that subtree. What should it return for `None`? When you find the node, what should the **parent** point at afterwards?

## Hint 2

Cases 1 and 2 together: if the node has no left child, return its right child (this is `None` for a leaf); if it has no right child, return its left child. Case 3 (both children exist): find the smallest node of the right subtree, copy its value into this node, and then delete **that value** from the right subtree. Why does the successor never have a left child?

## Hint 3

```
def delete(root, key):
    if root is None: return None
    if key < root.val:   root.left  = delete(root.left, key)
    elif key > root.val: root.right = delete(root.right, key)
    else:
        if root.left is None:  return root.right
        if root.right is None: return root.left
        succ = root.right
        while succ.left is not None: succ = succ.left
        root.val = succ.val
        root.right = delete(root.right, succ.val)
    return root
```
