from collections.abc import Callable
from typing import Any, ParamSpec, ParamSpecArgs, ParamSpecKwargs, get_args, get_origin, get_type_hints

import pytest

from solution import Emitter, EventBus


# ============================================================ Part 1: the generic structure
def test_emitter_is_generic_over_one_paramspec():
    params = getattr(Emitter, "__parameters__", ())
    assert len(params) == 1 and isinstance(params[0], ParamSpec), (
        "Emitter must be generic over ONE ParamSpec: class Emitter(Generic[P]) with P = ParamSpec('P'), "
        "or class Emitter[**P]."
    )


def test_subscripting_works_at_runtime():
    e = Emitter[[str, int]]()
    e.emit("a", 1)
    assert len(e) == 0, "Emitter[[str, int]]() creates an ordinary emitter; subscripting changes nothing at run time."
    assert Emitter[...]() is not None, "Emitter[...] (any parameters) must also work."


def test_on_once_off_hints_use_the_class_paramspec():
    (p,) = Emitter.__parameters__
    for name in ("on", "once"):
        h = get_type_hints(getattr(Emitter, name))
        assert get_origin(h["handler"]) is get_origin(Callable[[int], None]), f"{name}(handler: Callable[P, None])."
        assert get_args(h["handler"]) == (p, None), (
            f"{name}: handler must be Callable[P, None] with the SAME P as the class (and a None result)."
        )
        assert get_args(h["return"]) == (p, None), f"{name} returns the handler: -> Callable[P, None]."
    h = get_type_hints(Emitter.off)
    assert get_args(h["handler"]) == (p, None) and h["return"] is bool, "off(handler: Callable[P, None]) -> bool."


def test_emit_uses_p_args_and_p_kwargs():
    (p,) = Emitter.__parameters__
    h = get_type_hints(Emitter.emit)
    assert isinstance(h.get("args"), ParamSpecArgs) and h["args"].__origin__ is p, (
        "emit(self, *args: P.args, ...): the positional arguments are annotated with P.args."
    )
    assert isinstance(h.get("kwargs"), ParamSpecKwargs) and h["kwargs"].__origin__ is p, (
        "emit(self, ..., **kwargs: P.kwargs): the keyword arguments are annotated with P.kwargs."
    )
    assert h["return"] is type(None), "emit returns nothing: -> None."
    assert get_type_hints(Emitter.__len__)["return"] is int, "__len__ -> int."
    assert get_type_hints(Emitter.__init__)["return"] is type(None), "__init__ -> None."


def test_event_bus_hints():
    h = get_type_hints(EventBus.on)
    assert h["name"] is str and h["handler"] == Callable[..., None] and h["return"] == Callable[..., None], (
        "EventBus.on(name: str, handler: Callable[..., None]) -> Callable[..., None]."
    )
    h = get_type_hints(EventBus.emit)
    assert h["name"] is str and h["return"] is int, "EventBus.emit(name: str, *args, **kwargs) -> int."
    assert h["args"] is Any and h["kwargs"] is Any, "The bus does not track parameters: *args: Any, **kwargs: Any."
    assert get_type_hints(EventBus.names)["return"] == list[str], "names() -> list[str]."
    assert get_type_hints(EventBus.__init__)["return"] is type(None), "__init__ -> None."


# ============================================================ Part 2: Emitter behaviour
def test_emit_calls_handlers_in_order_with_arguments():
    log = []
    e = Emitter()
    e.on(lambda *a, **k: log.append(("first", a, k)))
    e.on(lambda *a, **k: log.append(("second", a, k)))
    e.emit(1, "x", flag=True)
    assert log == [("first", (1, "x"), {"flag": True}), ("second", (1, "x"), {"flag": True})], (
        "Every handler gets the same positional and keyword arguments, in registration order."
    )


def test_emit_with_no_handlers_is_fine():
    Emitter().emit(1, 2)


def test_on_returns_the_handler_and_works_as_decorator():
    e = Emitter()
    seen = []

    @e.on
    def handler(x):
        seen.append(x)

    assert callable(handler) and handler.__name__ == "handler", "on() must return the handler itself, so @e.on keeps the function."
    e.emit(5)
    assert seen == [5], "The decorated function is registered."
    handler(7)
    assert seen == [5, 7], "And it is still callable directly."


def test_same_handler_twice_is_called_twice():
    seen = []

    def h(x):
        seen.append(x)

    e = Emitter()
    e.on(h)
    e.on(h)
    e.emit(1)
    assert seen == [1, 1], "Registering the same function twice calls it twice."
    assert len(e) == 2, "len counts registrations, not distinct functions."


def test_off_removes_first_registration_only():
    seen = []

    def h(x):
        seen.append(x)

    e = Emitter()
    e.on(h)
    e.on(h)
    assert e.off(h) is True, "off returns True when it removed something."
    e.emit(1)
    assert seen == [1], "Only the FIRST registration is removed; the second still runs."
    assert e.off(h) is True and e.off(h) is False, "The second off removes the last one; a third finds nothing and returns False."
    assert len(e) == 0, "No registrations left."


def test_off_unknown_handler():
    assert Emitter().off(lambda: None) is False, "Removing a handler that was never registered returns False (no exception)."


def test_off_keeps_the_order_of_the_others():
    log = []
    a, b, c = (lambda: log.append("a")), (lambda: log.append("b")), (lambda: log.append("c"))
    e = Emitter()
    for f in (a, b, c):
        e.on(f)
    e.off(b)
    e.emit()
    assert log == ["a", "c"], "Removing one handler keeps the order of the others."


def test_once_runs_for_one_emit_only():
    seen = []
    e = Emitter()
    returned = e.once(lambda x: seen.append(x))
    assert callable(returned), "once returns the handler too."
    assert len(e) == 1, "A once-registration counts until it has run."
    e.emit(1)
    e.emit(2)
    assert seen == [1], "A once handler is called for the first emit only."
    assert len(e) == 0, "After running, the once registration is gone."


def test_once_and_on_mixed_order():
    log = []
    e = Emitter()
    e.on(lambda: log.append("on1"))
    e.once(lambda: log.append("once"))
    e.on(lambda: log.append("on2"))
    e.emit()
    e.emit()
    assert log == ["on1", "once", "on2", "on1", "on2"], "Order is registration order; the once handler runs only the first time."


def test_off_removes_a_once_registration():
    seen = []

    def h():
        seen.append(1)

    e = Emitter()
    e.once(h)
    assert e.off(h) is True, "off also removes a once registration."
    e.emit()
    assert seen == [], "A removed once handler never runs."


def test_once_is_removed_before_it_is_called():
    e = Emitter()
    lengths = []
    e.once(lambda: lengths.append(len(e)))
    e.emit()
    assert lengths == [0], "The once registration is removed BEFORE the call, so inside the handler len(e) is already 0."


def test_once_removed_even_if_it_raises():
    e = Emitter()

    def boom():
        raise RuntimeError("x")

    e.once(boom)
    with pytest.raises(RuntimeError):
        e.emit()
    assert len(e) == 0, "A once handler that raises is still removed (remove first, then call)."
    e.emit()


def test_snapshot_registering_during_emit():
    log = []
    e = Emitter()

    def late():
        log.append("late")

    def adder():
        log.append("adder")
        e.on(late)

    e.on(adder)
    e.emit()
    assert log == ["adder"], "A handler added during emit is not called in that emit (iterate over a copy)."
    e.emit()
    assert log == ["adder", "adder", "late"], "It is called from the next emit on."


def test_snapshot_removing_during_emit():
    log = []
    e = Emitter()

    def second():
        log.append("second")

    def first():
        log.append("first")
        e.off(second)

    e.on(first)
    e.on(second)
    e.emit()
    assert log == ["first", "second"], "Removing a handler during emit does not skip it in the current emit (snapshot)."
    e.emit()
    assert log == ["first", "second", "first"], "It is gone in the next emit."


def test_exception_propagates_and_stops_later_handlers():
    log = []
    e = Emitter()
    e.on(lambda: log.append("a"))

    def boom():
        raise ValueError("bad")

    e.on(boom)
    e.on(lambda: log.append("c"))
    with pytest.raises(ValueError, match="bad"):
        e.emit()
    assert log == ["a"], "An exception from a handler propagates; later handlers are not called."


def test_bound_methods_can_be_removed():
    class Listener:
        def __init__(self):
            self.got = []

        def handle(self, x):
            self.got.append(x)

    lst = Listener()
    e = Emitter()
    e.on(lst.handle)
    e.emit(1)
    assert e.off(lst.handle) is True, "lst.handle creates a new bound-method object each time; compare with ==, not 'is'."
    e.emit(2)
    assert lst.got == [1], "After off, the bound method no longer runs."


def test_emitters_are_independent():
    a, b = Emitter(), Emitter()
    a.on(lambda: None)
    assert len(a) == 1 and len(b) == 0, "Each Emitter has its own handler list (create it in __init__, not as a class attribute)."


# ============================================================ Part 3: EventBus
def test_bus_basic():
    bus = EventBus()
    seen = []
    assert bus.emit("nothing") == 0, "Unknown event: returns 0, no error."
    h = bus.on("greet", lambda name, punct="!": seen.append(name + punct))
    assert callable(h), "on returns the handler."
    assert bus.emit("greet", "Ada") == 1, "emit returns the number of registered handlers."
    assert bus.emit("greet", "Bo", punct="?") == 1, "Keyword arguments are passed on."
    assert seen == ["Ada!", "Bo?"], "The handler received the arguments."


def test_bus_counts_and_names():
    bus = EventBus()
    log = []
    bus.on("b", lambda: log.append("b1"))
    bus.on("a", lambda: log.append("a1"))
    bus.on("b", lambda: log.append("b2"))
    assert bus.names() == ["a", "b"], "names() is sorted."
    assert bus.emit("b") == 2, "Two handlers on 'b'."
    assert log == ["b1", "b2"], "Only the handlers of that event run, in order."
    assert bus.emit("a") == 1 and log[-1] == "a1", "Events are independent."


def test_bus_unknown_event_does_not_create_it():
    bus = EventBus()
    bus.emit("ghost")
    assert bus.names() == [], "Emitting an unknown event must not register it (names() only lists events with handlers)."


def test_bus_uses_emitter():
    import solution

    src = open(solution.__file__, encoding="utf-8").read()
    assert "Emitter" in src.split("class EventBus")[1], "EventBus should be built on Emitter (one emitter per event name)."


def test_once_and_on_of_the_same_function_are_separate_registrations():
    calls = []

    def h():
        calls.append(1)

    e = Emitter()
    e.on(h)
    e.once(h)
    e.emit()
    e.emit()
    e.emit()
    assert len(calls) == 2 + 1 + 1, (
        "h is registered twice (once with on, once with once). First emit: 2 calls. "
        "The once registration is removed (not the on one), so the next emits call h once each."
    )
    assert len(e) == 1, "One permanent registration is left."


def test_bus_emit_returns_the_count_at_the_moment_of_the_call():
    bus = EventBus()

    def adder():
        bus.on("x", lambda: None)

    bus.on("x", adder)
    assert bus.emit("x") == 1, "Count the handlers registered when emit is called (1), not the ones added during the emit."
    assert bus.emit("x") == 2, "Now there are two."
