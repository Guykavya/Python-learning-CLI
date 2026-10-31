class Box:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def map(self, func):
        return self

    def __repr__(self):
        return "Box"


def biggest(a, b):
    return a
