# Save and load JSON

Write two functions in `solution.py`:

- `save_json(path, data)` writes `data` as JSON to `path`:
  UTF-8, `indent=2`, keys **sorted**, non-ASCII characters kept as they are (not `\uXXXX`),
  and one final newline at the end of the file.
- `load_json(path)` reads it back and returns the Python data.

**Example**

```python
save_json("c.json", {"b": 1, "a": ["x", "é"]})
# c.json contains:
# {
#   "a": [
#     "x",
#     "é"
#   ],
#   "b": 1
# }
load_json("c.json")   # {'a': ['x', 'é'], 'b': 1}
```
