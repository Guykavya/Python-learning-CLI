class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def morris_inorder(root):
    """Values in inorder with O(1) extra memory (threads through right pointers). The tree is restored."""
    out = []
    cur = root
    # TODO: if cur.left is None: visit, go right.
    #       else find pred = rightmost node of cur.left; make or remove the thread pred.right = cur
    return out
