from solution import make_event_bus


def greet(name):
    return "hello " + name


def shout(name, punct="!"):
    return name.upper() + punct


def test_example():
    bus = make_event_bus()
    bus["on"]("join", greet)
    bus["on"]("join", shout)
    assert bus["emit"]("join", "asha") == ["hello asha", "ASHA!"], "Call every handler in registration order."
    assert bus["off"]("join", greet) is True
    assert bus["emit"]("join", "ravi", punct="?") == ["RAVI?"], "Forward keyword arguments: h(*args, **kwargs)."
    assert bus["off"]("join", greet) is False
    assert bus["emit"]("leave") == [], "No handlers: return []."


def test_registered_twice_called_twice():
    bus = make_event_bus()
    bus["on"]("tick", greet)
    bus["on"]("tick", greet)
    assert bus["emit"]("tick", "x") == ["hello x", "hello x"]
    assert bus["off"]("tick", greet) is True
    assert bus["emit"]("tick", "x") == ["hello x"], "off removes only the FIRST registration."


def test_independent_buses():
    a = make_event_bus()
    b = make_event_bus()
    a["on"]("e", greet)
    assert b["emit"]("e", "z") == [], "Each bus needs its own registry."


def test_events_are_separate():
    bus = make_event_bus()
    bus["on"]("a", lambda: 1)
    bus["on"]("b", lambda: 2)
    assert bus["emit"]("a") == [1] and bus["emit"]("b") == [2]


def test_register_during_emit():
    bus = make_event_bus()
    def adder():
        bus["on"]("e", lambda: "late")
        return "adder"
    bus["on"]("e", adder)
    assert bus["emit"]("e") == ["adder"], (
        "A handler registered during emit must not run in that same emit. Loop over a copy of the list.")
    assert bus["emit"]("e") == ["adder", "late"]


def test_remove_during_emit():
    bus = make_event_bus()
    def second():
        return 2
    def first():
        bus["off"]("e", second)
        return 1
    bus["on"]("e", first)
    bus["on"]("e", second)
    assert bus["emit"]("e") == [1, 2], "Handlers removed during an emit still run in that emit (loop over a copy)."
    assert bus["emit"]("e") == [1]


def test_off_unknown_event():
    assert make_event_bus()["off"]("nothing", greet) is False
