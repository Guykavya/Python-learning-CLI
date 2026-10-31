import copy

import pytest

from solution import balances, run_events, step

EVENTS = [("deposit", 50), ("withdraw", 20), ("withdraw", 100), ("deposit", 5)]


def test_step_deposit_and_withdraw():
    s = {"balance": 10, "history": ("+10",)}
    assert step(s, ("withdraw", 4)) == {"balance": 6, "history": ("+10", "-4")}, "A withdraw that fits subtracts and adds '-n'."
    assert step(s, ("deposit", 3)) == {"balance": 13, "history": ("+10", "+3")}, "A deposit adds and records '+n'."
    assert step(s, ("withdraw", 11)) == {"balance": 10, "history": ("+10", "rejected 11")}, (
        "Withdrawing more than the balance is rejected: balance unchanged, history gets 'rejected n'."
    )
    assert step(s, ("withdraw", 10)) == {"balance": 0, "history": ("+10", "-10")}, "Withdrawing exactly the balance is allowed."


def test_step_does_not_mutate():
    s = {"balance": 10, "history": ("+10",)}
    before = copy.deepcopy(s)
    new = step(s, ("deposit", 5))
    assert s == before, "step changed its input state. Build a new dict instead."
    assert new is not s, "Return a NEW dict."
    assert isinstance(new["history"], tuple), "Keep history a tuple: make a new one with state['history'] + (note,)."


def test_step_errors():
    s = {"balance": 0, "history": ()}
    with pytest.raises(ValueError):
        step(s, ("steal", 5))
    with pytest.raises(ValueError):
        step(s, ("deposit", -5))
    with pytest.raises(ValueError):
        step(s, ("deposit", 0))
    with pytest.raises(ValueError):
        step(s, ("deposit", 2.5))


def test_run_events():
    assert run_events(EVENTS) == {"balance": 35, "history": ("+50", "-20", "rejected 100", "+5")}, (
        "Fold every event with reduce(step, events, start)."
    )


def test_run_events_is_repeatable():
    first = run_events(EVENTS)
    second = run_events(EVENTS)
    assert first == second, "Running the same events twice must give the same result: no hidden global state."
    assert run_events([]) == {"balance": 0, "history": ()}, "No events: the start state."


def test_run_events_custom_start_not_mutated():
    start = {"balance": 100, "history": ("opening",)}
    before = copy.deepcopy(start)
    final = run_events([("withdraw", 30)], start)
    assert final == {"balance": 70, "history": ("opening", "-30")}, "Begin from the given start state."
    assert start == before, "run_events must not change the start state it was given."


def test_balances():
    assert balances(EVENTS) == [50, 30, 30, 35], "One balance after each event, not including the start."
    assert balances([]) == [], "No events, no balances."
    assert balances([("withdraw", 1)]) == [0], "A rejected first withdraw leaves 0."
