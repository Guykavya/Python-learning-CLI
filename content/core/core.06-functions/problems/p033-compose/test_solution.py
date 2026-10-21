from solution import compose


def inc(n):
    return n + 1


def double(n):
    return n * 2


def test_returns_function():
    assert callable(compose(inc)), "compose must RETURN a function, not call one."


def test_right_to_left():
    assert compose(inc, double)(5) == 11, "compose(inc, double)(5) is inc(double(5)) = 11: right to left."
    assert compose(double, inc)(5) == 12


def test_three():
    assert compose(str, inc, double)(4) == "9"


def test_string_methods():
    shout = compose(str.upper, str.strip)
    assert shout("  hi  ") == "HI"
    assert shout("x ") == "X", "The returned function must work on every call, not just the first."


def test_identity():
    assert compose()(42) == 42, "With no functions, return the argument unchanged."
    assert compose()("x") == "x"


def test_lazy():
    calls = []
    def record(x):
        calls.append(x)
        return x
    f = compose(record)
    assert calls == [], "compose must not call the functions itself; only the returned function does."
    f(1)
    f(2)
    assert calls == [1, 2]
