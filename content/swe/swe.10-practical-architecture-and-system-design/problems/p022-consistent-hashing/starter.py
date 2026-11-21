import bisect
import hashlib


def position(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


class Ring:
    def __init__(self, nodes=(), vnodes=100):
        self.vnodes = vnodes
        self.nodes = set()
        self.points = []                  # sorted list of (position, node)
        self.positions = []               # the positions alone, for bisect
        for node in nodes:
            self.add(node)

    def add(self, node):
        # TODO
        pass

    def remove(self, node):
        # TODO
        pass

    def node_for(self, key):
        # TODO: the first point clockwise from position(key), wrapping around
        return None
