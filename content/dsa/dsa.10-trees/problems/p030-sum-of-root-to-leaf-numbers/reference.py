class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def sum_numbers(root):
    def go(node, so_far):
        if node is None:
            return 0
        so_far = so_far * 10 + node.val
        if node.left is None and node.right is None:      # a leaf: the number is complete
            return so_far
        return go(node.left, so_far) + go(node.right, so_far)

    return go(root, 0)
