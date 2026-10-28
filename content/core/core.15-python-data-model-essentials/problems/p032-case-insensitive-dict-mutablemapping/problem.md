# A case-insensitive dict with `MutableMapping`

HTTP header names are case-insensitive: `Content-Type` and `content-type` are the same header.
You could subclass `dict`, but then `get`, `pop`, `update`, `in` and the constructor all need
patching. A better way is `collections.abc.MutableMapping`: you write **five** methods and the class
gives you `get`, `pop`, `popitem`, `setdefault`, `update`, `clear`, `keys`, `items`, `values`,
`in` and `==` for free. Write `CaseInsensitiveDict` in `solution.py`.

Rules:

- Keys are strings. Writing a non-string key (`d[1] = 2`) raises `TypeError`. Looking one up with
  `in` is just `False`.
- Lookup, writing, deleting and `in` ignore the case of the key.
- The dict remembers the **spelling of the key as last written**. Iteration, `keys()`, `items()`
  and `repr` show that spelling. Writing `d["HOST"]` when `"Host"` exists replaces both value and
  spelling and does not add a second entry.
- A missing key raises `KeyError` holding the key **as the caller wrote it**.
- `CaseInsensitiveDict(data=None, **kwargs)` takes a mapping, an iterable of pairs, and/or keyword
  arguments (the same as `dict(...)`).
- `==` compares with another case-insensitive dict or with a plain `dict`, ignoring key case.
  Anything that is not a mapping gives `NotImplemented` (so `d == 5` is `False`).
- `copy()` returns a new, independent `CaseInsensitiveDict`.
- `repr`: `CaseInsensitiveDict({'Host': 'x'})`.

Hint for the design: keep one inner dict `lowercase key -> (original key, value)`.

**Example**

```python
h = CaseInsensitiveDict({"Content-Type": "text/html"}, Accept="*/*")
h["content-type"]        # 'text/html'
"ACCEPT" in h            # True
h["ACCEPT"] = "text/plain"
list(h)                  # ['Content-Type', 'ACCEPT']
h == {"content-type": "text/html", "accept": "text/plain"}   # True
h["X"]                   # KeyError: 'X'
```
