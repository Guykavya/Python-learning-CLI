## Hint 1

For each leak ask: **who** still refers to the old objects? For the cache it is the module-level
dictionary, which only ever gets new keys. For the widgets it is the bus: `bus._handlers` holds
`self.on_event`, and a bound method holds its `self`. What has to happen when the cache is full,
and when a widget closes?

## Hint 2

A dictionary remembers insertion order, so "least recently used" can be "first key in the
dict" if you move a key to the end every time it is used. For the bus, remove the handler on
close, and loop over a **copy** of the list in `publish`.

```
parse_record(line):
    if line in cache:
        value = cache.pop(line); cache[line] = value    # move to the end = most recent
        return value
    parse, stats["computed"] += 1
    cache[line] = result
    if len(cache) > MAX_CACHE: del cache[next(iter(cache))]   # oldest

unsubscribe(handler): if handler in handlers: handlers.remove(handler)
publish(event): for h in list(handlers): h(event)
Widget.close(): self.bus.unsubscribe(self.on_event)
```
