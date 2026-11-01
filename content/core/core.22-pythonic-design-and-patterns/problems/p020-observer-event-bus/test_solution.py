from solution import EventBus


def test_handlers_run_in_subscription_order_with_data():
    bus, log = EventBus(), []
    bus.subscribe("saved", lambda **d: log.append(("a", d)))
    bus.subscribe("saved", lambda **d: log.append(("b", d)))
    bus.publish("saved", id=7, name="x")
    assert log == [("a", {"id": 7, "name": "x"}), ("b", {"id": 7, "name": "x"})], (
        f"Got {log}. Handlers run in the order they subscribed, each called as fn(**data)."
    )


def test_events_are_separate():
    bus, log = EventBus(), []
    bus.subscribe("a", lambda **d: log.append("a"))
    bus.subscribe("b", lambda **d: log.append("b"))
    bus.publish("b")
    assert log == ["b"], f"Publishing 'b' must only run the 'b' handlers, got {log}."


def test_publish_with_no_subscribers_returns_empty_list():
    assert EventBus().publish("nobody-listens", x=1) == [], (
        "Publishing an event nobody subscribed to is fine and returns an empty list of errors."
    )
    bus = EventBus()
    bus.subscribe("e", lambda **d: None)
    assert bus.publish("e") == [], "No handler failed, so publish returns []."


def test_failing_handler_does_not_stop_the_others():
    bus, log = EventBus(), []

    def boom(**d):
        raise ValueError("bad handler")

    bus.subscribe("e", lambda **d: log.append(1))
    bus.subscribe("e", boom)
    bus.subscribe("e", lambda **d: log.append(3))
    errors = bus.publish("e")
    assert log == [1, 3], (
        f"Handlers that ran: {log}. One failing handler must not stop the later ones: wrap each call in try/except."
    )
    assert len(errors) == 1 and isinstance(errors[0], ValueError) and str(errors[0]) == "bad handler", (
        f"publish must return the list of exceptions the handlers raised, got {errors}."
    )


def test_errors_keep_order():
    bus = EventBus()

    def first(**d):
        raise KeyError("one")

    def second(**d):
        raise RuntimeError("two")

    bus.subscribe("e", first)
    bus.subscribe("e", lambda **d: None)
    bus.subscribe("e", second)
    errors = bus.publish("e")
    assert [type(e) for e in errors] == [KeyError, RuntimeError], f"Errors must be in handler order, got {errors}."


def test_subscribe_returns_an_unsubscribe_function():
    bus, log = EventBus(), []
    handler = lambda **d: log.append("h")
    off = bus.subscribe("e", handler)
    assert callable(off), "subscribe must return a function that removes this subscription."
    bus.publish("e")
    off()
    bus.publish("e")
    assert log == ["h"], f"After unsubscribe the handler must not run again, got {log}."


def test_unsubscribe_twice_is_harmless():
    bus = EventBus()
    off = bus.subscribe("e", lambda **d: None)
    off()
    off()
    assert bus.publish("e") == [], "Calling the unsubscribe function twice must not raise."


def test_same_function_subscribed_twice_is_two_subscriptions():
    bus, log = EventBus(), []
    handler = lambda **d: log.append("h")
    off1 = bus.subscribe("e", handler)
    bus.subscribe("e", handler)
    bus.publish("e")
    assert log == ["h", "h"], "The same function subscribed twice runs twice."
    off1()
    log.clear()
    bus.publish("e")
    assert log == ["h"], (
        "Each unsubscribe removes only its own subscription; the second subscription of the same function stays."
    )


def test_unsubscribe_inside_a_handler_is_safe():
    bus, log = EventBus(), []
    offs = {}

    def once(**d):
        log.append("once")
        offs["once"]()

    offs["once"] = bus.subscribe("e", once)
    bus.subscribe("e", lambda **d: log.append("after"))
    errors = bus.publish("e")
    assert log == ["once", "after"], (
        f"Got {log}. Removing a handler while publish loops over the list skips the next handler. "
        "Loop over a copy (snapshot) of the handler list."
    )
    assert errors == [], f"Unexpected errors {errors}"
    log.clear()
    bus.publish("e")
    assert log == ["after"], f"The 'once' handler removed itself, so the second publish runs only 'after': {log}."


def test_subscribe_inside_a_handler_takes_effect_next_time():
    bus, log = EventBus(), []

    def adder(**d):
        log.append("adder")
        bus.subscribe("e", lambda **d: log.append("late"))

    off = bus.subscribe("e", adder)
    bus.publish("e")
    assert log == ["adder"], (
        f"Got {log}. A handler subscribed during a publish must not run in that same publish (loop over a snapshot)."
    )
    off()
    log.clear()
    bus.publish("e")
    assert log == ["late"], f"The new handler runs from the next publish on, got {log}."
