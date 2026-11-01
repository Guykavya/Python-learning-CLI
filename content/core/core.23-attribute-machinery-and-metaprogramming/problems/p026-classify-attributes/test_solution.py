import functools

import pytest

from solution import classify, describe, find_owner


class Spy:
    """A data descriptor whose __get__ must never run during classification."""

    calls = 0

    def __get__(self, instance, owner=None):
        Spy.calls += 1
        raise RuntimeError("classify ran __get__!")

    def __set__(self, instance, value):
        pass


class OnlyDelete:
    def __get__(self, instance, owner=None):
        return 1

    def __delete__(self, instance):
        pass


class GetOnly:
    def __get__(self, instance, owner=None):
        raise RuntimeError("classify ran __get__!")


class FakeDescriptor:
    """Has __set__ and __get__ in its INSTANCE dict, not on its type."""

    def __init__(self):
        self.__set__ = lambda *a: None
        self.__get__ = lambda *a: None


class InheritedSet(OnlyDelete):
    def __set__(self, instance, value):
        pass


class SubSpy(Spy):
    pass


class Base:
    kind = "base"
    tags = ["a"]
    nothing = None

    def hello(self):
        return "hi"

    @classmethod
    def build(cls):
        return cls()

    @staticmethod
    def helper():
        return 1


class Point(Base):
    __slots__ = ("x", "y")
    spy = Spy()

    @property
    def size(self):
        raise RuntimeError("classify ran the property!")

    class Inner:
        pass


class Meta(type):
    meta_only = 42

    @property
    def meta_prop(cls):
        raise RuntimeError("classify looked at the metaclass")

    def __getattr__(cls, name):
        return "invented"


class WithMeta(metaclass=Meta):
    own = 1


class Lazy:
    @functools.cached_property
    def total(self):
        raise RuntimeError("classify ran the cached_property")


def test_find_owner_walks_the_mro():
    assert find_owner(Point, "x") is Point, "Slots live in the __dict__ of the class that declares them."
    assert find_owner(Point, "hello") is Base, "hello is defined in Base; walk cls.__mro__ in order."
    assert find_owner(Point, "__init__") is object, "Names like __init__ come from object at the end of the MRO."
    assert find_owner(Point, "nope") is None, "Return None when no class in the MRO has the name."


def test_find_owner_nearest_class_wins():
    class Child(Base):
        kind = "child"

    assert find_owner(Child, "kind") is Child, (
        "The first class in the MRO that has the name wins; do not keep searching to the end."
    )


def test_data_descriptors():
    assert classify(Point, "x") == "data descriptor", "A slot is a member descriptor with __set__: data descriptor."
    assert classify(Point, "size") == "data descriptor", (
        "property always defines __set__ (it raises if there is no setter), so it is a data descriptor."
    )
    assert classify(Point, "spy") == "data descriptor", "A class with __get__ and __set__ is a data descriptor."

    class Holder:
        d = OnlyDelete()
        s = SubSpy()
        i = InheritedSet()

    assert classify(Holder, "d") == "data descriptor", "Defining __delete__ alone is enough to be a data descriptor."
    assert classify(Holder, "s") == "data descriptor", (
        "SubSpy inherits __set__ from Spy: look through the descriptor TYPE's MRO, not just its own __dict__."
    )
    assert classify(Holder, "i") == "data descriptor", "__set__ defined in a subclass of a descriptor counts too."


def test_non_data_descriptors():
    assert classify(Point, "hello") == "non-data descriptor", "A plain function has __get__ only: non-data descriptor."
    assert classify(Point, "build") == "non-data descriptor", "classmethod objects have __get__ but no __set__."
    assert classify(Point, "helper") == "non-data descriptor", "staticmethod objects have __get__ but no __set__."
    assert classify(Lazy, "total") == "non-data descriptor", (
        "cached_property has no __set__: that is exactly why the value it stores in the instance dict wins later."
    )

    class Holder:
        g = GetOnly()

    assert classify(Holder, "g") == "non-data descriptor", "A class with only __get__ is a non-data descriptor."


def test_plain_values():
    assert classify(Point, "kind") == "plain", "A string is not a descriptor."
    assert classify(Point, "tags") == "plain", "A list is not a descriptor."
    assert classify(Point, "nothing") == "plain", "None stored in the class is still a plain attribute, not missing."
    assert classify(Point, "Inner") == "plain", "A nested class is a plain attribute: type objects have no __get__."


def test_protocol_is_looked_up_on_the_type():
    class Holder:
        fake = FakeDescriptor()

    assert classify(Holder, "fake") == "plain", (
        "__set__/__get__ stored on the object itself do not count. Check type(obj), e.g. hasattr(type(obj), '__set__')."
    )


def test_missing():
    assert classify(Point, "nope") == "missing", "Not in any __dict__ of the MRO: 'missing'."
    assert classify(WithMeta, "meta_only") == "missing", (
        "meta_only lives on the metaclass, which is not in WithMeta.__mro__. Walk the MRO, do not use hasattr/getattr."
    )
    assert classify(WithMeta, "whatever") == "missing", (
        "The metaclass __getattr__ invents values for getattr(WithMeta, ...). classify must not be fooled by it."
    )
    assert classify(WithMeta, "own") == "plain", "own is in WithMeta.__dict__."


def test_nothing_is_triggered():
    Spy.calls = 0
    classify(Point, "spy")
    classify(Point, "size")
    classify(Lazy, "total")
    classify(WithMeta, "meta_prop")
    describe(Point)
    assert Spy.calls == 0, "classify called a descriptor's __get__. Read vars(klass)[name] instead of getattr."


def test_describe_own_names_in_order():
    assert describe(Point) == {
        "x": "data descriptor",
        "y": "data descriptor",
        "spy": "data descriptor",
        "size": "data descriptor",
        "Inner": "plain",
    }, "describe lists only Point's own names (not Base's), skips names starting with '__', and keeps definition order."
    assert list(describe(Base)) == ["kind", "tags", "nothing", "hello", "build", "helper"], (
        "describe must keep the order in which the class body defined the names."
    )
    assert describe(Base)["build"] == "non-data descriptor", "describe must use the same rules as classify."


def test_describe_skips_dunders_only():
    class C:
        _private = 1

        def __repr__(self):
            return "C"

    result = describe(C)
    assert result == {"_private": "plain"}, (
        "Skip names that start with '__' (like __module__, __repr__), but keep single-underscore names."
    )
