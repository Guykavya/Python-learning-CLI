class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def morris_inorder(root):
    out, cur = [], root
    while cur is not None:
        if cur.left is None:
            out.append(cur.val)
            cur = cur.right                          # may follow a thread back up
        else:
            pred = cur.left                          # the node visited just before cur
            while pred.right is not None and pred.right is not cur:
                pred = pred.right
            if pred.right is None:
                pred.right = cur                     # make the thread, then go left
                cur = cur.left
            else:
                pred.right = None                    # the left side is done: remove the thread
                out.append(cur.val)
                cur = cur.right
    return out
