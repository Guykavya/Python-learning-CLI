import pytest

from solution import Registry, auto_repr


def test_plain_decorator_registers_under_lowercase_class_name():
    reg = Registry()

    @reg
    class Dog:
        pass

    assert isinstance(Dog, type), "The decorator must return the class itself (`return cls`), otherwise the name Dog becomes None."
    assert reg["dog"] is Dog, "@reg registers the class under cls.__name__.lower()."
    assert Dog.registered_name == "dog", "The decorator also sets the class attribute registered_name."


def test_decorator_with_name():
    reg = Registry()

    @reg(name="woof")
    class Dog:
        pass

    assert isinstance(Dog, type), "@reg(name=...) must also return the class from the inner decorator."
    assert reg["woof"] is Dog and "dog" not in reg, "With name='woof' the class is stored under 'woof' only."
    assert Dog.registered_name == "woof", "registered_name holds the name that was used."


def test_both_forms_in_one_registry_and_helpers():
    reg = Registry()

    @reg
    class Zebra:
        pass

    @reg(name="ant")
    class Bee:
        pass

    assert len(reg) == 2, "len(registry) is the number of registered classes."
    assert reg.names() == ["ant", "zebra"], "names() returns the registered names sorted."
    assert "ant" in reg and "bee" not in reg, "`in` checks names."


def test_duplicate_name_rejected_and_registry_unchanged():
    reg = Registry()

    @reg
    class Cat:
        pass

    with pytest.raises(ValueError):
        @reg
        class cat:
            pass
    assert reg["cat"] is Cat, "A rejected duplicate must not replace the original class."
    assert len(reg) == 1, "A rejected duplicate must not be added."


def test_unknown_name():
    reg = Registry()
    with pytest.raises(KeyError) as info:
        reg["nope"]
    assert "nope" in str(info.value), "The KeyError message should name the missing key."


def test_registries_are_independent():
    a, b = Registry(), Registry()

    @a
    class X:
        pass

    assert "x" in a and "x" not in b and len(b) == 0, "Each Registry has its own dict created in __init__ (not a class attribute)."


def test_registered_classes_still_work_normally():
    reg = Registry()

    @reg(name="p")
    class Point:
        def __init__(self, x):
            self.x = x

    assert reg["p"](4).x == 4 and Point(5).x == 5, "The registry stores the real class: calling it creates objects."


def test_auto_repr_basic():
    @auto_repr
    class Point:
        _fields = ("x", "y")

        def __init__(self, x, y):
            self.x, self.y = x, y

    assert repr(Point(1, "a")) == "Point(x=1, y='a')", "auto_repr builds Name(field=repr(value), ...) from the names in cls._fields; use !r for values."
    assert isinstance(Point, type), "auto_repr must return the class."


def test_auto_repr_uses_actual_class_name_and_current_values():
    @auto_repr
    class Base:
        _fields = ("v",)

        def __init__(self, v):
            self.v = v

    class Child(Base):
        pass

    c = Child([1])
    c.v.append(2)
    assert repr(c) == "Child(v=[1, 2])", "Use type(self).__name__ (so subclasses show their own name) and read the CURRENT values with getattr."


def test_decorators_can_be_stacked():
    reg = Registry()

    @reg(name="pt")
    @auto_repr
    class Pt:
        _fields = ("n",)

        def __init__(self, n):
            self.n = n

    assert repr(reg["pt"](3)) == "Pt(n=3)", "Both decorators return the class, so they can be stacked."
