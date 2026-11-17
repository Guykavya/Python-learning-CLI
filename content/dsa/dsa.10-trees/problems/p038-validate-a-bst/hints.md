## Hint 1

Take the node `3` in `[5, 1, 6, None, None, 3, 7]`. It is the left child of `6`, and `3 < 6`, so the local check passes. Which **ancestor** does `3` break? The BST rule is about whole subtrees: every node in the right subtree of `5` must be larger than `5`.

## Hint 2

Pass a **range** down: each node must lie strictly between `lo` and `hi`. The root has no limit. Going **left** from a node with value `v` sets the new upper limit `hi = v`; going **right** sets `lo = v`. Use `None` for "no limit yet" (not a number like `2**31 - 1`, which can be a real value).

## Hint 3

```
def check(node, lo, hi):
    if node is None: return True
    if lo is not None and node.val <= lo: return False
    if hi is not None and node.val >= hi: return False
    return check(node.left, lo, node.val) and check(node.right, node.val, hi)

return check(root, None, None)
```

Another way: an inorder walk must give a strictly increasing sequence.
