## Hint 1

What two facts must you store for each key so that `get` can decide "hit or miss"? And what must you do to a key so that the cache remembers it was used just now?

## Hint 2

Store `key -> (expires_at, value)` in an `OrderedDict`. The order of the dict *is* the recency order: the first item is the least recently used.

```text
get(key):
    entry = items.get(key)
    if entry is None or entry.expires_at <= now(): (delete it if present); misses += 1; return default
    items.move_to_end(key); hits += 1; return entry.value

set(key, value, ttl):
    items[key] = (now() + (ttl or self.ttl), value); move_to_end(key)
    while len(items) > maxsize: items.popitem(last=False)
```

Careful: `ttl or self.ttl` treats `ttl=0` as "use the default". Write `self.ttl if ttl is None else ttl`.
