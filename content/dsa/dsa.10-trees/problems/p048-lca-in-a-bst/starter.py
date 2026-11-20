class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def lca_bst(root, p, q):
    """The lowest common ancestor of the nodes p and q in a BST (a node is its own ancestor). O(h)."""
    # TODO: go left if both are smaller, right if both are larger, otherwise this node is the answer
    return None
