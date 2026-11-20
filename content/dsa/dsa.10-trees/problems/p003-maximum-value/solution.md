## Approach

The answer for a node is the largest of three things: its own value, the largest of the left tree, the largest of the right tree. An empty subtree has no largest value, so its answer is `None`, and the combining step must skip it. Starting from `best = root.val` (a real value) and only replacing it by real answers solves both the negative-values trap and the `None` trap.

## Code

```python
def max_value(root):
    if root is None:
        return None
    best = root.val
    for child in (root.left, root.right):
        sub = max_value(child)
        if sub is not None and sub > best:
            best = sub
    return best
```

## Complexity

`O(n)` time, `O(h)` stack.

## Another way

Return `float("-inf")` for the empty tree inside a helper and convert it to `None` only in the public function: then the combining step is just `max(root.val, left, right)`. Or walk the tree with any traversal and keep a running maximum, starting from the root's value.
