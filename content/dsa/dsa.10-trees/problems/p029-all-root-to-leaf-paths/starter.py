class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def root_to_leaf_paths(root):
    """Every root-to-leaf path as a string like "1->2->5", leaves from left to right."""
    result = []
    # TODO: backtracking: append the value, recurse into both children, store at a leaf, then pop
    return result
