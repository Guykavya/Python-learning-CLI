## Approach

The longest downward path from a node starts with the node itself and continues into the deeper of the two subtrees. So the height is `1 + max(height(left), height(right))`. The empty tree has height 0 in the node-counting convention, which also makes a single node come out as `1 + max(0, 0) = 1` without a special case.

## Code

```python
def height(root):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))
```

## Complexity

`O(n)` time, `O(h)` stack (`h` is the height itself).

## Another way

Level order (chapter section 6): count the levels with a queue; the number of levels is the height, and the recursion limit does not matter. A depth-first walk that passes `depth` down and records the largest depth seen works too (top-down instead of bottom-up).
