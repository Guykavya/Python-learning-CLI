import pytest

from solution import Locked


class Point(Locked):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)


class Rect(Locked):
    def __init__(self, w, h):
        super().__init__(w=w, h=h, area=w * h)


class Named(Locked):
    def __init__(self, name):
        self.label = name.upper()  # normal assignment before locking is allowed
        super().__init__(name=name)


def test_fields_are_set_in_init():
    p = Point(1, 2)
    assert (p.x, p.y) == (1, 2), "Locked.__init__(**fields) must store every keyword as an attribute."
    r = Rect(3, 4)
    assert r.area == 12, "A subclass may pass computed fields to super().__init__."


def test_cannot_change_after_init():
    p = Point(1, 2)
    with pytest.raises(AttributeError) as info:
        p.x = 10
    assert "x" in str(info.value), "The AttributeError message must name the attribute you tried to set ('x')."
    assert p.x == 1, "A refused assignment must leave the old value in place."


def test_cannot_add_new_attributes():
    p = Point(1, 2)
    with pytest.raises(AttributeError) as info:
        p.z = 3
    assert "z" in str(info.value), "Adding a brand-new attribute after __init__ must be refused too, naming 'z'."


def test_cannot_delete():
    p = Point(1, 2)
    with pytest.raises(AttributeError) as info:
        del p.y
    assert "y" in str(info.value), "__delattr__ must refuse and name the attribute ('y')."
    assert p.y == 2, "A refused delete must not remove the value."


def test_setattr_builtin_is_blocked_too():
    p = Point(1, 2)
    with pytest.raises(AttributeError):
        setattr(p, "x", 5)


def test_instances_are_independent():
    a = Point(1, 2)
    b = Point(3, 4)
    assert (a.x, b.x) == (1, 3), (
        "Creating a second object must still work. Did you store the 'locked' flag on the class instead of the instance?"
    )


def test_assignment_before_lock_works_for_every_instance():
    a = Named("ada")
    b = Named("bob")
    assert (a.label, b.label) == ("ADA", "BOB"), (
        "Normal assignment must work until THIS object is locked. "
        "Did you store the 'locked' flag on the class, so the second object is locked from the start?"
    )
    with pytest.raises(AttributeError):
        a.label = "x"


def test_init_cannot_be_rerun():
    p = Point(1, 2)
    with pytest.raises(AttributeError):
        p.__init__(5, 6)
    assert (p.x, p.y) == (1, 2), (
        "Calling __init__ again on a locked object must fail: object.__setattr__ skips your guard, so check the flag in __init__."
    )


def test_repr_lists_fields_in_order():
    assert repr(Point(1, 2)) == "Point(x=1, y=2)", "repr must be ClassName(field=value, ...) in the order given."
    assert repr(Rect(2, 5)) == "Rect(w=2, h=5, area=10)", "Use type(self).__name__ so subclasses show their own name."
    assert repr(Point("a", None)) == "Point(x='a', y=None)", "Use repr() of each value (strings get quotes)."
