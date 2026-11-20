class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def recover_tree(root):
    first = second = prev = None
    stack, cur = [], root
    while cur is not None or stack:                # iterative inorder
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        if prev is not None and prev.val > cur.val:    # a descent: the order breaks here
            if first is None:
                first = prev                       # the larger side of the FIRST descent
            second = cur                           # the smaller side of the LATEST descent
        prev = cur
        cur = cur.right
    if first is not None:
        first.val, second.val = second.val, first.val
