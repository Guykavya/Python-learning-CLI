## Hint 1

In the old code, `apply` reads the state from globals and changes it. In the new code the state
comes in as an argument and goes out as the return value. What are the two values that change,
and how do you make a **new** tuple from an old one plus one item?

## Hint 2

In `step`, compute a local `balance` and a `note`, then return
`{"balance": balance, "history": state["history"] + (note,)}`. `reduce(step, events, start)` folds
the events. `accumulate(events, step, initial=START)` yields the start state first, then the
state after each event: skip the first one.

## Hint 3

```
step(state, event):
    kind, amount = event
    validate amount (positive int) else ValueError
    balance = state["balance"]
    deposit:  balance += amount; note = "+amount"
    withdraw: if amount > balance: note = "rejected amount"
              else: balance -= amount; note = "-amount"
    else: ValueError
    return {"balance": balance, "history": state["history"] + (note,)}

run_events: reduce(step, events, start or START)
balances:   [s["balance"] for s in accumulate(events, step, initial=START)][1:]
```
