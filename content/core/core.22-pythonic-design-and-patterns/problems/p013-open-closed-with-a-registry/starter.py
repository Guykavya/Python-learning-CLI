import math


# NEW API you must write (see problem.md):
def register(name):
    raise NotImplementedError


def shape_names():
    raise NotImplementedError


# OLD code: every new shape means editing this function.
def area(shape):
    kind = shape["type"]
    if kind == "circle":
        return math.pi * shape["r"] ** 2
    elif kind == "rect":
        return shape["w"] * shape["h"]
    elif kind == "square":
        return shape["side"] ** 2
    else:
        raise ValueError("unknown shape: " + kind)
