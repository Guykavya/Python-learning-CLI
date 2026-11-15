import pytest

from solution import is_valid


@pytest.mark.parametrize("text, want, why", [
    ("", True, "the empty string is valid: nothing is open"),
    ("()", True, "one pair"),
    ("()[]{}", True, "three pairs side by side"),
    ("([]{})", True, "pairs inside a pair"),
    ("{[()]}", True, "deep nesting"),
    ("a(b[c]d)e", True, "letters are ignored"),
    ("(]", False, "the closer does not match the most recent opener"),
    ("((", False, "openers are left at the end: check that the stack is empty"),
    ("(", False, "one opener that is never closed"),
    (")(", False, "a closer arrives when nothing is open: check for an empty stack before popping"),
    ("]", False, "a lone closer: do not crash on an empty stack"),
    ("([)]", False, "crossed pairs: the counts are balanced but ] must close [ only after ) closed ("),
    ("(()", False, "one ( is still open at the end"),
    ("())", False, "one ) too many"),
    ("{[}]", False, "crossed pairs of different kinds"),
    ("x)y(z", False, "the closer comes before its opener"),
])
def test_cases(text, want, why):
    try:
        got = is_valid(text)
    except IndexError:
        raise AssertionError(f"is_valid({text!r}) crashed with IndexError: check `not stack` before you pop.") from None
    assert got is want, f"is_valid({text!r}) should be {want}: {why}."


def test_long_valid_and_invalid():
    deep = "([{" * 20000 + "}])" * 20000
    assert is_valid(deep) is True, "60,000 openers followed by their closers in reverse order are valid."
    assert is_valid(deep + "(") is False, "The same string plus one extra '(' is invalid."
    assert is_valid("()" * 50000) is True, "100,000 characters of '()' pairs are valid."
