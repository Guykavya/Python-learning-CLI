class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def search(root, key):
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur
        cur = cur.left if key < cur.val else cur.right
    return None


def find_min(root):
    if root is None:
        return None
    while root.left is not None:
        root = root.left              # the smallest value is the leftmost node
    return root


def find_max(root):
    if root is None:
        return None
    while root.right is not None:
        root = root.right
    return root
