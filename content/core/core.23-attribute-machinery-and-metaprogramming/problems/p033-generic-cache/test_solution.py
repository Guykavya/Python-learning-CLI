import pytest

from solution import Box


def test_plain_box_accepts_anything():
    b = Box()
    with pytest.raises(LookupError) as info:
        b.get()
    assert str(info.value) == "box is empty", "get() on an empty box raises LookupError('box is empty')."
    b.put("x")
    b.put(None)
    assert b.get() is None, "put replaces the value; None is a valid value (use a private sentinel for 'empty')."
    assert Box.item_type is object, "Plain Box has item_type = object."


def test_subscription_creates_a_checking_subclass():
    IntBox = Box[int]
    assert isinstance(IntBox, type) and issubclass(IntBox, Box), "Box[int] must be a real class: a subclass of Box."
    assert IntBox is not Box, "Box[int] must be a new class, not Box itself."
    assert IntBox.__name__ == "Box[int]", "Name the new class f'{cls.__name__}[{param name}]'."
    assert IntBox.item_type is int, "The new class stores the parameter as item_type."
    b = IntBox()
    b.put(5)
    assert b.get() == 5, "Box[int] accepts ints."
    with pytest.raises(TypeError) as info:
        b.put("five")
    assert str(info.value) == "Box[int] accepts int, not str", (
        "The error names the box class, the expected type and the actual type: 'Box[int] accepts int, not str'."
    )
    assert b.get() == 5, "A rejected value must not replace the stored one."


def test_isinstance_rules_apply():
    b = Box[float]()
    with pytest.raises(TypeError):
        b.put(1)
    b.put(1.5)
    n = Box[int]()
    n.put(True)
    assert n.get() is True, "put uses isinstance, and bool is a subclass of int, so True is accepted."


def test_cache_returns_the_same_class():
    assert Box[int] is Box[int], "Box[int] must return the same class every time: cache it."
    assert Box[str] is not Box[int], "Different parameters give different classes."
    assert Box[list[int]] is Box[list[int]], "Generic aliases are cached too (equal aliases hash equally)."


def test_cache_is_per_class():
    class Special(Box):
        def shout(self):
            return str(self.get()).upper()

    S = Special[str]
    assert S is not Box[str], (
        "Special[str] must not come from Box's cache entry for str. Use (cls, param) as the cache key."
    )
    assert issubclass(S, Special) and S.__name__ == "Special[str]", "Special[str] subclasses Special and is named after it."
    s = S()
    s.put("hi")
    assert s.shout() == "HI", "The generated class inherits the methods of the class that was subscripted."
    assert Special[str] is S, "Special's subscriptions are cached too."


def test_repr():
    b = Box[int]()
    assert repr(b) == "Box[int](empty)", "Empty box repr: 'Box[int](empty)'."
    b.put(5)
    assert repr(b) == "Box[int](5)", "Full box repr: 'Box[int](5)'."
    s = Box[str]()
    s.put("a")
    assert repr(s) == "Box[str]('a')", "Use repr() of the value."
    assert repr(Box()) == "Box(empty)", "Plain Box works too."


def test_nested_boxes():
    inner = Box[int]()
    inner.put(1)
    Outer = Box[Box[int]]
    assert Outer.__name__ == "Box[Box[int]]", "A parameterised box is a class, so it can be a parameter: name it by __name__."
    o = Outer()
    o.put(inner)
    with pytest.raises(TypeError) as info:
        o.put(Box[str]())
    assert str(info.value) == "Box[Box[int]] accepts Box[int], not Box[str]", (
        "A Box[str] is not a Box[int]: the check is isinstance(value, Box[int])."
    )


def test_generic_alias_parameter():
    LB = Box[list[int]]
    assert LB.__name__ == "Box[list[int]]", "Name an alias parameter with repr(alias): 'list[int]'."
    assert LB.item_type == list[int], "item_type keeps the alias itself."
    b = LB()
    b.put([1, 2])
    b.put([])
    with pytest.raises(TypeError) as info:
        b.put("x")
    assert str(info.value) == "Box[list[int]] accepts list[int], not str", (
        "Check isinstance against the alias's __origin__ (list); isinstance(x, list[int]) itself raises TypeError."
    )


def test_bad_parameters():
    with pytest.raises(TypeError) as info:
        Box[int, str]
    assert str(info.value) == "Box takes exactly one type", (
        "Box[int, str] passes the tuple (int, str) to __class_getitem__: reject tuples."
    )
    with pytest.raises(TypeError):
        Box[3]
    with pytest.raises(TypeError):
        Box["int"]


def test_cannot_subscript_twice():
    with pytest.raises(TypeError):
        Box[int][str]


def test_subclass_of_parameterised_box():
    class IntBox(Box[int]):
        def double(self):
            return self.get() * 2

    b = IntBox()
    b.put(21)
    assert b.double() == 42, "A subclass of Box[int] works like a normal subclass."
    with pytest.raises(TypeError) as info:
        b.put("x")
    assert str(info.value) == "IntBox accepts int, not str", "The check is inherited; the message uses type(self).__name__."
