## Approach

The tree starting at `root` is either empty or a root with a left tree and a right tree. An empty tree has 0 nodes. Otherwise the answer is the root itself (1) plus the sizes of the two subtrees. The recursive calls already give the sizes of the smaller trees; trust them.

## Code

```python
def size(root):
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)
```

## Complexity

`O(n)` time: every node is visited once, and each `None` child costs one extra call, so there are `2n + 1` calls with constant work in each. `O(h)` extra memory for the call stack, where `h` is the height.

## Another way

An explicit stack (or a queue) walks the tree with a loop and a counter: pop a node, add 1, push its children. That version is not limited by the recursion limit. A global counter that every call increments also works, but it must be reset before each call, so the pure "return the answer" style is safer.
