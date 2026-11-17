class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


from collections import deque


def level_order(root):
    """Values level by level: [[root], [depth 1, left to right], ...]. [] for an empty tree."""
    levels = []
    # TODO: a queue; for each level take len(queue) nodes and append their children
    return levels
