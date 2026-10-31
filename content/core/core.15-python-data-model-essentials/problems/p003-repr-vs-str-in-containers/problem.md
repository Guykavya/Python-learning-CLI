# Trace: repr or str?

Two methods, many places that call them. Work out which one runs each time.

```python
class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Item({self.name!r})"

    def __str__(self):
        return self.name


class Plain:
    def __repr__(self):
        return "<Plain>"


it = Item("pen")
print(it)
print(repr(it))
print([it])
print((it, 1))
print({"k": it})
print(f"{it} / {it!r}")
print(str([it]))
print("item:", it)
print(Plain())
print([Plain()], str(Plain()))
print(it.name, repr(it.name))
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `print(x)`, `str(x)`, `f"{x}"` use `__str__` (which falls back to `__repr__`).
- `repr(x)`, `f"{x!r}"`, and the items **inside** a list, tuple or dict use `__repr__`.
- If a class has only `__repr__`, `__str__` falls back to it.

## Example of the format

```python
class Z:
    def __repr__(self):
        return "Z!"

print(Z(), [Z()])
```

prints

```text
Z! [Z!]
```
