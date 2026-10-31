# Refactor: from global state to a pure fold

Here is a small wallet program written with global state:

```python
balance = 0
history = []


def apply(event):
    global balance
    kind, amount = event
    if kind == "deposit":
        balance += amount
        history.append(f"+{amount}")
    elif kind == "withdraw":
        if amount > balance:
            history.append(f"rejected {amount}")
        else:
            balance -= amount
            history.append(f"-{amount}")
```

It is hard to test: every test changes the same globals, you cannot ask "what would happen if",
and running the events twice doubles everything. Rewrite it in a **functional style** in
`solution.py`.

A **state** is a dict `{"balance": int, "history": tuple_of_strings}`. The start state is
`{"balance": 0, "history": ()}`.

### 1. `step(state, event)`

Return a **new** state after one event. Never change `state`. `event` is `(kind, amount)`:

- `("deposit", n)`: add `n`; history gets `"+n"`.
- `("withdraw", n)`: if `n` is more than the balance, the balance stays and history gets
  `"rejected n"`; otherwise subtract `n` and history gets `"-n"`.
- An unknown kind, or an amount that is not a positive `int`, raises `ValueError`.

### 2. `run_events(events, start=None)`

Fold all events into one final state with `functools.reduce`. If `start` is `None`, begin from
the start state. Never change `start`.

### 3. `balances(events)`

Return a list of the balance **after each event**, from the start state. Use
`itertools.accumulate` with `step`.

**Example**

```python
events = [("deposit", 50), ("withdraw", 20), ("withdraw", 100), ("deposit", 5)]

run_events(events)
# {"balance": 35, "history": ("+50", "-20", "rejected 100", "+5")}

balances(events)    # [50, 30, 30, 35]

s = {"balance": 10, "history": ("+10",)}
step(s, ("withdraw", 4))   # {"balance": 6, "history": ("+10", "-4")}
s                          # unchanged: {"balance": 10, "history": ("+10",)}
```
