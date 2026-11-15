import random
import re
from fractions import Fraction

import pytest

from solution import to_postfix

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def tokenize(text):
    return re.findall(r"\d+|[-+*/()]", text)


def eval_postfix_exact(tokens):
    stack = []
    for t in tokens:
        if t in PREC:
            assert len(stack) >= 2, f"Your postfix {tokens} has an operator {t!r} without two operands before it."
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(a / b)
        else:
            assert t.isdigit(), f"Your postfix contains {t!r}; only numbers and + - * / may appear (no brackets)."
            stack.append(Fraction(int(t)))
    assert len(stack) == 1, f"Your postfix {tokens} leaves {len(stack)} values on the stack; it must leave exactly 1."
    return stack[0]


def eval_infix_exact(text):
    return eval(re.sub(r"\d+", lambda m: f"Fraction({m.group()})", text), {"Fraction": Fraction})


@pytest.mark.parametrize("text, want, why", [
    ("3 + 4 * 2", "3 4 2 * +", "* binds tighter than +"),
    ("(3 + 4) * 2", "3 4 + 2 *", "brackets first"),
    ("8 - 3 - 2", "8 3 - 2 -", "equal precedence goes left to right: use >= when popping"),
    ("12 / 3 / 2", "12 3 / 2 /", "/ is also left to right"),
    ("3 + 4 * 2 / (1 - 5)", "3 4 2 * 1 5 - / +", "the chapter example"),
    ("2 * (3 + 4) - 5", "2 3 4 + * 5 -", "a bracket in the middle"),
    ("7", "7", "a single number"),
    ("((7))", "7", "brackets never appear in the output"),
    ("1 - (2 - (3 - 4))", "1 2 3 4 - - -", "nested brackets on the right"),
    ("2 * 3 + 4 * 5", "2 3 * 4 5 * +", "two products added"),
    ("10 - 2 * 3 + 1", "10 2 3 * - 1 +", "the - must leave before the + arrives"),
])
def test_fixed(text, want, why):
    got = to_postfix(tokenize(text))
    assert got == want.split(), f"to_postfix({text!r}) should be {want.split()}, got {got}: {why}."


def random_expr(rng, depth):
    if depth == 0 or rng.random() < 0.3:
        return str(rng.randint(0, 20)), 3
    op = rng.choice("+-*/")
    left, lp = random_expr(rng, depth - 1)
    right, rp = random_expr(rng, depth - 1)
    p = PREC[op]
    if lp < p:
        left = f"({left})"
    if rp <= p:
        right = f"({right})"
    text = f"{left} {op} {right}"
    if rng.random() < 0.15:
        return f"({text})", 3
    return text, p


def test_random_against_eval():
    rng = random.Random(13)
    checked = 0
    for _ in range(1500):
        text, _ = random_expr(rng, rng.randint(1, 4))
        try:
            want = eval_infix_exact(text)
        except ZeroDivisionError:
            continue
        tokens = tokenize(text)
        got_postfix = to_postfix(list(tokens))
        try:
            got = eval_postfix_exact(got_postfix)
        except ZeroDivisionError:
            raise AssertionError(f"Your postfix {got_postfix} for {text!r} divides by zero, but eval does not: "
                                 "the operators are in the wrong order.") from None
        assert got == want, (f"For {text!r} your postfix {' '.join(got_postfix)} has value {got}, "
                             f"but eval gives {want}. Check precedence and left-to-right order (>=).")
        assert sorted(t for t in got_postfix if t.isdigit()) == sorted(t for t in tokens if t.isdigit()), (
            f"Your postfix for {text!r} must contain each number exactly once.")
        checked += 1
    assert checked > 1000


def test_long_input():
    tokens = ["1"] + ["+", "1"] * 4000 + ["*", "("] + ["2", "-"] * 999 + ["2", ")"]
    got = to_postfix(tokens)
    assert len(got) == 4001 + 4000 + 1 + 1000 + 999, "Every number and operator must appear exactly once in the output."
    assert eval_postfix_exact(got) == eval_infix_exact(" ".join(tokens))
