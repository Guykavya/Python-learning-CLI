from solution import CallCounter


def add(a, b=10):
    return a + b


def test_instance_is_callable_and_forwards():
    c = CallCounter(add)
    assert callable(c), "Define __call__ so that callable(obj) is True."
    assert c(1, 2) == 3, "Calling the object must call the wrapped function and RETURN its result."
    assert c(5) == 15 and c(a=1, b=1) == 2, "Forward positional and keyword arguments: *args, **kwargs."


def test_counts_calls():
    c = CallCounter(add)
    assert c.count == 0, "count starts at 0."
    c(1)
    c(2)
    c(3)
    assert c.count == 3, "Every call increases count by one."


def test_failed_calls_are_counted_and_error_propagates():
    c = CallCounter(int)
    try:
        c("x")
    except ValueError:
        pass
    else:
        raise AssertionError("The wrapped function's exception must not be swallowed.")
    assert c.count == 1, "Count the call BEFORE running the function, so a call that raises is still counted."


def test_reset():
    c = CallCounter(add)
    c(1)
    c.reset()
    assert c.count == 0, "reset() sets count back to 0."
    c(2)
    assert c.count == 1, "Counting continues after a reset."


def test_works_as_a_decorator_and_two_objects_are_independent():
    @CallCounter
    def hello(name):
        return "hi " + name

    assert hello("Asha") == "hi Asha" and hello.count == 1, "@CallCounter replaces the function by a CallCounter object; calls still work."
    other = CallCounter(add)
    other(1)
    assert hello.count == 1 and other.count == 1, "count must be an instance attribute (set in __init__), not a class attribute shared by all."


def test_works_with_builtins_and_lambdas():
    c = CallCounter(lambda *a: len(a))
    assert c(1, 2, 3) == 3, "Any callable can be wrapped."
    assert list(map(CallCounter(str.upper), ["a", "b"])) == ["A", "B"], "A CallCounter can be passed wherever a function is expected (map)."
