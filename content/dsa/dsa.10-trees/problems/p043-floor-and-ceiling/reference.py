class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def floor(root, key):
    best = None
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur.val
        if key > cur.val:
            best = cur                  # <= key: a candidate; a larger one may be on the right
            cur = cur.right
        else:
            cur = cur.left              # too large
    return best.val if best is not None else None


def ceiling(root, key):
    best = None
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur.val
        if key < cur.val:
            best = cur                  # >= key: a candidate; a smaller one may be on the left
            cur = cur.left
        else:
            cur = cur.right             # too small
    return best.val if best is not None else None
