class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder_iter(root):
    """Values in preorder (node, left, right), with a loop and an explicit stack. No recursion."""
    out = []
    stack = []
    # TODO: put the root on the stack; pop, visit, push the right child, then the left child
    return out
