class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def max_value(root):
    if root is None:
        return None
    best = root.val
    for child in (root.left, root.right):
        sub = max_value(child)
        if sub is not None and sub > best:
            best = sub
    return best
