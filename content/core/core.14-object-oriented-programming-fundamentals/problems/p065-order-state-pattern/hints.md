## Hint 1

Start with `OrderState`: four methods that all raise. Then each subclass overrides only what it
allows and returns the **next state object**. Why does the base class make the "not allowed" case free
for every state, also for states that do not exist yet?

## Hint 2

All four `Order` actions do the same three things: ask the current state, store the state it returns,
append its name to the history. Write that once in a helper `_apply(self, action)` and use
`getattr(self._state, action)` to pick the method by name.

If the state raises, Python leaves `_apply` before the two assignments, so nothing changes. You get
"a failed action changes nothing" for free, as long as you assign only **after** the call returned.

## Hint 3

```text
can(action):
    if action not in ("pay", "ship", "deliver", "cancel"): ValueError(...)
    saved = self.refunded
    try:
        getattr(self._state, action)(self)      # trial run, result thrown away
    except InvalidTransition:
        return False
    finally:
        self.refunded = saved                   # undo any side effect
    return True
```
