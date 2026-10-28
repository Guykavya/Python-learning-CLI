import math


def _positive(value, what):
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{what} must be a number above 0, got {value!r}")
    return value


class Shape:
    name = "shape"

    def area(self):
        raise NotImplementedError(f"{type(self).__name__} must define area()")

    def describe(self):
        return f"{self.name} with area {self.area():.2f}"


class Circle(Shape):
    name = "circle"

    def __init__(self, r):
        self.r = _positive(r, "radius")

    def area(self):
        return math.pi * self.r * self.r


class Rectangle(Shape):
    name = "rectangle"

    def __init__(self, w, h):
        self.w = _positive(w, "width")
        self.h = _positive(h, "height")

    def area(self):
        return self.w * self.h


class Square(Rectangle):
    name = "square"

    def __init__(self, side):
        super().__init__(side, side)
        self.side = side


class Triangle(Shape):
    name = "triangle"

    def __init__(self, a, b, c):
        self.a = _positive(a, "side a")
        self.b = _positive(b, "side b")
        self.c = _positive(c, "side c")
        longest = max(a, b, c)
        if longest >= a + b + c - longest:
            raise ValueError("these sides do not make a triangle")

    def area(self):
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))


def total_area(shapes):
    return round(sum(shape.area() for shape in shapes), 2)


def largest(shapes):
    if not shapes:
        raise ValueError("largest() needs at least one shape")
    best = shapes[0]
    for shape in shapes[1:]:
        if shape.area() > best.area():
            best = shape
    return best


def report(shapes):
    ordered = sorted(shapes, key=lambda shape: shape.area(), reverse=True)
    return [f"{i}. {shape.describe()}" for i, shape in enumerate(ordered, start=1)]
