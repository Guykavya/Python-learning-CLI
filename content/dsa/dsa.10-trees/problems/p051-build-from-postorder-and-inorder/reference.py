class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_from_in_post(inorder_vals, postorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(reversed(postorder_vals))    # roots from the end of the postorder

    def go(lo, hi):
        if lo > hi:
            return None
        val = next(next_root)
        node = TreeNode(val)
        mid = index[val]
        node.right = go(mid + 1, hi)              # the RIGHT subtree is built first
        node.left = go(lo, mid - 1)
        return node

    return go(0, len(inorder_vals) - 1)
