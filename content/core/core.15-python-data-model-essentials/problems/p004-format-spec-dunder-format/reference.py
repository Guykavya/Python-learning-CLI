class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def __format__(self, spec):
        if spec == "":
            return str(self)
        if spec == "hex":
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        if spec == "rgb":
            return f"rgb({self.r}, {self.g}, {self.b})"
        raise ValueError(f"unknown format spec: {spec}")
