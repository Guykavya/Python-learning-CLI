class EventBus:
    """First draft. It works for the happy path only."""

    def __init__(self):
        self.handlers = {}

    def subscribe(self, event, fn):
        self.handlers.setdefault(event, []).append(fn)

    def publish(self, event, **data):
        for fn in self.handlers.get(event, []):
            fn(**data)
