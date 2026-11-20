class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)


def is_subtree(root, sub):
    if sub is None:
        return True
    if root is None:
        return False
    return same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)
