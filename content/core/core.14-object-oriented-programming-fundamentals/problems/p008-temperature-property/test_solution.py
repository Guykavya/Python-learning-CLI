import math

import pytest

from solution import Temperature


def test_default_is_zero():
    assert Temperature().celsius == 0, "Temperature() should default to 0 degrees C."


def test_read_celsius():
    assert Temperature(25).celsius == 25, "Temperature(25).celsius should be 25."


def test_celsius_is_a_property():
    assert isinstance(vars(Temperature).get("celsius"), property), "celsius must be a property: use @property and @celsius.setter."
    assert isinstance(vars(Temperature).get("fahrenheit"), property), "fahrenheit must be a property too."


def test_value_stored_in_backing_attribute():
    t = Temperature(25)
    assert vars(t).get("_celsius") == 25, "Store the number in self._celsius (the backing attribute)."
    assert "fahrenheit" not in vars(t) and "_fahrenheit" not in vars(t), "Do not store Fahrenheit separately; compute it from celsius."


def test_set_celsius():
    t = Temperature(25)
    t.celsius = 30
    assert t.celsius == 30, "Setting t.celsius = 30 should change the temperature."


def test_absolute_zero_itself_is_allowed():
    assert Temperature(-273.15).celsius == -273.15, "-273.15 is allowed; only values BELOW it are rejected. Use <, not <=."


def test_setter_rejects_below_absolute_zero_and_keeps_old_value():
    t = Temperature(100)
    with pytest.raises(ValueError, match="below absolute zero"):
        t.celsius = -300
    assert t.celsius == 100, "A rejected value must not be stored. Raise before writing self._celsius."


def test_constructor_also_checks():
    try:
        Temperature(-274)
    except ValueError as e:
        assert "below absolute zero" in str(e), "Use the message 'below absolute zero'."
    else:
        pytest.fail("Temperature(-274) must raise ValueError. In __init__, write self.celsius = celsius (no underscore) so the setter checks it.")


def test_read_fahrenheit():
    assert math.isclose(Temperature(25).fahrenheit, 77.0), "25 C is 77 F: celsius * 9 / 5 + 32."
    assert math.isclose(Temperature(-40).fahrenheit, -40.0), "-40 is the same in C and F."


def test_fahrenheit_follows_celsius():
    t = Temperature(0)
    t.celsius = 100
    assert math.isclose(t.fahrenheit, 212.0), "fahrenheit must be computed from the CURRENT celsius each time it is read."


def test_set_fahrenheit_changes_celsius():
    t = Temperature(25)
    t.fahrenheit = 212
    assert math.isclose(t.celsius, 100.0), "Setting fahrenheit = 212 should make celsius 100: (f - 32) * 5 / 9."
    t.fahrenheit = 32
    assert math.isclose(t.celsius, 0.0), "32 F is 0 C."


def test_fahrenheit_setter_checks_too():
    t = Temperature(10)
    with pytest.raises(ValueError, match="below absolute zero"):
        t.fahrenheit = -500
    assert t.celsius == 10, "A rejected Fahrenheit value must leave the temperature unchanged."
