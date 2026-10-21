# Dig into nested data

Data from a web service is often nested dicts and lists. Write `dig(data, keys, default=None)`
that follows `keys` one at a time (`data[keys[0]][keys[1]]...`) and returns what it finds.

- If any step fails because a key is missing or an index is out of range, return `default`.
  Both are lookups that failed: handle them with **one** `except` clause naming their common
  parent class (section 4).
- If a step is impossible because of the **type** (indexing an int, or a list with a string),
  Python raises `TypeError`. That means the caller's path does not match the data's shape: a
  bug. Let it propagate.
- With an empty `keys` list, return `data` itself.

**Examples**

```python
order = {"customer": {"name": "Asha"}, "items": [{"name": "tea", "qty": 2}]}
dig(order, ["customer", "name"])          # 'Asha'
dig(order, ["items", 0, "qty"])           # 2
dig(order, ["items", 5, "qty"])           # None   (IndexError)
dig(order, ["customer", "phone"], "-")    # '-'    (KeyError)
dig(order, ["items", "first"])            # raises TypeError (a list needs an int index)
```
