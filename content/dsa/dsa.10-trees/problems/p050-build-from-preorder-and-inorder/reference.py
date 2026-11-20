class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_from_pre_in(preorder_vals, inorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(preorder_vals)               # hands out the roots in preorder

    def go(lo, hi):                               # build from inorder_vals[lo..hi]
        if lo > hi:
            return None
        val = next(next_root)                     # the next preorder item is this subtree's root
        node = TreeNode(val)
        mid = index[val]
        node.left = go(lo, mid - 1)               # left first: the preorder lists it first
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(inorder_vals) - 1)
