class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def successor(root, key):
    """The smallest value in the BST that is strictly larger than key, or None. O(h)."""
    # TODO: walk down; every time you go left, remember the node you left behind
    return None
