## Hint 1

The iterative inorder pushes the left spine (the root, its left child, and so on), then pops one node and moves to its right child. Suppose you do only the *first* push loop in the constructor, and one pop per `next()`. What is on the stack right after the constructor? Which node is on top?

## Hint 2

The top of the stack is the next smallest value. `next()` pops it, and then pushes the **left spine of its right child** (if there is one): those are the nodes that come next in the inorder. `has_next()` is "is the stack not empty?". Each node is pushed once and popped once in the whole walk, so the average cost of `next()` is `O(1)`.

## Hint 3

```
class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)
    def _push_left(self, node):
        while node is not None:
            self.stack.append(node); node = node.left
    def has_next(self): return len(self.stack) > 0
    def next(self):
        if not self.stack: raise StopIteration
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val
```
