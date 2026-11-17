class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def delete(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:                                         # this is the node to delete
        if root.left is None:                     # a leaf, or only a right child
            return root.right
        if root.right is None:                    # only a left child
            return root.left
        successor = root.right                    # two children: the smallest value of the right subtree
        while successor.left is not None:
            successor = successor.left
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root
