class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def size(root):
    """Number of nodes in the tree that starts at root (0 for an empty tree)."""
    # TODO: base case for None, then 1 + size(left) + size(right)
    return 0
