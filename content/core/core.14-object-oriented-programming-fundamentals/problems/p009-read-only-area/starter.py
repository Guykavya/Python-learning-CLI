import math


class Circle:
    def __init__(self, radius):
        # TODO: set the radius through its property so it is checked
        self.radius = radius
        self.diameter = 2 * radius
        self.area = math.pi * radius ** 2

    # TODO: radius property with a checking setter
    # TODO: read-only diameter and area properties
