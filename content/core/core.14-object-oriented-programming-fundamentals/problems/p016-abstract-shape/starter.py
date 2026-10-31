import math
from abc import ABC, abstractmethod


class Shape:
    # TODO: inherit from ABC; make area and perimeter abstract
    def area(self):
        return 0

    def perimeter(self):
        return 0

    def describe(self):
        # TODO: "<ClassName>: area <x.xx>, perimeter <y.yy>"
        raise NotImplementedError


class Square(Shape):
    def __init__(self, side):
        self.side = side


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
