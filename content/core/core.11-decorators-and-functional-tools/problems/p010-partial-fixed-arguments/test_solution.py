from functools import partial

from solution import cube, from_binary, from_hex, power, square


def test_square_and_cube():
    assert square(5) == 25, "square(5) must be 25. If you got 32, you fixed base=2 instead of exp=2: use partial(power, exp=2)."
    assert cube(2) == 8, "cube(2) is 2 ** 3 = 8. Fix exp with a keyword: partial(power, exp=3)."
    assert square(-3) == 9, "square(-3) is 9."


def test_parsers():
    assert from_binary("1010") == 10, "from_binary('1010') is 10. Fix int's keyword base=2."
    assert from_binary("111") == 7, "'111' in base 2 is 7."
    assert from_hex("ff") == 255, "from_hex('ff') is 255. Use partial(int, base=16)."
    assert from_hex("1A") == 26, "int accepts upper and lower case hex digits."


def test_are_partials():
    for name, obj in [("square", square), ("cube", cube), ("from_binary", from_binary), ("from_hex", from_hex)]:
        assert isinstance(obj, partial), f"{name} must be made with functools.partial, not def or lambda."


def test_partial_contents():
    assert square.func is power, "square must wrap the power function itself."
    assert square.keywords == {"exp": 2}, "Fix exp as a keyword argument (exp=2), so the caller's number becomes base."
    assert from_binary.func is int, "from_binary must wrap the built-in int."
    assert power(2, 10) == 1024, "Do not change power itself."
