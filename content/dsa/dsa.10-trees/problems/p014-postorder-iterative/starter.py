class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def postorder_iter(root):
    """Values in postorder (left, right, node), with a loop and explicit stacks. No recursion."""
    out = []
    # TODO: one way: a preorder that visits right before left, reversed at the end
    return out
