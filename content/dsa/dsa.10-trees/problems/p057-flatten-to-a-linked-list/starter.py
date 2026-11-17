class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def flatten(root):
    """Rearrange the tree in place: only right pointers, in the preorder of the original tree. Returns nothing."""
    # TODO: if cur has a left subtree, hang the old right subtree on the rightmost node of the left subtree
    return None
