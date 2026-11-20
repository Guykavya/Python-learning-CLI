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



INF = float("inf")


def min_cameras(root):
    if root is None:
        return 0

    def go(node):
        if node is None:
            return 0, 0, INF                       # nothing to watch, no camera possible
        l0, l1, l2 = go(node.left)
        r0, r1, r2 = go(node.right)
        open_ = l1 + r1                            # children watched, but none has a camera
        watched = min(l2 + min(r1, r2), r2 + min(l1, l2))
        camera = 1 + min(l0, l1, l2) + min(r0, r1, r2)
        return open_, watched, camera

    _, watched, camera = go(root)
    return min(watched, camera)
