class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def flatten(root):
    cur = root
    while cur is not None:
        if cur.left is not None:
            last = cur.left
            while last.right is not None:
                last = last.right              # the rightmost node of the left subtree
            last.right = cur.right             # the old right subtree goes after it
            cur.right = cur.left               # the left subtree moves to the right
            cur.left = None
        cur = cur.right                        # move on along the new right chain
