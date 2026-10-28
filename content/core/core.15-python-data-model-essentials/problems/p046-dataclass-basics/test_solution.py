import dataclasses

import pytest

from solution import Point, Product


def test_both_are_dataclasses():
    assert dataclasses.is_dataclass(Point), "Decorate Point with @dataclass (from dataclasses import dataclass)."
    assert dataclasses.is_dataclass(Product), "Decorate Product with @dataclass."


def test_generated_init_with_defaults():
    p = Point(3)
    assert (p.x, p.y) == (3, 0), "Point(3) uses the default y=0: write `y: int = 0` in the class body."
    q = Product("pen", 2.5)
    assert (q.name, q.price, q.qty) == ("pen", 2.5, 0), "Product(name, price, qty=0): qty defaults to 0."
    assert Product("ink", 4.0, qty=3).qty == 3, "Keyword arguments work with the generated __init__."


def test_fields_in_order():
    assert [f.name for f in dataclasses.fields(Point)] == ["x", "y"], "Fields are the annotated names, in the order written."
    assert [f.name for f in dataclasses.fields(Product)] == ["name", "price", "qty"], "Declare name, price, qty in this order."


def test_generated_repr():
    assert repr(Point(1, 2)) == "Point(x=1, y=2)", "The generated repr is Point(x=1, y=2). Do not write your own __repr__."
    assert repr(Product("pen", 2.5, 3)) == "Product(name='pen', price=2.5, qty=3)", "Strings show quotes in the generated repr."


def test_generated_eq():
    assert Point(1, 2) == Point(1, 2), "@dataclass generates __eq__ comparing all fields in order."
    assert Point(1, 2) != Point(2, 1), "Different field values are not equal."
    assert Point(1, 0) == Point(1), "A defaulted field is part of the comparison."
    assert (Point(1, 2) == (1, 2)) is False, "A dataclass is never equal to a tuple (different classes)."


def test_methods_still_work():
    assert Point(3, 4).distance_to_origin() == 5.0, "Methods are written in the class body as usual."
    assert Product("pen", 2.5, 4).total() == 10.0, "total() is price * qty."


def test_asdict_and_replace():
    p = Point(1, 2)
    assert dataclasses.asdict(p) == {"x": 1, "y": 2}, "asdict() turns the fields into a dict; it needs a real dataclass."
    q = dataclasses.replace(p, y=9)
    assert q == Point(1, 9) and p == Point(1, 2), "replace() makes a modified COPY; the original stays unchanged."


def test_default_dataclass_is_unhashable():
    with pytest.raises(TypeError):
        {Point(1, 2)}   # eq=True without frozen removes __hash__ (see problem 054)


def test_missing_arguments():
    with pytest.raises(TypeError):
        Point()
    with pytest.raises(TypeError):
        Product("pen")
