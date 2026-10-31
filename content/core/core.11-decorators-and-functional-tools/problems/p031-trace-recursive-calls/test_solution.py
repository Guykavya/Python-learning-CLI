import pytest

from solution import trace_calls


def test_factorial_tree():
    log = []

    @trace_calls(log)
    def fact(n):
        return 1 if n <= 1 else n * fact(n - 1)

    assert fact(3) == 6, "Return the function's result."
    assert log == [
        "fact(3)",
        "  fact(2)",
        "    fact(1)",
        "    -> 1",
        "  -> 2",
        "-> 6",
    ], "Indent two spaces per depth level. The '->' line has the same indent as its call line."


def test_branching_recursion():
    log = []

    @trace_calls(log)
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(3) == 2
    assert log == [
        "fib(3)",
        "  fib(2)",
        "    fib(1)",
        "    -> 1",
        "    fib(0)",
        "    -> 0",
        "  -> 1",
        "  fib(1)",
        "  -> 1",
        "-> 2",
    ], "After fib(2) returns, depth must go back to 1 before fib(1) is called."


def test_arguments_format():
    log = []

    @trace_calls(log)
    def greet(name, loud=False):
        return name.upper() if loud else name

    greet("ann", loud=True)
    assert log == ["greet('ann', loud=True)", "-> 'ANN'"], "Use repr for arguments and results; keywords as key=repr(value)."


def test_exception_restores_depth():
    log = []

    @trace_calls(log)
    def down(n):
        if n == 0:
            raise ValueError("bottom")
        return down(n - 1)

    with pytest.raises(ValueError):
        down(1)
    assert log == ["down(1)", "  down(0)", "  !! ValueError", "!! ValueError"], (
        "On an exception, log '!! ClassName' at the call's indent, then let the exception go on."
    )
    log.clear()
    with pytest.raises(ValueError):
        down(0)
    assert log == ["down(0)", "!! ValueError"], (
        "The depth did not go back down after the exception. Decrease it in a finally block."
    )


def test_each_function_has_its_own_depth():
    log = []
    tracer = trace_calls(log)

    @tracer
    def inner(x):
        return x + 1

    @tracer
    def outer(x):
        return inner(x) * 2

    outer(1)
    assert log == ["outer(1)", "inner(1)", "-> 2", "-> 4"], (
        "Each decorated function keeps its own depth (create it in decorator, not in trace_calls)."
    )


def test_wrapped_still_traces_inner_calls():
    log = []

    @trace_calls(log)
    def fact(n):
        return 1 if n <= 1 else n * fact(n - 1)

    assert fact.__wrapped__(3) == 6, "functools.wraps sets __wrapped__ to the original function."
    assert log == ["fact(2)", "  fact(1)", "  -> 1", "-> 2"], (
        "The outer call skipped the wrapper, but the body looks up the name fact at call time, "
        "and that name is the wrapper. So the inner calls are traced, starting at depth 0."
    )
    assert fact.__name__ == "fact"
