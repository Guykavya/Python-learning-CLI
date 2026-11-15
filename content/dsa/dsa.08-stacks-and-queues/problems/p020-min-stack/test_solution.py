import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import MinStack

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def test_example():
    m = MinStack()
    for x in (5, 3, 7, 3, 8):
        m.push(x)
    assert m.get_min() == 3, "The minimum of 5, 3, 7, 3, 8 is 3."
    assert (m.pop(), m.pop(), m.get_min()) == (8, 3, 3), "After popping 8 and one 3, the other 3 is still there."
    assert (m.pop(), m.pop(), m.get_min()) == (7, 3, 5), (
        "After popping 7 and the last 3, only 5 is left: the minimum must go back to 5.")
    assert m.top() == 5


def test_empty_raises():
    m = MinStack()
    for name in ("pop", "top", "get_min"):
        with pytest.raises(IndexError):
            getattr(m, name)()
    m.push(1)
    m.pop()
    with pytest.raises(IndexError):
        m.get_min()


def test_values_come_back_plain():
    m = MinStack()
    m.push(4)
    assert m.top() == 4 and m.pop() == 4, "top() and pop() return the value only, not a (value, minimum) pair."


def test_equal_minimums():
    m = MinStack()
    for x in (2, 2, 2):
        m.push(x)
    m.pop()
    m.pop()
    assert m.get_min() == 2, "Pushing 2 three times and popping twice leaves one 2: the minimum is still 2."


def test_random_against_list():
    rng = random.Random(20)
    m, model = MinStack(), []
    for step in range(5000):
        op = rng.choice(["push", "push", "push", "pop", "pop", "top", "min"])
        if op == "push":
            x = rng.randint(-20, 20)
            m.push(x)
            model.append(x)
        elif not model:
            continue
        elif op == "pop":
            assert m.pop() == model.pop(), f"Step {step}: pop() returned the wrong value."
        elif op == "top":
            assert m.top() == model[-1], f"Step {step}: top() should be {model[-1]}."
        if model:
            assert m.get_min() == min(model), (
                f"Step {step}: get_min() should be {min(model)} for the stack {model[-6:]} (last items). "
                "After a pop, the minimum of what is left must be known without a scan.")


def test_get_min_is_constant_time():
    code = (
        "from solution import MinStack\n"
        "m = MinStack()\n"
        "for x in range(100000, 0, -1):\n"
        "    m.push(x)\n"
        "    m.push(x + 1)\n"
        "    m.pop()\n"
        "total = 0\n"
        "for _ in range(100000):\n"
        "    total += m.get_min()\n"
        "print(total)\n"
    )
    out = run_code(code, 20, "100,000 calls of get_min on a stack of 100,000 items (get_min must be O(1), not a scan)")
    assert out == "100000", f"Every get_min() should return 1, so the total is 100000; got {out}."
