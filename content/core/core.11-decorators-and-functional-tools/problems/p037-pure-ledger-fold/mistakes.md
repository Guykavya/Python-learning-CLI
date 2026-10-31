- `state["balance"] += amount` inside `step`. It changes the caller's dict, so the "before" and
  "after" states are the same object.
- `state["history"].append(note)` on a list. A history that is a list is shared by every copy
  made with `dict(state)`, because the copy is shallow.
- `def run_events(events, start={"balance": 0, "history": []})`: a mutable default is created
  once and shared by all calls.
- Including the start state in `balances`, giving one value too many.
- Allowing `amount = True`: `True` is an `int` (it is 1). Reject `bool` explicitly.
- Forgetting the start value in `reduce`: with no start, `reduce` treats the first **event** as
  the state.
