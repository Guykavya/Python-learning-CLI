import dataclasses

from solution import Cart, Counter, Tags


def test_carts_do_not_share_items():
    a, b = Cart("asha"), Cart("ravi")
    a.add("pen")
    assert b.items == [], "Cart 'ravi' got Asha's pen: a default argument `items=[]` is created ONCE and shared by every call. Use a dataclass field with default_factory=list."
    assert a.items == ["pen"] and a.count() == 1 and b.count() == 0, "Each cart has its own list."


def test_cart_is_a_dataclass_with_generated_methods():
    assert dataclasses.is_dataclass(Cart), "Turn Cart into a dataclass: @dataclass, annotated fields, and `items: list = field(default_factory=list)`."
    assert repr(Cart("a")) == "Cart(owner='a', items=[])", "The generated repr is expected."
    assert Cart("a", ["x"]) == Cart("a", ["x"]) and Cart("a") != Cart("b"), "The generated __eq__ compares the fields."


def test_cart_keeps_a_list_given_by_the_caller():
    mine = ["pen"]
    c = Cart("a", mine)
    assert c.items is mine, "A list that is passed in is stored as is (the factory only runs when no value is passed)."


def test_tags_construct_without_arguments():
    t = Tags()
    assert t.names == set(), "Tags() should start with an empty set. `default_factory=set()` passes a set OBJECT; the factory must be the callable `set`, without parentheses."
    t.add("Python")
    assert t.names == {"python"}, "add() lower-cases the name."


def test_tags_are_independent():
    a, b = Tags(), Tags()
    a.add("x")
    assert b.names == set(), "Each Tags object needs its own set."


def test_counters_do_not_share_counts():
    a, b = Counter(), Counter()
    a.hit("x")
    a.hit("x")
    assert a.counts == {"x": 2}, "hit() counts per key."
    assert b.counts == {}, "The lambda returns the same module-level dict every time, so all counters share it. The factory must build a NEW dict: default_factory=dict."


def test_no_module_level_shared_state_is_used():
    import solution
    assert not hasattr(solution, "SHARED_COUNTS") or solution.SHARED_COUNTS == {}, "The shared dict SHARED_COUNTS must stay empty: nothing should write into it any more (remove it)."
    Counter().hit("z")
    assert not getattr(solution, "SHARED_COUNTS", {}), "Counter() still writes into SHARED_COUNTS."


def test_factories_are_real_callables_in_the_fields():
    by_name = {f.name: f for f in dataclasses.fields(Counter)}
    assert by_name["counts"].default_factory is dict, "counts should be field(default_factory=dict)."
    assert {f.name: f for f in dataclasses.fields(Tags)}["names"].default_factory is set, "names should be field(default_factory=set)."
