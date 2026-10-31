import sys

import pytest

from solution import call_counts


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def square(x):
    return x * x


def total_of_squares(items, scale=1):
    return sum(square(x) for x in items) * scale


def main():
    return [fib(i) for i in range(3)]


def boom():
    raise KeyError("missing")


def make_helper(k):
    def helper():
        return k
    return helper


helper_a = make_helper(1)
namespace = {}
exec(compile("def helper():\n    return 2\n", "other_file.py", "exec"), namespace)
helper_b = namespace["helper"]


def uses_two_helpers():
    for _ in range(3):
        helper_a()
    for _ in range(4):
        helper_b()


def test_recursive_fib():
    got = call_counts(fib, 10)
    assert got.get("fib") == 177, (
        f"fib(10) makes 177 calls of fib in total, got {got.get('fib')}. Use total_calls (index 1 of the stats "
        "tuple), not primitive_calls (index 0), which counts only the outermost call of a recursion."
    )


def test_fn_itself_is_counted():
    got = call_counts(square, 3)
    assert got == {"square": 1}, (
        f"Got {got}. Only Python functions belong in the result: square ran once. Skip entries whose filename is "
        "'~' (built-ins such as the profiler's own disable method)."
    )


def test_main_and_fib():
    got = call_counts(main)
    got.pop("<listcomp>", None)  # Python 3.11 shows the comprehension as a function
    assert got == {"main": 1, "fib": 5}, f"Got {got}. main runs once, fib runs 1 + 1 + 3 = 5 times for fib(0), fib(1), fib(2)."


def test_passes_args_and_kwargs():
    got = call_counts(total_of_squares, [1, 2, 3, 4], scale=2)
    assert got.get("total_of_squares") == 1 and got.get("square") == 4, (
        f"Got {got}. Pass both *args and **kwargs on to fn: fn(*args, **kwargs)."
    )


def test_no_builtins():
    got = call_counts(total_of_squares, range(5))
    bad = [name for name in got if name.startswith("<built-in") or name.startswith("<method")]
    assert not bad, f"Built-ins must be left out, found {bad}. Their stats key has filename '~'."


def test_same_name_counts_are_added():
    got = call_counts(uses_two_helpers)
    assert got.get("helper") == 7, (
        f"Two different functions are both called 'helper' (3 + 4 calls), got {got.get('helper')}. "
        "Add the counts together with counts[name] = counts.get(name, 0) + total; do not overwrite."
    )


def test_values_are_ints():
    got = call_counts(fib, 3)
    assert all(type(v) is int for v in got.values()), f"Counts must be ints, got {got}."


def test_exception_propagates_and_profiler_is_off():
    with pytest.raises(KeyError):
        call_counts(boom)
    # If the profiler was left on, the next one cannot start (Python 3.12+) or the counts get mixed up.
    try:
        got = call_counts(fib, 4)
    except ValueError as e:
        raise AssertionError(
            f"A second call_counts failed with {e!r}: the profiler from the call that raised is still on. "
            "Put profiler.disable() in a finally block."
        ) from None
    assert got == {"fib": 9}, f"After an exception the next run must start clean, got {got}. Disable in finally."


def test_fresh_profiler_each_call():
    call_counts(fib, 5)
    got = call_counts(fib, 5)
    assert got == {"fib": 15}, (
        f"fib(5) makes 15 calls, got {got}. Create a NEW cProfile.Profile() inside call_counts; a module-level "
        "profiler keeps counting from earlier runs."
    )
