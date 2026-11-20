class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def min_depth(root):
    """Number of nodes on the shortest path from the root to a leaf (0 for an empty tree)."""
    # TODO: a node with only one child must continue into that child
    return 0
