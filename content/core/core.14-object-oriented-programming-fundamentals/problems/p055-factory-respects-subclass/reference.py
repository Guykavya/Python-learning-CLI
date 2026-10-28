class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def parse_pair(text):
        parts = text.split(",")
        if len(parts) != 2:
            raise ValueError(f"expected 'x,y', got {text!r}")
        try:
            return float(parts[0]), float(parts[1])
        except ValueError as err:
            raise ValueError(f"expected 'x,y', got {text!r}") from err

    @classmethod
    def from_string(cls, text):
        x, y = cls.parse_pair(text)
        return cls(x, y)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)

    def scaled(self, k):
        return type(self)(self.x * k, self.y * k)

    def plus(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

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
