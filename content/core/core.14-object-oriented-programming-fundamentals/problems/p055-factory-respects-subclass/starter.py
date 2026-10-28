# This Vector works, but every factory hard-codes the class name `Vector`.
# Subclasses like Velocity get plain Vectors back. Fix it.


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def parse_pair(text):
        parts = text.split(",")
        return float(parts[0]), float(parts[1])

    @staticmethod
    def from_string(text):
        x, y = Vector.parse_pair(text)
        return Vector(x, y)

    @staticmethod
    def zero():
        return Vector(0.0, 0.0)

    def scaled(self, k):
        return Vector(self.x * k, self.y * k)

    def plus(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def kind(self):
        return "vector"


class Velocity(Vector):
    unit = "m/s"

    def kind(self):
        return "velocity"


class Labeled(Vector):
    def __init__(self, x, y, label="?"):
        super().__init__(x, y)
        self.label = label
