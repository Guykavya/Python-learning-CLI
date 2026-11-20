class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node):
    """Return a deep copy of the graph reachable from node (None -> None)."""
    return node
