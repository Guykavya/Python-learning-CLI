import heapq
from collections import deque


class Graph:
    def __init__(self, n, directed=False):
        self.n = n
        self.directed = directed
        self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v, w=1):
        pass

    def bfs(self, s):
        return []

    def dfs(self, s):
        return []

    def components(self):
        return []

    def topo(self):
        return None

    def shortest(self, s):
        return [0] * self.n
