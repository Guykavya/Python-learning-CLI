import ast
import random
from pathlib import Path

import pytest

from solution import calculate

SOLUTION = Path(__file__).with_name("solution.py")


class DivByZero(Exception):
    pass


def tdiv(a, b):
    if b == 0:
        raise DivByZero
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


PREC = {"+": 1, "-": 1, "*": 2, "/": 2}


def gen(rng, depth):
    """A random tree: an int, ("neg", child) or (op, left, right)."""
    r = rng.random()
    if depth == 0 or r < 0.25:
        return rng.randint(0, 30)
    if r < 0.38:
        return ("neg", gen(rng, depth - 1))
    return (rng.choice("+-*/"), gen(rng, depth - 1), gen(rng, depth - 1))


def value(t):
    if isinstance(t, int):
        return t
    if t[0] == "neg":
        return -value(t[1])
    a, b = value(t[1]), value(t[2])
    return {"+": a + b, "-": a - b, "*": a * b, "/": None}[t[0]] if t[0] != "/" else tdiv(a, b)


def prec(t):
    if isinstance(t, int):
        return 3
    if t[0] == "neg":
        return 2.5
    return PREC[t[0]]


def render(t, rng, leftmost):
    """Text for tree t. leftmost: t starts the whole text or comes right after '('."""
    if isinstance(t, int):
        return str(t)
    if t[0] == "neg":
        child = t[1]
        inner = f"({render(child, rng, True)})" if not isinstance(child, int) else str(child)
        text = "-" + inner
        return text if leftmost else f"({text})"
    op, left, right = t
    p = PREC[op]
    if prec(left) < p:
        ltext = f"({render(left, rng, True)})"
    else:
        ltext = render(left, rng, leftmost)
    if prec(right) <= p:
        rtext = f"({render(right, rng, True)})"
    else:
        rtext = render(right, rng, False)
    sp = " " if rng.random() < 0.5 else ""
    return f"{ltext}{sp}{op}{sp}{rtext}"


@pytest.mark.parametrize("s, want, why", [
    ("2-(5-6)", 3, "2 - (-1)"),
    ("1 + 1", 2, "spaces are ignored"),
    (" 3 + 5 / 2 ", 5, "/ before +, and 5 / 2 truncates to 2"),
    ("3+2*2", 7, "* before +"),
    ("14-3/2", 13, "14 - 1"),
    ("7-8/2*3", -5, "/ and * left to right: 8 / 2 * 3 = 12"),
    ("-(2+3)*4", -20, "unary minus at the start, before a bracket"),
    ("2*(5+5*2)/3+(6/2+8)", 21, "2 * 15 / 3 + 11"),
    ("(-7)/2", -3, "division truncates toward zero: -7 / 2 is -3, not -4"),
    ("-7/2", -3, "unary minus at the start, then truncating division"),
    ("10 - (-3)", 13, "unary minus right after ("),
    ("(1+(4+5+2)-3)+(6+8)", 23, "nested brackets"),
    ("((((42))))", 42, "deep brackets around one number"),
    ("100", 100, "a single multi-digit number"),
    ("0", 0, "zero"),
    ("8/3/2", 1, "8 / 3 = 2, then 2 / 2 = 1 (left to right)"),
    ("2-3-4", -5, "subtraction goes left to right"),
    ("-(-(5))", 5, "unary minus twice, each after ( or at the start"),
    ("(2+3)*(4-6)", -10, "two brackets multiplied"),
    ("123 * 0 + 7", 7, "multiplying by zero"),
])
def test_fixed(s, want, why):
    got = calculate(s)
    assert got == want, f"calculate({s!r}) should be {want}, got {got}: {why}."


def test_random_expressions():
    rng = random.Random(14)
    done = 0
    while done < 1500:
        t = gen(rng, rng.randint(1, 5))
        try:
            want = value(t)
        except DivByZero:
            continue
        s = render(t, rng, True)
        if "/" not in s:
            assert eval(s) == want, f"test generator problem for {s!r}"
        got = calculate(s)
        assert got == want, (f"calculate({s!r}) should be {want}, got {got}. "
                             "Check precedence, truncating division and unary minus after '('.")
        done += 1


def test_deep_brackets():
    s = "(" * 100 + "1+2" + ")" * 100 + "*3"
    assert calculate(s) == 9, "100 nested brackets around 1+2, times 3, is 9."


def test_long_flat_expression():
    s = "+".join(["7*3-20"] * 1500)
    assert calculate(s) == 1500, "1,500 copies of 7*3-20 added together is 1500."


def test_no_eval():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "eval" not in names and "exec" not in names, "Do not use eval or exec: evaluate the expression yourself."
