# Open/closed with a registry

**Open for extension, closed for modification**: to add a feature you add code, you do not edit
code that already works and is already tested. `area` in `starter.py` fails this: every new
shape means opening the function, adding another `elif`, and hoping you did not break the
others.

A **registry** fixes it. It is a dict from a name to a function, filled by a decorator:

```python
_AREAS = {}

def register(name):
    def decorator(func):
        _AREAS[name] = func
        return func          # give the function back unchanged
    return decorator

@register("circle")
def _circle(shape): ...
```

Then `area` is the same three lines forever: look up, call.

Copy `starter.py` to `solution.py` and write:

- `register(name)`: a decorator factory that stores the function under `name` and **returns the
  function unchanged**. Registering a name that is **already registered** raises `ValueError`.
- `shape_names()`: the registered names as a **sorted list**.
- the three built-in shapes (`circle` uses key `r`; `rect` uses `w`, `h`; `square` uses `side`), registered with
  the decorator.
- `area(shape)`: `shape` is a dict with a `"type"` key. Look up and call the registered function with the
  whole dict. An unknown type raises **`ValueError`** whose message contains the unknown name
  (not a raw `KeyError`).

The tests register **new** shapes from the test file (`triangle`, `hexagon`) and call `area`
without any change to your module. `area` must also not contain an `if`/`elif` chain of three or more
branches, nor the strings `"circle"`, `"rect"`, `"square"`.

**Example**

```python
@register("triangle")
def _triangle(shape):
    return 0.5 * shape["b"] * shape["h"]

area({"type": "triangle", "b": 4, "h": 3})   # 6.0
area({"type": "blob"})                       # ValueError: unknown shape: blob
```
