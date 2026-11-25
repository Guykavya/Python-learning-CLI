import pytest

from solution import parse_number

GOOD = [
    ("120.5", 120.5, "a plain decimal"),
    (" 98ms ", 98.0, "spaces and the unit 'ms'"),
    ("1,204", 1204.0, "a thousands separator"),
    ("$ 1,204.50", 1204.5, "a dollar sign, a space and a comma"),
    ("Rs. 500", 500.0, "'Rs.' in any case"),
    ("rs500", 500.0, "'rs' without a dot"),
    ("45%", 45.0, "a percent sign"),
    ("1e3", 1000.0, "scientific notation"),
    ("2.5E-2", 0.025, "scientific notation with a negative exponent in capitals"),
    ("-5", -5.0, "a negative number (not the missing marker '-')"),
    ("1 204", 1204.0, "a space inside the number"),
    ("0", 0.0, "zero is a value, not missing"),
]

MISSING_CASES = ["N/A", "n/a", "NA", "-", "", "   ", "None", "null", "?", "NaN"]

BAD = ["abc", "1.2.3", "inf", "-inf", "12 apples", "ms"]


@pytest.mark.parametrize("text,expected,what", GOOD)
def test_good_numbers(text, expected, what):
    got = parse_number(text)
    assert got == pytest.approx(expected, rel=1e-9), f"{text!r} ({what}) should give {expected}, got {got!r}."
    assert isinstance(got, float), f"{text!r}: return a float, not {type(got).__name__}."


@pytest.mark.parametrize("text", MISSING_CASES)
def test_missing_markers(text):
    assert parse_number(text) is None, f"{text!r} is a missing marker: return None, not 0 and not an error."


@pytest.mark.parametrize("text", BAD)
def test_garbage_raises_with_the_text(text):
    with pytest.raises(ValueError) as info:
        parse_number(text)
    assert repr(text) in str(info.value) or text in str(info.value), f"The ValueError message must contain the original text {text!r}."
