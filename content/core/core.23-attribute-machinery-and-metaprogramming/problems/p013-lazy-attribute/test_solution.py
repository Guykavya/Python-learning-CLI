import pytest

from solution import lazy


def make_circle_class():
    class Circle:
        def __init__(self, r):
            self.r = r
            self.calls = 0

        @lazy
        def area(self):
            """Area of the circle (pi taken as 3)."""
            self.calls += 1
            return 3 * self.r * self.r

    return Circle


def test_nothing_is_computed_at_creation():
    Circle = make_circle_class()
    c = Circle(2)
    assert c.calls == 0, "Creating the object must not run area(). The value is computed on the first READ."
    assert "area" not in vars(c), "Before the first read, nothing should be cached in the instance __dict__."


def test_first_read_computes_the_value():
    Circle = make_circle_class()
    c = Circle(2)
    assert c.area == 12, "c.area (no brackets) must call the decorated function with the instance and return 12."
    assert c.calls == 1, "The first read must call the function exactly once."


def test_value_is_computed_only_once():
    Circle = make_circle_class()
    c = Circle(2)
    values = [c.area, c.area, c.area]
    assert values == [12, 12, 12], "Every read must give the same value."
    assert c.calls == 1, (
        f"The function ran {c.calls} times for 3 reads. Store the result in instance.__dict__ "
        "the first time so later reads do not compute again."
    )


def test_value_is_cached_in_the_instance_dict_under_the_attribute_name():
    Circle = make_circle_class()
    c = Circle(2)
    c.area
    assert vars(c).get("area") == 12, (
        "After the first read, vars(c) must contain 'area': 12. The cache lives in the INSTANCE "
        "__dict__, under the attribute's name."
    )


def test_later_reads_do_not_call_get_at_all():
    get_calls = []

    class SpyLazy(lazy):
        def __get__(self, instance, owner=None):
            get_calls.append(instance)
            return super().__get__(instance, owner)

    class Box:
        @SpyLazy
        def size(self):
            return 5

    b = Box()
    b.size
    b.size
    b.size
    assert len(get_calls) == 1, (
        f"__get__ ran {len(get_calls)} times for 3 reads. Once the value is in b.__dict__, a NON-DATA "
        "descriptor is skipped: the instance dict wins. Did you define __set__ (which makes it a data descriptor)?"
    )


def test_lazy_is_a_non_data_descriptor():
    assert hasattr(lazy, "__get__"), "lazy needs __get__ to be a descriptor at all."
    assert not hasattr(lazy, "__set__"), (
        "lazy must NOT define __set__. With __set__ it becomes a data descriptor, which beats the "
        "instance __dict__, so the cached value would never be used directly."
    )
    assert not hasattr(lazy, "__delete__"), "lazy must not define __delete__ either (that also makes it a data descriptor)."


def test_each_instance_has_its_own_value():
    Circle = make_circle_class()
    small, big = Circle(1), Circle(2)
    assert small.area == 3, "Circle(1).area is 3."
    assert big.area == 12, (
        "Circle(2).area is 12. If you got 3, the value is cached ON THE DESCRIPTOR, which is shared "
        "by every instance of the class. Cache it in instance.__dict__ instead."
    )
    assert small.area == 3, "Reading big.area must not change small.area."


def test_del_forgets_the_value_and_the_next_read_recomputes():
    Circle = make_circle_class()
    c = Circle(2)
    assert c.area == 12
    c.r = 3
    assert c.area == 12, "The cached value stays until it is deleted, even if r changes."
    del c.area
    assert "area" not in vars(c), "del c.area must remove the cached value from the instance __dict__."
    assert c.area == 27, "After del, the next read must compute again (3 * 3 * 3 = 27)."
    assert c.calls == 2, "Two computations in total: one before and one after del."


def test_assignment_overrides_without_computing():
    Circle = make_circle_class()
    c = Circle(2)
    c.area = 99
    assert c.area == 99, "Assigning c.area = 99 must just store 99 in the instance __dict__ (no __set__)."
    assert c.calls == 0, "An assigned value must not trigger the computation."


def test_class_access_returns_the_descriptor():
    Circle = make_circle_class()
    assert isinstance(Circle.area, lazy), (
        "Circle.area (read on the CLASS) must return the lazy object itself. "
        "In __get__, return self when instance is None."
    )
    assert Circle.area.func.__name__ == "area", "Keep the decorated function as the attribute `func`."
    assert Circle.area.__doc__ == "Area of the circle (pi taken as 3).", (
        "Copy the function's docstring onto the descriptor (self.__doc__ = func.__doc__) so help() still works."
    )


def test_cache_key_comes_from_set_name():
    def _compute_total(self):
        return sum(self.items)

    class Basket:
        total = lazy(_compute_total)

        def __init__(self, items):
            self.items = items

    b = Basket([1, 2, 3])
    assert b.total == 6, "b.total must call _compute_total(b)."
    assert vars(b).get("total") == 6, (
        "The value must be cached under 'total', the name the descriptor was assigned to. "
        "Learn it in __set_name__; func.__name__ is '_compute_total' here."
    )
    assert "_compute_total" not in vars(b), "Do not cache under the function's own name."


def test_none_results_are_cached_too():
    calls = []

    class Thing:
        @lazy
        def nothing(self):
            calls.append(1)
            return None

    t = Thing()
    assert t.nothing is None and t.nothing is None, "The function returns None, so the attribute is None."
    assert len(calls) == 1, (
        "A None result must be cached too. Do not use 'if cached value is None: compute' as the test for 'not yet computed'."
    )


def test_an_exception_is_not_cached():
    class Report:
        def __init__(self):
            self.ready = False

        @lazy
        def text(self):
            if not self.ready:
                raise ValueError("data not loaded yet")
            return "done"

    r = Report()
    with pytest.raises(ValueError):
        r.text
    assert "text" not in vars(r), "If the function raises, nothing may be stored."
    r.ready = True
    assert r.text == "done", "After a failed read, the next read must try the computation again."
