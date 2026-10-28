# Trace: += and shared objects

`a += b` first tries `a.__iadd__(b)`, which is allowed to **change a in place** and must return the
object that `a` will now point to. If there is no `__iadd__`, Python uses `a = a + b`, which makes a new
object. That difference matters when two names point to the same object.

```python
class Bag:
    def __init__(self, items=()):
        self.items = list(items)

    def __add__(self, other):
        return Bag(self.items + other.items)

    def __iadd__(self, other):
        self.items.extend(other.items)
        return self

    def __repr__(self):
        return f"Bag({self.items})"


class Plain:
    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return Plain(self.val + other.val)


class Buggy:
    def __init__(self, items):
        self.items = list(items)

    def __iadd__(self, other):
        self.items.extend(other)


a = Bag([1])
b = a
a = a + Bag([2])
print(a, b, a is b)

a = Bag([1])
b = a
a += Bag([2])
print(a, b, a is b)

x = [1]
y = x
x += [2]
print(y)
x = x + [3]
print(x, y)

t = (1,)
u = t
t += (2,)
print(t, u)

p = Plain(1)
q = p
p += Plain(2)
print(p.val, q.val, p is q)

z = Buggy([1])
z += [2]
print(z)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `b = a` makes `b` a second name for the **same** object.
- Lists have `__iadd__`: `x += [2]` changes the list in place. Tuples and ints do not: `t += (2,)` builds a new tuple.
- After `a += w`, the name `a` points to whatever `__iadd__` returned (`None` if the method forgot to return).

## Example of the format

```python
x = [1]
y = x
x += [2]
print(y)
```

prints

```text
[1, 2]
```
