"""Helpers for a small desktop app: events, documents and a description cache.

    bus = EventBus()
    bus.subscribe(window.on_save)     # window.on_save(event) is called on every publish
    bus.publish("saved")

    doc = Document("report")
    page = doc.add_page()             # page.document is doc

    describe(obj)                     # an expensive summary, computed once per object
"""
import inspect
import weakref

log = []                    # Document.__del__ writes "freed <name>" here
stats = {"computed": 0}     # how many times describe() really computed a summary


class _Strong:
    """Looks like a weak reference (call it to get the callback) but holds the callback strongly."""

    def __init__(self, callback):
        self._callback = callback

    def __call__(self):
        return self._callback


class EventBus:
    """Calls every subscribed callback with each published event."""

    def __init__(self):
        self._subscribers = []          # "refs": call one to get the callback, or None if it died

    def subscribe(self, callback):
        if inspect.ismethod(callback):                  # fix 1: a bound method holds its object;
            ref = weakref.WeakMethod(callback)          # keep it weakly so the object can die
        else:
            ref = _Strong(callback)                     # functions, lambdas, builtin methods
        self._subscribers.append(ref)

    def unsubscribe(self, callback):
        for ref in self._subscribers:
            if ref() == callback:                       # compare callbacks, not the ref objects
                self._subscribers.remove(ref)
                return
        raise ValueError(f"{callback!r} is not subscribed")

    def _live(self):
        """Drop dead subscribers and return the live callbacks."""
        callbacks, alive = [], []
        for ref in self._subscribers:
            callback = ref()
            if callback is not None:
                alive.append(ref)
                callbacks.append(callback)
        self._subscribers = alive
        return callbacks

    def publish(self, event):
        for callback in self._live():
            callback(event)

    def subscriber_count(self):
        return len(self._live())


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
        self._document = weakref.ref(document)          # fix 2: no strong back-reference, no cycle

    @property
    def document(self):
        return self._document()                         # None once the document is gone


_cache = weakref.WeakKeyDictionary()                    # fix 3: entries vanish with their keys


def describe(obj):
    """A summary of obj, computed only the first time for each object."""
    if obj not in _cache:
        stats["computed"] += 1
        _cache[obj] = f"{type(obj).__name__} with {len(vars(obj))} attributes"
    return _cache[obj]


def cache_size():
    return len(_cache)
