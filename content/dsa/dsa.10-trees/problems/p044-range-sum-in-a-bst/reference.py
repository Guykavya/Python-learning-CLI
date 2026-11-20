class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def range_sum(root, lo, hi):
    if root is None:
        return 0
    if root.val < lo:
        return range_sum(root.right, lo, hi)       # everything on the left is too small
    if root.val > hi:
        return range_sum(root.left, lo, hi)        # everything on the right is too big
    return root.val + range_sum(root.left, lo, hi) + range_sum(root.right, lo, hi)
