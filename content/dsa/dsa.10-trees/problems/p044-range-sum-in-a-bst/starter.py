class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def range_sum(root, lo, hi):
    """Sum of the values v with lo <= v <= hi. Use the BST order to skip subtrees."""
    # TODO: v < lo -> only the right side matters; v > hi -> only the left side; else add v and both sides
    return -1
