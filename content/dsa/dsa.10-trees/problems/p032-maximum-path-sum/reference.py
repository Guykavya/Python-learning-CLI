class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def max_path_sum(root):
    best = float("-inf")

    def gain(node):
        """Best sum of a path that starts at `node` and goes down (at least `node` itself)."""
        nonlocal best
        if node is None:
            return 0
        left = max(0, gain(node.left))              # a negative branch is dropped
        right = max(0, gain(node.right))
        best = max(best, node.val + left + right)   # a path that bends at this node
        return node.val + max(left, right)          # the parent can continue only ONE way down

    gain(root)
    return best
