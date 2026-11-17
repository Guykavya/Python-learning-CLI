class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.sz = [1] * n                          # valid for roots only
        self.groups = n

    def find(self, x):
        root = x
        while self.parent[root] != root:           # walk up to the root
            root = self.parent[root]
        while self.parent[x] != root:              # path compression
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.sz[rx] < self.sz[ry]:
            rx, ry = ry, rx                        # rx is the bigger root
        self.parent[ry] = rx
        self.sz[rx] += self.sz[ry]
        self.groups -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def count(self):
        return self.groups

    def size(self, x):
        return self.sz[self.find(x)]
