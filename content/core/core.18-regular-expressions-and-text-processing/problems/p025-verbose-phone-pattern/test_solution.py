import re

import solution
from solution import parse_phone


def number(area, exchange, line, ext=None):
    return {"area": area, "exchange": exchange, "line": line, "ext": ext}


def test_pattern_is_verbose_and_readable():
    assert isinstance(solution.PHONE_RE, re.Pattern), "PHONE_RE must be a compiled pattern (re.compile)."
    assert solution.PHONE_RE.flags & re.VERBOSE, "Compile PHONE_RE with re.VERBOSE (or re.X)."
    assert "\n" in solution.PHONE_RE.pattern, "Spread the pattern over several lines (a triple-quoted raw string)."
    assert "#" in solution.PHONE_RE.pattern, "Add # comments that explain each piece."


def test_bracket_form():
    assert parse_phone("(555) 123-4567") == number("555", "123", "4567"), "Brackets around the area code are allowed; return the area WITHOUT them (strip '()')."
    assert parse_phone("(555)123-4567") == number("555", "123", "4567"), "The separator after the area code is optional."


def test_bare_forms():
    assert parse_phone("555-123-4567") == number("555", "123", "4567"), "Hyphens as separators."
    assert parse_phone("555.123.4567") == number("555", "123", "4567"), "Dots as separators (escape nothing inside [-. ]: a dot in a class is literal)."
    assert parse_phone("555 123 4567") == number("555", "123", "4567"), "Spaces as separators. In VERBOSE mode a bare space is ignored: write it inside a class [-. ] or as '\\ '."
    assert parse_phone("5551234567") == number("555", "123", "4567"), "No separators at all."


def test_country_code_and_whitespace():
    assert parse_phone("+1 555-123-4567") == number("555", "123", "4567"), "Optional +1 then a space or hyphen. Escape the plus: \\+1."
    assert parse_phone("+1-(555) 123-4567") == number("555", "123", "4567"), "+1 and a hyphen, then the bracket form."
    assert parse_phone("   555-123-4567  ") == number("555", "123", "4567"), "Spaces around the whole number are ignored: strip first."


def test_extensions():
    assert parse_phone("+1 555.123.4567 ext. 89") == number("555", "123", "4567", "89"), "Extension with 'ext.' and spaces."
    assert parse_phone("555-123-4567 x12345") == number("555", "123", "4567", "12345"), "Extension with 'x' and up to 5 digits."
    assert parse_phone("555-123-4567ext7") == number("555", "123", "4567", "7"), "The whitespace before and after 'ext' is optional (\\s*)."
    assert parse_phone("555-123-4567 x123456") is None, "An extension has at most 5 digits."


def test_ext_is_none_when_missing():
    result = parse_phone("555-123-4567")
    assert result is not None and "ext" in result and result["ext"] is None, "Always include the 'ext' key; groupdict() gives None for a group that did not take part."


def test_first_digit_rules():
    assert parse_phone("(155) 123-4567") is None, "An area code cannot start with 0 or 1: [2-9]\\d{2}."
    assert parse_phone("055-123-4567") is None, "An area code cannot start with 0 either."


def test_unbalanced_brackets():
    assert parse_phone("(555 123-4567") is None, "An opening bracket without a closing one is invalid. Optional \\(? and \\)? allow this: use two alternatives instead."
    assert parse_phone("555) 123-4567") is None, "A closing bracket without an opening one is invalid."


def test_garbage():
    assert parse_phone("555-123-456") is None, "The line part has exactly 4 digits."
    assert parse_phone("call 555-123-4567") is None, "Nothing else may be in the string: use fullmatch."
    assert parse_phone("555--123-4567") is None, "At most ONE separator between parts."
    assert parse_phone("") is None, "The empty string is not a phone number."
