class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def distance(root, p, q):
    parent = {root: None}
    stack = [root]
    while stack:                                  # a parent map, filled with a loop
        node = stack.pop()
        for child in (node.left, node.right):
            if child is not None:
                parent[child] = node
                stack.append(child)

    def depth(node):
        steps = 0
        while parent[node] is not None:
            node = parent[node]
            steps += 1
        return steps

    def lca(node):
        if node is None or node is p or node is q:
            return node
        left, right = lca(node.left), lca(node.right)
        if left is not None and right is not None:
            return node
        return left if left is not None else right

    ancestor = lca(root)
    return depth(p) + depth(q) - 2 * depth(ancestor)
