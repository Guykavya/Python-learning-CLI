class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def height(root):
    """Number of nodes on the longest path from the root down to a leaf (0 for an empty tree)."""
    # TODO: base case, then 1 + the larger of the two subtree heights
    return 0
