class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


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
