class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def longest_univalue_path(root):
    best = 0

    def down(node):
        """Edges of the longest same-value path that starts at `node` and goes down."""
        nonlocal best
        if node is None:
            return 0
        left, right = down(node.left), down(node.right)
        left_len = left + 1 if node.left is not None and node.left.val == node.val else 0
        right_len = right + 1 if node.right is not None and node.right.val == node.val else 0
        best = max(best, left_len + right_len)       # a path that bends at this node
        return max(left_len, right_len)              # the parent can continue only one way

    down(root)
    return best
