## Approach

The iterative inorder keeps a stack of the nodes whose turn has not come yet. Turn the loop into an object: the stack is the state. The constructor pushes the left spine of the root, so the smallest value is on top. `next()` pops the top, pushes the left spine of its right child (the nodes that follow it in the inorder), and returns the value. `has_next()` asks whether the stack is empty. Memory is the stack: never more than one node per level, so `O(h)`.

## Code

```python
class BSTIterator:
    def __init__(self, root):
        self.stack = []                     # the nodes that still wait, the next one on top
        self._push_left(root)

    def _push_left(self, node):
        while node is not None:
            self.stack.append(node)
            node = node.left

    def has_next(self):
        return len(self.stack) > 0

    def next(self):
        if not self.stack:
            raise StopIteration
        node = self.stack.pop()
        self._push_left(node.right)         # the nodes that come right after `node`
        return node.val
```

## Complexity

`next()` is `O(1)` amortised: one call may push many nodes, but over the whole walk every node is pushed once and popped once, so `n` calls cost `O(n)` in total. The constructor costs `O(h)`. Memory `O(h)`.

## Another way

A generator does the same with less code: `def iter_inorder(root):` with the recursive `yield from` (problem 15), and `next(it, None)` to read it. A class with `next` and `has_next` is what interview problems ask for, and it shows how a stack replaces the call stack. Morris traversal (problem 24) gives `O(1)` memory but changes the tree temporarily, which is risky for an iterator that can stop at any time.
