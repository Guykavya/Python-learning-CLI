class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def iter_inorder(root):
    """A generator: yield the values in inorder, one at a time, doing only the work needed for the next one."""
    # TODO: the iterative inorder with `yield cur.val` instead of out.append(...)
    return iter([])
