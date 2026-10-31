import pytest

from solution import Labeled, Vector, Velocity


def test_kinds_of_methods():
    assert isinstance(vars(Vector)["from_string"], classmethod), "from_string must be a @classmethod so it receives cls."
    assert isinstance(vars(Vector)["zero"], classmethod), "zero must be a @classmethod."
    assert isinstance(vars(Vector)["parse_pair"], staticmethod), (
        "parse_pair only parses text and needs neither self nor cls: keep it a @staticmethod."
    )


def test_from_string_on_vector():
    v = Vector.from_string("3,4")
    assert type(v) is Vector and (v.x, v.y) == (3.0, 4.0), "Vector.from_string('3,4') gives Vector(3.0, 4.0)."


def test_from_string_respects_subclass():
    v = Velocity.from_string("3,4")
    assert type(v) is Velocity, (
        f"Velocity.from_string returned a {type(v).__name__}. Return cls(x, y), not Vector(x, y)."
    )
    assert v.kind() == "velocity" and v.unit == "m/s", "A real Velocity has the Velocity methods and attributes."


def test_zero_respects_subclass():
    assert type(Vector.zero()) is Vector, "Vector.zero() is a Vector."
    z = Velocity.zero()
    assert type(z) is Velocity and (z.x, z.y) == (0.0, 0.0), "Velocity.zero() must return cls(0.0, 0.0), a Velocity."


def test_factory_through_an_instance():
    v = Velocity(5, 5).from_string("1,1")
    assert type(v) is Velocity, "Called through an instance, a classmethod still gets the class of that instance."


def test_subclass_with_extra_init_argument():
    lab = Labeled.from_string("1,2")
    assert type(lab) is Labeled and lab.label == "?", "Labeled.from_string builds cls(x, y), so label gets its default '?'."
    assert type(Labeled.zero()) is Labeled, "Labeled.zero() is a Labeled."


def test_scaled_keeps_type_and_does_not_mutate():
    v = Velocity(1, 2)
    w = v.scaled(3)
    assert type(w) is Velocity, f"scaled returned a {type(w).__name__}. Use type(self)(...), not Vector(...)."
    assert (w.x, w.y) == (3, 6), "scaled(k) multiplies x and y by k."
    assert (v.x, v.y) == (1, 2), "scaled must return a NEW object and leave self unchanged."
    assert w is not v, "Return a new object."


def test_plus_keeps_type():
    v = Vector(1, 2).plus(Vector(3, 4))
    assert type(v) is Vector and (v.x, v.y) == (4, 6), "Vector(1, 2).plus(Vector(3, 4)) is Vector(4, 6)."
    w = Velocity(1, 1).plus(Vector(1, 1))
    assert type(w) is Velocity, "plus returns an object of the same class as self: type(self)(...)."


def test_labeled_scaled_keeps_class():
    lab = Labeled(1, 1, "a").scaled(2)
    assert type(lab) is Labeled, "type(self)(x, y) works for Labeled too (its label falls back to '?')."


def test_parse_pair():
    assert Vector.parse_pair("3,4") == (3.0, 4.0), "parse_pair returns a tuple of two floats."
    assert Vector.parse_pair(" 3 , 4 ") == (3.0, 4.0), "float() ignores spaces around a number."
    assert Velocity.parse_pair("-1.5,2") == (-1.5, 2.0), "Negative and decimal numbers work."
    assert type(Vector.parse_pair("1,2")) is tuple, "Return a tuple, not a Vector."


@pytest.mark.parametrize("bad", ["3;4", "3", "1,2,3", "a,b", "", "3,"])
def test_bad_strings(bad):
    with pytest.raises(ValueError) as info:
        Velocity.from_string(bad)
    assert str(info.value) == f"expected 'x,y', got {bad!r}", (
        f"The message must be \"expected 'x,y', got {bad!r}\" for every bad input. Got {str(info.value)!r}."
    )


def test_bad_number_is_chained():
    with pytest.raises(ValueError) as info:
        Vector.from_string("a,b")
    assert isinstance(info.value.__cause__, ValueError), (
        "When float() fails, raise the new ValueError `from` the original one so __cause__ keeps it."
    )
