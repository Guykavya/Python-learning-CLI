class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def sorted_to_bst(values):
    def go(lo, hi):                                # the tree of values[lo:hi]
        if lo >= hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(values[mid])
        node.left = go(lo, mid)
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(values))
