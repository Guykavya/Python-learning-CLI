import pytest

from solution import Rectangle


def test_attributes():
    r = Rectangle(3, 4)
    assert (r.width, r.height) == (3, 4), "Rectangle(3, 4) should store width=3 and height=4 on self."


def test_area_and_perimeter():
    r = Rectangle(3, 4)
    assert r.area() == 12, "Area of 3 x 4 is 12: width * height."
    assert r.perimeter() == 14, "Perimeter of 3 x 4 is 2 * (3 + 4) = 14. Did you forget the brackets?"


def test_area_is_computed_from_current_size():
    r = Rectangle(2, 2)
    r.width = 10
    assert r.area() == 20, "area() must use the current self.width and self.height, not a value saved in __init__."


def test_is_square():
    assert Rectangle(5, 5).is_square() is True, "5 x 5 is a square: return True."
    assert Rectangle(5, 6).is_square() is False, "5 x 6 is not a square: return False (a real bool, not None)."


def test_scale_changes_in_place_and_returns_none():
    r = Rectangle(3, 4)
    result = r.scale(2)
    assert result is None, "scale() changes the rectangle in place, so it returns None (like list.sort())."
    assert (r.width, r.height) == (6, 8), "After scale(2), 3 x 4 becomes 6 x 8. Write the new values to self.width and self.height."
    assert r.area() == 48, "The area after scale(2) is 4 times the old area: 48."


def test_scale_by_fraction():
    r = Rectangle(10, 4)
    r.scale(0.5)
    assert (r.width, r.height) == (5, 2), "scale(0.5) halves both sides: 10 x 4 becomes 5 x 2."


def test_scale_twice():
    r = Rectangle(1, 2)
    r.scale(3)
    r.scale(2)
    assert (r.width, r.height) == (6, 12), "Scaling builds on the current size: (1, 2) * 3 * 2 = (6, 12)."


@pytest.mark.parametrize("bad", [0, -1])
def test_scale_rejects_non_positive(bad):
    r = Rectangle(3, 4)
    with pytest.raises(ValueError, match="factor must be positive"):
        r.scale(bad)
    assert (r.width, r.height) == (3, 4), "A rejected scale must not change the rectangle. Check the factor first."


def test_scale_only_changes_that_rectangle():
    a = Rectangle(1, 1)
    b = Rectangle(1, 1)
    a.scale(5)
    assert (b.width, b.height) == (1, 1), "scale() changes only self, not other rectangles."
