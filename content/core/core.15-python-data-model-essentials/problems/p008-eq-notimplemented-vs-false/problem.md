# Trace: NotImplemented or False?

`a == b` first calls `a.__eq__(b)`. If the answer is `NotImplemented`, Python tries
`b.__eq__(a)`. If that is also `NotImplemented` (or missing), the result is the default: `a is b`.
Returning plain `False` ends the search at once.

Each `__eq__` below prints a line so you can follow the calls.

```python
class Always:
    def __eq__(self, other):
        print("Always.eq")
        return True


class Strict:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        print("Strict.eq")
        if not isinstance(other, Strict):
            return NotImplemented
        return self.v == other.v


class Loose:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        print("Loose.eq")
        if not isinstance(other, Loose):
            return False
        return self.v == other.v


print(Strict(1) == Strict(1))
print(Strict(1) == Always())
print(Always() == Strict(1))
print(Loose(1) == Always())
print(Strict(1) == 5)
print(Strict(1) != Always())
print(Loose(2) != Loose(3))
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `a != b` calls `a.__ne__(b)`. The default `__ne__` calls `__eq__` and inverts the answer (unless it is `NotImplemented`).
- `print(a, b)` puts a space between the values.

## Example of the format

```python
class P:
    def __eq__(self, other):
        print("P.eq")
        return True

print(P() == 1)
```

prints

```text
P.eq
True
```
