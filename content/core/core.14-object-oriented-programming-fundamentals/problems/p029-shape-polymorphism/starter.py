import math


class Shape:
    name = "shape"

    def area(self):
        raise NotImplementedError

    def describe(self):
        # TODO
        return ""


class Circle(Shape):
    def __init__(self, r):
        pass


class Rectangle(Shape):
    def __init__(self, w, h):
        pass


class Square(Rectangle):
    def __init__(self, side):
        pass


class Triangle(Shape):
    def __init__(self, a, b, c):
        pass


def total_area(shapes):
    return 0


def largest(shapes):
    return None


def report(shapes):
    return []
