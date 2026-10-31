import typing
from collections.abc import Iterable
from dataclasses import dataclass
from typing import get_args, get_origin, get_type_hints

import solution
from solution import classify, names_of, total_area


class Circle:
    def __init__(self, r):
        self.r = r

    def area(self):
        return 3 * self.r**2


@dataclass
class Person:
    name: str


class Pet:
    name = 42


class NamedCircle(Circle):
    name = "disc"


class Silent:
    pass


def test_protocols_are_runtime_checkable():
    HasArea, Named = solution.HasArea, solution.Named
    assert typing.is_protocol(HasArea) and typing.is_protocol(Named), "Both classes must be Protocols."
    assert typing.get_protocol_members(HasArea) == frozenset({"area"}), "HasArea has one member: area."
    assert typing.get_protocol_members(Named) == frozenset({"name"}), "Named has one member: the attribute name."
    assert get_type_hints(Named) == {"name": str}, "Named declares name: str."
    try:
        ok = isinstance(Circle(1), HasArea) and not isinstance(5, HasArea) and isinstance(Person("a"), Named)
    except TypeError:
        raise AssertionError("isinstance() raised TypeError: put @runtime_checkable above both protocol classes.") from None
    assert ok, "isinstance(Circle(1), HasArea) is True, isinstance(5, HasArea) is False, isinstance(Person('a'), Named) is True."


def test_function_hints():
    h = get_type_hints(total_area)
    assert get_origin(h["things"]) is Iterable and get_args(h["things"]) == (object,), "total_area(things: Iterable[object])."
    assert h["return"] is float, "total_area -> float."
    assert get_type_hints(names_of)["return"] == list[str], "names_of -> list[str]."
    assert get_type_hints(classify) == {"thing": object, "return": str}, "classify(thing: object) -> str."


def test_total_area():
    assert total_area([Circle(1), "text", 5, Circle(2)]) == 15.0, "Add up area() of the items that have it (3 + 12) and skip the rest."
    assert total_area([]) == 0.0, "No items: 0.0."
    assert total_area(["a", None, 3]) == 0.0, "Nothing has an area: 0.0."
    assert total_area(x for x in [Circle(1)]) == 3.0, "things may be a generator."


def test_names_of():
    assert names_of([Person("ana"), 5, Person("ben")]) == ["ana", "ben"], "Collect the names of the Named items, in order."
    assert names_of([Pet(), Person("c")]) == ["c"], (
        "Pet has a name that is 42. isinstance(Pet(), Named) is True (the runtime check only looks at the NAME), so also test isinstance(t.name, str)."
    )
    assert names_of([NamedCircle(1)]) == ["disc"], "A class with both area and name is also Named."
    assert names_of([]) == [], "No items: empty list."


def test_classify():
    assert classify(NamedCircle(1)) == "both", "area and name: 'both'."
    assert classify(Circle(1)) == "area", "Only area: 'area'."
    assert classify(Person("x")) == "name", "Only name: 'name'."
    assert classify(Pet()) == "name", "A Pet has a name attribute: for classify it counts as Named even though 42 is not a str."
    assert classify(Silent()) == "neither", "Neither: 'neither'."
    assert classify(5) == "neither", "An int has neither."
