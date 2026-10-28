from solution import Point


def test_basic_repr():
    assert repr(Point(3, 4)) == "Point(3, 4)", "repr(Point(3, 4)) should be exactly 'Point(3, 4)'. Define __repr__ and RETURN a string."


def test_floats_and_negatives():
    assert repr(Point(1.5, -2)) == "Point(1.5, -2)", "Show the values with repr: Point(1.5, -2)."


def test_strings_keep_quotes():
    assert repr(Point("a", "b")) == "Point('a', 'b')", "Use {self.x!r} (repr of the value) so strings keep their quotes: Point('a', 'b')."


def test_print_falls_back_to_repr(capsys):
    print(Point(3, 4))
    assert capsys.readouterr().out == "Point(3, 4)\n", "print() uses __str__, which falls back to __repr__ when you do not define __str__."


def test_inside_a_list():
    assert str([Point(1, 2), Point(0, 0)]) == "[Point(1, 2), Point(0, 0)]", "Lists show their items with repr, so __repr__ must be defined (not only __str__)."


def test_returns_string_not_prints(capsys):
    r = Point(1, 1).__repr__()
    assert isinstance(r, str), "__repr__ must return a str, not print it."
    assert capsys.readouterr().out == "", "__repr__ must not print anything; it only returns the text."
