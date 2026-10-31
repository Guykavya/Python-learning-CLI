# Trace: truthiness, `__bool__` and `__len__`

When Python needs a true/false value (in `if`, `while`, `not`, `and`, `or`, `bool()`), it asks the
object: first `__bool__`; if that does not exist, `__len__` (zero means false); if neither exists, the
object is true.

Read the code and write down exactly what it prints.

```python
class Plain:
    pass


class Bag:
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n


class Flag:
    def __init__(self, on, n):
        self.on = on
        self.n = n

    def __bool__(self):
        return self.on

    def __len__(self):
        return self.n


class Bad:
    def __bool__(self):
        return 1


def label(x):
    return "yes" if x else "no"


print(label(Plain()), label(Bag(0)), label(Bag(3)))
print(label(Flag(False, 5)), label(Flag(True, 0)))
print(bool(Bag(2)), bool(Flag(True, 0)), not Bag(0))
print(len(Flag(False, 5)))
print(Bag(0) or "fallback")
print(Bag(4) and "second")
print(type(Bag(0) or Bag(0)).__name__)
print([label(x) for x in (0, 0.0, "", [], {}, None, "0", [0])])
print(any([Bag(0), Bag(0)]), any([Bag(0), Bag(1)]), all([Plain(), Bag(1)]))
try:
    bool(Bad())
except TypeError as err:
    print("TypeError:", err)
try:
    len(Plain())
except TypeError as err:
    print("TypeError:", err)
```

In `answer.txt`, write the printed output, one line per printed line.

Facts you need:

- `print(Bag(0) or "fallback")` prints the value that `or` returns. If it is the string, it prints
  the string; if it is a `Bag`, it would print `<...Bag object at 0x...>`, so the program avoids
  printing a `Bag` directly.
- `type(x).__name__` is the class name as text.
- `__bool__` must return a real `bool`.

## Example of the format

```python
class Empty:
    def __len__(self):
        return 0

print(bool(Empty()), len(Empty()))
```

prints `False 0`.
