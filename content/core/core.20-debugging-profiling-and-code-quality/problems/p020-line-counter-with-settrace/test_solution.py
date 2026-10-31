import sys

import pytest

from solution import line_hits

# The demo functions are compiled from this string, so their relative line numbers are easy
# to read: the line under each "def" is line 2 of that function.
SRC = '''\
def count_evens(numbers):
    evens = 0
    for n in numbers:
        if n % 2 == 0:
            evens += 1
    return evens

def collatz_steps(n):
    steps = 0
    while n != 1:
        if n % 2:
            n = 3 * n + 1
        else:
            n //= 2
        steps += 1
    return steps

def double(x):
    y = x * 2
    return y

def total_doubled(xs):
    total = 0
    for x in xs:
        total += double(x)
    return total

def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)

def gen_sum(xs):
    return sum(x for x in xs)

def explode(x):
    y = x + 1
    raise ValueError(y)
'''

ns = {}
exec(compile(SRC, "demo.py", "exec"), ns)


@pytest.fixture(autouse=True)
def keep_trace():
    """Whatever happens in a test, put back the trace function pytest/coverage had."""
    before = sys.gettrace()
    yield
    sys.settrace(before)


def loop_header_ok(got, line, items):
    # Python 3.10+ reports a loop header once per item plus once for the final check.
    return got.get(line) in (items + 1, items)


def test_example_count_evens():
    got = line_hits(ns["count_evens"], [1, 2, 3, 4, 6])
    assert got.get(2) == 1 and got.get(6) == 1, f"Got {got}. Lines 2 and 6 run once. Keys are RELATIVE: def line = 1 (f_lineno - co_firstlineno + 1)."
    assert got.get(4) == 5 and got.get(5) == 3, f"Got {got}. The if (line 4) runs for 5 numbers, the += (line 5) for the 3 even ones."
    assert loop_header_ok(got, 3, 5), f"Got {got}. The for line runs once per item plus a final check: 6 times."
    assert 1 not in got, f"Got {got}. The def line itself is not executed when the function is called."


def test_relative_not_absolute():
    got = line_hits(ns["double"], 4)
    assert got == {2: 1, 3: 1}, (
        f"Got {got}. double starts at line 18 of the source, but keys must be relative: "
        "line_number - fn.__code__.co_firstlineno + 1."
    )


def test_unrun_lines_missing():
    got = line_hits(ns["count_evens"], [])
    assert 4 not in got and 5 not in got, f"Got {got}. With an empty list the loop body never runs, so lines 4 and 5 must be missing."
    assert got.get(2) == 1 and got.get(6) == 1, f"Got {got}. Lines 2 and 6 still run once."


def test_while_loop():
    got = line_hits(ns["collatz_steps"], 6)  # 6 3 10 5 16 8 4 2 1: 8 steps
    assert got.get(4) == 8 and got.get(8) == 8, f"Got {got}. 6 reaches 1 in 8 steps: the if (line 4) and steps += 1 (line 8) run 8 times."
    assert got.get(5) == 2 and got.get(7) == 6, f"Got {got}. 2 odd values (3, 5) take line 5, 6 even values take line 7."
    assert 6 not in got, f"Got {got}. 'else:' is not a line that runs on its own."
    assert loop_header_ok(got, 3, 8), f"Got {got}. The while line runs once per step plus the final check."


def test_called_functions_not_counted():
    got = line_hits(ns["total_doubled"], [1, 2, 3])
    assert got.get(2) == 1 and got.get(4) == 3 and got.get(5) == 1, f"Got {got}. Expected line 2 once, line 4 three times, line 5 once."
    assert set(got) <= {2, 3, 4, 5}, (
        f"Got {got}. Lines of double() leaked in. Only trace frames whose f_code IS fn.__code__: "
        "the global tracer must return None for other frames."
    )


def test_recursion_adds_up():
    got = line_hits(ns["fact"], 4)
    assert got == {2: 4, 3: 1, 4: 3}, (
        f"Got {got}. fact(4) has 4 frames of the same code: line 2 runs 4 times, line 4 three times, "
        "line 3 once. Count every frame whose f_code is fn.__code__, not only the first."
    )


def test_generator_expression_is_other_code():
    got = line_hits(ns["gen_sum"], [1, 2, 3])
    assert got == {2: 1}, f"Got {got}. The generator expression is its own code object, so only line 2 of gen_sum counts, once."


def test_result_is_fresh_each_call():
    line_hits(ns["double"], 1)
    got = line_hits(ns["double"], 1)
    assert got == {2: 1, 3: 1}, f"Got {got}. Each call must start with a new empty dictionary."


def test_kwargs_passed():
    got = line_hits(ns["count_evens"], numbers=[2])
    assert got.get(5) == 1, f"Got {got}. Pass **kwargs on to fn."


def test_restores_previous_tracer():
    calls = []

    def other_tool(frame, event, arg):  # stands in for a debugger or coverage
        calls.append(event)
        return None

    sys.settrace(other_tool)
    try:
        line_hits(ns["double"], 3)
        now = sys.gettrace()
    finally:
        sys.settrace(None)
    assert now is other_tool, (
        f"After line_hits, sys.gettrace() is {now!r}. Save old = sys.gettrace() first and finish with "
        "sys.settrace(old), not sys.settrace(None): other tools (debugger, coverage) use the same hook."
    )


def test_restores_on_exception():
    before = sys.gettrace()
    with pytest.raises(ValueError):
        line_hits(ns["explode"], 1)
    assert sys.gettrace() is before, "When fn raises, the old tracer must still be restored: use try/finally."


def test_exception_reaches_caller():
    try:
        hits = line_hits(ns["explode"], 1)
    except ValueError:
        hits = None
    assert hits is None, "The ValueError from fn must reach the caller; do not catch it inside line_hits."
