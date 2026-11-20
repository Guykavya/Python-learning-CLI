class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def has_path_sum(root, target):
    """True if some path from the root down to a LEAF has the values adding up to target."""
    # TODO: at a leaf compare the value; otherwise subtract the value and ask both children
    return False
