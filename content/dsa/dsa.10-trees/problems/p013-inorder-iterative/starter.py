class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def inorder_iter(root):
    """Values in inorder (left, node, right), with a loop and an explicit stack. No recursion."""
    out = []
    stack = []
    cur = root
    # TODO: go left as far as possible (push), pop and visit, then move to the right child
    return out
