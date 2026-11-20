class EdgeIndex:
    def __init__(self, n, edges, directed=False):
        self.adj = [[] for _ in range(n)]
        self.nbr = [set() for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.nbr[u].add(v)
            if not directed and u != v:
                self.adj[v].append(u)
                self.nbr[v].add(u)

    def neighbours(self, u):
        return list(self.adj[u])

    def has_edge(self, u, v):
        return v in self.nbr[u]
