import ast
from pathlib import Path

import pytest

import solution
from solution import Prop


def make_circle_class():
    class Circle:
        def __init__(self, r):
            self._r = r

        @Prop
        def radius(self):
            """The radius in cm."""
            return self._r

        @radius.setter
        def radius(self, value):
            if value < 0:
                raise ValueError("radius must be >= 0")
            self._r = value

        @radius.deleter
        def radius(self):
            del self._r

        @Prop
        def area(self):
            return 3 * self._r ** 2

    return Circle


def test_getter_runs_on_read():
    Circle = make_circle_class()
    c = Circle(2)
    assert c.radius == 2, "c.radius must call fget(c)."
    assert c.area == 12, "c.area must call the area function with the instance."


def test_setter_runs_on_assignment():
    Circle = make_circle_class()
    c = Circle(2)
    c.radius = 5
    assert c._r == 5 and c.radius == 5, "c.radius = 5 must call fset(c, 5)."
    assert "radius" not in vars(c), "The setter decides where data goes; Prop itself must not store 'radius' in the instance dict."
    with pytest.raises(ValueError):
        c.radius = -1


def test_read_only_refuses_assignment():
    Circle = make_circle_class()
    c = Circle(2)
    with pytest.raises(AttributeError) as err:
        c.area = 1
    assert "area" in str(err.value), "The AttributeError must name the property ('area')."
    assert "area" not in vars(c), (
        "Without a setter, assignment must raise and store NOTHING. Prop must always define __set__ "
        "(a data descriptor); otherwise c.area = 1 quietly lands in the instance dict and hides the property."
    )
    assert c.area == 12


def test_deleter():
    Circle = make_circle_class()
    c = Circle(2)
    del c.radius
    assert not hasattr(c, "_r"), "del c.radius must call fdel(c)."
    with pytest.raises(AttributeError) as err:
        del c.area
    assert "area" in str(err.value), "No deleter: AttributeError naming the property."


def test_missing_getter():
    class T:
        x = Prop()

    with pytest.raises(AttributeError) as err:
        T().x
    assert "x" in str(err.value), "Reading a Prop without fget raises AttributeError naming it ('x', from __set_name__)."


def test_class_access_returns_the_prop():
    Circle = make_circle_class()
    assert isinstance(Circle.radius, Prop), "Circle.radius on the class must return the Prop itself."
    assert Circle.radius.fget.__name__ == "radius", "Keep the getter as .fget."
    assert Circle.radius.fset is not None and Circle.radius.fdel is not None, (
        "After @radius.setter and @radius.deleter, the final Prop has all three functions."
    )
    assert Circle.area.fset is None, "area has no setter."


def test_doc_comes_from_getter_or_argument():
    Circle = make_circle_class()
    assert Circle.radius.__doc__ == "The radius in cm.", (
        "__doc__ must come from fget, and .setter/.deleter must carry it over to the new Prop."
    )
    assert Prop(lambda self: 1, doc="explicit").__doc__ == "explicit", "An explicit doc wins."


def test_setter_returns_a_new_object_and_keeps_the_old_one():
    def get(self):
        return 1

    def put(self, value):
        pass

    def remove(self):
        pass

    original = Prop(get)
    with_setter = original.setter(put)
    assert with_setter is not original, ".setter() must return a NEW Prop, not change and return self."
    assert original.fset is None, "The original Prop must be unchanged after .setter()."
    assert with_setter.fget is get and with_setter.fset is put, "The new Prop has the old getter and the new setter."
    full = with_setter.deleter(remove)
    assert full.fget is get and full.fset is put and full.fdel is remove, ".deleter() keeps fget and fset."
    assert with_setter.fdel is None, ".deleter() must not change the Prop it was called on."
    replaced = full.getter(remove)
    assert replaced.fget is remove and replaced.fset is put and full.fget is get, ".getter() works the same way."


def test_subclass_can_add_a_setter_without_changing_the_base():
    class Base:
        def __init__(self):
            self._v = 1

        @Prop
        def v(self):
            return self._v

    class Child(Base):
        @Base.v.setter
        def v(self, value):
            self._v = value * 2

    child = Child()
    child.v = 3
    assert child.v == 6, "Child's v has Base's getter and its own setter."
    with pytest.raises(AttributeError):
        Base().v = 3
    assert Base.v.fset is None, (
        "Adding a setter in Child changed Base.v. .setter() must build a new object, never modify self."
    )


def test_subclass_of_prop_keeps_its_type():
    class LoggedProp(Prop):
        pass

    p = LoggedProp(lambda self: 1).setter(lambda self, value: None)
    assert type(p) is LoggedProp, "Build the new object with type(self)(...), so subclasses of Prop survive .setter()."


def test_prop_is_not_the_builtin():
    assert not issubclass(Prop, property), "Write Prop yourself; do not subclass property."
    tree = ast.parse(Path(solution.__file__).read_text())
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "property" not in used, "Do not use the built-in property anywhere in solution.py."
