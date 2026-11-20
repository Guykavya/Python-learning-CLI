## Hint 1

Take the chain `1 -> 2 -> 3` where every node has only a right child. What does the formula `1 + min(left, right)` compute at the root? The left call is on `None`. What does it return, and does that mean there is a path of length 0 on the left?

## Hint 2

A missing child is not a path to a leaf. So if one child is `None`, the answer must come from the other child only. Handle three cases: only a right child, only a left child, both children.

## Hint 3

```
if root is None: return 0
if root.left is None:  return 1 + min_depth(root.right)
if root.right is None: return 1 + min_depth(root.left)
return 1 + min(min_depth(root.left), min_depth(root.right))
```
(A leaf falls into the first case: `1 + min_depth(None) = 1`.)
