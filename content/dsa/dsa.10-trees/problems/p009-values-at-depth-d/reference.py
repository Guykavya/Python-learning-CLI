class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def values_at_depth(root, d):
    if root is None:
        return []
    if d == 0:
        return [root.val]
    return values_at_depth(root.left, d - 1) + values_at_depth(root.right, d - 1)
