## Approach

Three small ideas:

1. **Snapshot**: loop over `list(entries)`, so removing or adding handlers during `publish`
   cannot skip or add a handler in the middle of the loop.
2. **Error isolation**: `try/except Exception` around each call; keep the exception and go on.
   Returning them (instead of printing or swallowing) lets the caller decide what to do.
3. **Subscription identity**: each `subscribe` stores a fresh object, so an unsubscribe function
   removes its own entry even if the same function was subscribed twice, and a second call finds nothing and returns.

## Code

```python
class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event, fn):
        entry = (fn,)
        self._handlers.setdefault(event, []).append(entry)

        def unsubscribe():
            entries = self._handlers.get(event, [])
            for i, item in enumerate(entries):
                if item is entry:
                    del entries[i]
                    return

        return unsubscribe

    def publish(self, event, **data):
        errors = []
        for (fn,) in list(self._handlers.get(event, [])):
            try:
                fn(**data)
            except Exception as exc:
                errors.append(exc)
        return errors
```

## Complexity

`publish`: O(h) for h handlers (plus the copy, also O(h)). `unsubscribe`: O(h). A dict keyed
by a counter makes unsubscribe O(1) and still keeps insertion order.

## Another way

Keep `{event: {token: fn}}` with `token = next(counter)`. Python dicts keep insertion order, so
the handler order is preserved, and `pop(token, None)` makes a repeated unsubscribe safe.
Use `tuple(d.values())` as the snapshot.

Catching `Exception` (not a bare `except:`) is deliberate: `KeyboardInterrupt` and
`SystemExit` should still stop the program.
