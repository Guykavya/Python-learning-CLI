class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder_iter(root):
    out = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right is not None:
            stack.append(node.right)        # pushed first, visited last
        if node.left is not None:
            stack.append(node.left)
    return out
