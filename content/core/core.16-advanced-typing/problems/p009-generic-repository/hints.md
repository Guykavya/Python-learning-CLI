## Hint 1

The class has two placeholders: the type of the keys (`K`) and the type of the values (`V`). Look at each method: which of `K`, `V` is the *argument* and which is the *result*? For `get`, the answer might be missing: what does that do to the return hint?

## Hint 2

Keep a `dict[K, V]` in `__init__` (`self._data: dict[K, V] = {}`). A dict keeps insertion order, so `all()` and `find()` can use `self._data.values()`. For `get` returning `None` when missing, `self._data.get(key)` does it. For `require` and `remove`, what does indexing or `.pop(key)` raise when the key is missing?

## Hint 3

```
class Repository(Generic[K, V]):
    __init__:  self._data = {}   (hint: dict[K, V])
    add(key, value):  if key in self._data: raise KeyError(key) ; store
    get(key):         return self._data.get(key)
    require(key):     return self._data[key]
    remove(key):      return self._data.pop(key)
    find(pred):       [v for v in values if pred(v)]
    all():            list(values)
    __len__, __contains__:  on the dict
```
