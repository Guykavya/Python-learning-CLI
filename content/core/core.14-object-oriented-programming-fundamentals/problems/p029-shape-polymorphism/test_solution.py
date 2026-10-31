import math

import pytest

from solution import Circle, Rectangle, Shape, Square, Triangle, largest, report, total_area


class Hexagon(Shape):
    """A shape the solution has never seen: the functions must still work."""
    name = "hexagon"

    def __init__(self, side):
        self.side = side

    def area(self):
        return 3 * math.sqrt(3) / 2 * self.side ** 2


def test_areas():
    assert abs(Circle(2).area() - math.pi * 4) < 1e-9, "Circle area is math.pi * r * r."
    assert Rectangle(2, 3).area() == 6, "Rectangle area is w * h."
    assert Square(2).area() == 4, "Square(2) is a 2 x 2 rectangle."
    assert abs(Triangle(3, 4, 5).area() - 6.0) < 1e-9, "Heron's formula gives 6.0 for sides 3, 4, 5."


def test_names_and_describe():
    assert [s.name for s in (Shape(), Circle(1), Rectangle(1, 1), Square(1), Triangle(2, 2, 2))] == [
        "shape", "circle", "rectangle", "square", "triangle",
    ], "Give every class its own class attribute `name`."
    assert Circle(2).describe() == "circle with area 12.57", "describe() is f'{self.name} with area {self.area():.2f}'."
    assert Square(2).describe() == "square with area 4.00", "Square inherits describe(); self.name finds 'square'."


def test_base_area_not_implemented():
    with pytest.raises(NotImplementedError):
        Shape().area()


def test_square_is_a_rectangle():
    sq = Square(3)
    assert isinstance(sq, Rectangle), "Square must be a subclass of Rectangle."
    assert (sq.side, sq.w, sq.h) == (3, 3, 3), "Square(3) has side 3 and, through super().__init__(side, side), w = h = 3."
    assert "area" not in vars(Square), "Square should reuse Rectangle.area instead of defining its own."


def test_attributes_stored():
    assert Circle(5).r == 5, "Store the radius as r."
    r = Rectangle(2, 7)
    assert (r.w, r.h) == (2, 7), "Store w and h."
    t = Triangle(3, 4, 5)
    assert (t.a, t.b, t.c) == (3, 4, 5), "Store a, b and c."


def test_invalid_lengths():
    for make in (lambda: Circle(0), lambda: Circle(-1), lambda: Rectangle(2, 0),
                 lambda: Square(-3), lambda: Triangle(3, 4, 0)):
        with pytest.raises(ValueError):
            make()


def test_impossible_triangle():
    for sides in ((1, 2, 3), (1, 1, 5), (10, 2, 3)):
        try:
            Triangle(*sides)
        except ValueError:
            continue
        pytest.fail(
            f"Triangle{sides} was accepted. Every side must be shorter than the other two together; "
            "check the longest side, wherever it is in the argument list."
        )
    assert Triangle(2, 3, 4).area() > 0, "2, 3, 4 is a real triangle (4 < 2 + 3)."


def test_total_area():
    shapes = [Rectangle(2, 3), Circle(2), Square(2), Triangle(3, 4, 5)]
    assert total_area(shapes) == 28.57, "6 + 12.566... + 4 + 6 = 28.566..., rounded to 28.57."
    assert total_area([]) == 0, "The total of no shapes is 0."


def test_largest():
    shapes = [Rectangle(2, 3), Circle(2), Square(2), Triangle(3, 4, 5)]
    assert largest(shapes) is shapes[1], "largest returns the shape object itself, here the circle."
    tie = [Rectangle(2, 3), Triangle(3, 4, 5)]
    assert largest(tie) is tie[0], "Equal areas: return the first one. Use > not >= when you compare."
    with pytest.raises(ValueError):
        largest([])


def test_report():
    shapes = [Rectangle(2, 3), Circle(2), Square(2), Triangle(3, 4, 5)]
    assert report(shapes) == [
        "1. circle with area 12.57",
        "2. rectangle with area 6.00",
        "3. triangle with area 6.00",
        "4. square with area 4.00",
    ], "Biggest area first, numbered from 1; the rectangle and triangle tie at 6, so they keep input order."
    assert report([]) == [], "No shapes, no lines."


def test_functions_work_with_a_new_shape():
    shapes = [Square(1), Hexagon(2)]
    assert report(shapes) == ["1. hexagon with area 10.39", "2. square with area 1.00"], (
        "report must work for any Shape subclass. Call shape.area() and shape.describe(); do not check the type."
    )
    assert largest(shapes) is shapes[1], "largest must work for a new kind of shape too."
    assert total_area(shapes) == 11.39, "total_area must work for a new kind of shape too."


def test_report_does_not_change_input():
    shapes = [Square(1), Circle(1)]
    report(shapes)
    assert shapes[0].name == "square", "report must not sort the caller's list in place. Use sorted(), not list.sort()."
