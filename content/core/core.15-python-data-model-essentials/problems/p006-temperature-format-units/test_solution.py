import pytest

from solution import Temperature


def test_default_is_celsius_one_decimal():
    assert f"{Temperature(100)}" == "100.0 C", "Empty spec: Celsius with 1 decimal, like '100.0 C'."


def test_units():
    t = Temperature(100)
    assert format(t, "C") == "100.0 C", "'C' keeps Celsius."
    assert format(t, "F") == "212.0 F", "Fahrenheit is c * 9 / 5 + 32: 100 C = 212.0 F."
    assert format(t, "K") == "373.1 K" or format(t, "K") == "373.2 K", "Kelvin is c + 273.15 (373.15 shown with 1 decimal)."


def test_precision():
    t = Temperature(100)
    assert format(t, ".2K") == "373.15 K", "'.2K' means 2 decimals in Kelvin: 373.15 K."
    assert format(t, ".0F") == "212 F", "'.0F' means no decimals: '212 F'."
    assert format(t, ".2") == "100.00 C", "A precision with no unit keeps Celsius: '100.00 C'."


def test_negative_and_freezing():
    assert format(Temperature(0), "F") == "32.0 F", "0 C is 32.0 F."
    assert format(Temperature(-40), "F") == "-40.0 F", "-40 C equals -40 F."
    assert format(Temperature(36.6), ".2F") == "97.88 F", "36.6 C is 97.88 F."


@pytest.mark.parametrize("bad", ["X", "2F", "F.2", ".F", "..1", "CF", ".-1"])
def test_bad_specs_raise(bad):
    with pytest.raises(ValueError):
        format(Temperature(1), bad)


def test_object_not_changed():
    t = Temperature(100)
    format(t, "F")
    assert t.celsius == 100, "Formatting must not change the stored Celsius value."


def test_repr():
    assert repr(Temperature(100)) == "Temperature(100)", "repr is provided; do not change it."
