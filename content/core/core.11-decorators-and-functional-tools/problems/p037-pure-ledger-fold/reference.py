from functools import reduce
from itertools import accumulate

START = {"balance": 0, "history": ()}


def step(state, event):
    kind, amount = event
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError(f"amount must be a positive int, got {amount!r}")
    balance = state["balance"]
    if kind == "deposit":
        balance += amount
        note = f"+{amount}"
    elif kind == "withdraw":
        if amount > balance:
            note = f"rejected {amount}"
        else:
            balance -= amount
            note = f"-{amount}"
    else:
        raise ValueError(f"unknown event kind {kind!r}")
    return {"balance": balance, "history": state["history"] + (note,)}


def run_events(events, start=None):
    if start is None:
        start = START
    return reduce(step, events, start)


def balances(events):
    states = accumulate(events, step, initial=START)
    next(states)
    return [state["balance"] for state in states]
