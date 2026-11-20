class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def invert(root):
    if root is None:
        return None
    root.left, root.right = invert(root.right), invert(root.left)
    return root
