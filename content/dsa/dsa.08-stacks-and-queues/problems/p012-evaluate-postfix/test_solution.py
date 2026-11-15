import pytest

from solution import eval_rpn


@pytest.mark.parametrize("expr, want, why", [
    ("2 1 + 3 *", 9, "(2 + 1) * 3"),
    ("4 13 5 / +", 6, "4 + 13 / 5 = 4 + 2"),
    ("10 6 9 3 + -11 * / * 17 + 5 +", 22, "the long example; -11 is a number, not an operator"),
    ("42", 42, "a single number is its own value"),
    ("-5", -5, "a single negative number"),
    ("8 3 -", 5, "8 - 3: the FIRST pop is the right operand b, the second pop is a"),
    ("3 8 -", -5, "3 - 8"),
    ("12 4 /", 3, "12 / 4"),
    ("4 12 /", 0, "4 / 12 truncates to 0: did you swap the operands?"),
    ("7 2 /", 3, "7 / 2 truncates to 3"),
    ("-7 2 /", -3, "-7 / 2 truncates TOWARD ZERO to -3; Python's // gives -4"),
    ("7 -2 /", -3, "7 / -2 truncates toward zero to -3"),
    ("-7 -2 /", 3, "-7 / -2 is 3"),
    ("-1 3 /", 0, "-1 / 3 truncates to 0, not -1"),
    ("3 -4 *", -12, "multiplication with a negative number"),
    ("2 3 4 * 5 - +", 9, "2 + (3 * 4 - 5)"),
])
def test_cases(expr, want, why):
    got = eval_rpn(expr.split())
    assert got == want, f"eval_rpn({expr.split()}) should be {want}, got {got}: {why}."


def test_huge_numbers_no_floats():
    got = eval_rpn(["1000000000000000001", "1", "/"])
    assert got == 1000000000000000001, (
        f"1000000000000000001 / 1 should be 1000000000000000001, got {got}. "
        "int(a / b) goes through a float and loses the last digits: divide integers with // on the absolute values.")
    got = eval_rpn(["-9999999999999999999", "3", "/"])
    assert got == -3333333333333333333, f"-9999999999999999999 / 3 should be -3333333333333333333, got {got}."


def test_result_is_int():
    assert isinstance(eval_rpn(["6", "3", "/"]), int), "The result must be an int (6 / 3 is 2, not 2.0)."


def test_long_expression():
    tokens = ["1"] + ["1", "+"] * 5000
    assert eval_rpn(tokens) == 5001, "1 + 1 + ... (5,000 additions) is 5001."
    tokens = ["1"] * 5001 + ["+"] * 5000
    assert eval_rpn(tokens) == 5001, "5,001 ones pushed first, then 5,000 additions: 5001."
