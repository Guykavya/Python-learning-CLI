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


def is_mirror(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and is_mirror(a.left, b.right) and is_mirror(a.right, b.left)


def is_symmetric(root):
    return root is None or is_mirror(root.left, root.right)
