## Approach

The registry is a dict from event names to lists of handlers, living in `make_event_bus`'s scope
and shared by the three closures. None of them rebinds `handlers`, so no `nonlocal` is needed:
they only mutate the dict and its lists. `emit` copies the list before looping, so changes made by
handlers take effect from the next `emit`, and forwards its arguments with `*args, **kwargs`.

## Code

```python
def make_event_bus():
    """Return {'on': on, 'off': off, 'emit': emit} sharing a private registry of handlers."""
    handlers = {}

    def on(event, handler):
        handlers.setdefault(event, []).append(handler)

    def off(event, handler):
        registered = handlers.get(event, [])
        if handler in registered:
            registered.remove(handler)
            return True
        return False

    def emit(event, *args, **kwargs):
        current = list(handlers.get(event, []))
        return [h(*args, **kwargs) for h in current]

    return {"on": on, "off": off, "emit": emit}
```

## Complexity

`on` O(1); `off` O(k) for k handlers of that event; `emit` O(k) plus the handlers' own work.

## Another way

`off` could rebuild the list without the handler, but that would remove every registration, not
only the first. This publish/subscribe pattern is how GUI toolkits and games wire up buttons and
events; in the adventure project, rooms could subscribe to an "enter" event.
