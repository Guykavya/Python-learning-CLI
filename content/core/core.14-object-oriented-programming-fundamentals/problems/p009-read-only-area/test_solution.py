import math

import pytest

from solution import Circle


def test_radius_and_diameter():
    c = Circle(2)
    assert c.radius == 2, "Circle(2).radius should be 2."
    assert c.diameter == 4, "The diameter is 2 * radius."


def test_area():
    assert math.isclose(Circle(2).area, math.pi * 4), "The area is math.pi * radius ** 2 (about 12.57 for radius 2)."
    assert math.isclose(Circle(1).area, math.pi), "A circle of radius 1 has area pi."


def test_properties_exist_in_class():
    for name in ("radius", "diameter", "area"):
        assert isinstance(vars(Circle).get(name), property), f"{name} must be a property defined in the class (use @property)."


def test_radius_stored_in_backing_attribute_only():
    c = Circle(2)
    assert vars(c) == {"_radius": 2}, (
        "The object should store only _radius. Diameter and area are computed by properties, not saved in __init__."
    )


def test_computed_values_follow_radius():
    c = Circle(2)
    c.radius = 3
    assert c.diameter == 6, "After c.radius = 3, the diameter must be 6. Compute it in the property, do not save it in __init__."
    assert math.isclose(c.area, math.pi * 9), "After c.radius = 3, the area must be pi * 9."


def test_area_is_read_only():
    c = Circle(2)
    try:
        c.area = 100
    except AttributeError:
        pass
    else:
        pytest.fail("c.area = 100 must raise AttributeError. Make area a property with no setter.")
    assert math.isclose(c.area, math.pi * 4), "The area must not change after a failed assignment."


def test_diameter_is_read_only():
    c = Circle(2)
    with pytest.raises(AttributeError):
        c.diameter = 10


@pytest.mark.parametrize("bad", [0, -1, -0.5])
def test_setter_rejects_non_positive(bad):
    c = Circle(5)
    with pytest.raises(ValueError, match="radius must be positive"):
        c.radius = bad
    assert c.radius == 5, "A rejected radius must not be stored."


def test_constructor_checks_radius():
    try:
        Circle(-2)
    except ValueError as e:
        assert "radius must be positive" in str(e), "Use the message 'radius must be positive'."
    else:
        pytest.fail("Circle(-2) must raise ValueError. In __init__, assign self.radius = radius so the setter checks it.")


def test_float_radius():
    c = Circle(0.5)
    assert c.diameter == 1.0, "A float radius works too: 2 * 0.5 = 1.0."
