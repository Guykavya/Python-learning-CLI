import math


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def diameter(self):
        return 2 * self.radius

    @property
    def area(self):
        return math.pi * self.radius ** 2
