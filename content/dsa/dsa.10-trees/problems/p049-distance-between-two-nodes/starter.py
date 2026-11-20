class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def distance(root, p, q):
    """Number of edges on the path between the nodes p and q."""
    # TODO: find the LCA, then depth(p) + depth(q) - 2 * depth(lca)
    return -1
