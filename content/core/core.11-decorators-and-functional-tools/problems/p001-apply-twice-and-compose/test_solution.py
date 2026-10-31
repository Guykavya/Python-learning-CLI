from solution import apply_twice, compose


def add_one(n):
    return n + 1


def double(n):
    return n * 2


def test_apply_twice():
    assert apply_twice(add_one, 5) == 7, "apply_twice(add_one, 5) is add_one(add_one(5)) = 7. Did you call f only once?"
    assert apply_twice(double, 3) == 12, "double(double(3)) = 12. Pass the first result into the second call."
    assert apply_twice(str.strip, "  a  ") == "a", "apply_twice must work with any function, also str methods."


def test_compose_returns_a_function():
    h = compose(add_one, double)
    assert callable(h), "compose must return a function (a callable), not a value. Define an inner function and return it."
    assert h(5) == 11, "compose(f, g)(x) is f(g(x)): double first (10), then add_one (11). Check the order."


def test_compose_order_matters():
    assert compose(double, add_one)(5) == 12, "compose(double, add_one)(5) is double(add_one(5)) = 12. g runs first, then f."
    assert compose(str.upper, str.strip)("  hi ") == "HI", "Strip first, then upper: the result is 'HI'."


def test_compose_does_not_call_early():
    calls = []

    def f(x):
        calls.append("f")
        return x

    def g(x):
        calls.append("g")
        return x

    h = compose(f, g)
    assert calls == [], "compose must not call f or g when it builds the new function. Call them only inside the inner function."
    h(1)
    assert calls == ["g", "f"], "When the new function runs, g must run first and then f."


def test_compose_reusable():
    h = compose(add_one, add_one)
    assert [h(0), h(10)] == [2, 12], "The returned function must work again and again with different inputs."
