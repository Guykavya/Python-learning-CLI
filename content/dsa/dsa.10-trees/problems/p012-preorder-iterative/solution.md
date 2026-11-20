## Approach

The stack holds the nodes that still have to be visited. Pop one, visit it, then push its children so that the left one is on top: push the right child first. The next pop is then the left child, and the whole left subtree is finished before the right child (still waiting below) is touched. The loop ends when nothing is waiting.

## Code

```python
def preorder_iter(root):
    out = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right is not None:
            stack.append(node.right)        # pushed first, visited last
        if node.left is not None:
            stack.append(node.left)
    return out
```

## Complexity

`O(n)` time: each node is pushed once and popped once. The stack holds at most one waiting right child per level, plus the current node, so `O(h)` memory. There is no recursion, so the depth of the tree does not matter.

## Another way

The chapter's "one template for all three" (pairs `(node, done)`) gives the three orders with one loop; for preorder you push `(right, False)`, `(left, False)`, `(node, True)`. A version that pushes `None` too is possible but needs a `continue` after popping. With recursion the same function is three lines, but it fails on a skewed tree with 5,000 nodes.
