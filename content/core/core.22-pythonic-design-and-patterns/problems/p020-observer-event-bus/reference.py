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
