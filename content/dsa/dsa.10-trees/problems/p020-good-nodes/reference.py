class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def count_good_nodes(root):
    def go(node, biggest):
        if node is None:
            return 0
        good = 1 if node.val >= biggest else 0
        biggest = max(biggest, node.val)               # the children see the new maximum
        return good + go(node.left, biggest) + go(node.right, biggest)

    if root is None:
        return 0
    return go(root, root.val)
