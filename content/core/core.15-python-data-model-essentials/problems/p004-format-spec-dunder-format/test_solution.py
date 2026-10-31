import pytest

from solution import Color


def test_hex():
    assert format(Color(255, 128, 0), "hex") == "#ff8000", "'hex' should give '#ff8000': lowercase, two digits per channel."


def test_hex_pads_small_numbers():
    assert f"{Color(0, 5, 10):hex}" == "#00050a", "Pad each channel to 2 digits: use {value:02x}, not hex()."


def test_rgb():
    assert format(Color(255, 128, 0), "rgb") == "rgb(255, 128, 0)", "'rgb' should give 'rgb(255, 128, 0)'."


def test_empty_spec_is_str():
    c = Color(1, 2, 3)
    assert format(c, "") == str(c) == "Color(1, 2, 3)", "An empty spec must behave like str(c). f'{c}' calls __format__('')."


def test_fstring_default():
    assert f"{Color(9, 9, 9)}" == "Color(9, 9, 9)", "f'{c}' with no spec should still work."


def test_unknown_spec_raises():
    with pytest.raises(ValueError) as e:
        format(Color(1, 2, 3), "xyz")
    assert "xyz" in str(e.value), "Include the bad spec in the ValueError message, e.g. 'unknown format spec: xyz'."


def test_returns_str():
    assert isinstance(format(Color(1, 2, 3), "hex"), str), "__format__ must return a str."
