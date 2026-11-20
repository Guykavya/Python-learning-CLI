## Hint 1

If you put the **middle** value at the root, how many values are left for the left side and for the right side? Which values go left and which go right, so that the BST rule holds? What problem is the left half, seen from the left subtree's point of view?

## Hint 2

The same problem on a smaller list: the left subtree is `sorted_to_bst` of the left half, the right subtree is `sorted_to_bst` of the right half. Use two indices `lo` and `hi` instead of slicing: `go(lo, hi)` builds the tree of `values[lo:hi]` and returns `None` for an empty range. The middle is `(lo + hi) // 2`.

## Hint 3

```
def go(lo, hi):                    # the values[lo:hi]
    if lo >= hi: return None
    mid = (lo + hi) // 2
    node = TreeNode(values[mid])
    node.left  = go(lo, mid)
    node.right = go(mid + 1, hi)
    return node
return go(0, len(values))
```
