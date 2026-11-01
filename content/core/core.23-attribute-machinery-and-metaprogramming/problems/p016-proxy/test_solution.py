import copy

import pytest

from solution import ReadOnlyProxy


class Order:
    def __init__(self, items):
        self.items = items
        self.paid = False

    def total(self):
        return sum(self.items)

    def __repr__(self):
        return f"Order({self.items!r})"


def test_reads_are_delegated():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    assert view.items == [10, 5], "proxy.items must return target.items (use __getattr__ to forward)."
    assert view.paid is False


def test_methods_work_and_run_on_the_target():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    assert view.total() == 15, "Methods must be forwarded too: view.total() is order.total()."
    assert view.total.__self__ is order, (
        "The method must be bound to the real target (getattr(target, name)), so it sees the target's data."
    )


def test_live_view_not_a_copy():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    order.paid = True
    order.items.append(1)
    assert view.paid is True, "The proxy must read the target each time, not keep a snapshot from __init__."
    assert view.total() == 16


def test_writes_are_refused_and_target_unchanged():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    with pytest.raises(AttributeError) as err:
        view.paid = True
    assert "paid" in str(err.value), "The error message must name the attribute that was being set."
    assert order.paid is False, "A refused write must not reach the target."
    with pytest.raises(AttributeError):
        view.brand_new = 1
    assert not hasattr(order, "brand_new"), "New attributes must not be created on the target either."


def test_deletes_are_refused():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    with pytest.raises(AttributeError) as err:
        del view.items
    assert "items" in str(err.value), "The error message must name the attribute that was being deleted."
    assert order.items == [10, 5], "A refused delete must not reach the target."


def test_proxy_own_internals_cannot_be_replaced():
    view = ReadOnlyProxy(Order([1]))
    with pytest.raises(AttributeError):
        view._target = Order([2])
    assert view.items == [1], "Even the proxy's own attributes must not be assignable from outside."


def test_reads_are_counted_per_name():
    view = ReadOnlyProxy(Order([10, 5]))
    assert view.access_count("items") == 0, "Nothing has been read yet."
    view.items
    view.items
    view.total()
    assert view.access_count("items") == 2, "Count each successful read of a name."
    assert view.access_count("total") == 1, "Reading a method (view.total) counts as one read of 'total'."
    assert view.access_count("paid") == 0, "Names never read have count 0."


def test_counts_are_per_proxy():
    order = Order([1])
    first, second = ReadOnlyProxy(order), ReadOnlyProxy(order)
    first.items
    assert second.access_count("items") == 0, (
        "Each proxy must have its own counts. A dict created at class level would be shared by all proxies."
    )


def test_missing_attribute_raises_and_is_not_counted():
    view = ReadOnlyProxy(Order([1]))
    with pytest.raises(AttributeError):
        view.colour
    assert not hasattr(view, "colour"), "hasattr must return False for a name the target does not have."
    assert view.access_count("colour") == 0, "Failed reads are not counted."


def test_repr():
    view = ReadOnlyProxy(Order([1, 2]))
    assert repr(view) == "ReadOnlyProxy(Order([1, 2]))", (
        f"repr(proxy) must be 'ReadOnlyProxy(<repr of target>)', got {repr(view)!r}. "
        "repr() looks up __repr__ on the type, so define it in the class; __getattr__ is never asked."
    )


def test_copy_does_not_recurse():
    order = Order([10, 5])
    view = ReadOnlyProxy(order)
    try:
        clone = copy.copy(view)
    except RecursionError:
        pytest.fail(
            "copy.copy(proxy) hit RecursionError. copy makes the new object WITHOUT __init__, so _target "
            "is missing and self._target inside __getattr__ calls __getattr__ again, forever. "
            "Use object.__getattribute__(self, '_target') (or vars(self)) inside __getattr__."
        )
    assert clone.total() == 15, "The copy must be a working proxy for the same target."


def test_half_built_proxy_gives_attribute_error():
    blank = ReadOnlyProxy.__new__(ReadOnlyProxy)
    try:
        result = hasattr(blank, "anything")
    except RecursionError:
        pytest.fail(
            "A proxy whose __init__ never ran must answer hasattr(...) with False, not RecursionError. "
            "Inside __getattr__, read your own attributes without going through __getattr__ again."
        )
    assert result is False
