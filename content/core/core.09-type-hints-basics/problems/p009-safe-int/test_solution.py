from typing import get_type_hints

from solution import parse_all, safe_int, safe_int_or


def test_hints():
    assert get_type_hints(safe_int) == {"text": str, "return": int | None}, (
        "safe_int may return None, so the hint is -> int | None."
    )
    assert get_type_hints(safe_int_or) == {"text": str, "default": int, "return": int}, (
        "safe_int_or never returns None: text: str, default: int, -> int."
    )
    assert get_type_hints(parse_all) == {"texts": list[str], "return": list[int]}, (
        "parse_all takes list[str] and returns list[int] (the Nones are removed)."
    )


def test_valid_numbers():
    assert safe_int("42") == 42, "'42' is the int 42."
    assert safe_int(" -7 ") == -7, "Spaces around the number are allowed; negative numbers too."
    assert safe_int("0") == 0, "'0' parses to 0, which is a valid answer (not None)."


def test_invalid_gives_none():
    assert safe_int("abc") is None, "Letters are not a number: return None, do not raise."
    assert safe_int("") is None, "The empty string is not a number: return None."
    assert safe_int("4.5") is None, "A decimal is not a whole number: int('4.5') raises ValueError."


def test_safe_int_or():
    assert safe_int_or("x", 0) == 0, "Bad text gives the default."
    assert safe_int_or("12", 0) == 12, "Good text ignores the default."
    assert safe_int_or("0", 5) == 0, "'0' is a valid number. Check 'is None', not 'if not n'."


def test_parse_all():
    assert parse_all(["1", "x", "3", ""]) == [1, 3], "Keep only the texts that parse, in order."
    assert parse_all([]) == [], "No texts, no numbers."
    assert parse_all(["0", "a", "0"]) == [0, 0], "0 values must be kept: filter with 'is not None'."
