## Hint 1

Look at one node. If its value is **smaller than `lo`**, every value in its left subtree is smaller still, so none of them can be in `[lo, hi]`. What does that let you skip? What does the mirror case (value larger than `hi`) let you skip?

## Hint 2

Three cases at each node: `v < lo`: only the right subtree can contain values of the range, so return `range_sum(right)`. `v > hi`: return `range_sum(left)`. Otherwise the node is in the range: return `v` plus the sums of both subtrees. An empty tree gives `0`.

## Hint 3

```
def range_sum(node, lo, hi):
    if node is None: return 0
    if node.val < lo: return range_sum(node.right, lo, hi)
    if node.val > hi: return range_sum(node.left, lo, hi)
    return node.val + range_sum(node.left, lo, hi) + range_sum(node.right, lo, hi)
```
