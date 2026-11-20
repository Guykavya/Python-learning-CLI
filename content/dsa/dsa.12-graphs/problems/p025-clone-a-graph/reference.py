from collections import deque


class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node):
    if node is None:
        return None
    copy_of = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        u = queue.popleft()
        for v in u.neighbors:
            if v not in copy_of:
                copy_of[v] = Node(v.val)
                queue.append(v)
            copy_of[u].neighbors.append(copy_of[v])
    return copy_of[node]
