class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def values_at_depth(root, d):
    """Values of the nodes at depth d (the root has depth 0), left to right. [] if there are none."""
    # TODO: None gives [], depth 0 gives [root.val], otherwise ask both children for depth d - 1
    return []
