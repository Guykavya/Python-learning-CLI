class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class BSTIterator:
    """Walk a BST in increasing order, one value per next(), with O(h) memory."""

    def __init__(self, root):
        # TODO: keep a stack of the nodes that still wait; push the left spine of the root
        pass

    def next(self):
        """The next smallest value. Raise StopIteration when there is none."""
        return None

    def has_next(self):
        """True if next() would return a value."""
        return False
