from solution import curry


def volume(l, w, h):
    """Volume of a box."""
    return l * w * h


def greet(greeting, name, punct="!"):
    return f"{greeting}, {name}{punct}"


def test_all_ways_of_splitting():
    v = curry(volume)
    assert v(2)(3)(4) == 24, "One argument per call: keep collecting until you have three."
    assert v(2, 3)(4) == 24, "Two, then one."
    assert v(2)(3, 4) == 24, "One, then two."
    assert v(2, 3, 4) == 24, "All at once: call func right away."


def test_partial_results_are_independent():
    v = curry(volume)
    base = v(2)
    assert base(3)(4) == 24
    assert base(5)(1) == 10, (
        "base must not remember arguments from an earlier use. Build a NEW tuple of arguments on "
        "each call (saved + new) instead of appending to a shared list."
    )
    a = base(3)
    b = base(10)
    assert a(1) == 6 and b(1) == 20 and a(2) == 12, "Every partly-applied function keeps only its own arguments."


def test_curry_does_not_call_early():
    calls = []

    def add(a, b):
        calls.append((a, b))
        return a + b

    c = curry(add)
    assert calls == [], "curry(func) itself must not call func."
    half = c(1)
    assert calls == [] and callable(half), "With too few arguments, return a function; do not call func."
    assert half(2) == 3
    assert calls == [(1, 2)]


def test_defaults_and_keywords():
    g = curry(greet)
    hello = g("Hello")
    assert hello("Ann") == "Hello, Ann!", "A parameter with a default is not required: two arguments are enough."
    assert hello(punct="?")("Bo") == "Hello, Bo?", "Keywords are collected and passed at the end."
    assert g(punct=".")("Hi")("Cy") == "Hi, Cy.", "A keyword may come in the very first call."
    assert g("Yo", punct="?")(punct="!!")("Di") == "Yo, Di!!", "A later keyword wins over an earlier one."
    assert hello("Ed") == "Hello, Ed!", "Keywords given to one branch must not leak into another."


def test_no_required_parameters():
    def answer(x=42):
        return x

    assert curry(answer)() == 42, "With no required parameters, the first call calls func."
    assert curry(answer)(7) == 7


def test_metadata():
    v = curry(volume)
    assert v.__name__ == "volume" and v.__doc__ == "Volume of a box.", "Use functools.wraps on the curried function."
    assert v(1).__name__ == "volume", "Partly-applied functions keep the name too."
