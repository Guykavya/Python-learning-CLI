class DSU:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        return x

    def union(self, x, y):
        return False

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def count(self):
        return len(self.parent)

    def size(self, x):
        return 1
