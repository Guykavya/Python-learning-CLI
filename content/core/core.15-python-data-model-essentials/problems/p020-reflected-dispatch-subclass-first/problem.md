# Trace: which operator method runs?

For `a + b` Python follows these steps:

1. If `type(b)` is a **proper subclass** of `type(a)` **and overrides** `__radd__`, try `b.__radd__(a)` first.
2. Otherwise try `a.__add__(b)`.
3. If that returns `NotImplemented` (or `a` has no `__add__`), try `b.__radd__(a)`
   (unless it was already tried in step 1).
4. If everything declined, raise `TypeError`.

Each method below prints its name so you can follow the dispatch.

```python
class A:
    def __add__(self, other):
        print("A.add")
        return "A+"

    def __radd__(self, other):
        print("A.radd")
        return "A r+"


class B(A):
    def __radd__(self, other):
        print("B.radd")
        return "B r+"


class C:
    def __radd__(self, other):
        print("C.radd")
        return "C r+"


class D:
    def __add__(self, other):
        print("D.add")
        return NotImplemented


print(A() + A())
print(A() + B())
print(B() + A())
print(B() + B())
print(D() + C())
print(1 + A())
try:
    D() + 1
except TypeError as e:
    print("error:", e)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `int.__add__(1, other)` returns `NotImplemented` for a type it does not know.
- `print("error:", e)` prints the message of the caught `TypeError` after `error:`.
- A method that returns without a `return` statement returns `None`, and `None` is printed as `None`.

## Example of the format

```python
class Z:
    def __add__(self, other):
        print("Z.add")
        return 1

print(Z() + 5)
```

prints

```text
Z.add
1
```
