class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def evaluate(root):
    """Value of the expression tree: numbers at the leaves, "+", "-", "*", "/" in the other nodes."""
    # TODO: a leaf returns its number; otherwise evaluate both children, then apply the operator
    return 0
