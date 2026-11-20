from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """Build a tree from a level-order list; None means no child (chapter section 18)."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def rob_tree(root):
    def go(node):
        if node is None:
            return 0, 0                           # (rob, skip)
        lrob, lskip = go(node.left)
        rrob, rskip = go(node.right)
        rob = node.val + lskip + rskip
        skip = max(lrob, lskip) + max(rrob, rskip)
        return rob, skip

    return max(go(root))
