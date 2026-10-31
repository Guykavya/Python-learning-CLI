"""A small app module. It works, and memory now stays bounded."""

MAX_CACHE = 1000

_cache = {}
stats = {"computed": 0}


def parse_record(line):
    """'alice, 30, Paris' -> ('alice', 30, 'Paris'). Repeated lines are answered from the cache."""
    if line in _cache:
        result = _cache.pop(line)  # re-insert at the end: most recently used
        _cache[line] = result
        return result
    stats["computed"] += 1
    name, age, city = (part.strip() for part in line.split(","))
    result = (name, int(age), city)
    _cache[line] = result
    if len(_cache) > MAX_CACHE:
        del _cache[next(iter(_cache))]  # the first key is the least recently used
    return result


def cache_size():
    return len(_cache)


def clear_cache():
    _cache.clear()
    stats["computed"] = 0


class EventBus:
    def __init__(self):
        self._handlers = []

    def subscribe(self, handler):
        self._handlers.append(handler)

    def unsubscribe(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)

    def publish(self, event):
        for handler in list(self._handlers):  # a handler may unsubscribe while we loop
            handler(event)

    def handler_count(self):
        return len(self._handlers)


class Widget:
    def __init__(self, bus):
        self.bus = bus
        self.seen = []
        bus.subscribe(self.on_event)

    def on_event(self, event):
        self.seen.append(event)

    def close(self):
        self.bus.unsubscribe(self.on_event)
        self.seen.clear()
