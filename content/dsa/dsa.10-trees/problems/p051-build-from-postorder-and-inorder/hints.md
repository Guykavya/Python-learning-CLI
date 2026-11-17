## Hint 1

Postorder is `left subtree, right subtree, root`. So the **last** item is the root. Find it in the inorder list: everything to its left is the left subtree, everything to its right is the right subtree, as before. If you read the postorder **from the end**, which comes just before the root: the last item of the left subtree or of the right subtree?

## Hint 2

Reading from the end gives: root, then the items of the **right** subtree (from its root backwards), then the items of the left subtree. So build the **right** subtree first, then the left. A helper `go(lo, hi)` builds the subtree of `inorder[lo..hi]`: if `lo > hi` return `None`; take the next item from the **end** of the postorder as the root; find `mid` in a dictionary; right = `go(mid + 1, hi)`, then left = `go(lo, mid - 1)`.

## Hint 3

```
index = {v: i for i, v in enumerate(inorder_vals)}
next_root = iter(reversed(postorder_vals))        # roots from the end
def go(lo, hi):
    if lo > hi: return None
    val = next(next_root)
    node = TreeNode(val)
    mid = index[val]
    node.right = go(mid + 1, hi)                  # RIGHT first
    node.left  = go(lo, mid - 1)
    return node
return go(0, len(inorder_vals) - 1)
```
