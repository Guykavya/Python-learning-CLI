class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def serialize(root):
    out = []

    def go(node):
        if node is None:
            out.append("#")                    # a marker for a missing child
            return
        out.append(str(node.val))
        go(node.left)
        go(node.right)

    go(root)
    return ",".join(out)


def deserialize(text):
    tokens = iter(text.split(","))

    def go():
        token = next(tokens)
        if token == "#":
            return None
        node = TreeNode(int(token))
        node.left = go()
        node.right = go()
        return node

    return go()
