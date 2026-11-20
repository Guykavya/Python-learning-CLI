class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def delete(root, key):
    """Remove key from the BST and return the new root. A missing key changes nothing."""
    # TODO: find the node; leaf and one child: return the child; two children: copy the successor, delete it
    return root
