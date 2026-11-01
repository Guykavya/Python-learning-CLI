import pytest

from solution import NonEmptyStr, OneOf, Range, Validator


def make_shirt_class():
    class Shirt:
        size = OneOf("S", "M", "L")
        price = Range(0, 500)
        label = NonEmptyStr(max_len=10)

    return Shirt


def message(exc_info):
    return str(exc_info.value)


def test_valid_values_are_stored_per_instance():
    Shirt = make_shirt_class()
    a, b = Shirt(), Shirt()
    a.size, a.price, a.label = "M", 19.5, "summer"
    b.size, b.price, b.label = "L", 30, "winter"
    assert (a.size, a.price, a.label) == ("M", 19.5, "summer"), (
        "a's values changed when b was set. Store values per instance (instance.__dict__), not on the descriptor."
    )
    assert (b.size, b.price, b.label) == ("L", 30, "winter")


def test_validator_is_abstract():
    with pytest.raises(TypeError):
        Validator()

    class Forgetful(Validator):
        pass

    with pytest.raises(TypeError):
        Forgetful()


def test_a_new_validator_only_needs_validate():
    class Even(Validator):
        def validate(self, value):
            if value % 2:
                raise ValueError(f"{self.name} must be even")

    class Pair:
        count = Even()

    p = Pair()
    p.count = 4
    assert p.count == 4, "The base class must do the storing; a subclass only writes validate()."
    with pytest.raises(ValueError, match="count must be even"):
        p.count = 3
    assert p.count == 4, "Validate BEFORE storing: a rejected value must not replace the old one."
    assert Pair.count.name == "count", "__set_name__ in the base class must set self.name."


def test_class_access_returns_descriptor():
    Shirt = make_shirt_class()
    assert isinstance(Shirt.price, Range), "Shirt.price on the class must return the Range object itself."
    assert Shirt.size.name == "size", "The descriptor must know its field name."


def test_unset_field_raises_attribute_error():
    Shirt = make_shirt_class()
    s = Shirt()
    with pytest.raises(AttributeError, match="price"):
        s.price
    assert not hasattr(s, "label"), "hasattr needs an AttributeError (not KeyError) for an unset field."


def test_range_limits_are_inclusive():
    Shirt = make_shirt_class()
    s = Shirt()
    s.price = 0
    s.price = 500
    assert s.price == 500, "Both limits are allowed values (0 <= value <= 500)."


def test_range_rejects_out_of_range_with_field_name():
    Shirt = make_shirt_class()
    s = Shirt()
    s.price = 10
    with pytest.raises(ValueError) as err:
        s.price = -1
    assert message(err) == "price must be >= 0, got -1", f"Expected 'price must be >= 0, got -1', got {message(err)!r}"
    with pytest.raises(ValueError) as err:
        s.price = 500.5
    assert message(err) == "price must be <= 500, got 500.5", (
        f"Expected 'price must be <= 500, got 500.5', got {message(err)!r}"
    )
    assert s.price == 10, "Rejected values must not be stored."


def test_range_rejects_non_numbers_and_bool():
    Shirt = make_shirt_class()
    s = Shirt()
    with pytest.raises(TypeError) as err:
        s.price = "10"
    assert message(err) == "price must be a number, got str", f"Got {message(err)!r}"
    with pytest.raises(TypeError):
        s.price = True


def test_range_with_one_side_open():
    class Account:
        balance = Range(min_value=0)
        temperature = Range(max_value=100)

    a = Account()
    a.balance = 10**12
    a.temperature = -273
    assert (a.balance, a.temperature) == (10**12, -273), "None means 'no limit on this side'."
    with pytest.raises(ValueError):
        a.balance = -0.01


def test_one_of():
    Shirt = make_shirt_class()
    s = Shirt()
    s.size = "S"
    with pytest.raises(ValueError) as err:
        s.size = "XL"
    assert message(err) == "size must be one of 'S', 'M', 'L', got 'XL'", (
        f"Show the options in the given order with repr, then the bad value. Got {message(err)!r}"
    )
    assert s.size == "S", "Rejected value must not be stored."


def test_one_of_with_numbers():
    class Dice:
        face = OneOf(1, 2, 3, 4, 5, 6)

    d = Dice()
    d.face = 6
    with pytest.raises(ValueError, match="face must be one of 1, 2, 3, 4, 5, 6, got 7"):
        d.face = 7


def test_non_empty_str():
    Shirt = make_shirt_class()
    s = Shirt()
    s.label = "x" * 10
    with pytest.raises(ValueError) as err:
        s.label = ""
    assert message(err) == "label must not be empty", f"Got {message(err)!r}"
    with pytest.raises(ValueError, match="label must not be empty"):
        s.label = "   "
    with pytest.raises(ValueError) as err:
        s.label = "x" * 12
    assert message(err) == "label must be at most 10 characters, got 12", f"Got {message(err)!r}"
    with pytest.raises(TypeError) as err:
        s.label = 5
    assert message(err) == "label must be a str, got int", f"Got {message(err)!r}"
    assert s.label == "x" * 10, "None of the rejected values may be stored."


def test_non_empty_str_without_limit():
    class Note:
        text = NonEmptyStr()

    n = Note()
    n.text = "a" * 10_000
    assert len(n.text) == 10_000, "max_len=None means no length limit."


def test_two_fields_of_the_same_kind_do_not_mix():
    class Box:
        width = Range(0, 10)
        height = Range(0, 10)

    b = Box()
    b.width = 3
    b.height = 7
    assert (b.width, b.height) == (3, 7), (
        "Two Range fields in one class must keep separate values. Store under self.name, learned in __set_name__."
    )
    with pytest.raises(ValueError, match="height"):
        b.height = 11
