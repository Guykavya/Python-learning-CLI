class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def diameter(root):
    best = 0

    def go(node):                                  # returns the height of the subtree (in nodes)
        nonlocal best
        if node is None:
            return 0
        left = go(node.left)
        right = go(node.right)
        best = max(best, left + right)             # a path with `node` as its highest point
        return 1 + max(left, right)                # what the parent needs

    go(root)
    return best
