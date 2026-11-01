"""Line events differ a little between Python versions (for example whether the `for` line
or a generator's `yield` line is reported again when a loop or generator resumes). These tests
only check what is the same on 3.11 to 3.14: which body lines run, how often plain loop-body
lines run, and the order of calls."""

import json
import sys

import pytest

from solution import line_counts, trace_lines


def straight(x):
    y = x + 1
    z = y * 2
    return z


def loop(n):
    total = 0
    for i in range(n):
        total += i
    return total


def countdown(n):
    while n > 0:
        n -= 1
    return n


def doubles(items):
    for x in items:
        yield x * 2


def use_gen():
    out = []
    for v in doubles([1, 2, 3]):
        out.append(v)
    return out


def helper(a):
    return a * 10


def caller():
    a = helper(1)
    b = helper(2)
    return json.dumps([a, b])


def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)


def greet(name, punctuation="."):
    return "hi " + name + punctuation


def boom():
    x = 1
    raise ValueError(x)


def body_lines(events, name):
    """Lines >= 1 of one function, with consecutive repeats removed."""
    out = []
    for func_name, line in events:
        if func_name == name and line >= 1 and (not out or out[-1] != line):
            out.append(line)
    return out


@pytest.fixture(autouse=True)
def no_tracer_left_behind():
    yield
    leftover = sys.gettrace()
    sys.settrace(None)
    assert leftover is None, "trace_lines must restore the previous trace function (here: None) when it finishes."


def test_result_is_returned():
    result, events = trace_lines(straight, 3)
    assert result == 8, "trace_lines returns (func's result, events)."
    assert isinstance(events, list) and all(isinstance(e, tuple) and len(e) == 2 for e in events), (
        "events is a list of (function name, relative line) tuples."
    )


def test_arguments_are_passed():
    assert trace_lines(greet, "ada", punctuation="!")[0] == "hi ada!", "Pass *args and **kwargs on to func."


def test_straight_line_code():
    _, events = trace_lines(straight, 3)
    assert body_lines(events, "straight") == [1, 2, 3], (
        "Record (frame.f_code.co_name, frame.f_lineno - frame.f_code.co_firstlineno) for every 'line' event. "
        "Line numbers are relative to the def line, so the first body line is 1."
    )


def test_loop_body_counts():
    _, events = trace_lines(loop, 4)
    counts = line_counts(events, "loop")
    assert counts[1] == 1 and counts[4] == 1, "total = 0 and return total run once each."
    assert counts[3] == 4, "The loop body (total += i) runs 4 times for n = 4: record EVERY line event, also repeats."


def test_while_loop_counts():
    _, events = trace_lines(countdown, 3)
    assert line_counts(events, "countdown")[2] == 3, "n -= 1 runs three times."


def test_calls_are_traced():
    _, events = trace_lines(caller)
    names = {name for name, _ in events}
    assert "helper" in names, (
        "The global trace function is called for EVERY new frame; return the local tracer for helper too, "
        "not only for func."
    )
    first = events.index(("caller", 1))
    inside = events.index(("helper", 1))
    second = events.index(("caller", 2))
    assert first < inside < second, "helper's line runs after caller's line 1 and before caller's line 2."
    assert line_counts(events, "helper")[1] == 2, "helper is called twice."


def test_library_code_is_not_traced():
    _, events = trace_lines(caller)
    names = {name for name, _ in events}
    assert names == {"caller", "helper"}, (
        f"Only code from func's file should be recorded, got names {sorted(names)}. json.dumps is Python code "
        "in another file: compare frame.f_code.co_filename with func.__code__.co_filename."
    )


def test_generators_are_traced():
    result, events = trace_lines(use_gen)
    assert result == [2, 4, 6]
    assert line_counts(events, "use_gen")[3] == 3, "out.append(v) runs once per item."
    assert line_counts(events, "doubles")[2] >= 3, (
        "The generator's frame is traced too: each resume is a new 'call' event for its frame, so return the "
        "local tracer for it. Its yield line runs (at least) once per item."
    )


def test_recursion():
    result, events = trace_lines(fact, 3)
    assert result == 6
    counts = line_counts(events, "fact")
    assert counts[1] == 3, "Each of the 3 calls fact(3), fact(2), fact(1) tests n <= 1 once."
    assert counts[2] == 1 and counts[3] == 2, "Only fact(1) returns 1; fact(3) and fact(2) recurse."


def test_previous_tracer_is_restored():
    calls = []

    def outer_tracer(frame, event, arg):
        calls.append(event)
        return None

    sys.settrace(outer_tracer)
    try:
        trace_lines(straight, 1)
        current = sys.gettrace()
    finally:
        sys.settrace(None)
    assert current is outer_tracer, (
        "Save sys.gettrace() before installing your tracer and put it back afterwards (a debugger or coverage "
        "tool may have installed one)."
    )


def test_restored_even_when_func_raises():
    with pytest.raises(ValueError):
        trace_lines(boom)
    assert sys.gettrace() is None, "Restore the old tracer in a finally: block, so it happens even if func raises."


def test_line_counts():
    events = [("f", 1), ("f", 2), ("g", 1), ("f", 2), ("f", 3)]
    assert line_counts(events, "f") == {1: 1, 2: 2, 3: 1}, "line_counts counts lines of ONE function."
    assert line_counts(events, "nobody") == {}, "No events for that name: an empty Counter."
