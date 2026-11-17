class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


from collections import deque


def children_and_depths(parent):
    n = len(parent)
    children = [[] for _ in range(n)]
    root = -1
    for node, p in enumerate(parent):
        if p == -1:
            root = node
        else:
            children[p].append(node)                 # going upwards keeps every list sorted
    depth = [0] * n
    queue = deque([root])
    while queue:                                     # every node is reached after its parent
        node = queue.popleft()
        for c in children[node]:
            depth[c] = depth[node] + 1
            queue.append(c)
    return children, depth
