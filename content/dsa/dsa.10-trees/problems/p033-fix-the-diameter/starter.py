class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))


def diameter(root):
    """Length in EDGES of the longest path between any two nodes."""
    if root is None:
        return 0
    return height(root.left) + height(root.right)        # a classmate's version
