from solution import is_even


def test_small_even():
    assert is_even(4) is True, "4 is even, but your function did not return True. Check the remainder test."


def test_small_odd():
    assert is_even(7) is False, "7 is odd, so is_even(7) must return False."


def test_zero_is_even():
    assert is_even(0) is True, "0 is even (0 % 2 == 0), so is_even(0) must be True."


def test_negative_numbers():
    assert is_even(-4) is True, "-4 is even. In Python -4 % 2 == 0."
    assert is_even(-3) is False, "-3 is odd. In Python -3 % 2 == 1, so no special case is needed."


def test_returns_a_real_bool():
    assert is_even(10) is True, "Return the bool True, not 1 or something that merely looks true."
    assert is_even(11) is False, "Return the bool False, not 0 or None."
