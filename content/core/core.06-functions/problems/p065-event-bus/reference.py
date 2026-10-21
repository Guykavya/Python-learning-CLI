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
