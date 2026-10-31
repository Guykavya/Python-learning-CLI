# Trace: `__slots__`, missing `__dict__` and `AttributeError`

A class with `__slots__` has no per-object `__dict__`, so only the named attributes can be set. A slot
that has not been assigned yet is **empty**, and reading it raises `AttributeError`, just like a
missing attribute. Subclasses inherit the slots but get a `__dict__` again unless they also declare
`__slots__`.

Read the code and write down exactly what it prints.

```python
class P:
    __slots__ = ("x", "y")

    def __init__(self, x):
        self.x = x


class Q(P):
    pass


class R(P):
    __slots__ = ("z",)


class S:
    __slots__ = ("a", "__dict__")


p = P(1)
print(p.x)
try:
    print(p.y)
except AttributeError as err:
    print("1", type(err).__name__, err)
try:
    p.z = 3
except AttributeError as err:
    print("2", type(err).__name__)
print(hasattr(p, "__dict__"), hasattr(Q(1), "__dict__"), hasattr(R(1), "__dict__"))
q = Q(2)
q.extra = "ok"
print(q.extra, q.x)
r = R(3)
r.z = 4
print(r.x, r.z)
try:
    r.w = 0
except AttributeError as err:
    print("3", type(err).__name__)
s = S()
s.a = 1
s.anything = 2
print(s.a, s.anything, vars(s))
try:
    vars(p)
except TypeError as err:
    print("4", type(err).__name__, err)
try:
    del p.x
    print(p.x)
except AttributeError as err:
    print("5", type(err).__name__)
print(P.__slots__, type(P.x).__name__)
```

In `answer.txt`, write the printed output, one line per printed line.

Facts you need:

- `print("1", type(err).__name__, err)` prints the label, the class name of the error and its message.
  The message of a missing attribute is `'P' object has no attribute 'y'` (with the class name of
  the object).
- `hasattr(obj, "__dict__")` is `True` if the object has an instance dictionary.
- `vars(obj)` returns `obj.__dict__`; for an object without one it raises
  `TypeError: vars() argument must have __dict__ attribute`.
- `print(tuple)` shows `('x', 'y')`. `type(P.x).__name__` is the class name of the object stored in `P.x`:
  for a slot, Python puts a *descriptor* object on the class, named `member_descriptor`.

## Example of the format

```python
class Tiny:
    __slots__ = ("a",)

t = Tiny()
try:
    print(t.a)
except AttributeError as err:
    print("empty slot:", type(err).__name__)
```

prints `empty slot: AttributeError`.
