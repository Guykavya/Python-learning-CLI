class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


from collections import deque


def right_side_view(root):
    """The rightmost value of every level, from the top level down."""
    view = []
    # TODO: level order; keep the last node of each level
    return view
