## Approach

Think of `values_at_depth(node, d)` as "the nodes `d` levels below `node`". If `d` is 0 that is the node itself. Otherwise the nodes `d` levels below `node` are the nodes `d - 1` levels below its left child followed by those below its right child. The target depth shrinks by one at every step down, so `d` is the information that travels **down**. A `None` subtree has no nodes at all.

## Code

```python
def values_at_depth(root, d):
    if root is None:
        return []
    if d == 0:
        return [root.val]
    return values_at_depth(root.left, d - 1) + values_at_depth(root.right, d - 1)
```

## Complexity

`O(n)` time in the worst case. The recursion stops at depth `d`, so only the nodes of depth up to `d` are visited. `O(h)` stack, plus the output.

## Another way

Level order (chapter section 6): build the levels with a queue and return `levels[d]` if it exists. Or a depth-first walk that passes the current depth and appends to a list when `depth == d`. For a shallow `d` the recursive version above is faster than building every level.
