class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def count_one_child(root):
    if root is None:
        return 0
    mine = 1 if (root.left is None) != (root.right is None) else 0
    return mine + count_one_child(root.left) + count_one_child(root.right)
