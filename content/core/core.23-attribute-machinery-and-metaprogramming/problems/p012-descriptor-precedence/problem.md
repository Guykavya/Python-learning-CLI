# Trace: data vs non-data descriptors

A **descriptor** is an object stored on a class that has `__get__` (and maybe `__set__` or
`__delete__`). The lookup rule for `obj.name` is:

1. If the class (or a base) has `name` as a **data descriptor** (it defines `__set__` or
   `__delete__`), call its `__get__`. The instance dict is not even looked at.
2. Otherwise, if `name` is in the instance `__dict__`, return that.
3. Otherwise, if the class has `name` as a **non-data descriptor** (only `__get__`), call its
   `__get__`; if it is a plain class attribute, return it.

Writing `obj.name = v` calls the data descriptor's `__set__` if there is one; otherwise it stores
`v` in the instance `__dict__`. `del obj.name` calls `__delete__` for a data descriptor, otherwise
it removes the entry from the instance `__dict__`.

Work out exactly what this program prints, one line per printed line. It needs no input.

```python
class Data:
    def __get__(self, obj, owner):
        if obj is None:
            return "Data on class"
        return "from Data"

    def __set__(self, obj, value):
        print("Data.__set__", value)


class NonData:
    def __get__(self, obj, owner):
        if obj is None:
            return "NonData on class"
        return "from NonData"


class Thing:
    d = Data()
    n = NonData()
    plain = "class attr"


t = Thing()
print(t.d, t.n, t.plain)
t.d = 1
t.n = 2
t.plain = 3
print(t.d, t.n, t.plain)
print(sorted(vars(t)))
t.__dict__["d"] = 99
print(t.d, vars(t)["d"])
del t.n
print(t.n)
try:
    del t.d
except AttributeError as e:
    print(type(e).__name__)
print(Thing.d, Thing.n)
Thing.d = "replaced"
print(t.d)
del t.d
print(t.d)
del t.plain
print(t.plain, Thing.plain)
```

Write your answer in `answer.txt`.

**Example (a different program)**

```python
class Five:
    def __get__(self, obj, owner):
        return 5

class A:
    v = Five()

a = A()
a.v = 1
print(a.v, A.v)
```

prints

```
1 5
```

(`Five` has no `__set__`, so it is a non-data descriptor: the instance value wins. Class access
calls `__get__` with `obj` set to `None`.)
