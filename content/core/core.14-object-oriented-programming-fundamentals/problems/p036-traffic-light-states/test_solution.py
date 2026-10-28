import pytest

from solution import TrafficLight

FAST = {"red": 3, "green": 2, "yellow": 1}


def test_class_attributes():
    assert TrafficLight.NEXT == {"red": "green", "green": "yellow", "yellow": "red"}, "NEXT maps each colour to the next one."
    assert TrafficLight.DEFAULT_DURATIONS == {"red": 30, "green": 25, "yellow": 5}, "Keep the default durations as given."


def test_defaults():
    t = TrafficLight()
    assert (t.state, t.time_left, t.history) == ("red", 30, ["red"]), (
        "Start red with 30 seconds left, and the history starts with the start colour."
    )
    g = TrafficLight("green")
    assert (g.state, g.time_left) == ("green", 25), "time_left starts at the duration of the start colour."


def test_bad_arguments():
    with pytest.raises(ValueError):
        TrafficLight("blue")
    for bad in ({"red": 3, "green": 2}, {"red": 3, "green": 2, "yellow": 0},
                {"red": 3, "green": 2, "yellow": 1, "blue": 4}, {"red": 3, "green": 2.5, "yellow": 1}):
        with pytest.raises(ValueError):
            TrafficLight(durations=bad)


def test_durations_are_copied_and_defaults_untouched():
    d = dict(FAST)
    t = TrafficLight(durations=d)
    d["green"] = 99
    t.advance()
    assert t.time_left == 2, "Keep your own copy of durations; later changes to the caller's dict must not matter."
    TrafficLight().advance()
    assert TrafficLight.DEFAULT_DURATIONS["red"] == 30, "Never change the class attribute DEFAULT_DURATIONS."


def test_advance_cycle():
    t = TrafficLight(durations=FAST)
    assert [t.advance() for _ in range(4)] == ["green", "yellow", "red", "green"], "The cycle is red -> green -> yellow -> red."
    assert t.time_left == 2, "advance() sets time_left to the full duration of the new colour (green: 2)."
    assert t.history == ["red", "green", "yellow", "red", "green"], "Every colour shown is in the history."


def test_read_only_properties():
    t = TrafficLight()
    for name, value in (("state", "green"), ("time_left", 5), ("history", [])):
        with pytest.raises(AttributeError):
            setattr(t, name, value)


def test_history_is_a_copy():
    t = TrafficLight()
    h = t.history
    h.append("purple")
    assert t.history == ["red"], "history must return a new list each time."


def test_tick_example_step_by_step():
    t = TrafficLight(durations=FAST)
    assert t.tick(2) == [], "red has 3 s; after 2 s nothing changes."
    assert t.time_left == 1, "3 - 2 = 1 second left."
    assert t.tick(1) == ["green"], "1 s left and 1 s passes: time_left reaches 0, so it changes to green (>=, not >)."
    assert (t.state, t.time_left) == ("green", 2), "Green starts with its full 2 s."
    assert t.tick(5) == ["yellow", "red"], "5 s: 2 to finish green, 1 to finish yellow, then 2 of red's 3."
    assert (t.state, t.time_left) == ("red", 1), "3 - 2 = 1 second of red left."
    assert t.history == ["red", "green", "yellow", "red"], "History after the ticks."


def test_tick_zero_and_long():
    t = TrafficLight(durations=FAST)
    t.tick(2)
    assert t.tick(0) == [] and t.time_left == 1, "tick(0) changes nothing."
    assert t.tick(7) == ["green", "yellow", "red", "green"], (
        "7 s from red with 1 left: 1 -> green, 2 -> yellow, 1 -> red, 3 -> green (exactly 0 left means change)."
    )
    assert (t.state, t.time_left) == ("green", 2), "All 7 seconds are used up; green has its full 2 s."


def test_tick_full_cycles():
    t = TrafficLight(durations=FAST)
    assert t.tick(12) == ["green", "yellow", "red", "green", "yellow", "red"], "One cycle is 3 + 2 + 1 = 6 s; 12 s is two full cycles."
    assert (t.state, t.time_left) == ("red", 3), "After whole cycles the light is back at the start, with a full timer."


def test_tick_bad_seconds():
    t = TrafficLight()
    for bad in (-1, 1.5, "3"):
        with pytest.raises(ValueError):
            t.tick(bad)


def test_emergency_from_green():
    t = TrafficLight(durations=FAST)
    t.advance()
    t.tick(1)
    t.emergency()
    assert (t.state, t.time_left) == ("red", 3), "emergency() switches to red with red's full duration."
    assert t.history == ["red", "green", "red"], "Switching to red is added to the history."
    assert t.tick(3) == ["green"], "After an emergency the normal cycle goes on from red."


def test_emergency_when_already_red():
    t = TrafficLight(durations=FAST)
    t.tick(2)
    t.emergency()
    assert (t.state, t.time_left) == ("red", 3), "Already red: only the timer restarts."
    assert t.history == ["red"], "Already red: do not add another 'red' to the history."


def test_repr():
    t = TrafficLight(durations=FAST)
    t.advance()
    assert repr(t) == "TrafficLight(state='green', time_left=2)", (
        "__repr__ must return exactly TrafficLight(state='green', time_left=2); use {self._state!r} for the quotes."
    )
