## Hint 1

The first item of the preorder is the root. Find that value in the inorder list: everything **to its left** is the left subtree, everything **to its right** is the right subtree. The preorder lists the whole left subtree before the whole right subtree. How many items does the left subtree have? (You can count it from the inorder list.)

## Hint 2

Keep the preorder as a "supply of roots": a pointer `pos` or an iterator that hands out the next root. A helper `go(lo, hi)` builds the subtree whose values are `inorder[lo..hi]`: if `lo > hi` return `None`; take the next root from the preorder; its position in the inorder list is `mid`; build the left subtree from `go(lo, mid - 1)` **first**, then the right from `go(mid + 1, hi)`. A dictionary `value -> index in inorder` makes finding `mid` `O(1)`.

## Hint 3

```
index = {v: i for i, v in enumerate(inorder_vals)}
next_root = iter(preorder_vals)
def go(lo, hi):
    if lo > hi: return None
    val = next(next_root)
    node = TreeNode(val)
    mid = index[val]
    node.left  = go(lo, mid - 1)       # left first: the preorder lists it first
    node.right = go(mid + 1, hi)
    return node
return go(0, len(inorder_vals) - 1)
```
