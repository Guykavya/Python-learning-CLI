import pytest

from solution import EnumMeta, MiniEnum


def make_color():
    class Color(MiniEnum):
        RED = 1
        GREEN = 2
        BLUE = 3
        _private = 99

        def describe(self):
            return f"{self.name} is {self.value}"

        @classmethod
        def default(cls):
            return cls.RED

        @staticmethod
        def help():
            return "pick a color"

        @property
        def is_warm(self):
            return self is type(self).RED

    return Color


def test_members_are_instances_with_name_and_value():
    Color = make_color()
    assert type(Color.RED) is Color, "Each member must be an instance of the enum class (create it with object.__new__(cls))."
    assert isinstance(Color.GREEN, Color) and isinstance(Color, EnumMeta), "Members are Color instances; Color is an EnumMeta instance."
    assert Color.RED.name == "RED" and Color.RED.value == 1, "name and value come from the class body."
    assert Color.BLUE.value == 3, "Every plain attribute becomes a member."


def test_non_members_stay_normal_attributes():
    Color = make_color()
    assert len(Color) == 3, (
        "Only RED, GREEN, BLUE are members: skip names starting with '_' and values whose type has __get__ "
        "(functions, classmethod, staticmethod, property)."
    )
    assert Color._private == 99, "_private stays a plain class attribute."
    assert Color.GREEN.describe() == "GREEN is 2", "Methods in the body must work on members."
    assert Color.default() is Color.RED, "classmethods keep working."
    assert Color.help() == "pick a color", "staticmethods keep working."
    assert Color.RED.is_warm is True and Color.BLUE.is_warm is False, "Properties keep working on members."


def test_iteration_and_len_in_definition_order():
    Color = make_color()
    assert [m.name for m in Color] == ["RED", "GREEN", "BLUE"], (
        "Define __iter__ on the metaclass, yielding members in definition order (the namespace dict keeps it)."
    )
    assert list(Color) == [Color.RED, Color.GREEN, Color.BLUE], "Iteration yields the member objects themselves."
    assert len(Color) == 3, "Define __len__ on the metaclass: len(Color) calls type(Color).__len__(Color)."


def test_lookup_by_value_returns_the_same_object():
    Color = make_color()
    assert Color(2) is Color.GREEN, "Color(2) must return the existing member: override __call__ on the metaclass."
    assert Color(1) is Color(1), "Lookup never creates a new object."
    with pytest.raises(ValueError) as info:
        Color(7)
    assert str(info.value) == "7 is not a valid Color", "Unknown value: ValueError(f'{value!r} is not a valid {name}')."


def test_lookup_by_name():
    Color = make_color()
    assert Color["BLUE"] is Color.BLUE, "Color['BLUE'] needs __getitem__ on the metaclass."
    with pytest.raises(KeyError):
        Color["PURPLE"]


def test_membership():
    Color = make_color()
    assert Color.RED in Color, "Members are in the enum (define __contains__ on the metaclass)."
    assert 1 not in Color, "A raw value is not a member: 1 in Color must be False."
    assert "RED" not in Color, "A name is not a member either."

    class Other(MiniEnum):
        RED = 1

    assert Other.RED not in Color, "A member of a different enum with the same name and value is not in Color."


def test_members_are_immutable():
    Color = make_color()
    with pytest.raises(AttributeError):
        Color.RED.value = 10
    with pytest.raises(AttributeError):
        Color.RED.name = "ROSE"
    with pytest.raises(AttributeError):
        Color.RED.extra = 1
    with pytest.raises(AttributeError):
        del Color.RED.value
    assert Color.RED.value == 1 and Color.RED.name == "RED", (
        "Members must not change. Block __setattr__/__delattr__ on members and set _name/_value with object.__setattr__."
    )


def test_class_members_cannot_be_reassigned_or_deleted():
    Color = make_color()
    with pytest.raises(AttributeError):
        Color.RED = 5
    with pytest.raises(AttributeError):
        del Color.GREEN
    assert Color.RED.value == 1 and len(Color) == 3, "Define __setattr__ and __delattr__ on the metaclass to protect members."
    Color.note = "ok"
    assert Color.note == "ok", "Setting a new, non-member attribute on the class is still allowed."


def test_repr_and_str():
    Color = make_color()
    assert repr(Color.RED) == "<Color.RED: 1>", "repr(member) is '<Class.NAME: value!r>'."
    assert str(Color.GREEN) == "Color.GREEN", "str(member) is 'Class.NAME'."

    class Word(MiniEnum):
        HI = "hello"

    assert repr(Word.HI) == "<Word.HI: 'hello'>", "Use repr() of the value inside repr(member)."


def test_members_are_hashable_and_not_equal_to_values():
    Color = make_color()
    names = {Color.RED: "r", Color.GREEN: "g"}
    assert names[Color(1)] == "r", "Members can be dict keys."
    assert Color.RED != 1, "A member is not equal to its value (do not define __eq__ comparing values)."


def test_duplicate_values_rejected():
    with pytest.raises(ValueError) as info:
        class Bad(MiniEnum):
            A = 1
            B = 1
    assert "B" in str(info.value), "The duplicate-value error must name the second member."


def test_cannot_extend_an_enum_with_members():
    Color = make_color()
    with pytest.raises(TypeError):
        class More(Color):
            PURPLE = 4

    class Base(MiniEnum):
        def shout(self):
            return self.name.upper() + "!"

    class Answer(Base):
        yes = 1
        no = 0

    assert Answer.yes.shout() == "YES!", "Extending an enum without members is allowed and shares its methods."
    assert len(Answer) == 2 and len(Base) == 0, "Each enum class has its own members."


def test_empty_enum_is_truthy():
    class Empty(MiniEnum):
        pass

    assert len(Empty) == 0 and list(Empty) == [], "An enum without members has length 0."
    assert bool(Empty) is True and bool(MiniEnum) is True, (
        "Defining __len__ on the metaclass makes an empty class falsy. Define __bool__ on the metaclass returning True."
    )


def test_tuple_values():
    class Rgb(MiniEnum):
        RED = (255, 0, 0)
        BLACK = (0, 0, 0)

    assert Rgb((0, 0, 0)) is Rgb.BLACK, "Any non-descriptor value can be a member value."
