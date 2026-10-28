import math


class Point:
    def __init__(self, x, y):
        # TODO: store x and y on the new object (self)
        pass

    def distance_to(self, other):
        # TODO: return the distance from self to other
        raise NotImplementedError

    def moved(self, dx, dy):
        # TODO: return a NEW Point; do not change self
        raise NotImplementedError
