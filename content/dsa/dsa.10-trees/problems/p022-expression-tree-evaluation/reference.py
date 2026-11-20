class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def evaluate(root):
    if root.left is None and root.right is None:       # a leaf: a number
        return root.val
    a = evaluate(root.left)                            # postorder: both children first
    b = evaluate(root.right)
    if root.val == "+":
        return a + b
    if root.val == "-":
        return a - b
    if root.val == "*":
        return a * b
    return a / b
