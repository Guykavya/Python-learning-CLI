"""A small app module. It works, but a long-running server using it slowly runs out of memory."""

MAX_CACHE = 1000

_cache = {}
stats = {"computed": 0}


def parse_record(line):
    """'alice, 30, Paris' -> ('alice', 30, 'Paris'). Repeated lines are answered from the cache."""
    if line in _cache:
        return _cache[line]
    stats["computed"] += 1
    name, age, city = (part.strip() for part in line.split(","))
    result = (name, int(age), city)
    _cache[line] = result
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
        pass

    def publish(self, event):
        for handler in self._handlers:
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
        self.seen.clear()
