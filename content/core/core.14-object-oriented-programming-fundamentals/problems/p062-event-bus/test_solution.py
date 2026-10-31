import pytest

from solution import Event, EventBus


class Recorder:
    def __init__(self, log, tag):
        self.log = log
        self.tag = tag

    def handle(self, event):
        self.log.append((self.tag, event.name, event.payload))


class Broken:
    def __init__(self, message="boom"):
        self.message = message

    def handle(self, event):
        raise RuntimeError(self.message)


class BadValue:
    def handle(self, event):
        raise ValueError("bad payload")


def test_event_attributes():
    e = Event("x", 5)
    assert (e.name, e.payload) == ("x", 5), "Event stores name and payload."
    assert Event("y").payload is None, "payload defaults to None."


def test_publish_in_order_and_count():
    log = []
    bus = EventBus()
    bus.subscribe("paid", Recorder(log, "a"))
    bus.subscribe("paid", Recorder(log, "b"))
    assert bus.publish("paid", 10) == 2, "publish returns how many handle() calls it made."
    assert log == [("a", "paid", 10), ("b", "paid", 10)], "Call the listeners in the order they subscribed."


def test_one_event_object_for_everyone():
    seen = []

    class Keep:
        def handle(self, event):
            seen.append(event)

    bus = EventBus()
    bus.subscribe("e", Keep())
    bus.subscribe("e", Keep())
    bus.publish("e")
    assert len(seen) == 2 and seen[0] is seen[1], "Build ONE Event per publish and give the same object to every listener."
    assert isinstance(seen[0], Event), "Listeners receive an Event object."


def test_no_listeners():
    assert EventBus().publish("nobody") == 0, "No listeners: nothing happens, return 0."


def test_duck_typing_any_class_works():
    class Anything:
        def __init__(self):
            self.count = 0

        def handle(self, event):
            self.count += 1

    bus = EventBus()
    a = Anything()
    bus.subscribe("e", a)
    bus.publish("e")
    assert a.count == 1, "Any object with a callable handle works; no base class is needed."


@pytest.mark.parametrize("bad", [object(), 42, "text"])
def test_listener_without_handle(bad):
    with pytest.raises(TypeError, match=r"listener needs a handle\(event\) method"):
        EventBus().subscribe("e", bad)


def test_handle_must_be_callable():
    class NotCallable:
        handle = "not a method"

    try:
        EventBus().subscribe("e", NotCallable())
    except TypeError as e:
        assert str(e) == "listener needs a handle(event) method", "Use the exact message from problem.md."
    else:
        pytest.fail("handle exists but is a string, not a method. Check callable(getattr(listener, 'handle', None)), not only hasattr.")


def test_same_listener_twice_is_ignored():
    log = []
    bus = EventBus()
    r = Recorder(log, "a")
    bus.subscribe("e", r)
    bus.subscribe("e", r)
    assert bus.publish("e") == 1 and len(log) == 1, "Subscribing the same object twice to the same event does nothing."


def test_two_equal_but_different_listeners_both_count():
    log = []
    bus = EventBus()
    bus.subscribe("e", Recorder(log, "same"))
    bus.subscribe("e", Recorder(log, "same"))
    assert bus.publish("e") == 2, "Two different objects are two listeners, even if they look alike. Compare with `is`."


def test_wildcard():
    log = []
    bus = EventBus()
    bus.subscribe("*", Recorder(log, "all"))
    bus.subscribe("a", Recorder(log, "only a"))
    bus.publish("a", 1)
    bus.publish("b", 2)
    assert log == [("only a", "a", 1), ("all", "a", 1), ("all", "b", 2)], (
        f"Got {log}. Specific listeners first, then the '*' listeners, which get every event."
    )


def test_listener_on_specific_and_wildcard_gets_it_twice():
    log = []
    bus = EventBus()
    r = Recorder(log, "r")
    bus.subscribe("a", r)
    bus.subscribe("*", r)
    assert bus.publish("a") == 2 and len(log) == 2, "Subscribed to 'a' and to '*': two calls."


def test_cannot_publish_wildcard():
    with pytest.raises(ValueError, match="cannot publish '\\*'"):
        EventBus().publish("*")


def test_listeners_returns_copy():
    log = []
    bus = EventBus()
    r = Recorder(log, "r")
    bus.subscribe("e", r)
    bus.subscribe("*", Recorder(log, "w"))
    got = bus.listeners("e")
    assert got == [r] and got[0] is r, "listeners('e') lists the exact listeners of 'e', without the '*' ones."
    got.clear()
    assert bus.listeners("e") == [r], "Return a NEW list; clearing it must not unsubscribe anyone."
    assert bus.listeners("unknown") == [], "Unknown names give []."


def test_unsubscribe():
    log = []
    bus = EventBus()
    a, b = Recorder(log, "a"), Recorder(log, "b")
    bus.subscribe("e", a)
    bus.subscribe("e", b)
    bus.unsubscribe("e", a)
    bus.publish("e")
    assert log == [("b", "e", None)], "After unsubscribe, a is not called any more."
    with pytest.raises(ValueError, match="listener is not subscribed to 'e'"):
        bus.unsubscribe("e", a)
    with pytest.raises(ValueError, match="listener is not subscribed to 'other'"):
        bus.unsubscribe("other", b)


def test_failures_are_collected_after_everyone_ran():
    log = []
    bus = EventBus()
    bus.subscribe("e", Broken("first"))
    bus.subscribe("e", Recorder(log, "ok"))
    bus.subscribe("e", BadValue())
    with pytest.raises(ExceptionGroup) as info:
        bus.publish("e", 7)
    assert log == [("ok", "e", 7)], "A failing listener must not stop the others. Catch, remember, continue."
    eg = info.value
    assert eg.message == "2 listener(s) failed for 'e'", f"Group message: f\"{{n}} listener(s) failed for {{event_name!r}}\". Got {eg.message!r}."
    assert [type(e).__name__ for e in eg.exceptions] == ["RuntimeError", "ValueError"], "Keep the errors in the order they happened."
    assert str(eg.exceptions[0]) == "first", "Put the original exception objects into the group."


def test_notes_name_the_listener():
    bus = EventBus()
    bus.subscribe("e", Broken())
    bus.subscribe("*", BadValue())
    with pytest.raises(ExceptionGroup) as info:
        bus.publish("e")
    notes = [getattr(e, "__notes__", []) for e in info.value.exceptions]
    assert notes == [["listener: Broken"], ["listener: BadValue"]], (
        f"Got {notes}. Call exc.add_note(f'listener: {{type(listener).__name__}}') before collecting it."
    )


def test_base_exceptions_are_not_swallowed():
    class Quit:
        def handle(self, event):
            raise KeyboardInterrupt

    bus = EventBus()
    bus.subscribe("e", Quit())
    try:
        bus.publish("e")
    except KeyboardInterrupt:
        return
    except Exception as e:
        pytest.fail(
            f"publish raised {type(e).__name__}: {e}. Catch only Exception in publish; a KeyboardInterrupt "
            "must pass straight through (it cannot even go into an ExceptionGroup)."
        )
    pytest.fail("A KeyboardInterrupt from a listener must not be swallowed. Catch Exception, not BaseException.")


def test_unsubscribe_during_publish():
    log = []
    bus = EventBus()

    class Once:
        def handle(self, event):
            log.append("once")
            bus.unsubscribe("e", self)

    bus.subscribe("e", Once())
    bus.subscribe("e", Recorder(log, "after"))
    bus.publish("e")
    assert log == ["once", ("after", "e", None)], (
        "Unsubscribing during publish must not make the bus skip the next listener. Loop over a copy of the list."
    )
    bus.publish("e")
    assert log[-1] == ("after", "e", None) and log.count("once") == 1, "The change counts from the next publish."


def test_subscribe_during_publish():
    log = []
    bus = EventBus()

    class Adder:
        def handle(self, event):
            log.append("adder")
            bus.subscribe("e", Recorder(log, "new"))

    bus.subscribe("e", Adder())
    assert bus.publish("e") == 1, "A listener added during publish is not called in that same publish."
    assert log == ["adder"], "The new listener starts with the next publish."
