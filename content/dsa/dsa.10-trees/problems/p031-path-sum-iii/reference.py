class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def path_sum_count(root, target):
    counts = {0: 1}                                     # the empty stretch before the root
    total = 0

    def go(node, running):
        nonlocal total
        if node is None:
            return
        running += node.val
        total += counts.get(running - target, 0)        # paths that end at this node
        counts[running] = counts.get(running, 0) + 1    # choose
        go(node.left, running)
        go(node.right, running)
        counts[running] -= 1                            # un-choose

    go(root, 0)
    return total
