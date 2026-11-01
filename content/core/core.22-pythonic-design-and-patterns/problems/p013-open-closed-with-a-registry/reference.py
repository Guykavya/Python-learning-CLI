import math

_AREAS = {}


def register(name):
    def decorator(func):
        if name in _AREAS:
            raise ValueError(f"shape already registered: {name}")
        _AREAS[name] = func
        return func

    return decorator


def shape_names():
    return sorted(_AREAS)


@register("circle")
def _circle(shape):
    return math.pi * shape["r"] ** 2


@register("rect")
def _rect(shape):
    return shape["w"] * shape["h"]


@register("square")
def _square(shape):
    return shape["side"] ** 2


def area(shape):
    kind = shape["type"]
    try:
        func = _AREAS[kind]
    except KeyError:
        raise ValueError(f"unknown shape: {kind}") from None
    return func(shape)
