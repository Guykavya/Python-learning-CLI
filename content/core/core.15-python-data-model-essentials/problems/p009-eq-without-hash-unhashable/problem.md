# Trace: __eq__ without __hash__

A class that defines `__eq__` and does **not** define `__hash__` gets `__hash__ = None`, so its
objects cannot be dict keys or set members. A subclass that redefines `__eq__` loses an inherited
`__hash__` in the same way.

```python
class P:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return isinstance(other, P) and self.v == other.v


class Q:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return isinstance(other, Q) and self.v == other.v

    def __hash__(self):
        return hash(self.v)


class S(Q):
    def __eq__(self, other):
        return True


print(P.__hash__)
print(P(1) == P(1), P(1) in [P(1)])
try:
    hash(P(1))
except TypeError as e:
    print("error:", e)
try:
    d = {P(1): "x"}
except TypeError:
    print("error: P cannot be a dict key")
s = {Q(1), Q(1), Q(2)}
print(len(s), Q(1) in s)
print(Q.__hash__ is None, S.__hash__ is None)
try:
    {S(1)}
except TypeError:
    print("error: S cannot be a set element")
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `hash(obj)` on an unhashable object raises `TypeError` with the message `unhashable type: 'ClassName'`.
- `print("error:", e)` prints the message of the caught exception after `error:`.
- Using an unhashable object as a dict key or set element raises the same kind of `TypeError`.
- A set keeps one copy of objects that are equal **and** have equal hashes.

## Example of the format

```python
class Z:
    def __eq__(self, other):
        return True

print(Z.__hash__)
```

prints

```text
None
```
