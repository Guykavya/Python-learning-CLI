## Approach

The shortest path to a leaf must end at a leaf, so a missing child cannot be used as the end of a path. If a node has only one child, the path continues into that child. Only a node with two children takes the `min` of its two sides. A leaf has no children: the first case gives `1 + min_depth(None) = 1`.

## Code

```python
def min_depth(root):
    if root is None:
        return 0
    if root.left is None:                          # only a right child: the path must go right
        return 1 + min_depth(root.right)
    if root.right is None:
        return 1 + min_depth(root.left)
    return 1 + min(min_depth(root.left), min_depth(root.right))
```

## Complexity

`O(n)` time in the worst case (a depth-first search looks at the whole tree), `O(h)` stack.

## Another way

Breadth-first search (chapter section 6, "Try it 3"): walk level by level and return the depth of the first leaf you meet. It stops early, and it cannot be fooled by missing children. The depth-first form above is the "what does each call return" style; the BFS form is better for a tree that is very deep on one side.
