import math

from solution import Point


def test_stores_x_and_y():
    p = Point(3, 4)
    assert p.x == 3, "Point(3, 4).x should be 3. In __init__, write self.x = x."
    assert p.y == 4, "Point(3, 4).y should be 4. In __init__, write self.y = y."


def test_two_points_are_independent():
    a = Point(1, 2)
    b = Point(10, 20)
    assert (a.x, a.y) == (1, 2), "Each object keeps its own attributes. Did you store x and y on the class instead of on self?"
    assert (b.x, b.y) == (10, 20), "The second Point must not change the first one."


def test_distance_3_4_5():
    a = Point(0, 0)
    b = Point(3, 4)
    assert math.isclose(a.distance_to(b), 5.0), "The distance from (0, 0) to (3, 4) is 5.0 (a 3-4-5 triangle)."


def test_distance_is_symmetric_and_handles_negatives():
    a = Point(-1, -1)
    b = Point(2, 3)
    assert math.isclose(a.distance_to(b), 5.0), "From (-1, -1) to (2, 3): dx = 3, dy = 4, so 5.0. Use other.x - self.x."
    assert math.isclose(b.distance_to(a), 5.0), "Distance is the same in both directions. Square the differences so the sign does not matter."


def test_distance_to_itself_is_zero():
    p = Point(7, -2)
    assert p.distance_to(p) == 0, "A point is at distance 0 from itself."


def test_distance_returns_float():
    d = Point(0, 0).distance_to(Point(1, 1))
    assert isinstance(d, float), "distance_to should return a float (math.sqrt gives one)."
    assert math.isclose(d, math.sqrt(2)), "From (0, 0) to (1, 1) the distance is sqrt(2), about 1.414."


def test_moved_returns_new_point():
    a = Point(0, 0)
    c = a.moved(2, -1)
    assert isinstance(c, Point), "moved() should return a Point object, not a tuple or None."
    assert (c.x, c.y) == (2, -1), "Point(0, 0).moved(2, -1) should be at (2, -1): add dx to x and dy to y."
    assert c is not a, "moved() must build a NEW Point with Point(...), not return self."


def test_moved_does_not_change_original():
    a = Point(5, 5)
    a.moved(1, 1)
    assert (a.x, a.y) == (5, 5), "moved() must not change the original point. Do not write self.x += dx."


def test_moved_can_be_chained():
    p = Point(1, 1).moved(1, 0).moved(0, 2)
    assert (p.x, p.y) == (2, 3), "Because moved() returns a Point, you can call moved() on its result again."
