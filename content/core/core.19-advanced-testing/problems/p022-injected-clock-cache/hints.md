## Hint 1

What do you store next to each value so that you can decide later whether it is still fresh? When do
you read the clock: at `set`, at `get`, at both?

## Hint 2

Store `(value, time_set)`. In `get` compare `clock() - time_set` with `ttl` using the right operator
for the border. `__len__` needs the same freshness test for every entry. Can you write it once as a
small helper method?

## Hint 3

```
__init__: validate ttl; self.ttl, self.clock, self._data = ttl, clock, {}
set(k, v): self._data[k] = (v, self.clock())
_alive(entry, now): now - entry[1] < self.ttl
get(k, default): entry = _data.get(k); if entry is None or not alive: return default; return entry[0]
__len__: now = clock(); sum(1 for e in values if alive)
```
