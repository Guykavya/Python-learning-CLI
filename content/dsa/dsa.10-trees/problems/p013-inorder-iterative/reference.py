class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def inorder_iter(root):
    out, stack, cur = [], [], root
    while cur is not None or stack:
        while cur is not None:              # go left as far as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()                   # the next node in inorder
        out.append(cur.val)
        cur = cur.right                     # then handle its right subtree
    return out
