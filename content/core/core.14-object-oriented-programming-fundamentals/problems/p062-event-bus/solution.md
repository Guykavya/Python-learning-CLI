## Approach

- **Composition:** the bus *has* a dict `event name -> list of listeners`. Nothing inherits.
- **Duck typing** (chapter section 15): a listener is anything with a callable `handle`.
  `callable(getattr(listener, "handle", None))` checks that in one expression, because the default
  `None` is not callable.
- **Exception groups** (chapter section 19): one failure must not hide the others, so `publish`
  collects them and raises one `ExceptionGroup` at the end. `add_note` (chapter section 18) records
  which listener failed without changing the exception's type or message.
- **Iterate over a snapshot:** `publish` copies the target list before calling anyone, so listeners can
  (un)subscribe safely.

## Code

```python
class Event:
    def __init__(self, name, payload=None):
        self.name = name
        self.payload = payload


class EventBus:
    def __init__(self):
        self._listeners = {}  # event name -> list of listeners

    def subscribe(self, event_name, listener):
        if not callable(getattr(listener, "handle", None)):
            raise TypeError("listener needs a handle(event) method")
        group = self._listeners.setdefault(event_name, [])
        if not any(existing is listener for existing in group):
            group.append(listener)

    def unsubscribe(self, event_name, listener):
        group = self._listeners.get(event_name, [])
        for i, existing in enumerate(group):
            if existing is listener:
                del group[i]
                return
        raise ValueError(f"listener is not subscribed to {event_name!r}")

    def listeners(self, event_name):
        return list(self._listeners.get(event_name, []))

    def publish(self, event_name, payload=None):
        if event_name == "*":
            raise ValueError("cannot publish '*'")
        event = Event(event_name, payload)
        targets = self.listeners(event_name) + self.listeners("*")  # copies: safe to change during publish
        errors = []
        for listener in targets:
            try:
                listener.handle(event)
            except Exception as exc:
                exc.add_note(f"listener: {type(listener).__name__}")
                errors.append(exc)
        if errors:
            raise ExceptionGroup(f"{len(errors)} listener(s) failed for {event_name!r}", errors)
        return len(targets)
```

## Complexity

`publish` is O(k) for k listeners (plus their own work). `subscribe` and `unsubscribe` are O(k) for the
`is` scan of one event's list.

## Another way

Accept plain functions too: store `listener.handle` if it exists, else the listener itself if
`callable(listener)`. Then `bus.subscribe("e", print)` works. You could also let callers handle the
group with `except*`, for example `except* ValueError` for bad payloads and `except* RuntimeError` for
crashes, which is exactly why the bus keeps the original exception types.
