class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_subtree(root, sub):
    """True if some node of root starts a subtree that is exactly the same as sub (down to the leaves)."""
    # TODO: sub empty -> True; root empty -> False; same_tree at this node, or recurse into both children
    return False
