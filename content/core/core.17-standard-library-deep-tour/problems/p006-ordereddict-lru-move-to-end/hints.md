## Hint 1

Keep one `OrderedDict` inside the object. Decide on a direction: the **end** of the dict is "most recently used", the **start** is "least recently used". Which method moves a key to the end, and which removes the item at the start?

## Hint 2

`get`: if the key is missing, return the default and do nothing else. If present, `move_to_end(key)` and return the value. `put`: assign, then `move_to_end(key)` (assigning to an existing key does **not** move it). Then, while `len > capacity`, `popitem(last=False)`.

## Hint 3

```
class LRUCache:
    __init__(capacity): check >= 1; self._data = OrderedDict()
    get(key, default=None):
        if key not in self._data: return default
        self._data.move_to_end(key)
        return self._data[key]
    put(key, value):
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)
    __len__: len(self._data)
    keys: list(self._data)
```
