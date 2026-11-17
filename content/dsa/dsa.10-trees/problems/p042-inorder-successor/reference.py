class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def successor(root, key):
    best = None
    cur = root
    while cur is not None:
        if key < cur.val:
            best = cur                  # a possible answer; look for a smaller one on the left
            cur = cur.left
        else:
            cur = cur.right             # key >= cur.val: the answer must be larger
    return best.val if best is not None else None
