# Recursive generators: deep flatten and folder walk

A generator can call itself. `yield from f(part)` hands every item of the smaller problem up to the
caller, one at a time. Write two recursive generator functions in `solution.py`.

## 1. `flatten(data)`

`data` is a list or tuple that can hold other lists and tuples, nested to **any depth**. Yield
every item that is not a list or tuple, from left to right. Strings, numbers, dicts and everything
else are single items: a string is **not** split into letters.

```python
list(flatten([1, [2, [3, [4]]], (5, 6), []]))   # [1, 2, 3, 4, 5, 6]
list(flatten(["ab", ["cd", ("ef",)]]))          # ["ab", "cd", "ef"]
list(flatten([]))                                # []
```

## 2. `walk(tree)`

`tree` is a dict that describes folders. A key is a name. If its value is a dict, it is a folder;
otherwise the value is the size of a file. Yield a tuple `(path, size)` for every **file**, with
the names joined by `"/"`, in the order of the dict. Empty folders give nothing.

```python
tree = {
    "README.md": 5,
    "src": {"main.py": 120, "lib": {"a.py": 30, "b.py": 7}},
    "empty": {},
}
list(walk(tree))
# [("README.md", 5), ("src/main.py", 120), ("src/lib/a.py", 30), ("src/lib/b.py", 7)]
```

Both functions must be **generators**: they produce items when asked, and they do not build the
full result list first. Use `isinstance(x, (list, tuple))` and `isinstance(x, dict)` to test the type.
