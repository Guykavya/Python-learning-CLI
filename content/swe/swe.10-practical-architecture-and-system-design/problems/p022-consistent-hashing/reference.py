import bisect
import hashlib


def position(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


class Ring:
    def __init__(self, nodes=(), vnodes=100):
        self.vnodes = vnodes
        self.nodes = set()
        self.points = []
        self.positions = []
        for node in nodes:
            self.add(node)

    def _rebuild(self):
        self.points = sorted((position(f"{n}#{i}"), n) for n in self.nodes for i in range(self.vnodes))
        self.positions = [p for p, _ in self.points]

    def add(self, node):
        if node in self.nodes:
            raise ValueError(f"{node!r} is already on the ring")
        self.nodes.add(node)
        self._rebuild()

    def remove(self, node):
        if node not in self.nodes:
            raise KeyError(node)
        self.nodes.remove(node)
        self._rebuild()

    def node_for(self, key):
        if not self.points:
            raise ValueError("the ring is empty")
        return self.points[bisect.bisect(self.positions, position(key)) % len(self.points)][1]
