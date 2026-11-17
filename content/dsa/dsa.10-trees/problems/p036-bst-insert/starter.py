class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def insert(root, key):
    """Put key into the BST as a new leaf and return the root. A key that is already there changes nothing."""
    # TODO: an empty place gives a new node; otherwise go left or right and reattach the result
    return root
