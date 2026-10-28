import pytest

from solution import all_definitions, defined_in


class Base:
    kind = "base"

    def save(self):
        return "Base.save"

    def load(self):
        return "Base.load"


class Left(Base):
    def save(self):
        return "Left.save"


class Right(Base):
    kind = "right"

    def load(self):
        return "Right.load"


class Child(Left, Right):
    def __init__(self):
        self.only_on_instance = 1


class Plain:
    pass


def test_found_in_first_parent():
    assert defined_in(Child, "save") is Left, "Child does not define save, Left does. Check name in vars(klass), not hasattr. Return the class object, not its name."


def test_diamond_uses_mro_not_depth_first():
    assert defined_in(Child, "load") is Right, (
        "The MRO is Child, Left, Right, Base, object. Right comes BEFORE Base. "
        "Walking Left -> Base -> Right (depth first, or via __bases__) gives the wrong answer. Use cls.__mro__."
    )
    assert defined_in(Child, "kind") is Right, "Class attributes count too: Right.kind overrides Base.kind."


def test_own_definition_first():
    assert defined_in(Child, "__init__") is Child, "Child defines __init__ itself, so the answer is Child."
    assert defined_in(Left, "save") is Left, "A class that defines the name itself is the first in its own MRO."


def test_object_at_the_end():
    assert defined_in(Plain, "__init__") is object, "Every MRO ends with object, which defines __init__."
    assert defined_in(Plain, "__repr__") is object, "object defines __repr__ too."


def test_missing_name():
    assert defined_in(Child, "missing") is None, "Return None when no class in the MRO defines the name."


def test_instance_attributes_do_not_count():
    assert defined_in(Child, "only_on_instance") is None, (
        "only_on_instance is set in __init__ on each instance. It is not in any class's vars(). "
        "Do not use hasattr on an instance."
    )


def test_inherited_name_is_not_in_child_vars():
    # hasattr(Child, "save") is True, but vars(Child) has no "save".
    assert defined_in(Child, "save") is not Child, "hasattr(cls, name) is True for inherited names too. Check name in vars(klass)."


def test_later_assignment_to_class_counts():
    class Late(Base):
        pass

    assert defined_in(Late, "extra") is None, "Late does not have extra yet."
    Late.extra = 42
    assert defined_in(Late, "extra") is Late, "Assigning to the class later puts the name into vars(Late)."


def test_all_definitions_order():
    assert all_definitions(Child, "load") == ["Right", "Base"], "List every definer in MRO order: Right first, then Base."
    assert all_definitions(Child, "save") == ["Left", "Base"], "save is defined in Left and in Base."
    assert all_definitions(Child, "kind") == ["Right", "Base"], "kind is a class attribute in Right and Base."


def test_all_definitions_returns_names():
    result = all_definitions(Child, "__init__")
    assert result == ["Child", "object"], "Return class NAMES (klass.__name__) as strings, in MRO order."


def test_all_definitions_empty():
    assert all_definitions(Child, "missing") == [], "Nobody defines it: return an empty list."


def test_needs_a_class():
    with pytest.raises(TypeError, match="defined_in\\(\\) needs a class"):
        defined_in(Child(), "save")
    with pytest.raises(TypeError, match="all_definitions\\(\\) needs a class"):
        all_definitions("Child", "save")


def test_works_for_builtins():
    assert defined_in(bool, "__and__") is bool, "bool defines its own __and__."
    assert defined_in(bool, "bit_length") is int, "bool inherits bit_length from int."
