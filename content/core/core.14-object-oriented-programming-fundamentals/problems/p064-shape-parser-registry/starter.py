import math
from abc import ABC, abstractmethod

SHAPES = {}


def register_shape(cls):
    # TODO: store cls in SHAPES under cls.kind (no duplicates) and return cls
    return cls


class ShapeError(Exception):
    pass


# TODO: UnknownShapeError, BadShapeLine


class Shape(ABC):
    kind = ""
    n_args = 0

    # TODO: abstract area(), describe(), classmethod from_args(cls, args)


# TODO: Circle, Rect, Square (registered with @register_shape)


def parse_shape(text):
    # TODO
    raise NotImplementedError


def parse_shapes(lines):
    # TODO
    return []


def parse_all(lines):
    # TODO
    return []
