# pickle keeps types, json forgets them

`json` can only store strings, numbers, booleans, `null`, lists and dicts with text keys. Other values are changed
or refused. `pickle` can store almost any Python object. (Only load pickles that **your own program** wrote. See the
explain problem about the danger.)

Write three functions in `solution.py`:

- `save_pickle(obj, path)`: write `obj` to `path` with `pickle.dump` (binary mode).
- `load_pickle(path)`: read it back with `pickle.load`.
- `json_loses(obj)`: return `True` if the object does **not** survive `json.loads(json.dumps(obj))`
  unchanged. That is the case when the round trip gives a different value, **or** when `json.dumps`
  raises `TypeError` (for example for a set or bytes). Otherwise return `False`.

**Example**

```python
json_loses({"a": [1, 2, 3]})     # False
json_loses({"point": (1, 2)})    # True   (the tuple comes back as a list)
json_loses({1: "one"})           # True   (the key comes back as "1")
json_loses({"tags": {"x"}})      # True   (a set cannot be written)
```
