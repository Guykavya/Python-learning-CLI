## Approach

Whether a node is good depends on the path from the root, which is information from **above**, so it travels down as a parameter. `go(node, biggest)` counts 1 if `node.val >= biggest`, then passes `max(biggest, node.val)` to both children. Starting with the root's own value as `biggest` makes the root good without a special case (and works for negative values); starting with `float("-inf")` does the same.

## Code

```python
def count_good_nodes(root):
    def go(node, biggest):
        if node is None:
            return 0
        good = 1 if node.val >= biggest else 0
        biggest = max(biggest, node.val)               # the children see the new maximum
        return good + go(node.left, biggest) + go(node.right, biggest)

    if root is None:
        return 0
    return go(root, root.val)
```

## Complexity

`O(n)` time, one visit per node. `O(h)` stack.

## Another way

Pass the pair `(node, biggest)` through a loop with an explicit stack, so a chain of 5,000 nodes works. The same idea (carry the best value so far down) solves "maximum depth with a condition" and the BST validation of chapter section 9 (carry the allowed range down). A brute force that walks the ancestors of every node is `O(n * h)`.
