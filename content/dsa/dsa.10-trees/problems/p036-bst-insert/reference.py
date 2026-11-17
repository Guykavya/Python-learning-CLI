class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def insert(root, key):
    if root is None:
        return TreeNode(key)                 # found the empty place
    if key < root.val:
        root.left = insert(root.left, key)   # reattach: the subtree may be new
    elif key > root.val:
        root.right = insert(root.right, key)
    return root                              # also for an equal key: already there
