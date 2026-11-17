class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


from collections import deque


def zigzag(root):
    """Levels, alternating direction: left to right, right to left, left to right, ..."""
    levels = []
    # TODO: a normal level order; reverse every second level (the 2nd, 4th, ...)
    return levels
