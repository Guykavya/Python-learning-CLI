## Approach

A leak in Python is almost always "something still refers to the object". For each report, find
that reference and make it weak, or remove the cycle.

1. **Bound-method subscribers.** `w.on_save` is a bound method object that holds `w` in its
   `__self__`. The bus keeps the bound method in a list, so `w` lives as long as the bus. We cannot
   store `weakref.ref(w.on_save)`: the bound method is a temporary object that dies immediately.
   `weakref.WeakMethod` solves exactly this: it keeps weak references to the object and the function
   and rebuilds the bound method on demand. Plain functions and lambdas must stay strong (often
   nothing else refers to a lambda), and builtin methods such as `list.append` are not "methods" for
   `inspect.ismethod` and cannot be weakly referenced anyway. To keep the loop simple, both kinds are
   stored as "call me to get the callback": a `WeakMethod`, or a tiny `_Strong` wrapper.
   `unsubscribe` must compare the callbacks (`ref() == callback`), because a `WeakMethod` is never
   equal to a bound method.
2. **The page/document cycle.** `doc.pages -> page -> page.document -> doc` is a cycle. Reference
   counting can never free a cycle, so the document waited for the cyclic garbage collector, which
   runs only when enough allocations have happened: "random moments". Since PEP 442 (Python 3.4)
   the collector does call `__del__` for cycles, so it was not lost forever, only late. Making the
   child-to-parent link a `weakref.ref` removes the cycle, and the document is freed the moment its
   last reference goes. A property keeps `page.document` working.
3. **The cache.** A plain dict holds its keys strongly. A `WeakKeyDictionary` holds them weakly and
   removes an entry when its key is collected, so the cache never outlives the objects it describes.

## Code

```python
import inspect
import weakref


class _Strong:
    def __init__(self, callback):
        self._callback = callback

    def __call__(self):
        return self._callback


class EventBus:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        if inspect.ismethod(callback):
            ref = weakref.WeakMethod(callback)
        else:
            ref = _Strong(callback)
        self._subscribers.append(ref)

    def unsubscribe(self, callback):
        for ref in self._subscribers:
            if ref() == callback:
                self._subscribers.remove(ref)
                return
        raise ValueError(f"{callback!r} is not subscribed")

    def _live(self):
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


class Page:
    def __init__(self, document):
        self._document = weakref.ref(document)

    @property
    def document(self):
        return self._document()


_cache = weakref.WeakKeyDictionary()
```

`Document`, `describe`, `cache_size`, `log` and `stats` are unchanged.

## Complexity

`subscribe` is O(1); `publish`, `subscriber_count` and `unsubscribe` are O(s) for s subscribers
(they were O(s) before too). `describe` stays O(1) on average. Nothing else changes.

## Another way

- **Bug 1:** keep the strong list but make subscribers responsible for calling `unsubscribe` when
  they close. That is the usual design in GUI toolkits, but a single forgotten call brings the leak
  back; weak subscriptions make forgetting harmless. A `weakref.finalize(callback.__self__, ...)`
  that removes the entry is another way to drop dead subscribers immediately instead of lazily.
- **Bug 2:** instead of a weak back-reference, give `Document` a `close()` that clears
  `self.pages` (breaking the cycle by hand), or do not store the parent at all and pass it when it
  is needed. Replacing `__del__` by `weakref.finalize(self, log.append, f"freed {name}")` makes the
  logging safer, but does not fix the delay: the cycle is still there.
- **Bug 3:** `functools.lru_cache(maxsize=...)` bounds the memory but still keeps the most recent
  objects alive. Store the summary on the object itself (`obj._summary`) if you own the class:
  then it dies with the object automatically.
