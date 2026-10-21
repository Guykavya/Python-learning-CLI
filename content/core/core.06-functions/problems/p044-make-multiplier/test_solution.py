from solution import make_multiplier


def test_returns_callable():
    assert callable(make_multiplier(2)), "make_multiplier must return a function (no parentheses after its name)."


def test_independent():
    double = make_multiplier(2)
    triple = make_multiplier(3)
    assert double(10) == 20 and triple(10) == 30, "Each returned function remembers its own factor."
    assert double(10) == 20, "Creating triple must not change double."
    assert double(triple(5)) == 30


def test_float_and_zero():
    assert make_multiplier(0.5)(9) == 4.5
    assert make_multiplier(0)(123) == 0


def test_is_closure():
    assert make_multiplier(7).__closure__ is not None, (
        "The returned function should be a closure over factor, defined inside make_multiplier.")
