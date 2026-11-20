class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def path_sum_count(root, target):
    """How many downward paths (any start, any end below it) have the values adding up to target? O(n)."""
    # TODO: running sum + a dictionary of the running sums on the current root path
    return -1
