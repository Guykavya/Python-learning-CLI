"""Helpers for a small desktop app: events, documents and a description cache.

    bus = EventBus()
    bus.subscribe(window.on_save)     # window.on_save(event) is called on every publish
    bus.publish("saved")

    doc = Document("report")
    page = doc.add_page()             # page.document is doc

    describe(obj)                     # an expensive summary, computed once per object
"""

log = []                    # Document.__del__ writes "freed <name>" here
stats = {"computed": 0}     # how many times describe() really computed a summary


class EventBus:
    """Calls every subscribed callback with each published event."""

    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        self._subscribers.remove(callback)        # ValueError if it was not subscribed

    def publish(self, event):
        for callback in list(self._subscribers):
            callback(event)

    def subscriber_count(self):
        return len(self._subscribers)


class Document:
    """A document made of pages. Logs when it is freed."""

    def __init__(self, name):
        self.name = name
        self.pages = []

    def add_page(self):
        page = Page(self)
        self.pages.append(page)
        return page

    def __del__(self):
        log.append(f"freed {self.name}")


class Page:
    def __init__(self, document):
        self.document = document


_cache = {}


def describe(obj):
    """A summary of obj, computed only the first time for each object."""
    if obj not in _cache:
        stats["computed"] += 1
        _cache[obj] = f"{type(obj).__name__} with {len(vars(obj))} attributes"
    return _cache[obj]


def cache_size():
    return len(_cache)
