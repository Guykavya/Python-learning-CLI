import pytest

from solution import Typed


def make_point_class():
    class Point:
        x = Typed(int)
        y = Typed(int, float)

        def __init__(self, x, y):
            self.x = x
            self.y = y

    return Point


def test_valid_values_are_stored_and_read_back():
    Point = make_point_class()
    p = Point(1, 2.5)
    assert (p.x, p.y) == (1, 2.5), "Values that pass the check must be stored and returned unchanged."
    p.y = 7
    assert p.y == 7, "y accepts int as well as float."


def test_each_instance_has_its_own_values():
    Point = make_point_class()
    a, b = Point(1, 1), Point(2, 2)
    assert a.x == 1 and b.x == 2, (
        f"a.x is {a.x}, b.x is {b.x}. If both are 2, the value is stored ON THE DESCRIPTOR, which every "
        "instance shares. Store it per instance (for example in instance.__dict__[self.name])."
    )


def test_wrong_type_raises_type_error_naming_class_and_field():
    Point = make_point_class()
    p = Point(1, 2)
    with pytest.raises(TypeError) as err:
        p.x = "3"
    msg = str(err.value)
    assert "Point.x" in msg, f"The message must name the class and field as 'Point.x'. Got: {msg!r}"
    assert "must be int" in msg and "got str" in msg, (
        f"The message should read 'Point.x must be int, got str'. Got: {msg!r}"
    )


def test_message_lists_all_expected_types_in_order():
    Point = make_point_class()
    p = Point(1, 2)
    with pytest.raises(TypeError) as err:
        p.y = [1]
    msg = str(err.value)
    assert "Point.y must be int or float, got list" in msg, (
        f"With Typed(int, float) the message must be 'Point.y must be int or float, got list'. Got: {msg!r}"
    )


def test_rejected_value_keeps_the_old_one():
    Point = make_point_class()
    p = Point(1, 2)
    with pytest.raises(TypeError):
        p.x = "3"
    assert p.x == 1, "Check the type BEFORE storing: after a rejected assignment the old value must remain."


def test_check_runs_in_init_too():
    Point = make_point_class()
    with pytest.raises(TypeError):
        Point("1", 2)


def test_values_are_not_converted():
    class Money:
        amount = Typed(float)

    m = Money()
    with pytest.raises(TypeError):
        m.amount = 3
    with pytest.raises(TypeError):
        m.amount = "3.5"
    m.amount = 3.5
    assert m.amount == 3.5, "Typed checks; it never converts. 3 is an int, not a float, so Typed(float) rejects it."


def test_subclasses_of_the_type_are_accepted():
    class Name(str):
        pass

    class Person:
        name = Typed(str)

    p = Person()
    p.name = Name("Ann")
    assert p.name == "Ann", "Use isinstance: an instance of a subclass of str is a str."


def test_bool_is_rejected_for_int_fields():
    Point = make_point_class()
    p = Point(1, 2)
    with pytest.raises(TypeError) as err:
        p.x = True
    assert "got bool" in str(err.value), (
        "True is an int subclass, but a bool in an int field is almost always a bug: reject it and say 'got bool'."
    )
    with pytest.raises(TypeError):
        p.y = False
    assert (p.x, p.y) == (1, 2), "Rejected bools must not be stored."


def test_bool_allowed_when_asked_for():
    class Flags:
        active = Typed(bool)
        count = Typed(int, allow_bool=True)

    f = Flags()
    f.active = True
    f.count = False
    assert f.active is True and f.count is False, (
        "bool is accepted when bool is one of the types, or when allow_bool=True was given."
    )
    with pytest.raises(TypeError):
        f.active = 1


def test_class_access_returns_the_descriptor():
    Point = make_point_class()
    assert isinstance(Point.x, Typed), "Point.x on the CLASS must return the Typed object (instance is None)."
    assert Point.x is Point.__dict__["x"], "Return self from __get__ when instance is None."
    assert Point.x.name == "x" and Point.y.name == "y", "__set_name__ must store the field name in .name."


def test_unset_field_raises_attribute_error():
    class Item:
        price = Typed(float)

    item = Item()
    with pytest.raises(AttributeError) as err:
        item.price
    assert "price" in str(err.value), "The AttributeError must name the field."
    assert hasattr(item, "price") is False, (
        "hasattr must return False for an unset field. That only works if you raise AttributeError, not KeyError."
    )
    assert getattr(item, "price", 0.0) == 0.0, "getattr with a default relies on AttributeError too."


def test_delete():
    Point = make_point_class()
    p = Point(1, 2)
    del p.x
    assert not hasattr(p, "x"), "After del p.x, reading p.x must raise AttributeError."
    with pytest.raises(AttributeError):
        del p.x
    p.x = 5
    assert p.x == 5, "A deleted field can be set again."


def test_bad_construction():
    with pytest.raises(TypeError):
        Typed()
    with pytest.raises(TypeError):
        Typed("int")
