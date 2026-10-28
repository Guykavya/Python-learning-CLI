## Approach

A **pure function** depends only on its arguments and changes nothing outside itself. `step`
takes the old state and one event and returns the new state. Because the history is a tuple
and we build a new dict, nobody holding the old state sees it change.

Once you have a pure `step`, the rest is folding:

- `reduce(step, events, start)` keeps only the final state.
- `accumulate(events, step, initial=START)` keeps every state along the way. Its first item is
  `START` itself, so we skip it.

Notice `start` is never copied: we do not need to copy it, because `step` never changes the
state it is given.

## Code

```python
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
```

`START` is shared by every call, and that is safe only because nothing ever changes a state.
If `step` mutated its input, the shared `START` would be the first thing to break.

## Complexity

Each step copies the history tuple, so `run_events` is O(n²) over n events in the worst case.
For a wallet that is fine; for millions of events you would keep the history in a list owned by
one function, or store only the balance.

## Another way

`balances` could call `run_events` on each prefix: `[run_events(events[:i])["balance"] for i in
range(1, n + 1)]`. That is O(n²) folds and recomputes everything; `accumulate` does one pass.

The pay-off of the pure version: "what if" questions are free. `run_events(events + [("withdraw",
500)])` tells you what would happen without touching the real state.
