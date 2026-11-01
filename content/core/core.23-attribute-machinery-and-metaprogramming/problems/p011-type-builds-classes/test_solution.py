import pytest

from solution import make_record_class


def test_class_has_the_given_name():
    Point = make_record_class("Point", ["x", "y"])
    assert isinstance(Point, type), "make_record_class must return a class."
    assert Point.__name__ == "Point", "type(name, bases, namespace) sets __name__ to the name you pass."
    assert Point.__qualname__ == "Point", (
        "__qualname__ must be the plain name too (a class statement inside the function would give "
        "'make_record_class.<locals>...')."
    )


def test_init_sets_fields_in_order():
    Point = make_record_class("Point", ["x", "y"])
    p = Point(3, 4)
    assert (p.x, p.y) == (3, 4), "__init__ assigns the values to the fields in the order given."


def test_wrong_number_of_values():
    Point = make_record_class("Point", ["x", "y"])
    with pytest.raises(TypeError) as info:
        Point(1)
    assert "2" in str(info.value), "The TypeError must say how many values are expected (2)."
    with pytest.raises(TypeError):
        Point(1, 2, 3)


def test_repr():
    Person = make_record_class("Person", ("name", "age"))
    assert repr(Person("Ada", 36)) == "Person(name='Ada', age=36)", "repr is Name(field=repr(value), ...)."
    Empty = make_record_class("Empty", [])
    assert repr(Empty()) == "Empty()", "A class with no fields has repr 'Empty()'."


def test_slots_no_instance_dict():
    Point = make_record_class("Point", ["x", "y"])
    assert Point.__slots__ == ("x", "y"), "__slots__ must be a tuple of the field names."
    p = Point(1, 2)
    assert not hasattr(p, "__dict__"), "With __slots__ in the namespace, instances have no __dict__."
    with pytest.raises(AttributeError):
        p.z = 3
    p.x = 10
    assert p.x == 10, "Declared fields can still be reassigned."


def test_equality():
    Point = make_record_class("Point", ["x", "y"])
    assert Point(1, 2) == Point(1, 2), "Two records of the same class with equal values are equal."
    assert Point(1, 2) != Point(2, 1), "Order of values matters."
    assert (Point(1, 2) == (1, 2)) is False, "A record is not equal to a tuple. Return NotImplemented for other types."


def test_different_classes_are_never_equal():
    Point = make_record_class("Point", ["x", "y"])
    Vector = make_record_class("Vector", ["x", "y"])
    assert Point(1, 2) != Vector(1, 2), (
        "Records of different classes are not equal even with the same fields: compare type(self) and type(other)."
    )


def test_classes_are_independent():
    A = make_record_class("A", ["a"])
    B = make_record_class("B", ["b", "c"])
    assert repr(A(1)) == "A(a=1)" and repr(B(2, 3)) == "B(b=2, c=3)", (
        "Each call builds its own class with its own fields."
    )
    assert A is not make_record_class("A", ["a"]), "Every call returns a new class object."


def test_input_list_is_copied():
    fields = ["x"]
    Rec = make_record_class("Rec", fields)
    fields.append("y")
    assert repr(Rec(1)) == "Rec(x=1)", "Changing the caller's list afterwards must not change the class. Copy it into a tuple."
