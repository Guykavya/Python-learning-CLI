class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def root_to_leaf_paths(root):
    result, path = [], []

    def go(node):
        if node is None:
            return
        path.append(node.val)                                  # choose
        if node.left is None and node.right is None:
            result.append("->".join(map(str, path)))          # a string is a new object: no copy needed
        else:
            go(node.left)
            go(node.right)
        path.pop()                                             # un-choose

    go(root)
    return result
