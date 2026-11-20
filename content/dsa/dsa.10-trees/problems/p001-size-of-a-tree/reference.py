class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def size(root):
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)
