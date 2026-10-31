import math
from abc import ABC

import pytest

from solution import Circle, Shape, Square


def test_shape_is_abstract():
    assert issubclass(Shape, ABC), "Shape must inherit from abc.ABC."
    with pytest.raises(TypeError):
        Shape()


def test_abstract_methods_are_area_and_perimeter():
    assert getattr(Shape, "__abstractmethods__", frozenset()) == frozenset({"area", "perimeter"}), (
        "Exactly area and perimeter should be abstract (@abstractmethod). describe is a normal method."
    )


def test_square():
    s = Square(3)
    assert isinstance(s, Shape), "Square must be a subclass of Shape."
    assert s.area() == 9, "Square(3).area() is 3 ** 2 = 9."
    assert s.perimeter() == 12, "Square(3).perimeter() is 4 * 3 = 12."


def test_circle():
    c = Circle(2)
    assert isinstance(c, Shape), "Circle must be a subclass of Shape."
    assert math.isclose(c.area(), math.pi * 4), "Circle(2).area() is pi * 2 ** 2."
    assert math.isclose(c.perimeter(), 4 * math.pi), "Circle(2).perimeter() is 2 * pi * 2."


def test_describe():
    assert Square(3).describe() == "Square: area 9.00, perimeter 12.00", "Use :.2f for both numbers and type(self).__name__ for the name."
    assert Circle(1).describe() == "Circle: area 3.14, perimeter 6.28", "describe() is inherited and calls the Circle's own area() and perimeter()."


def test_describe_is_written_once():
    assert "describe" not in vars(Square) and "describe" not in vars(Circle), "Write describe() once, in Shape. Subclasses inherit it."


def test_describe_works_for_new_subclass():
    class Rect(Shape):
        def area(self):
            return 6

        def perimeter(self):
            return 10

    assert Rect().describe() == "Rect: area 6.00, perimeter 10.00", (
        "describe() must use type(self).__name__ and self.area()/self.perimeter(), not a fixed name or type checks."
    )


def test_subclass_missing_a_method_cannot_be_created():
    class Half(Shape):
        def area(self):
            return 1

    try:
        Half()
    except TypeError:
        pass
    else:
        pytest.fail("A subclass that does not define perimeter() must fail with TypeError. Mark perimeter with @abstractmethod.")


def test_polymorphic_total():
    shapes = [Square(2), Circle(2)]
    assert round(sum(s.area() for s in shapes), 2) == 16.57, "4 + 4 * pi is about 16.57."
