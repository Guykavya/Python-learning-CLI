import pytest

from solution import bracket_error

# Every expected value below was traced by hand and then confirmed by running the reference.


@pytest.mark.parametrize("text, want, why", [
    ("", (-1, "ok"), "nothing to check"),
    ("([]{})", (-1, "ok"), "balanced"),
    ("a(b[c]d)e", (-1, "ok"), "letters are ignored"),
    ("(]", (1, "mismatch"), "] at index 1 does not close ("),
    ("a(b]c", (3, "mismatch"), "the ] is at index 3; letters still count for the index"),
    ("([)]", (2, "mismatch"), ") at index 2 meets [ on top"),
    (")(", (0, "unexpected"), "a closer at index 0 with nothing open"),
    ("()))", (2, "unexpected"), "the first ) closes index 0; the second ) at index 2 has nothing to close"),
    ("x(y)z)", (5, "unexpected"), "the last ) is extra"),
    ("((", (0, "unclosed"), "two open brackets left: report the earliest, index 0"),
    ("(()", (0, "unclosed"), "index 1 is closed by index 2; index 0 stays open"),
    ("{[()]", (0, "unclosed"), "only the { at index 0 is still open"),
    ("{}((", (2, "unclosed"), "the {} pair is fine; the earliest open bracket is at index 2"),
    ("(()[", (0, "unclosed"), "indices 0 and 3 stay open; the earliest is the BOTTOM of the stack"),
    ("(]((", (1, "mismatch"), "the mismatch in the middle is reported at once, not the unclosed ones at the end"),
    ("((]", (2, "mismatch"), "a mismatch wins over the brackets that are still open"),
])
def test_cases(text, want, why):
    try:
        got = bracket_error(text)
    except IndexError:
        raise AssertionError(f"bracket_error({text!r}) crashed with IndexError: check for an empty stack first.") from None
    assert got == want, f"bracket_error({text!r}) should be {want}, got {got}: {why}."


def test_long_unclosed():
    text = "[" + "()" * 50000 + "{"
    assert bracket_error(text) == (0, "unclosed"), "The [ at index 0 and the final { are open: report index 0."
    text = "()" * 50000 + ")"
    assert bracket_error(text) == (100000, "unexpected"), "The extra ) is at index 100000."
