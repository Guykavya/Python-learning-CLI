import io
import math
from abc import ABC

import pytest

import solution
from solution import (SHAPES, BadShapeLine, Circle, Rect, Shape, ShapeError, Square, UnknownShapeError,
                      parse_all, parse_shape, parse_shapes, register_shape)


@pytest.fixture
def clean_registry():
    saved = dict(SHAPES)
    yield
    SHAPES.clear()
    SHAPES.update(saved)


def test_registry_contents():
    assert SHAPES.get("circle") is Circle and SHAPES.get("rect") is Rect and SHAPES.get("square") is Square, (
        "Decorate Circle, Rect and Square with @register_shape so SHAPES maps kind -> class."
    )


def test_shape_is_abstract():
    assert issubclass(Shape, ABC), "Shape inherits from ABC."
    with pytest.raises(TypeError):
        Shape()


def test_areas_and_describe():
    assert parse_shape("circle 2").describe() == "circle area=12.57", "Circle area is math.pi * r * r; describe uses :.2f."
    assert parse_shape("rect 3 4").describe() == "rect area=12.00", "Rect area is w * h."
    assert math.isclose(parse_shape("square 2.5").area(), 6.25), "Square(2.5) is a 2.5 x 2.5 Rect."


def test_square_is_a_rect():
    sq = parse_shape("square 2")
    assert type(sq) is Square and isinstance(sq, Rect), "Square inherits from Rect and calls super().__init__(side, side)."
    assert (sq.w, sq.h) == (2.0, 2.0), "Square passes side twice to Rect.__init__."


def test_from_args_builds_cls():
    c = Circle.from_args(["3"])
    assert type(c) is Circle and c.r == 3.0, "from_args converts strings to floats and returns cls(*numbers)."
    assert type(Square.from_args(["1"])) is Square, "Because from_args is a classmethod, Square.from_args builds a Square."


def test_case_and_spaces():
    assert type(parse_shape("  RECT   3   4  ")) is Rect, "Split on any whitespace and lowercase the kind."


def test_unknown_shape():
    with pytest.raises(UnknownShapeError, match="unknown shape 'hexagon'") as info:
        parse_shape("hexagon 1")
    assert info.value.kind == "hexagon", "UnknownShapeError stores the kind."
    assert isinstance(info.value.__cause__, KeyError), "Raise UnknownShapeError(kind) from the KeyError."
    assert isinstance(info.value, ShapeError), "UnknownShapeError is a ShapeError."


@pytest.mark.parametrize("text, message", [
    ("rect 3", "rect needs 2 number(s), got 1"),
    ("circle", "circle needs 1 number(s), got 0"),
    ("square 1 2", "square needs 1 number(s), got 2"),
    ("circle abc", "not a number: 'abc'"),
    ("circle -1", "sizes must be positive"),
    ("rect 3 0", "sizes must be positive"),
    ("", "empty shape line"),
    ("   ", "empty shape line"),
])
def test_value_errors(text, message):
    with pytest.raises(ValueError) as info:
        parse_shape(text)
    assert str(info.value) == message, f"parse_shape({text!r}) should raise ValueError({message!r}), got {str(info.value)!r}."


def test_count_checked_before_numbers():
    with pytest.raises(ValueError, match=r"rect needs 2 number\(s\), got 1"):
        parse_shape("rect abc")


def test_not_a_number_is_chained():
    with pytest.raises(ValueError) as info:
        parse_shape("circle x")
    assert isinstance(info.value.__cause__, ValueError), "Raise ValueError(f'not a number: ...') from the float() error."


def test_parse_shapes_skips_blank_and_comments():
    lines = ["# drawing", "circle 1", "", "   ", "  # indented comment", "rect 2 3"]
    shapes = parse_shapes(lines)
    assert [type(s).__name__ for s in shapes] == ["Circle", "Rect"], "Skip blank lines and lines starting with # (after spaces)."


def test_parse_shapes_from_file_like():
    shapes = parse_shapes(io.StringIO("circle 1\nsquare 2\n"))
    assert [s.kind for s in shapes] == ["circle", "square"], "lines can be any iterable of strings, like a file (lines end with \\n)."


def test_bad_line_number_and_cause():
    lines = ["# my drawing", "circle 1", "", "rect 2 x"]
    with pytest.raises(BadShapeLine) as info:
        parse_shapes(lines)
    err = info.value
    assert str(err) == "line 4: not a number: 'x'", f"Count ALL lines from 1, also skipped ones. Got {str(err)!r}."
    assert (err.line_no, err.line, err.reason) == (4, "rect 2 x", "not a number: 'x'"), "BadShapeLine stores line_no, the stripped line, and reason."
    assert isinstance(err.__cause__, ValueError), "Raise BadShapeLine from the original error."


def test_bad_line_unknown_kind():
    with pytest.raises(BadShapeLine) as info:
        parse_shapes(["circle 1", "blob 2"])
    assert str(info.value) == "line 2: unknown shape 'blob'", "The reason is str() of the UnknownShapeError."
    assert isinstance(info.value.__cause__, UnknownShapeError), "The cause is the UnknownShapeError."


def test_parse_shapes_stops_at_first_error():
    with pytest.raises(BadShapeLine) as info:
        parse_shapes(["blob 1", "rect 1"])
    assert info.value.line_no == 1, "parse_shapes raises at the FIRST bad line."


def test_parse_all_collects_everything():
    lines = ["circle 1", "blob 2", "# note", "rect 1 1", "square -2"]
    with pytest.raises(ExceptionGroup) as info:
        parse_all(lines)
    eg = info.value
    assert eg.message == "2 bad line(s)", f"Group message f'{{n}} bad line(s)'. Got {eg.message!r}."
    assert all(isinstance(e, BadShapeLine) for e in eg.exceptions), "The group holds one BadShapeLine per bad line."
    assert [str(e) for e in eg.exceptions] == ["line 2: unknown shape 'blob'", "line 5: sizes must be positive"], (
        "One BadShapeLine for every bad line, in order, with the right line numbers."
    )
    assert isinstance(eg.exceptions[0].__cause__, UnknownShapeError), "Each BadShapeLine keeps its cause (set __cause__ or use raise ... from inside a try)."
    assert isinstance(eg.exceptions[1].__cause__, ValueError), "Each BadShapeLine keeps its cause."


def test_parse_all_success():
    shapes = parse_all(["circle 1", "", "rect 2 2"])
    assert [s.kind for s in shapes] == ["circle", "rect"], "With no bad lines, parse_all returns the shapes."


def test_register_new_shape(clean_registry):
    @register_shape
    class Triangle(Shape):
        kind = "triangle"
        n_args = 2

        def __init__(self, base, height):
            self.base = base
            self.height = height

        def area(self):
            return self.base * self.height / 2

    assert Triangle.__name__ == "Triangle" and SHAPES["triangle"] is Triangle, "register_shape must RETURN the class, or the name Triangle becomes None."
    t = parse_shape("triangle 3 4")
    assert type(t) is Triangle and t.area() == 6.0, "A registered class works in the parser without changing it."
    assert t.describe() == "triangle area=6.00", "describe is inherited from Shape."


def test_register_duplicate(clean_registry):
    class Fake(Shape):
        kind = "circle"
        n_args = 1

        def __init__(self, r):
            self.r = r

        def area(self):
            return 0

    with pytest.raises(ValueError, match="shape 'circle' is already registered"):
        register_shape(Fake)
    assert SHAPES["circle"] is Circle, "A duplicate must not replace the registered class."


def test_parser_uses_registry_not_if_chain(clean_registry):
    SHAPES.pop("rect")
    with pytest.raises(UnknownShapeError):
        parse_shape("rect 1 2")
