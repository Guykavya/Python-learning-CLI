import pytest

from solution import (Cancelled, Delivered, InvalidTransition, Order, OrderState, Paid, Pending,
                      Shipped)


def test_invalid_transition():
    e = InvalidTransition("pending", "ship")
    assert (e.state, e.action) == ("pending", "ship"), "InvalidTransition stores state and action."
    assert str(e) == "cannot ship an order that is pending", f"Message format from problem.md. Got {str(e)!r}."


def test_state_classes():
    expected = {Pending: "pending", Paid: "paid", Shipped: "shipped", Delivered: "delivered", Cancelled: "cancelled"}
    for cls, name in expected.items():
        assert issubclass(cls, OrderState), f"{cls.__name__} must inherit from OrderState."
        assert cls.name == name, f"{cls.__name__}.name should be {name!r}."


def test_base_state_refuses_everything():
    class Nothing(OrderState):
        name = "frozen"

    order = Order("X", initial=Nothing())
    for action in ("pay", "ship", "deliver", "cancel"):
        with pytest.raises(InvalidTransition, match=f"cannot {action} an order that is frozen"):
            getattr(order, action)()


def test_state_methods_return_next_state():
    order = Order("X")
    nxt = Pending().pay(order)
    assert isinstance(nxt, Paid), "Pending().pay(order) returns a Paid() object."
    assert isinstance(Paid().ship(order), Shipped), "Paid().ship(order) returns Shipped()."
    assert isinstance(Shipped().deliver(order), Delivered), "Shipped().deliver(order) returns Delivered()."


def test_happy_path():
    o = Order("A1")
    assert (o.order_id, o.state, o.refunded) == ("A1", "pending", False), "A new order is pending, not refunded."
    o.pay()
    o.ship()
    o.deliver()
    assert o.state == "delivered", "pay, ship, deliver -> delivered."
    assert o.history == ["pending", "paid", "shipped", "delivered"], f"history lists every state. Got {o.history}."
    assert isinstance(o.state_object, Delivered), "state_object is the current state object."


def test_cancel_pending_no_refund():
    o = Order("A1")
    o.cancel()
    assert (o.state, o.refunded) == ("cancelled", False), "Cancelling a pending order: nothing was paid, no refund."


def test_cancel_paid_refunds():
    o = Order("A1")
    o.pay()
    o.cancel()
    assert (o.state, o.refunded) == ("cancelled", True), "Cancelling a paid order sets refunded = True (done by Paid.cancel)."
    assert o.history == ["pending", "paid", "cancelled"], "history after pay, cancel."


@pytest.mark.parametrize("steps, bad, state", [
    ([], "ship", "pending"),
    ([], "deliver", "pending"),
    (["pay"], "pay", "paid"),
    (["pay", "ship"], "cancel", "shipped"),
    (["pay", "ship", "deliver"], "cancel", "delivered"),
    (["cancel"], "pay", "cancelled"),
])
def test_invalid_actions_change_nothing(steps, bad, state):
    o = Order("A1")
    for step in steps:
        getattr(o, step)()
    before = list(o.history)
    with pytest.raises(InvalidTransition) as info:
        getattr(o, bad)()
    assert (info.value.state, info.value.action) == (state, bad), f"Expected InvalidTransition({state!r}, {bad!r})."
    assert o.state == state and o.history == before, "A failed action must not change the state or the history."


def test_properties_are_read_only():
    o = Order("A1")
    with pytest.raises(AttributeError):
        o.state = "delivered"
    with pytest.raises(AttributeError):
        o.state_object = Delivered()


def test_can():
    o = Order("A1")
    assert [o.can(a) for a in ("pay", "ship", "deliver", "cancel")] == [True, False, False, True], "A pending order can pay or cancel."
    assert o.state == "pending" and o.history == ["pending"], "can() must not change the order."
    o.pay()
    assert o.can("ship") and o.can("cancel") and not o.can("pay"), "A paid order can ship or cancel."


def test_can_does_not_refund():
    o = Order("A1")
    o.pay()
    assert o.can("cancel") is True, "A paid order can be cancelled."
    assert o.refunded is False and o.state == "paid", (
        "can('cancel') runs Paid.cancel as a trial, which sets order.refunded. Put the old value back."
    )


def test_can_unknown_action():
    with pytest.raises(ValueError, match="unknown action 'fly'"):
        Order("A1").can("fly")


def test_new_state_plugs_in():
    class Review(OrderState):
        name = "in review"

        def pay(self, order):
            return Paid()

    r = Order("B2", initial=Review())
    assert r.state == "in review" and r.history == ["in review"], "Order starts in the state object it is given."
    assert r.can("cancel") is False and r.can("pay") is True, "can() must ask the state object, not a table in Order."
    with pytest.raises(InvalidTransition, match="cannot cancel an order that is in review"):
        r.cancel()
    r.pay()
    assert r.history == ["in review", "paid"], "Order delegates: whatever state the state object returns becomes current."


def test_custom_state_can_change_the_order():
    class Express(OrderState):
        name = "express"

        def ship(self, order):
            order.priority = True
            return Shipped()

    o = Order("C3", initial=Express())
    o.ship()
    assert o.state == "shipped" and o.priority is True, "Pass the order itself to the state method: self._state.ship(self)."


def test_each_order_has_its_own_history():
    a, b = Order("A"), Order("B")
    a.pay()
    assert b.history == ["pending"], "history must be a new list for each order (set it in __init__)."
