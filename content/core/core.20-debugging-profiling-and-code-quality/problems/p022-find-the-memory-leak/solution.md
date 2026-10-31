## Approach

Find **who holds the references**, then decide when they should let go.

**Leak 1, the cache.** `_cache` lives as long as the module (for the whole run of the server),
and every new line adds a key. Old keys are never removed. Fix: bound it. A dictionary keeps
insertion order, so an LRU cache is a dict where a used key is moved to the end (pop and
re-insert) and, when the dict is too big, the **first** key (the least recently used) is
deleted.

**Leak 2, the listeners.** `bus.subscribe(self.on_event)` stores a bound method. A bound method
holds a reference to its object (`self.on_event.__self__ is self`), so as long as the bus lives,
every widget ever created lives too, with its `seen` list. Fix: `unsubscribe` really removes,
and `close()` calls it.

**The loop trap.** If a handler unsubscribes during `publish`, `list.remove` shifts the later
items one place to the left while the `for` loop's position moves on, so the next handler is
skipped. Looping over a copy (`list(self._handlers)`) avoids that.

## Code

```python
def parse_record(line):
    if line in _cache:
        result = _cache.pop(line)
        _cache[line] = result
        return result
    stats["computed"] += 1
    name, age, city = (part.strip() for part in line.split(","))
    result = (name, int(age), city)
    _cache[line] = result
    if len(_cache) > MAX_CACHE:
        del _cache[next(iter(_cache))]
    return result


class EventBus:
    ...
    def unsubscribe(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)

    def publish(self, event):
        for handler in list(self._handlers):
            handler(event)


class Widget:
    ...
    def close(self):
        self.bus.unsubscribe(self.on_event)
        self.seen.clear()
```

`self.on_event` creates a **new** bound method object each time, but two bound methods of the
same function and the same object compare equal, so `in` and `remove` find it.

## Complexity

`parse_record`: O(1) on average per call (dict lookup, pop, insert, delete first). Memory:
at most `MAX_CACHE` entries. `unsubscribe`: O(number of handlers). `publish`: O(handlers) plus
the O(handlers) copy.

## Another way

`functools.lru_cache(maxsize=MAX_CACHE)` does the LRU work for you:

```python
@functools.lru_cache(maxsize=MAX_CACHE)
def parse_record(line):
    stats["computed"] += 1          # only runs on a miss
    ...

def cache_size():
    return parse_record.cache_info().currsize

def clear_cache():
    parse_record.cache_clear()
    stats["computed"] = 0
```

For listeners, `weakref.WeakMethod` lets the bus hold a handler **without** keeping its object
alive, so a widget that is forgotten without `close()` can still be collected. Explicit
`close()` is clearer and is what most libraries do.
