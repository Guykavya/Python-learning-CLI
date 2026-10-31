from solution import Point


def test_equal_by_value():
    assert Point(1, 2) == Point(1, 2), "Two Points with the same x and y should be ==. Define __eq__."


def test_not_equal():
    assert not (Point(1, 2) == Point(2, 1)), "Different coordinates (even swapped) are not equal."
    assert Point(1, 2) != Point(3, 4), "!= should work from __eq__ without writing __ne__."


def test_other_types_are_not_equal():
    assert not (Point(1, 2) == (1, 2)), "A Point is not equal to a tuple. Check isinstance(other, Point) first."
    assert not (Point(1, 2) == 5), "Comparing with an int must give False, not raise AttributeError."
    assert not (Point(1, 2) == None), "Comparing with None must give False."


def test_returns_notimplemented_for_foreign_types():
    assert Point(1, 2).__eq__(5) is NotImplemented, "For types you do not understand, return NotImplemented (not False)."


def test_in_and_index():
    pts = [Point(0, 0), Point(1, 2)]
    assert Point(1, 2) in pts, "`in` uses == on every item, so it needs __eq__."
    assert pts.index(Point(1, 2)) == 1, "list.index also uses ==."


def test_works_with_floats_and_same_object():
    p = Point(1.0, 2)
    assert p == p, "An object is equal to itself."
    assert Point(1.0, 2) == Point(1, 2), "1.0 == 1 in Python, so these Points are equal."
