class EdgeIndex:
    def __init__(self, n, edges, directed=False):
        pass

    def neighbours(self, u):
        """Neighbours of u in edge-list order."""
        return []

    def has_edge(self, u, v):
        """True if there is an edge u -> v (both ways if undirected). O(1) average."""
        return False
