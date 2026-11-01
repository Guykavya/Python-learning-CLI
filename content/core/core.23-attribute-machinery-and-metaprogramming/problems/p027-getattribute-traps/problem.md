# Trace: `__getattribute__` traps

The class below has **both** attribute hooks, and each one prints when it runs:

- `__getattribute__` prints `get NAME`. It runs for every `t.NAME` lookup written with a dot (or with `getattr`/`hasattr`).
- `__getattr__` prints `fallback NAME`. It runs only when the normal lookup raised `AttributeError`.

Three facts decide the output (not the answer itself):

1. The arguments of `print(...)` are evaluated **before** `print` writes anything.
2. If a property's getter raises `AttributeError`, Python treats it like "attribute not found"
   and calls `__getattr__`, even if the error came from a bug inside the getter.
3. Built-in operations such as `len(t)` and `repr(t)` look up the special method on the
   **type**, not through the instance, so they skip `__getattribute__`.

```python
class Tracked:
    def __init__(self):
        self.size = 3

    def __getattribute__(self, name):
        print(f"get {name}")
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print(f"fallback {name}")
        if name.startswith("_"):
            raise AttributeError(name)
        return f"<{name}>"

    @property
    def area(self):
        return self.width * 2

    @property
    def broken(self):
        raise AttributeError("broken inside")

    def __len__(self):
        return self.size

    def __repr__(self):
        return "T"


t = Tracked()
print("A", t.size)
print("B", t.color)
print("C", t.area)
print("D", t.broken)
print("E", len(t))
print("F", t.__len__())
print("G", repr(t))
print("H", hasattr(t, "_secret"))
print("I", hasattr(t, "anything"))
print("J", getattr(t, "_x", "default"))
t.color = "red"
print("K", t.color)
print("L", type(t).__name__)
```

**Example**: the first two lines of output are

```
get size
A 3
```

`get size` comes first because `t.size` is evaluated before `print` writes `A 3`.

Write in `answer.txt` all the lines the program prints, in order (30 lines).
