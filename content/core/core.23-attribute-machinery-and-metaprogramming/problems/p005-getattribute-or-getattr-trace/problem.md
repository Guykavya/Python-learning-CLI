# Trace: which hook fires?

A class can have two reading hooks:

- `__getattribute__(self, name)` runs for **every** attribute read on an instance (`obj.name`),
  whether the attribute exists or not.
- `__getattr__(self, name)` runs **only** when the normal lookup failed, that is when
  `__getattribute__` raised `AttributeError`.

Setting an attribute (`obj.name = value`) uses neither of them.

The class below has both hooks, and each one prints a line. Work out exactly what the program
prints. Write one line per printed line, in order. The program needs no input.

```python
class Probe:
    kind = "probe"

    def __init__(self):
        self.x = 1

    @property
    def area(self):
        return 10

    @property
    def broken(self):
        raise AttributeError("inside broken")

    def __getattribute__(self, name):
        print("getattribute", name)
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print("getattr", name)
        return "fallback-" + name


p = Probe()
print(p.x)
print(p.kind)
print(p.area)
print(p.missing)
print(p.broken)
print(getattr(p, "y", 0))
print(hasattr(p, "z"))
p.y = 5
print(p.y)
print(len(vars(p)))
```

Write your answer in `answer.txt`, one output line per printed line (the hooks print too).

**Example (a different program)**

```python
class Echo:
    def __getattr__(self, name):
        print("getattr", name)
        return name * 2

e = Echo()
e.a = 1
print(e.a, e.b)
```

prints

```
getattr b
1 bb
```

(`e.a` exists, so `__getattr__` is not called for it. Both arguments are evaluated before
`print` prints anything, so the hook's line comes first.)
