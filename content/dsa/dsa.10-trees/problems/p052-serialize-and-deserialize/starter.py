class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def serialize(root):
    """A string that describes the tree (None allowed). The format is yours."""
    # TODO: a preorder with a marker for every missing child, tokens separated by commas
    return ""


def deserialize(text):
    """The tree described by a string made by serialize. Return the root (or None)."""
    # TODO: read the tokens in the same order; a marker means None, otherwise make a node and read two subtrees
    return None
