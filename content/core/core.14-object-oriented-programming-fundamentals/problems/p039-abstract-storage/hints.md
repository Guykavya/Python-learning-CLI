## Hint 1

Which methods depend on **how** the data is stored, and which can be written using only other
methods? `get_or` only needs `get` and a `try/except KeyError`. `items` only needs `keys` and `get`.
Put those in the base class. Mark the other four with `@abstractmethod`: their body can be just a
docstring.

## Hint 2

`PrefixStorage` holds the inner storage in an attribute and adds the prefix on the way in:
`self._inner.set(self._prefix + key, value)`. Why does it also need to inherit from `Storage`?
(Think of who else may want to wrap it, and which methods it then gets for free.) To make the
`KeyError` show the short key, catch the inner one and raise `KeyError(key) from None`.

## Hint 3

```
class Storage(ABC):
    @abstractmethod get / set / delete / keys
    get_or(key, default):  try: return self.get(key)  except KeyError: return default
    contains(key):         try: self.get(key)  except KeyError: return False;  return True
    pop(key):              value = self.get(key); self.delete(key); return value
    items():               [(k, self.get(k)) for k in sorted(self.keys())]

class PrefixStorage(Storage):
    __init__(inner, prefix): check isinstance(inner, Storage), prefix non-empty str
    keys(): [k[len(prefix):] for k in inner.keys() if k.startswith(prefix)]
```
