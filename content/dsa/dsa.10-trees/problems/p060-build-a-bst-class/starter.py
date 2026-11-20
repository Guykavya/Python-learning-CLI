class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class BST:
    """A binary search tree of distinct keys, made of TreeNode objects. Every method is a loop (no recursion)."""

    def __init__(self):
        self.root = None
        # TODO: also keep the number of keys

    def insert(self, key):
        """Add key. True if added, False if it was already there."""
        return False

    def delete(self, key):
        """Remove key (successor rule for two children). True if removed, False if it was not there."""
        return False

    def contains(self, key):
        return False

    def height(self):
        """Number of nodes on the longest root-to-leaf path; 0 for an empty tree."""
        return 0

    def inorder(self):
        """A new list with all keys in increasing order."""
        return []

    def __len__(self):
        return 0
