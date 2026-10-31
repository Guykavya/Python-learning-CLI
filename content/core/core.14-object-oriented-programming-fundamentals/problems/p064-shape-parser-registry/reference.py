import math
from abc import ABC, abstractmethod

SHAPES = {}


def register_shape(cls):
    if cls.kind in SHAPES:
        raise ValueError(f"shape {cls.kind!r} is already registered")
    SHAPES[cls.kind] = cls
    return cls


class ShapeError(Exception):
    pass


class UnknownShapeError(ShapeError):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"unknown shape {kind!r}")


class BadShapeLine(ShapeError):
    def __init__(self, line_no, line, reason):
        self.line_no = line_no
        self.line = line
        self.reason = reason
        super().__init__(f"line {line_no}: {reason}")


class Shape(ABC):
    kind = ""
    n_args = 0

    @abstractmethod
    def area(self):
        ...

    def describe(self):
        return f"{self.kind} area={self.area():.2f}"

    @classmethod
    def from_args(cls, args):
        if len(args) != cls.n_args:
            raise ValueError(f"{cls.kind} needs {cls.n_args} number(s), got {len(args)}")
        numbers = []
        for text in args:
            try:
                numbers.append(float(text))
            except ValueError as err:
                raise ValueError(f"not a number: {text!r}") from err
        if any(n <= 0 for n in numbers):
            raise ValueError("sizes must be positive")
        return cls(*numbers)


@register_shape
class Circle(Shape):
    kind = "circle"
    n_args = 1

    def __init__(self, r):
        self.r = r

    def area(self):
        return math.pi * self.r * self.r


@register_shape
class Rect(Shape):
    kind = "rect"
    n_args = 2

    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h


@register_shape
class Square(Rect):
    kind = "square"
    n_args = 1

    def __init__(self, side):
        super().__init__(side, side)


def parse_shape(text):
    words = text.split()
    if not words:
        raise ValueError("empty shape line")
    kind, rest = words[0].lower(), words[1:]
    try:
        cls = SHAPES[kind]
    except KeyError as err:
        raise UnknownShapeError(kind) from err
    return cls.from_args(rest)


def _numbered(lines):
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield line_no, stripped


def parse_shapes(lines):
    shapes = []
    for line_no, line in _numbered(lines):
        try:
            shapes.append(parse_shape(line))
        except (ValueError, UnknownShapeError) as err:
            raise BadShapeLine(line_no, line, str(err)) from err
    return shapes


def parse_all(lines):
    shapes = []
    errors = []
    for line_no, line in _numbered(lines):
        try:
            shapes.append(parse_shape(line))
        except (ValueError, UnknownShapeError) as err:
            bad = BadShapeLine(line_no, line, str(err))
            bad.__cause__ = err
            errors.append(bad)
    if errors:
        raise ExceptionGroup(f"{len(errors)} bad line(s)", errors)
    return shapes
