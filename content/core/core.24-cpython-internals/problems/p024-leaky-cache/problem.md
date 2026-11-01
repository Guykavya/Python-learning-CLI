# Fix: three memory leaks

`starter.py` is a helper module from a small desktop app:

- `EventBus`: `subscribe(callback)`, `unsubscribe(callback)`, `publish(event)` calls every
  subscriber with the event, `subscriber_count()`.
- `Document(name)` with `add_page()`; each `Page` knows its document as `page.document`.
  `Document.__del__` appends `"freed <name>"` to the module list `log`.
- `describe(obj)`: an "expensive" summary of an object, cached so that it is computed once per
  object (`stats["computed"]` counts the real computations); `cache_size()`.

Everything works in a short demo. After a day of use, three bug reports arrive:

1. *"Memory grows every time I open and close a window. Closed windows even keep reacting to
   `publish`!"* (Each window subscribes its bound method `window.on_save`.)
2. *"The `freed report` line appears at random moments, sometimes minutes after the document was
   closed, and the document's file stays locked until then."*
3. *"The memory used by `describe` only ever grows. An object that was described once is never
   freed."*

Copy `starter.py` to `solution.py` and fix all three. Each report has one cause. Reproduce it
first: make the object, delete your last reference, call `gc.collect()`, and check with a
`weakref.ref` whether the object is really gone. Keep the public interface exactly as it is.

The intended behaviour, which the tests check:

- A subscribed **bound method** must not keep its object alive. When the object dies, it silently
  stops being a subscriber (`publish` skips it, `subscriber_count` no longer counts it).
  **Plain functions, lambdas and builtin methods** (like `some_list.append`) stay subscribed:
  nothing else may hold them, so they must be kept strongly.
- `unsubscribe` still works for both kinds, and still raises `ValueError` for a callback that is
  not subscribed.
- Deleting the last reference to a `Document` frees it **at once** by reference counting, without
  waiting for the cyclic garbage collector (the test switches the collector off with
  `gc.disable()` to check). `page.document` still returns the document while it exists, and `None`
  after it is gone.
- `describe` still computes once per object, but its cache must not keep objects alive, and the
  entries of freed objects must disappear.

**Example**

```python
bus = EventBus()
w = Window("temp")              # a class with an on_save(self, event) method
bus.subscribe(w.on_save)
r = weakref.ref(w)
del w; gc.collect()
r()                              # starter: <Window object at 0x...> (leaked)   fixed: None
bus.subscriber_count()          # starter: 1                                 fixed: 0

gc.disable()
doc = Document("report"); doc.add_page()
del doc
log                              # starter: []    fixed: ['freed report']
gc.enable()

t = Thing(); describe(t); r = weakref.ref(t)
del t; gc.collect()
r()                              # starter: <Thing object at 0x...>             fixed: None
```

Useful tools from the chapter: `weakref.ref`, `weakref.WeakMethod` (a weak reference to a bound
method: calling it gives a fresh bound method, or `None` once the object is gone),
`weakref.WeakKeyDictionary`, `inspect.ismethod`.
