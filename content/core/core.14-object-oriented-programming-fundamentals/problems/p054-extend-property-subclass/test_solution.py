import pytest

from solution import BoundedValue, Value


def bounded(value, upper):
    try:
        return BoundedValue(value, upper)
    except AttributeError as e:
        pytest.fail(
            f"BoundedValue({value!r}, {upper!r}) raised AttributeError: {e}. Value.__init__ assigns self.value, "
            "which runs BoundedValue's setter, which reads self.upper. Store self.upper BEFORE super().__init__(value)."
        )


def test_value_basic():
    v = Value(5)
    assert v.value == 5, "Value(5).value should be 5."
    v.value = 2.5
    assert v.value == 2.5, "Floats are allowed."
    assert v._value == 2.5, "Store the number in self._value (the property's backing attribute)."


def test_value_is_a_property():
    assert isinstance(vars(Value).get("value"), property), "Value.value must be a property defined in Value."
    assert isinstance(vars(BoundedValue).get("value"), property), (
        "BoundedValue must define its own value property (override it), not just add a method."
    )


@pytest.mark.parametrize("bad", ["7", None, True, [1]])
def test_value_type_check(bad):
    v = Value(1)
    with pytest.raises(TypeError, match="value must be a number"):
        v.value = bad
    assert v.value == 1, "A failed assignment must not change the value. bool counts as not a number here."


def test_value_negative():
    with pytest.raises(ValueError, match="value must be >= 0"):
        Value(-1)
    v = Value(0)
    assert v.value == 0, "0 is allowed (>= 0)."


def test_bounded_basic():
    b = bounded(5, 10)
    assert (b.value, b.upper) == (5, 10), "BoundedValue(5, 10): value 5, upper 10."
    b.value = 10
    assert b.value == 10, "The upper limit is inclusive: value == upper is fine."


def test_bounded_upper_check():
    b = bounded(5, 10)
    with pytest.raises(ValueError, match="value must be <= 10"):
        b.value = 11
    assert b.value == 5, "A failed assignment must leave the old value."
    b.value = 7.5
    with pytest.raises(ValueError, match="value must be <= 10"):
        b.value = 10.01


def test_bounded_reuses_base_checks():
    b = bounded(5, 10)
    with pytest.raises(ValueError, match="value must be >= 0"):
        b.value = -3
    with pytest.raises(TypeError, match="value must be a number"):
        b.value = "7"
    assert b.value == 5, "Failed assignments change nothing."


def test_base_setter_really_reused(monkeypatch):
    calls = []
    original = Value.value.fset

    def spy(self, new):
        calls.append(new)
        original(self, new)

    monkeypatch.setattr(Value, "value", property(Value.value.fget, spy))
    b = BoundedValue.__new__(BoundedValue)
    b.upper = 10
    b.value = 4
    assert calls == [4], (
        "BoundedValue's setter must hand the value to Value's setter (Value.value.fset(self, new)) "
        "instead of copying the checks or writing self._value itself."
    )


def test_check_runs_in_init():
    with pytest.raises(ValueError, match="value must be <= 10"):
        BoundedValue(20, 10)
    with pytest.raises(ValueError, match="value must be >= 0"):
        BoundedValue(-1, 10)


@pytest.mark.parametrize("bad", [-5, "10", None, True])
def test_bad_upper(bad):
    with pytest.raises(ValueError, match="upper must be a number >= 0"):
        BoundedValue(1, bad)


def test_upper_zero():
    b = bounded(0, 0)
    with pytest.raises(ValueError, match="value must be <= 0"):
        b.value = 1


def test_base_class_unchanged():
    v = Value(1000)
    assert v.value == 1000, "Value itself has no upper limit. Do not change Value when you write BoundedValue."
    assert not hasattr(v, "upper"), "Only BoundedValue has an upper attribute."


def test_getter_works_on_subclass():
    b = bounded(3, 5)
    assert BoundedValue.value.fget(b) == 3, "The getter returns self._value, the same as in Value."
