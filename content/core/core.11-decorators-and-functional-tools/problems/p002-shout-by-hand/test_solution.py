from solution import greet, loud_greet, shout


def test_greet_unchanged():
    assert greet("ann") == "hello, ann", "greet itself must still return the normal text. shout must not change the original function."


def test_loud_greet():
    assert loud_greet("ann") == "HELLO, ANN", "loud_greet = shout(greet) must return greet's result in upper case."
    assert loud_greet is not greet, "shout must return a NEW function (the wrapper), not the same function."


def test_shout_passes_arguments():
    def label(item, price=0):
        return f"{item}: {price}"

    assert shout(label)("tea", price=20) == "TEA: 20", "The wrapper must pass both positional and keyword arguments: func(*args, **kwargs)."
    assert shout(label)("tea") == "TEA: 0", "Default values of func must still work through the wrapper."


def test_shout_does_not_call_early():
    calls = []

    def f():
        calls.append(1)
        return "x"

    w = shout(f)
    assert calls == [], "shout(f) must not call f. Only the wrapper calls f, later."
    assert w() == "X", "Calling the wrapper calls f and upper-cases its result."
    assert calls == [1], "Each call of the wrapper must call f exactly once."
