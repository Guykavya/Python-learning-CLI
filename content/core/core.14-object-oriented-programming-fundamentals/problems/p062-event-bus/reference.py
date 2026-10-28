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
